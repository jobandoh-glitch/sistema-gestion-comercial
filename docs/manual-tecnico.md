# Manual técnico — Sistema de Gestión Comercial

## 1. Identificación del programa
Sistema de consola desarrollado en Python para una pequeña empresa.
Versión del código entregado: 1.0.0 (propuesta de versión; se debe publicar el tag en GitHub).
Arquitectura: aplicación local por módulos, persistencia JSON, sin dependencias externas.

## 2. Requisitos técnicos
- Windows, Linux o macOS.
- Python **3.10 o superior** (recomendado 3.11 o posterior).
- Consola, Terminal, PowerShell o terminal integrada de VS Code.
- Permiso de lectura y escritura en la carpeta `data/`.
- No requiere instalar paquetes de terceros ni base de datos.

## 3. Instalación y ejecución
1. Descargar el proyecto y extraerlo en una carpeta.
2. Abrir una terminal dentro de `sistema-gestion-comercial`.
3. En Windows ejecutar `py src/main.py`; en cualquier sistema con Python en PATH, `python src/main.py`.
4. El archivo `data/sistema.json` se crea automáticamente al realizar la primera operación guardada.
5. Para probar funciones sin alterar datos reales: `python -m unittest discover -s tests -v`.

## 4. Arquitectura y responsabilidades

| Módulo | Función |
|---|---|
| `src/main.py` | Menús, interacción, confirmación y persistencia de operaciones |
| `src/productos.py` | Registrar, buscar, listar, modificar y desactivar productos |
| `src/ventas.py` | Validaciones, ventas, IVA 12 %, salidas y matriz de ventas |
| `src/inventario.py` | Entradas, ajustes, stock mínimo, historial de movimientos |
| `src/reportes.py` | Indicadores calculados desde los registros |
| `src/archivos.py` | Lectura, validación básica y escritura atómica del JSON |
| `src/estructuras.py` | Estructuras iniciales, fecha, validaciones y moneda |
| `tests/test_sistema.py` | Pruebas automatizadas y aisladas |

## 5. Estructuras de datos

El archivo `data/sistema.json` tiene estas listas:

```json
{
  "productos": [
    {"codigo":"P001", "nombre":"Teclado", "categoria":"Electrónica", "precio":100.0,
     "cantidad":5, "stock_minimo":2, "activo":true}
  ],
  "ventas": [],
  "movimientos": []
}
```

Un registro de venta contiene: `numero`, `fecha` ISO-8601, `detalles` (lista de
`codigo`, `nombre`, `cantidad`, `precio_unitario`, `subtotal`), `subtotal`, `iva`, `total`.
Un movimiento contiene: `fecha`, `codigo`, `tipo`, `cantidad`, `descripcion`,
`existencia_anterior`, `existencia_nueva` y, para venta, `numero_venta`.

**Vectores:** las colecciones de productos, ventas y movimientos son listas de
Python. **Matriz:** `matriz_ventas()` crea filas `[número, código, cantidad,
subtotal]`; cada fila representa un producto en una venta.

## 6. Reglas y fórmulas

- Código único sin distinguir minúsculas; se normaliza a mayúsculas.
- Nombre y categoría obligatorios; precio >= Q0 con máximo dos decimales.
- Existencia inicial y stock mínimo: enteros no negativos.
- Ventas: cantidades enteras positivas, producto existente/activo y stock suficiente.
- Subtotal de cada línea = precio unitario × unidades.
- Subtotal general = suma de subtotales de línea.
- IVA = subtotal general × 0.12, redondeado a dos decimales.
- Total de venta = subtotal general + IVA.
- Valor del inventario = suma de precio de venta × existencias para productos activos.
- Total de ingresos = suma de **totales facturados con IVA**.
- Más vendido = producto con mayor suma de unidades vendidas.
- Promedio por período = suma del total de ventas del período / número de ventas del período.
- No se modifican cantidades directamente desde Gestión de Productos; se registran en Inventario.
- Los cálculos usan `Decimal` y la información monetaria se guarda en JSON como número.

## 7. Persistencia y manejo de fallos

Por defecto se usa `data/sistema.json` desde la raíz del proyecto. También se
admite la variable de entorno `SGC_DATA_FILE` apuntando a otro archivo, útil
para pruebas. La operación de guardado escribe en un archivo temporal con
codificación UTF-8 y ejecuta `os.replace` para evitar un JSON truncado en
condiciones normales. La interfaz restaura los datos anteriores en memoria si
falla la escritura. Al leer un archivo con JSON inválido, el programa se detiene
con un mensaje y **no sobrescribe el archivo**.

**Alcance:** este es un programa local para un usuario a la vez. No incluye
bloqueos multiproceso, control de usuarios, devoluciones ni facturación fiscal
formal. Para varios puestos simultáneos convendría una base de datos transaccional.

## 8. Operaciones y funciones clave

```python
registrar_producto(datos, codigo, nombre, categoria, precio, cantidad, stock_minimo)
modificar_producto(datos, codigo, nombre=None, categoria=None, precio=None, stock_minimo=None)
registrar_venta(datos, [{"codigo": "P001", "cantidad": 2}])
registrar_entrada(datos, "P001", 5, "Compra a proveedor")
ajustar_existencias(datos, "P001", 12, "Conteo físico")
promedio_ventas_por_periodo(datos, "mes")  # o dia / anio
```

Estas funciones generan excepciones `ValueError` en validaciones incorrectas.
`main.py` las captura, muestra mensajes claros y no termina el proceso por una
opción de menú inválida.

## 9. Pruebas y reproducción

Ejecute `python -m unittest discover -s tests -v`. Las pruebas usan diccionarios
en memoria y rutas temporales, por lo que **no alteran** el archivo del usuario.
Revise `docs/pruebas.md` y `evidencias/resultado-pruebas.txt`.

Para una prueba manual puede copiar `data/ejemplo.json` como `data/sistema.json`
antes de iniciar. Haga una copia de seguridad de sus datos actuales si ya existen.

## 10. Mantenimiento y copias de seguridad

Cierre el programa antes de copiar o restaurar `data/sistema.json`. Guarde una
copia periódica fuera del repositorio, por ejemplo `respaldo-2026-10-29.json`.
No edite el archivo manualmente ni haga que dos procesos escriban el mismo JSON.
El `.gitignore` excluye `data/sistema.json` para evitar publicar datos reales.

## 11. Diagramas y trazabilidad

Consulte `docs/analisis-de-procesos.md` y los seis diagramas en
`docs/diagramas`. El código está distribuido según estos procesos, y los
casos de prueba validan tanto las rutas normales como las alternativas.

## Arquitectura modular
main_gui.py administra la interfaz Tkinter. productos.py, ventas.py e inventario.py implementan las operaciones. archivos.py guarda y recupera la informacion en JSON. reportes.py calcula las estadisticas.

