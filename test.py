# test_color.py
import argparse
from miio import Yeelight

def set_color(ip: str, token: str, r: int, g: int, b: int):
    """
    Enciende la Yeelight y la cambia al color RGB dado.
    La librería espera un iterable de tres enteros: [R, G, B].
    """
    bulb = Yeelight(ip, token)
    try:
        bulb.on()  # asegurar que esté encendida
        bulb.set_rgb((r, g, b))  # pasar una tupla de tres elementos
        print(f"✅ Color puesto a RGB({r}, {g}, {b})")
    except Exception as e:
        print(f"❌ Error cambiando color: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="Cambia la Yeelight a un color RGB")
    parser.add_argument("ip",    help="IP de la bombilla")
    parser.add_argument("token", help="Token de 32 hex")
    parser.add_argument("R",     type=int, help="Rojo (0–255)")
    parser.add_argument("G",     type=int, help="Verde (0–255)")
    parser.add_argument("B",     type=int, help="Azul (0–255)")
    args = parser.parse_args()

    set_color(args.ip, args.token, args.R, args.G, args.B)

if __name__ == "__main__":
    main()
