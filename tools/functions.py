TOOLS = [
  {
    "type": "function",
    "name": "control_device",
    "description": "Controla dispositivos domóticos Tapo: enciende o apaga según el estado indicado",
    "parameters": {
      "type": "object",
      "properties": {
        "device_name": {
          "type": "string",
          "description": "Nombre del dispositivo a controlar (p. ej. 'luz habitación', 'televisor cocina', 'calefactor cocina')"
        },
        "state": {
          "type": "string",
          "description": "Estado al que se quiere pasar el dispositivo",
          "enum": ["encendido", "apagado"]
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
  }
]
