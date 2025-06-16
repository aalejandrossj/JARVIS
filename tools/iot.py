import asyncio
import os
from tapo import ApiClient
import logging
from miio import Yeelight
from typing import Optional

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

class IOT:
    @staticmethod
    async def _get_device(ip: str):
        """Obtiene el dispositivo Tapo de forma asíncrona"""
        user = os.getenv("USERTAPO")
        pwd = os.getenv("PASSWORDTAPO")
        
        if not user or not pwd:
            raise ValueError("Debes definir USERTAPO y PASSWORDTAPO en las variables de entorno")
        
        api = ApiClient(user, pwd)
        return await api.p100(ip)

    @staticmethod
    async def toggle_device_async(ip: str, state: str, brand: str, color: Optional[str] = None) -> bool:
        """
        Cambia el estado del dispositivo (True = encendido, False = apagado).

        :param ip: IP del dispositivo
        :param state: 'encendido' | 'apagado'
        :returns: estado final (True si queda encendido, False si queda apagado)
        :raises ValueError: si state no es válido o ya coincide con el estado actual
        """
        if brand == "tapo":
            if state not in ("encendido", "apagado"):
                raise ValueError("state debe ser 'encendido' o 'apagado'")

            try:
                device = await IOT._get_device(ip)
                info = await device.get_device_info()
                desired_on = state == "encendido"

                log.info(f"Estado actual del dispositivo {ip}: "
                        f"{'encendido' if info.device_on else 'apagado'}")

                if info.device_on == desired_on:
                    raise ValueError(f"El dispositivo ya está {state}")

                if desired_on:
                    await device.on()
                else:
                    await device.off()

                log.info(f"Dispositivo {ip} {'encendido' if desired_on else 'apagado'}")
                return desired_on

            except Exception as e:
                log.error(f"Error controlando dispositivo {ip}: {e}")
                raise

        elif brand == "yeelight":
            token = os.getenv("TOKENYEELIGHT") or \
                    ValueError("TOKENYEELIGHT no definido")
            bulb = Yeelight(ip, token)

            try:
                if color:                      # cambiar color
                    r, g, b = map(int, color.split(","))
                    bulb.on()
                    bulb.set_rgb((r, g, b))
                    return True
                else:
                    info = bulb.status()            # estado actual
                    desired_on = state == "encendido"

                    log.info(
                        "Estado actual de %s: %s",
                        ip,
                        "encendido" if info.is_on else "apagado",
                    )

                    if info.is_on == desired_on:
                        raise ValueError(f"La luz ya está {state}")

                    bulb.on() if desired_on else bulb.off()
                    log.info("Luz %s %s", ip, "encendida" if desired_on else "apagada")
                    return desired_on

            except Exception as e:
                log.error("Error controlando dispositivo %s: %s", ip, e)
                raise                       # vuelve a propagar si lo necesitas

