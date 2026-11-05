# Sistema de Gestión Comercial — Python

Aplicación para gestionar **productos**, **ventas**, **inventario** y **reportes**
de una pequeña empresa. Funciona en consola, usa **Python estándar** y guarda
los datos en **JSON**, incluso cuando se cierra el programa.

## Iniciar en 3 pasos

1. Tener instalado Python 3.10 o posterior.
2. Descargar este repositorio y abrir la terminal en su carpeta raíz.
3. Ejecutar:

```bash
python src/main.py
```

En Windows puede usar `py src/main.py`. No se requiere `pip install`.
**Elegir 5 en el menú principal para salir**; elegir 0 para regresar desde un submenú.

## Funcionalidades

- **Productos:** registrar, consultar, listar, editar y desactivar; códigos
  únicos, validación de números y rangos.
- **Ventas:** varios artículos, validación de stock, factura con IVA 12 %,
  número automático, descuento de existencias e historial.
- **Inventario:** entradas, ajustes con motivo, alertas de mínimo e historial.
- **Reportes:** productos, alertas, ventas, ingresos, más vendido, valor de
  inventario, promedios por día/mes/año y matriz de venta.
- **Persistencia:** `data/sistema.json` se crea al guardar por primera vez.
  Si está corrupto, el programa informa el error sin reemplazarlo.

## Estructura

```text
sistema-gestion-comercial/
├── README.md
├── .gitignore
├── requirements.txt
├── src/
│   ├── main.py
│   ├── productos.py
│   ├── ventas.py
│   ├── inventario.py
│   ├── archivos.py
│   ├── reportes.py
│   └── estructuras.py
├── data/
│   ├── .gitkeep
│   └── ejemplo.json                 # solo datos ficticios para practicar
├── tests/
│   └── test_sistema.py
├── docs/
│   ├── analisis-de-procesos.md
│   ├── analisis/                # seis análisis detallados
│   ├── diagramas/               # seis diagramas DOT, PNG y SVG
│   ├── manual-tecnico.md
│   ├── manual-usuario.md
│   ├── pruebas.md
│   └── github-paso-a-paso.md
└── evidencias/
    ├── resultado-pruebas.txt
    └── capturas PNG
```

## Ejecutar las pruebas

Desde la raíz del proyecto:

```bash
python -m unittest discover -s tests -v
```

Los 17 casos están en `tests/test_sistema.py`; usan datos temporales o en
memoria y no alteran los datos del usuario. Los resultados y las capturas de
una ejecución automatizada están en `evidencias/`.

## Cargar un ejemplo ficticio (opcional)

Para experimentar con productos, ventas y reportes precargados, **siempre haga
una copia de seguridad si ya tiene datos**. Después copie `data/ejemplo.json`
a `data/sistema.json` antes de ejecutar. Para empezar vacío, no copie el archivo.

## Documentación

- [Índice de análisis y diagramas](docs/analisis-de-procesos.md)
- [Manual técnico](docs/manual-tecnico.md)
- [Manual de usuario](docs/manual-usuario.md)
- [Pruebas y casos documentados](docs/pruebas.md)
- [Pasos para GitHub: commits, rama, PR, Issues y release](docs/github-paso-a-paso.md)
- [Guion de presentación y demostración](docs/guion-presentacion.md)

## Nota para entrega académica

Los archivos de código, análisis, diagramas, manuales y pruebas están incluidos.
**Publicar el repositorio, obtener un enlace público, registrar ocho commits
reales, acreditar aportes de cada integrante, crear un pull request, abrir
Issues y publicar la etiqueta/release son tareas del equipo en GitHub.**
No se han creado acciones en cuentas externas ni se afirma que existan.
Revise los textos y registre las evidencias de su propia demostración.

## Privacidad y limitaciones

No suba contraseñas, credenciales ni datos personales. `data/sistema.json` está
excluido mediante `.gitignore`. El programa está pensado para **un operador a
la vez**; para acceso simultáneo haría falta una base de datos transaccional.

## Ejecutar interfaz grafica
Abrir una terminal en la carpeta principal y ejecutar: uv run --python 3.14 src/main_gui.py

