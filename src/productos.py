"""Alta, búsqueda, consulta, edición y desactivación de productos."""
from estructuras import (cantidad_valida, codigo_valido, precio_valido,
                         texto_valido)


def consultar_producto(datos, codigo):
    codigo = codigo_valido(codigo)
    for producto in datos["productos"]:
        if producto["codigo"] == codigo:
            return producto
    return None


def listar_productos(datos):
    return sorted(datos["productos"], key=lambda producto: producto["codigo"])


def registrar_producto(datos, codigo, nombre, categoria, precio, cantidad, stock_minimo):
    codigo = codigo_valido(codigo)
    nombre = texto_valido(nombre, "nombre")
    categoria = texto_valido(categoria, "categoría")
    precio = precio_valido(precio)
    cantidad = cantidad_valida(cantidad)
    stock_minimo = cantidad_valida(stock_minimo, "stock mínimo")
    if consultar_producto(datos, codigo) is not None:
        raise ValueError("Ya existe un producto con ese código.")
    producto = {"codigo": codigo, "nombre": nombre, "categoria": categoria,
                "precio": precio, "cantidad": cantidad,
                "stock_minimo": stock_minimo, "activo": True}
    datos["productos"].append(producto)
    return producto


def modificar_producto(datos, codigo, nombre=None, categoria=None,
                       precio=None, stock_minimo=None):
    producto = consultar_producto(datos, codigo)
    if producto is None:
        raise ValueError("No existe un producto con ese código.")
    # Se valida todo antes de modificar para no dejar cambios parciales.
    cambios = {}
    if nombre is not None:
        cambios["nombre"] = texto_valido(nombre, "nombre")
    if categoria is not None:
        cambios["categoria"] = texto_valido(categoria, "categoría")
    if precio is not None:
        cambios["precio"] = precio_valido(precio)
    if stock_minimo is not None:
        cambios["stock_minimo"] = cantidad_valida(stock_minimo, "stock mínimo")
    producto.update(cambios)
    return producto


def desactivar_producto(datos, codigo):
    producto = consultar_producto(datos, codigo)
    if producto is None:
        raise ValueError("No existe un producto con ese código.")
    if not producto["activo"]:
        raise ValueError("El producto ya está desactivado.")
    producto["activo"] = False
    return producto
