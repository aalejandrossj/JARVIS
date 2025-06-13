import os, uvicorn, json, asyncio, logging, ssl
from fastapi import FastAPI, WebSocket
from websockets import connect as ws_connect
from dotenv import load_dotenv
import asyncio, sys
from config.prompt import AGENT_PROMPT  # Prompt de sistema
from tools.functions import TOOLS # lista de tools
from tools.tools import control_device, search #funciones para las tools



load_dotenv()

# Configuración básica --------------------------------------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("Debes definir OPENAI_API_KEY")

MODEL = os.getenv("OPENAI_REALTIME_MODEL", "gpt-4o-realtime-preview-2024-10-01")
OPENAI_WS_URL = f"wss://api.openai.com/v1/realtime?model={MODEL}"

headers = {
    "Authorization": f"Bearer {OPENAI_API_KEY}",
    "OpenAI-Beta": "realtime=v1",
}

# Logging --------------------------------------------------------------------
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger(__name__)
log.info(f"Modelo: {MODEL}")
log.info(f"URL WebSocket: {OPENAI_WS_URL}")

# SSL (solo para pruebas) -----------------------------------------------------
ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

# FastAPI ---------------------------------------------------------------------
app = FastAPI()

# Parsear eventos de openai

def parse_openai_event(raw: str | bytes):
    if isinstance(raw, bytes):
        try:
            raw = raw.decode()
        except UnicodeDecodeError:
            log.debug("Bytes no decodificables desde OpenAI")
            return None
    try:
        evt = json.loads(raw)
    except json.JSONDecodeError:
        log.debug("JSON inválido desde OpenAI: %s", raw)
        return None
    return evt if isinstance(evt, dict) else None


# WebSocket /chat -------------------------------------------------------------

@app.websocket("/chat")
async def chat_endpoint(client_ws: WebSocket):
    await client_ws.accept()
    log.info("Cliente conectado")

    # Conexión con OpenAI ------------------------------------------------------
    try:
        openai_ws = await ws_connect(
            OPENAI_WS_URL,
            extra_headers=headers,
            max_size=None,
            ssl=ssl_ctx,
        )
        log.info("Conectado a OpenAI")

        # Configurar sesión con herramientas ----------------------------------
        await openai_ws.send(json.dumps({
            "type": "session.update",
            "session": {
                "modalities": ["text", "audio"],
                "instructions": AGENT_PROMPT,
                "voice": "alloy",
                "tools": TOOLS,
                "tool_choice": "auto"
            }
        }))
        log.info("Sesión configurada con herramientas")

    except Exception as e:
        log.error("Error conectando a OpenAI: %s", e)
        await client_ws.send_json({"type": "error", "error": str(e)})
        return

    # Recibir cliente → OpenAI -------------------------------------------------
    async def recv_from_client_and_forward():
        try:
            while True:
                data = await client_ws.receive_text()
                event = json.loads(data)
                log.debug("<-- Cliente: %s", event)

                if event.get("type") == "audio_chunk":
                    # Aquí se envía audio al agente
                    await openai_ws.send(json.dumps({
                        "type": "input_audio_buffer.append",
                        "audio": event["audio"],
                    }))

                elif event.get("type") == "user_message":
                    # Aquí se envía texto al agente
                    await openai_ws.send(json.dumps({
                        "type": "conversation.item.create",
                        "item": {
                            "type": "message",
                            "role": "user",
                            "content": [
                                {"type": "input_text", "text": event["text"]},
                            ],
                        },
                    }))
                    await openai_ws.send(json.dumps({"type": "response.create"}))
                    
                elif event.get("type") == "input_audio_buffer.commit":
                    # Procesar audio acumulado
                    await openai_ws.send(json.dumps({"type": "input_audio_buffer.commit"}))
                    await openai_ws.send(json.dumps({"type": "response.create"}))
                    
        except Exception:
            log.exception("Conexión cliente finalizada")

    # Recibir OpenAI → cliente -------------------------------------------------
    async def recv_from_openai_and_forward():
        try:
            async for raw in openai_ws:
                evt = parse_openai_event(raw)
                if evt is None:
                    continue
                etype = evt.get("type")
                log.debug("--> OpenAI: %s", evt)

                if etype == "response.audio.delta":
                    if chunk := evt.get("delta"):
                        await client_ws.send_json({"type": "audio_chunk", "audio": chunk})

                elif etype in (
                    "response.audio_transcript.done",
                    "conversation.item.input_audio_transcription.completed",
                ):
                    await client_ws.send_json({
                        "type": "transcript",
                        "role": "assistant" if etype.startswith("response") else "user",
                        "text": evt.get("transcript"),
                    })

                elif etype == "response.output_item.done":
                    item = evt.get("item", {})
                    if item.get("type") == "function_call":
                        try:
                            name = item.get("name")
                            if name == "control_device":
                                args = json.loads(item.get("arguments", "{}"))
                                result = await control_device(args.get("device_name", ""), args.get("state", ""))
                            elif name == "web_search":
                                args = json.loads(item.get("arguments", "{}"))
                                result = await search(args.get("text", ""))
                            else:
                                result = f"Función desconocida: {name}"
                        except Exception as e:
                            result = str(e)
                        await openai_ws.send(json.dumps({
                            "type": "conversation.item.create",
                            "item": {
                                "type": "function_call_output",
                                "call_id": item["call_id"],
                                "output": result,
                            },
                        }))
                        await openai_ws.send(json.dumps({"type": "response.create"}))


                elif etype == "error":
                    await client_ws.send_json({"type": "error", "error": evt.get("error")})
                    log.warning("Error desde OpenAI: %s", evt.get("error"))
                    
        except Exception:
            log.exception("Excepción en canal OpenAI")

    # Ejecutar corutinas -------------------------------------------------------
    try:
        await asyncio.gather(
            recv_from_client_and_forward(),
            recv_from_openai_and_forward(),
        )
    finally:
        await openai_ws.close()
        await client_ws.close()
        log.info("Conexión cerrada")

# Entrypoint ------------------------------------------------------------------
if __name__ == "__main__":
    if sys.platform.startswith("win"):
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    cfg = uvicorn.Config("main:app", host="0.0.0.0", port=8000, reload=True)
    server = uvicorn.Server(cfg)
    asyncio.run(server.serve())