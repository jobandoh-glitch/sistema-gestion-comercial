"""Validaciones y estructuras compartidas del sistema comercial."""
from datetime import datetime
from decimal import Decimal, InvalidOperation


def datos_iniciales():
    """Estructura que se almacena en el archivo JSON."""
    return {"productos": [], "ventas": [], "movimientos": []}


def fecha_actual():
    return datetime.now().astimezone().isoformat(timespec="seconds")


def codigo_valido(codigo):
    if not isinstance(codigo, str) or not codigo.strip():
        raise ValueError("El código del producto es obligatorio.")
    return codigo.strip().upper()


def texto_valido(valor, campo):
    if not isinstance(valor, str) or not valor.strip():
        raise ValueError(f"El campo {campo} no puede estar vacío.")
    return valor.strip()


def cantidad_valida(valor, campo="cantidad", minimo=0):
    # bool también es int en Python; aquí NO se acepta.
    if type(valor) is not int or valor < minimo:
        raise ValueError(f"{campo.capitalize()}: ingrese un número entero mayor o igual a {minimo}.")
    return valor


def precio_valido(valor):
    try:
        numero = Decimal(str(valor))
    except (InvalidOperation, ValueError):
        raise ValueError("El precio debe ser numérico.") from None
    if not numero.is_finite() or numero < 0:
        raise ValueError("El precio no puede ser negativo ni infinito.")
    if numero != numero.quantize(Decimal("0.01")):
        raise ValueError("El precio puede tener máximo dos decimales.")
    return float(numero)


def monto(valor):
    """Para calcular importes sin los errores binarios de float."""
    return Decimal(str(valor)).quantize(Decimal("0.01"))


def formato_dinero(valor):
    return f"Q{monto(valor):,.2f}"
