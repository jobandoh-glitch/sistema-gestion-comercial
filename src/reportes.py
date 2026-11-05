"""Reportes calculados únicamente sobre información registrada."""
from collections import defaultdict
from decimal import Decimal
from estructuras import monto
from inventario import productos_bajo_minimo
from productos import listar_productos
from ventas import historial_ventas, matriz_ventas


def reporte_productos(datos):
    return listar_productos(datos)


def reporte_stock_minimo(datos):
    return productos_bajo_minimo(datos)


def reporte_ventas(datos):
    return historial_ventas(datos)


def total_ingresos(datos):
    return sum((monto(venta["total"]) for venta in datos["ventas"]), Decimal("0.00"))


def producto_mas_vendido(datos):
    cantidades = defaultdict(int)
    nombres = {}
    for venta in datos["ventas"]:
        for detalle in venta["detalles"]:
            cantidades[detalle["codigo"]] += detalle["cantidad"]
            nombres[detalle["codigo"]] = detalle["nombre"]
    if not cantidades:
        return None
    codigo = sorted(cantidades, key=lambda clave: (-cantidades[clave], clave))[0]
    return {"codigo": codigo, "nombre": nombres[codigo], "unidades": cantidades[codigo]}


def valor_inventario(datos):
    """Valor de existencias de productos activos a precio de venta."""
    return sum((monto(producto["precio"]) * producto["cantidad"]
                for producto in datos["productos"] if producto["activo"]),
               Decimal("0.00"))


def promedio_ventas_por_periodo(datos, periodo):
    """Promedio del total por transacción, agrupado por día, mes o año."""
    longitudes = {"dia": 10, "mes": 7, "anio": 4}
    if periodo not in longitudes:
        raise ValueError("El período debe ser 'dia', 'mes' o 'anio'.")
    grupos = defaultdict(list)
    for venta in datos["ventas"]:
        clave = venta["fecha"][:longitudes[periodo]]
        grupos[clave].append(monto(venta["total"]))
    return [{"periodo": clave, "ventas": len(importes),
             "total": sum(importes, Decimal("0.00")),
             "promedio": sum(importes, Decimal("0.00")) / len(importes)}
            for clave, importes in sorted(grupos.items())]


def reporte_matriz(datos):
    return matriz_ventas(datos)
