"""Interfaz de consola del sistema de gestión comercial (sin dependencias extra)."""
from copy import deepcopy
from archivos import cargar_datos, guardar_datos
from estructuras import formato_dinero
from productos import (consultar_producto, desactivar_producto,
                       listar_productos, modificar_producto, registrar_producto)
from inventario import (ajustar_existencias, existencias, historial_movimientos,
                        productos_bajo_minimo, registrar_entrada)
from ventas import historial_ventas, registrar_venta
from reportes import (producto_mas_vendido, promedio_ventas_por_periodo,
                      reporte_matriz, total_ingresos, valor_inventario)


def solicitar_entero(mensaje, minimo=0):
    while True:
        entrada = input(mensaje).strip()
        try:
            numero = int(entrada)
            if numero >= minimo:
                return numero
        except ValueError:
            pass
        print(f"Error: ingrese un número entero mayor o igual a {minimo}.")


def solicitar_precio(mensaje):
    while True:
        valor = input(mensaje).strip()
        try:
            from estructuras import precio_valido
            return precio_valido(valor)
        except ValueError as error:
            print("Error:", error)


def solicitar_texto(mensaje):
    while True:
        valor = input(mensaje).strip()
        if valor:
            return valor
        print("Error: este dato no puede estar vacío.")


def mostrar_producto(producto):
    estado = "Activo" if producto["activo"] else "Desactivado"
    print(f"{producto['codigo']:<10} {producto['nombre']:<22.22} "
          f"{producto['categoria']:<16.16} {formato_dinero(producto['precio']):>12} "
          f"Disp: {producto['cantidad']:>4}  Mín: {producto['stock_minimo']:>4}  {estado}")


def mostrar_productos(productos):
    if not productos:
        print("No hay productos registrados.")
        return
    for producto in productos:
        mostrar_producto(producto)


def mostrar_venta(venta):
    print(f"\nVenta {venta['numero']} | {venta['fecha']}")
    for detalle in venta["detalles"]:
        print(f"  {detalle['codigo']} - {detalle['nombre']}: {detalle['cantidad']} x "
              f"{formato_dinero(detalle['precio_unitario'])} = "
              f"{formato_dinero(detalle['subtotal'])}")
    print(f"  Subtotal: {formato_dinero(venta['subtotal'])} | "
          f"IVA 12%: {formato_dinero(venta['iva'])} | TOTAL: {formato_dinero(venta['total'])}")


def operar_y_guardar(datos, operacion, *argumentos, **opciones):
    """Solo guarda operaciones que terminaron sin errores de validación."""
    copia = deepcopy(datos)
    try:
        resultado = operacion(datos, *argumentos, **opciones)
        guardar_datos(datos)
    except (ValueError, OSError):
        # Si falla el archivo, el programa revierte el estado de memoria.
        datos.clear()
        datos.update(copia)
        raise
    return resultado


