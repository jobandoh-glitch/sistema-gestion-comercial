"""Lectura y guardado atómico de los datos permanentes en JSON."""
import json
import os
import tempfile
from pathlib import Path
from estructuras import datos_iniciales


CARPETA_PROYECTO = Path(__file__).resolve().parent.parent
RUTA_PREDETERMINADA = CARPETA_PROYECTO / "data" / "sistema.json"


def obtener_ruta(ruta=None):
    if ruta is not None:
        return Path(ruta)
    return Path(os.environ.get("SGC_DATA_FILE", str(RUTA_PREDETERMINADA)))


def verificar_estructura(datos):
    if not isinstance(datos, dict):
        raise ValueError("El archivo de datos no contiene un objeto JSON válido.")
    for campo in ("productos", "ventas", "movimientos"):
        if not isinstance(datos.get(campo), list):
            raise ValueError(f"El archivo de datos no contiene la lista '{campo}'.")
    return datos


def cargar_datos(ruta=None):
    destino = obtener_ruta(ruta)
    if not destino.exists():
        return datos_iniciales()
    try:
        with destino.open("r", encoding="utf-8") as archivo:
            datos = json.load(archivo)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"No se pudo leer {destino}: {error}") from error
    return verificar_estructura(datos)


def guardar_datos(datos, ruta=None):
    """Reemplaza UN solo archivo, para mantener productos/ventas/stock coherentes."""
    verificar_estructura(datos)
    destino = obtener_ruta(ruta)
    destino.parent.mkdir(parents=True, exist_ok=True)
    temporal = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=destino.parent,
                                         prefix="datos_", suffix=".tmp", delete=False) as archivo:
            temporal = Path(archivo.name)
            json.dump(datos, archivo, ensure_ascii=False, indent=2, allow_nan=False)
            archivo.write("\n")
            archivo.flush()
            os.fsync(archivo.fileno())
        os.replace(temporal, destino)
    finally:
        if temporal is not None and temporal.exists():
            temporal.unlink()
