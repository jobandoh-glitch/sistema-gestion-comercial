"""Ventas con validación de stock, IVA del 12 % y registro permanente."""
from decimal import Decimal, ROUND_HALF_UP
from estructuras import cantidad_valida, codigo_valido, fecha_actual, monto
from productos import consultar_producto
from inventario import crear_movimiento

IVA = Decimal("0.12")


def siguiente_numero(datos):
    numeros = []
    for venta in datos["ventas"]:
        numero = str(venta.get("numero", ""))
        if numero.startswith("V") and numero[1:].isdigit():
            numeros.append(int(numero[1:]))
    return f"V{max(numeros, default=0) + 1:04d}"


def registrar_venta(datos, items):
    """items: lista de {'codigo': 'P001', 'cantidad': 2}."""
    if not isinstance(items, list) or not items:
        raise ValueError("La venta debe incluir al menos un producto.")

    # Un mismo producto puede aparecer varias veces: acumulamos su cantidad.
    cantidades = {}
    for item in items:
        if not isinstance(item, dict):
            raise ValueError("El detalle de la venta no es válido.")
        codigo = codigo_valido(item.get("codigo"))
        cantidad = cantidad_valida(item.get("cantidad"), minimo=1)
        cantidades[codigo] = cantidades.get(codigo, 0) + cantidad

    # Se comprueba TODO el pedido antes de descontar UNA sola unidad.
    detalles = []
    subtotal = Decimal("0.00")
    for codigo, cantidad in cantidades.items():
        producto = consultar_producto(datos, codigo)
        if producto is None:
            raise ValueError(f"El producto {codigo} no existe.")
        if not producto["activo"]:
            raise ValueError(f"El producto {codigo} está desactivado.")
        if producto["cantidad"] < cantidad:
            raise ValueError(f"Inventario insuficiente para {codigo}: "
                             f"hay {producto['cantidad']} y se piden {cantidad}.")
        precio = monto(producto["precio"])
        importe = precio * cantidad
        detalles.append({"codigo": codigo, "nombre": producto["nombre"],
                         "cantidad": cantidad, "precio_unitario": float(precio),
                         "subtotal": float(importe)})
        subtotal += importe

    iva = (subtotal * IVA).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    total = subtotal + iva
    numero = siguiente_numero(datos)
    venta = {"numero": numero, "fecha": fecha_actual(), "detalles": detalles,
             "subtotal": float(subtotal), "iva": float(iva), "total": float(total)}

    # Todo se mantiene en un único diccionario y un único archivo al guardar.
    for detalle in detalles:
        producto = consultar_producto(datos, detalle["codigo"])
        anterior = producto["cantidad"]
        producto["cantidad"] -= detalle["cantidad"]
        crear_movimiento(datos, detalle["codigo"], "SALIDA_VENTA",
                         detalle["cantidad"], f"Venta {numero}",
                         anterior, producto["cantidad"], numero)
    datos["ventas"].append(venta)
    return venta


def historial_ventas(datos):
    return list(datos["ventas"])


def matriz_ventas(datos):
    """Matriz (lista de filas): [venta, código, unidades, subtotal de línea]."""
    matriz = []
    for venta in datos["ventas"]:
        for detalle in venta["detalles"]:
            matriz.append([venta["numero"], detalle["codigo"],
                           detalle["cantidad"], detalle["subtotal"]])
    return matriz