def menu_productos(datos):
    while True:
        print("\n--- GESTIÓN DE PRODUCTOS ---")
        print("1. Registrar  2. Consultar por código  3. Listar")
        print("4. Modificar  5. Desactivar  0. Menú principal")
        opcion = input("Opción: ").strip()
        if opcion == "0":
            return
        try:
            if opcion == "1":
                codigo = solicitar_texto("Código: ")
                nombre = solicitar_texto("Nombre: ")
                categoria = solicitar_texto("Categoría: ")
                precio = solicitar_precio("Precio (Q): ")
                cantidad = solicitar_entero("Cantidad inicial: ")
                minimo = solicitar_entero("Stock mínimo: ")
                producto = operar_y_guardar(datos, registrar_producto, codigo, nombre,
                                           categoria, precio, cantidad, minimo)
                # La existencia inicial también queda en el registro del producto.
                print("Registrado:")
                mostrar_producto(producto)
            elif opcion == "2":
                producto = consultar_producto(datos, solicitar_texto("Código: "))
                mostrar_producto(producto) if producto else print("Producto no encontrado.")
            elif opcion == "3":
                mostrar_productos(listar_productos(datos))
            elif opcion == "4":
                codigo = solicitar_texto("Código del producto a modificar: ")
                producto = consultar_producto(datos, codigo)
                if producto is None:
                    print("Producto no encontrado.")
                    continue
                print("Deje en blanco lo que no desea cambiar. La cantidad se cambia en Inventario.")
                nombre = input(f"Nombre [{producto['nombre']}]: ").strip()
                categoria = input(f"Categoría [{producto['categoria']}]: ").strip()
                entrada_precio = input(f"Precio [{producto['precio']}]: ").strip()
                entrada_minimo = input(f"Stock mínimo [{producto['stock_minimo']}]: ").strip()
                precio = None
                minimo = None
                if entrada_precio:
                    from estructuras import precio_valido
                    precio = precio_valido(entrada_precio)
                if entrada_minimo:
                    minimo = int(entrada_minimo)
                modificado = operar_y_guardar(datos, modificar_producto, codigo,
                                              nombre or None, categoria or None,
                                              precio, minimo)
                print("Producto actualizado:")
                mostrar_producto(modificado)
            elif opcion == "5":
                codigo = solicitar_texto("Código: ")
                confirmar = input("¿Desactivar este producto? (s/n): ").strip().lower()
                if confirmar == "s":
                    operar_y_guardar(datos, desactivar_producto, codigo)
                    print("Producto desactivado.")
                else:
                    print("Operación cancelada.")
            else:
                print("Opción inválida, intente nuevamente.")
        except (ValueError, OSError) as error:
            print("Error:", error)


def menu_ventas(datos):
    while True:
        print("\n--- REGISTRO DE VENTAS ---")
        print("1. Nueva venta  2. Historial  0. Menú principal")
        opcion = input("Opción: ").strip()
        if opcion == "0":
            return
        try:
            if opcion == "1":
                items = []
                print("Ingrese productos. Escriba FIN en el código para terminar.")
                while True:
                    codigo = solicitar_texto("Código (o FIN): ").upper()
                    if codigo == "FIN":
                        break
                    cantidad = solicitar_entero("Cantidad: ", minimo=1)
                    items.append({"codigo": codigo, "cantidad": cantidad})
                if not items:
                    print("Venta cancelada: no se agregaron productos.")
                    continue
                confirmar = input("¿Confirmar la venta? (s/n): ").strip().lower()
                if confirmar != "s":
                    print("Venta cancelada.")
                    continue
                venta = operar_y_guardar(datos, registrar_venta, items)
                mostrar_venta(venta)
                print("Venta guardada e inventario actualizado.")
            elif opcion == "2":
                ventas = historial_ventas(datos)
                if not ventas:
                    print("No hay ventas registradas.")
                for venta in ventas:
                    mostrar_venta(venta)
            else:
                print("Opción inválida, intente nuevamente.")
        except (ValueError, OSError) as error:
            print("Error:", error)


def menu_inventario(datos):
    while True:
        print("\n--- CONTROL DE INVENTARIO ---")
        print("1. Consultar existencias  2. Entrada  3. Ajustar cantidad")
        print("4. Stock mínimo  5. Historial movimientos  0. Menú principal")
        opcion = input("Opción: ").strip()
        if opcion == "0":
            return
        try:
            if opcion == "1":
                mostrar_productos(existencias(datos))
            elif opcion == "2":
                codigo = solicitar_texto("Código: ")
                cantidad = solicitar_entero("Unidades a ingresar: ", minimo=1)
                descripcion = solicitar_texto("Descripción (ej. Compra a proveedor): ")
                movimiento = operar_y_guardar(datos, registrar_entrada, codigo,
                                              cantidad, descripcion)
                print("Entrada registrada. Nueva existencia:", movimiento["existencia_nueva"])
            elif opcion == "3":
                codigo = solicitar_texto("Código: ")
                cantidad = solicitar_entero("Cantidad real después del ajuste: ")
                descripcion = solicitar_texto("Motivo del ajuste: ")
                movimiento = operar_y_guardar(datos, ajustar_existencias, codigo,
                                              cantidad, descripcion)
                print("Ajuste registrado:", movimiento["tipo"])
            elif opcion == "4":
                bajos = productos_bajo_minimo(datos)
                if not bajos:
                    print("Ningún producto activo está en stock mínimo o por debajo.")
                else:
                    mostrar_productos(bajos)
            elif opcion == "5":
                movimientos = historial_movimientos(datos)
                if not movimientos:
                    print("No hay movimientos registrados.")
                for mov in movimientos:
                    print(f"{mov['fecha']} | {mov['codigo']} | {mov['tipo']} | "
                          f"Unidades: {mov['cantidad']} | {mov['existencia_anterior']} -> "
                          f"{mov['existencia_nueva']} | {mov['descripcion']}")
            else:
                print("Opción inválida, intente nuevamente.")
        except (ValueError, OSError) as error:
            print("Error:", error)


