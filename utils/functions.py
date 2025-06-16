from utils.dispositivos import DEVICE_IPS

names = [name for name in DEVICE_IPS.keys()]

TOOLS = [
  {
    "type": "function",
    "name": "control_device",
    "description": "Controla dispositivos domóticos: enciende o apaga según el estado indicado",
    "parameters": {
      "type": "object",
      "properties": {
        "device_name": {
          "type": "string",
          "description": f"Nombre del dispositivo a controlar (p. ej. {', '.join(names)})"
        },
        "state": {
          "type": "string",
          "description": "Estado al que se quiere pasar el dispositivo",
          "enum": ["encendido", "apagado"]
        },
        "color": {
        "type": "string",
        "description": "Nuevo color en formato \"R,G,B\" (0-255). Solo válido para luces Yeelight, si no se especifica, se mantiene el color actual"
      }
      },
      "required": ["device_name", "state"]
    }
  },
  {
    "type": "function",
    "name": "web_search",
    "description": "Realiza una búsqueda en internet y devuelve los resultados más relevantes",
    "parameters": {
      "type": "object",
      "properties": {
        "text": {
          "type": "string",
          "description": "Cadena de texto a buscar (no vacía)",
          "minLength": 1
        }
      },
      "required": ["text"]
    }
  },
  {
    "type": "function",
    "name": "limpieza",
    "description": "Controla la limpieza del robot aspirador",
    "parameters": {
      "type": "object",
      "properties": {
        "status": {
          "type": "string",
          "description": "Estado al que se quiere pasar el dispositivo",
          "enum": ["encendido", "apagado", "volver_a_base"]
        }
      },
      "required": ["status"]
    }
  }
]

