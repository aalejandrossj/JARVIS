from miio import MiotDevice, DeviceException
import logging

log = logging.getLogger(__name__)

IP    = "192.168.1.132"
TOKEN = "71533875324c34576c5a42546d735647"

vac = MiotDevice(IP, TOKEN, model="xiaomi.vacuum.c102gl")

def _accion(siid: int, aiid: int) -> bool:
    """Devuelve True si el robot aceptó la orden."""
    try:
        res = vac.call_action_by(siid, aiid)          # sin timeout extra
        return isinstance(res, list) and res and res[0].get("code") == 0
    except DeviceException as e:
        log.error("Acción %s.%s falló: %s", siid, aiid, e)
        return False

def encender() -> bool:        # Start Sweep
    return _accion(2, 1)

def apagar() -> bool:          # Stop Sweep
    return _accion(2, 2)

def volver_a_base() -> bool:   # Start Charge
    return _accion(3, 1)

def run(status: str) -> str:
    status = status.lower()
    if status == "encendido":
        return "OK" if encender() else "error"
    if status == "apagado":
        return "OK" if apagar() else "error"
    if status == "volver_a_base":
        return "OK" if volver_a_base() else "error"
    raise ValueError("Status no válido")