def menu_reportes(datos):
    while True:
        print("\n--- REPORTES Y ESTADÍSTICAS ---")
        print("1. Productos  2. Stock mínimo  3. Historial ventas")
        print("4. Ingresos  5. Más vendido  6. Valor inventario")
        print("7. Promedio por período  8. Matriz de ventas  0. Menú principal")
        opcion = input("Opción: ").strip()
        if opcion == "0":
            return
        if opcion == "1":
            mostrar_productos(listar_productos(datos))
        elif opcion == "2":
            mostrar_productos(productos_bajo_minimo(datos))
        elif opcion == "3":
            ventas = historial_ventas(datos)
            if not ventas:
                print("No hay ventas registradas.")
            for venta in ventas:
                mostrar_venta(venta)
        elif opcion == "4":
            print("Total de ingresos por ventas:", formato_dinero(total_ingresos(datos)))
        elif opcion == "5":
            mayor = producto_mas_vendido(datos)
            if mayor is None:
                print("Aún no hay ventas.")
            else:
                print(f"Más vendido: {mayor['codigo']} - {mayor['nombre']} "
                      f"({mayor['unidades']} unidades)")
        elif opcion == "6":
            print("Valor de inventario activo a precio de venta:",
                  formato_dinero(valor_inventario(datos)))
        elif opcion == "7":
            periodo = input("Período (1=día, 2=mes, 3=año): ").strip()
            opcion_periodo = {"1": "dia", "2": "mes", "3": "anio"}.get(periodo)
            if opcion_periodo is None:
                print("Período inválido.")
                continue
            resultados = promedio_ventas_por_periodo(datos, opcion_periodo)
            if not resultados:
                print("No hay ventas en el archivo.")
            for fila in resultados:
                print(f"{fila['periodo']}: {fila['ventas']} ventas | "
                      f"Total: {formato_dinero(fila['total'])} | "
                      f"Promedio: {formato_dinero(fila['promedio'])}")
        elif opcion == "8":
            filas = reporte_matriz(datos)
            if not filas:
                print("No hay datos para la matriz.")
            for numero, codigo, cantidad, subtotal in filas:
                print(f"[{numero}, {codigo}, {cantidad}, {formato_dinero(subtotal)}]")
        else:
            print("Opción inválida, intente nuevamente.")


def main():
    try:
        datos = cargar_datos()
    except ValueError as error:
        print("Error al cargar la información:", error)
        print("Revise el archivo de datos antes de continuar. No fue modificado.")
        return 1
    print("=== SISTEMA DE GESTIÓN COMERCIAL ===")
    try:
        while True:
            print("\n--- MENÚ PRINCIPAL ---")
            print("1. Gestión de productos")
            print("2. Registro de ventas")
            print("3. Control de inventario")
            print("4. Reportes y estadísticas")
            print("5. Salir")
            opcion = input("Seleccione una opción: ").strip()
            if opcion == "1":
                menu_productos(datos)
            elif opcion == "2":
                menu_ventas(datos)
            elif opcion == "3":
                menu_inventario(datos)
            elif opcion == "4":
                menu_reportes(datos)
            elif opcion == "5":
                print("Gracias por utilizar el sistema. Hasta pronto.")
                return 0
            else:
                print("Opción inválida. El sistema sigue funcionando.")
    except (KeyboardInterrupt, EOFError):
        print("\nSesión finalizada de forma controlada.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
