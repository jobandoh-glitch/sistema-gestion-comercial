# Pruebas del sistema

## Objetivo y entorno

Comprobar registro, ventas, inventario, archivos, reportes y la matriz, incluso
con datos anómalos. Entorno de ejecución: Python 3.13 sobre Linux, usando
`unittest` de la biblioteca estándar. Pruebas ejecutadas sobre datos ficticios
independientes; no se necesitó un servidor externo.

**Comando:** `python -m unittest discover -s tests -v`

## Casos, datos, resultados y conclusiones

| Caso | Prueba | Datos utilizados | Resultado esperado | Resultado obtenido | Conclusión |
|---|---|---|---|---|---|
| 01 | Alta válida | P001, Teclado, Q100, 5 ud | Producto almacenado | Se consulta P001 y existen 2 artículos | Correcto |
| 02 | Código duplicado | Registrar de nuevo P001 | Error: código existente; sin alta | ValueError; catálogo permanece en 2 artículos | Correcto |
| 03 | Datos inválidos | Precio -1, cantidad -5, texto abc, 2.5 y 1.999 | Rechazar las entradas | Los cinco tipos inválidos se rechazan | Correcto |
| 04 | Consulta y edición | Código NOEXISTE; edición P001 Q120 | Ausente devuelve vacío; cambio correcto | Consulta ausente y edición confirmada | Correcto |
| 05 | Desactivación | Desactivar P001 y vender 1 | Venta rechazada | Venta rechazada por estado inactivo | Correcto |
| 06 | Venta sin stock | P001 x1, P002 x50 | Rechazar todo y no descontar | Comparación íntegra confirma que nada cambió | Correcto |
| 07 | IVA y existencias | P001 x2 y P002 x1 | Subtotal 250, IVA 30, total 280 | Q250 / Q30 / Q280, stock 3 y 2 | Correcto |
| 08 | Códigos repetidos | P001 x2 y P001 x3 | Sumar 5 unidades, una línea | 1 línea por 5; existencia 0 | Correcto |
| 09 | Cantidades inválidas | 0, -2, dos, 2.5 | Rechazar y no registrar ventas | Ninguna venta se creó | Correcto |
| 10 | Movimientos | Entrada 3; ajuste a 7 | Registrar saldo 8 y ajuste a 7 | Dos movimientos; ajuste de salida | Correcto |
| 11 | Stock mínimo | P001 5/mín 2; P002 3/mín 3 | Alertar únicamente P002 | Se detectó P002 | Correcto |
| 12 | Reportes y matriz | Venta P001 x2 y P002 x1 | Ingreso Q280, inventario Q400, matriz dos filas | 280, 400, filas V0001/P001 y V0001/P002 | Correcto |
| 13 | Promedio por período | Venta de Q112 y otra de Q56 | Total Q168, media Q84 en día/mes/año | Resultado 168 y 84 en los 3 agrupamientos | Correcto |
| 14 | Guardar y leer | Persistencia JSON temporal | Recuperar datos y venta V0001 | Datos completos iguales a los guardados | Correcto |
| 15 | Archivo corrupto | Contenido {archivo_dañado | Mostrar error sin sobrescribir | ValueError y contenido intacto | Correcto |
| 16 | Menú inválido | Elegir 99 y después 5 | Mostrar aviso y terminar normalmente | Retorno 0 y mensajes esperados | Correcto |
| 17 | Centavos de IVA | Cable Q0.05 x1 | IVA Q0.01, total Q0.06 | 0.01 y 0.06 | Correcto |

## Evidencias

- [`resultado-pruebas.txt`](../evidencias/resultado-pruebas.txt): salida real del
  comando de prueba, con los 17 casos y resultado `OK`.
- [`01-productos.png`](../evidencias/01-productos.png): menú y registro de un producto.
- [`02-venta.png`](../evidencias/02-venta.png): subtotal, IVA, total y registro de venta.
- [`03-reportes.png`](../evidencias/03-reportes.png): reporte de ingresos, matriz y salida.
- [`04-errores.png`](../evidencias/04-errores.png): código duplicado y venta sin stock.

Las imágenes son capturas renderizadas a partir de la **salida real** de una
sesión de terminal ejecutada con entradas automatizadas; muestran datos
ficticios. Para la presentación final, el equipo puede adjuntar además capturas
propias de VS Code o Windows y capturas de GitHub en `evidencias/github/`.

## Conclusión general

Los 17 casos definidos dieron resultado correcto en la ejecución registrada.
Las pruebas automáticas no sustituyen una demostración manual ni validan el
comportamiento bajo acceso concurrente, que queda fuera del alcance.
