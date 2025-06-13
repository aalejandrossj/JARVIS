import logging, asyncio
from tools.iot import IOT
from tools.search import WebFinder
from config.dispositivos import DEVICE_IPS 
import json

# Logging --------------------------------------------------------------------
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger(__name__)


async def control_device(device_name: str, state: str) -> str:
    """Recibe nombre de dispositivo, ejecuta toggle y devuelve estado ('on'/'off')."""
    log.info(f"Intentando controlar dispositivo: {device_name}")
    
    desired_state = state

    ip = DEVICE_IPS.get(device_name.lower())
    if not ip:
        log.error(f"Dispositivo '{device_name}' no encontrado en DEVICE_IPS")
        return "unknown-device"
    
    log.info(f"IP encontrada para '{device_name}': {ip}")
    
    try:
        iot = IOT()
        state = await iot.toggle_device_async(ip, desired_state)
        log.info(f"Dispositivo '{device_name}' controlado exitosamente. Estado: {'encendido' if state else 'apagado'}")
        return "on" if state else "off"
    except Exception as e:
        log.error(f"Error controlando {device_name}: {e}")
        return f"error: {e}"
    
async def search(text: str):
    try:
        wf = WebFinder()
        log.info("Buscando"+text)
        content = await wf.find_and_crawl(text, 3)
        return json.dumps(content, ensure_ascii=False)
    except Exception as e:
        log.exception(e)
        return f"error: {e}"
    

if __name__ == "__main__":
    result = asyncio.run(search("hola"))
    print(result)