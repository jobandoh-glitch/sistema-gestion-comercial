# Guía de publicación y evaluación en GitHub

## 1. Crear el repositorio

1. Inicie sesión en https://github.com y pulse **New repository**.
2. Nombre sugerido: `sistema-gestion-comercial-python`.
3. Seleccione **Public**. Si sube los archivos de este paquete, no necesita
   generar un README adicional en la web (ya está incluido).
4. Cree el repositorio y copie su URL HTTPS.

Desde la terminal, en la carpeta del proyecto:

```bash
git init
git branch -M main
git add .
git commit -m "Inicializar estructura y documentación base"
git remote add origin https://github.com/USUARIO/sistema-gestion-comercial-python.git
git push -u origin main
```

**Importante:** esta descarga contiene un proyecto completo; subirlo de una
sola vez **no demuestra ocho etapas reales de trabajo**. Para obtener ocho
commits significativos, el equipo debe registrar cambios auténticos durante
su revisión, corrección y mejora del proyecto (véase tabla). No simule
historial de otras personas.

## 2. Plan de ocho commits significativos (ejemplos)

Cada fila representa una modificación real que el equipo debe implementar,
revisar y confirmar por separado; cada commit debe incluir los archivos
modificados. No ejecute los ocho commits sin haber hecho cambios.

| Etapa | Mensaje sugerido, cuando exista el cambio |
|---|---|
| 1 | `Agregar estructura inicial y configuración de archivos` |
| 2 | `Implementar validaciones para registro y consulta de productos` |
| 3 | `Incorporar edición y desactivación de productos` |
| 4 | `Desarrollar registro de ventas con IVA y control de stock` |
| 5 | `Añadir entradas, ajustes e historial de inventario` |
| 6 | `Calcular estadísticas a partir de ventas y existencias` |
| 7 | `Documentar procesos y agregar diagramas de flujo` |
| 8 | `Añadir pruebas automatizadas y capturas de ejecución` |

Para revisar los commits existentes:

```bash
git log --oneline --decorate --all
```

### Participación del equipo

Cada integrante configura su propio Git (`git config user.name` y
`git config user.email`) en su computadora, aporta cambios verificables y
publica usando su cuenta. Conserven enlaces a commits, Issues y PR por autor.

## 3. Rama y pull request

1. Desde `main` actualizada, cree una rama para una mejora real:

```bash
git checkout -b mejora/reporte-categorias
```

2. Realice una mejora comprobable, por ejemplo un reporte adicional por
   categoría; incorpore su prueba y documentación.
3. Ejecute las pruebas y haga commit de **los cambios reales**:

```bash
git add .
git commit -m "Agregar reporte de inventario por categoría"
git push -u origin mejora/reporte-categorias
```

4. En GitHub, abra **Pull requests > New pull request** de esa rama a `main`.
5. Describa qué hace, adjunte captura de pruebas y solicite revisión de otro
   integrante. Integre el PR con **Merge pull request** si funciona.
6. Actualice `main` localmente con `git checkout main` y `git pull`.

## 4. Registrar Issues

En **Issues > New issue**, abra al menos:

- **Problema reproducible:** por ejemplo, si se encuentra un mensaje poco
  claro al ingresar un dato inválido. Incluya pasos, resultado esperado,
  resultado real y evidencia (no invente fallos que no ocurrieron).
- **Mejora pendiente:** permitir exportar reportes a CSV o imprimir tickets.
  Describa alcance y criterio de aceptación.

## 5. Crear etiqueta/release

Después de integrar el PR y comprobar el código:

```bash
git checkout main
git pull
git tag -a v1.0.0 -m "Versión estable 1.0.0"
git push origin v1.0.0
```

En la web, abra **Releases > Draft a new release**, seleccione `v1.0.0`,
resuma los cambios y publique la release.

## 6. Evidencias para la entrega

Guarden capturas reales de la página del repositorio, historial de commits,
ramas, pull request integrado, Issues y release en `evidencias/github/`.
Suban el documento técnico, manuales, análisis y diagrama actualizados.
Presenten el enlace público junto a una demostración del programa.

**No incluya archivos de datos de clientes ni `data/sistema.json` en GitHub.**
