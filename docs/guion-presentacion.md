# Guion de presentación y demostración funcional

## Sugerencia de 8 diapositivas

1. **Portada.** Nombre del proyecto, equipo, curso y fecha.
2. **Objetivo y necesidad.** Administrar catálogo, controlar unidades, evitar ventas sin stock y obtener información confiable.
3. **Arquitectura.** Mostrar el árbol `src/`, la carpeta `data/` y explicar que el JSON conserva operaciones.
4. **Productos.** Registrar, consultar, editar y desactivar; destacar la prohibición de códigos duplicados.
5. **Ventas.** Explicar subtotal por línea, IVA 12 %, total, número de venta y descuento de stock.
6. **Inventario.** Mostrar entrada, ajuste, alerta de stock mínimo e historial de movimientos.
7. **Reportes y pruebas.** Presentar ingresos, producto más vendido, promedio y matriz; mencionar las 17 pruebas realizadas.
8. **GitHub y conclusión.** Mostrar la URL real del repositorio, ocho commits reales, rama, pull request, Issues y release publicados por el equipo.

## Secuencia para demostrar ante el docente

1. Iniciar con `python src/main.py`; mostrar el menú principal.
2. Elegir **1 > 1**; registrar `P010`, `Auriculares`, `Audio`, `80`, `10`, `3`.
3. Elegir **1 > 2** para consultar `P010`.
4. Volver al menú principal, ingresar en **2 > 1** y vender 2 unidades del producto `P010`. Escribir `FIN` y confirmar con `s`.
5. Mostrar el comprobante: subtotal Q160.00, IVA Q19.20 y total Q179.20.
6. Abrir **3 > 1**; comprobar que las existencias cambiaron de 10 a 8.
7. Abrir **3 > 5** y mostrar el movimiento `SALIDA_VENTA`.
8. Abrir **4 > 4**, **4 > 5** y **4 > 8** para mostrar ingresos, más vendido y matriz (vuelva al menú de reportes entre opciones).
9. Volver a Productos, intentar registrar de nuevo `P010`; mostrar el aviso de código duplicado.
10. Intentar vender 99 unidades para comprobar el rechazo por stock insuficiente.
11. Salir con la opción **5** del menú principal. Ejecutar las pruebas automáticas desde la terminal.
12. Abrir el repositorio **publicado realmente por el equipo** y enseñar commits, PR, Issues y release.

> Utilice datos ficticios. Si ya existen datos reales de una empresa,
> haga la demostración con una copia independiente del archivo JSON.

## Demostracion funcional
1. Registrar y consultar productos.
2. Registrar una venta y verificar el IVA.
3. Consultar las existencias actualizadas.
4. Mostrar alertas de stock minimo.
5. Consultar ingresos y estadisticas.

