"""Existencias, entradas, ajustes y movimientos de inventario."""
from estructuras import cantidad_valida, fecha_actual, texto_valido
from productos import consultar_producto, listar_productos


def existencias(datos):
    return listar_productos(datos)


def productos_bajo_minimo(datos):
    return [producto for producto in listar_productos(datos)
            if producto["activo"] and producto["cantidad"] <= producto["stock_minimo"]]


def historial_movimientos(datos):
    return list(datos["movimientos"])


def crear_movimiento(datos, codigo, tipo, cantidad, descripcion, anterior, nuevo,
                     numero_venta=None):
    movimiento = {"fecha": fecha_actual(), "codigo": codigo, "tipo": tipo,
                  "cantidad": cantidad, "descripcion": descripcion,
                  "existencia_anterior": anterior, "existencia_nueva": nuevo}
    if numero_venta is not None:
        movimiento["numero_venta"] = numero_venta
    datos["movimientos"].append(movimiento)
    return movimiento


def registrar_entrada(datos, codigo, cantidad, descripcion):
    producto = consultar_producto(datos, codigo)
    if producto is None:
        raise ValueError("No existe un producto con ese código.")
    if not producto["activo"]:
        raise ValueError("No se pueden ingresar unidades a un producto desactivado.")
    cantidad = cantidad_valida(cantidad, minimo=1)
    descripcion = texto_valido(descripcion, "descripción")
    anterior = producto["cantidad"]
    producto["cantidad"] += cantidad
    return crear_movimiento(datos, producto["codigo"], "ENTRADA", cantidad,
                           descripcion, anterior, producto["cantidad"])


def ajustar_existencias(datos, codigo, nueva_cantidad, descripcion):
    producto = consultar_producto(datos, codigo)
    if producto is None:
        raise ValueError("No existe un producto con ese código.")
    if not producto["activo"]:
        raise ValueError("No se pueden ajustar existencias de un producto desactivado.")
    nueva_cantidad = cantidad_valida(nueva_cantidad, "nueva cantidad")
    descripcion = texto_valido(descripcion, "descripción")
    anterior = producto["cantidad"]
    diferencia = nueva_cantidad - anterior
    if diferencia == 0:
        raise ValueError("La nueva cantidad es igual a la cantidad registrada.")
    producto["cantidad"] = nueva_cantidad
    tipo = "AJUSTE_ENTRADA" if diferencia > 0 else "AJUSTE_SALIDA"
    return crear_movimiento(datos, producto["codigo"], tipo, abs(diferencia),
                           descripcion, anterior, nueva_cantidad)
