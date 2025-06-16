import logging, asyncio
from tools.iot import IOT
from tools.search import WebFinder
from utils.dispositivos import DEVICE_IPS 
import json
from tools.limpieza import run
from typing import Optional

# Logging --------------------------------------------------------------------
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
log = logging.getLogger(__name__)


async def control_device(device_name: str, state: str, color: Optional[str] = None) -> str:
    log.info("Intentando controlar dispositivo: %s", device_name)

    ip, brand = DEVICE_IPS.get(device_name.lower(), (None, None))
    if not ip:
        log.error("Dispositivo '%s' no encontrado", device_name)
        return "unknown-device"

    iot = IOT()
    try:
        final_state = await iot.toggle_device_async(ip, state, brand, color)
        return "on" if final_state else "off"
    except Exception as e:
        log.error("Error controlando %s: %s", device_name, e)
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
    
def limpieza(status: str):
    try:
        log.info(f"Limpieza: {status}")
        run(status)
        return f"Se ha {status} el robot aspirador"           
    except Exception as e:
        log.exception(e)
        return f"error: {e}"
