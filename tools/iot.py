import asyncio
import os
from tapo import ApiClient
import logging
from miio import Yeelight

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
    async def toggle_device_async(ip: str, state: str, brand: str) -> bool:
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
            if state not in ("encendido", "apagado"):
                raise ValueError("state debe ser 'encendido' o 'apagado'")
            
            token = os.getenv("TOKENYEELIGHT")
            if not token:
                raise ValueError("Debes definir TOKENYEELIGHT en las variables de entorno")

            luz = Yeelight(ip, token)

            try:
                info = luz.status()            # estado actual
                desired_on = state == "encendido"

                log.info(
                    "Estado actual de %s: %s",
                    ip,
                    "encendido" if info.is_on else "apagado",
                )

                if info.is_on == desired_on:
                    raise ValueError(f"La luz ya está {state}")

                luz.on() if desired_on else luz.off()
                log.info("Luz %s %s", ip, "encendida" if desired_on else "apagada")
                return desired_on

            except Exception:
                log.error(f"Error controlando dispositivo {ip}: {e}")
                raise
