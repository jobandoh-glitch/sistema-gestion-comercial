# Análisis de procesos del sistema

Este documento sirve de índice al análisis requerido antes de la implementación.
Cada proceso documenta objetivo, descripción, entradas, procesamiento, salidas,
reglas, validaciones, errores y su diagrama de flujo.

| Proceso | Análisis | Diagrama |
|---|---|---|
| Registro de productos | [Documento](analisis/registro-productos.md) | [Imagen](diagramas/registro-productos.png) |
| Consulta y modificación de productos | [Documento](analisis/consulta-modificacion.md) | [Imagen](diagramas/consulta-modificacion.png) |
| Registro de ventas | [Documento](analisis/registro-ventas.md) | [Imagen](diagramas/registro-ventas.png) |
| Actualización de inventario | [Documento](analisis/actualizacion-inventario.md) | [Imagen](diagramas/actualizacion-inventario.png) |
| Lectura de archivos | [Documento](analisis/lectura-archivos.md) | [Imagen](diagramas/lectura-archivos.png) |
| Generación de reportes | [Documento](analisis/generacion-reportes.md) | [Imagen](diagramas/generacion-reportes.png) |

### Simbología normalizada de los diagramas

- **Óvalo:** inicio o fin.
- **Paralelogramo:** entrada o salida de datos.
- **Rectángulo:** procesamiento.
- **Rombo:** condición, con rutas Sí y No.
- **Cilindro:** almacenamiento o lectura de archivo.
- **Flecha:** dirección del flujo; las flechas de retorno indican ciclos.

Los diagramas están disponibles en PNG para consultar, SVG para ampliar y DOT
para editar con Graphviz. Se pueden importar como imágenes en diagrams.net.
