"""Sistema de Gestión Comercial — interfaz gráfica (Tkinter).

Ejecutar desde la raíz del proyecto con:
    uv run --python 3.14 src/main_gui.py

Usa exactamente el mismo data/sistema.json que la versión de consola.
No requiere paquetes externos; tkinter forma parte de Python cuando está instalado.
"""

import copy
import csv
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from archivos import cargar_datos, guardar_datos, obtener_ruta
from estructuras import formato_dinero, monto, precio_valido
from productos import (consultar_producto, desactivar_producto, listar_productos,
                       modificar_producto, registrar_producto)
from inventario import (ajustar_existencias, existencias, historial_movimientos,
                        productos_bajo_minimo, registrar_entrada)
from ventas import historial_ventas, registrar_venta, siguiente_numero
from reportes import (producto_mas_vendido, promedio_ventas_por_periodo,
                      reporte_matriz, total_ingresos, valor_inventario)

# Paleta de la aplicación: azul oscuro y blanco, con un azul vivo como acento.
C = {
    "nav": "#101A30", "nav_alt": "#1D2B47", "background": "#F3F6FB",
    "white": "#FFFFFF", "primary": "#2563EB", "primary_hover": "#1D4ED8",
    "ink": "#14213B", "muted": "#64748B", "line": "#E2E8F0",
    "green": "#0F766E", "pale_green": "#DFF7EE", "red": "#B42318",
    "pale_red": "#FFF0ED", "pale_blue": "#EAF1FF", "header": "#E9EFF9",
}
FONT = "Segoe UI"


def entero(texto, nombre="cantidad", minimo=0):
    """Valida campos enteros con mensajes claros para el usuario."""
    try:
        valor = int(str(texto).strip())
    except (TypeError, ValueError):
        raise ValueError(f"{nombre.capitalize()}: escriba un número entero válido.") from None
    if str(texto).strip() not in (str(valor), f"+{valor}"):
        raise ValueError(f"{nombre.capitalize()}: escriba un número entero válido.")
    if valor < minimo:
        raise ValueError(f"{nombre.capitalize()}: debe ser mayor o igual a {minimo}.")
    return valor


def etiqueta(parent, texto, color="ink", size=10, bold=False, **kwargs):
    return tk.Label(parent, text=texto, fg=C.get(color, color),
                    bg=parent.cget("bg"), font=(FONT, size, "bold" if bold else "normal"),
                    **kwargs)


def boton(parent, texto, comando, variante="primary", ancho=None):
    colors = {
        "primary": (C["primary"], C["white"], C["primary_hover"]),
        "neutral": (C["pale_blue"], C["ink"], C["header"]),
        "danger": (C["pale_red"], C["red"], "#FFE2DA"),
        "success": (C["green"], C["white"], "#115E59"),
    }
    bg, fg, hover = colors[variante]
    kwargs = {"width": ancho} if ancho is not None else {}
    b = tk.Button(parent, text=texto, command=comando, font=(FONT, 10, "bold"),
                  bg=bg, fg=fg, activebackground=hover, activeforeground=fg,
                  bd=0, highlightthickness=0, relief="flat", padx=17, pady=10, cursor="hand2", **kwargs)
    b.bind("<Enter>", lambda _e: b.configure(bg=hover))
    b.bind("<Leave>", lambda _e: b.configure(bg=bg))
    return b


def caja(parent, **kwargs):
    return tk.Frame(parent, bg=C["white"], highlightbackground=C["line"],
                    highlightthickness=1, **kwargs)


def hacer_tabla(parent, columnas, anchos=None, alto=12):
    """Crea una tabla de selección única, con cabeceras y barra de desplazamiento."""
    cont = tk.Frame(parent, bg=C["white"])
    cont.pack(fill="both", expand=True)
    tabla = ttk.Treeview(cont, columns=[c[0] for c in columnas], show="headings",
                         selectmode="browse", height=alto)
    for i, (ident, cabecera) in enumerate(columnas):
        tabla.heading(ident, text=cabecera)
        ancho = anchos[i] if anchos else 130
        tabla.column(ident, width=ancho, minwidth=75,
                     anchor="e" if ident in ("precio", "cant", "minimo", "unidades", "subtotal", "iva", "total", "promedio", "anterior", "nuevo") else "w",
                     stretch=ident in ("nombre", "categoria", "descripcion", "fecha"))
    y = ttk.Scrollbar(cont, orient="vertical", command=tabla.yview)
    x = ttk.Scrollbar(cont, orient="horizontal", command=tabla.xview)
    tabla.configure(yscrollcommand=y.set, xscrollcommand=x.set)
    cont.grid_columnconfigure(0, weight=1)
    cont.grid_rowconfigure(0, weight=1)
    tabla.grid(row=0, column=0, sticky="nsew")
    y.grid(row=0, column=1, sticky="ns")
    x.grid(row=1, column=0, sticky="ew")
    tabla.tag_configure("bajo", background="#FFF3E8", foreground="#9A3412")
    tabla.tag_configure("inactivo", foreground="#94A3B8")
    return tabla


class Formulario(tk.Toplevel):
    """Ventana modal común: el usuario puede corregir campos sin perder los datos."""

    def __init__(self, app, titulo, campos, al_guardar, ancho=510):
        super().__init__(app.root)
        self.app, self.campos, self.al_guardar = app, campos, al_guardar
        self.title(titulo)
        self.configure(bg=C["white"])
        self.resizable(False, False)
        self.transient(app.root)
        self.entries = {}
        alto = 170 + 69 * len(campos)
        self.geometry(f"{ancho}x{alto}")
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        bloque = tk.Frame(self, bg=C["white"], padx=28, pady=24)
        bloque.pack(fill="both", expand=True)
        etiqueta(bloque, titulo, size=18, bold=True).pack(anchor="w", pady=(0, 5))
        etiqueta(bloque, "Complete los datos y presione Guardar.", "muted").pack(anchor="w", pady=(0, 15))
        for clave, titulo_campo, valor, bloqueado in campos:
            etiqueta(bloque, titulo_campo, "muted", size=10, bold=True).pack(anchor="w", pady=(7, 3))
            e = ttk.Entry(bloque, font=(FONT, 11))
            e.insert(0, str(valor) if valor is not None else "")
            if bloqueado:
                e.configure(state="readonly")
            e.pack(fill="x", ipady=6)
            self.entries[clave] = e
        pie = tk.Frame(bloque, bg=C["white"])
        pie.pack(fill="x", pady=(24, 0))
        boton(pie, "Cancelar", self.destroy, "neutral").pack(side="right", padx=(9, 0))
        boton(pie, "Guardar", self.guardar).pack(side="right")
        self.bind("<Return>", lambda _e: self.guardar())
        self.after(50, self._enfocar)
        app.centrar(self)

    def _enfocar(self):
        for entrada in self.entries.values():
            if str(entrada.cget("state")) != "readonly":
                entrada.focus_set()
                break

    def guardar(self):
        valores = {clave: entry.get().strip() for clave, entry in self.entries.items()}
        try:
            self.al_guardar(valores)
        except (ValueError, OSError) as error:
            messagebox.showerror("Revisar información", str(error), parent=self)
            return
        self.destroy()


class Aplicacion:
    def __init__(self, root):
        self.root = root
        root.title("SGC • Sistema de Gestión Comercial")
        root.geometry("1230x790")
        root.minsize(1030, 680)
        root.configure(bg=C["background"])
        self.datos = cargar_datos()
        self.pagina = "Inicio"
        self.carrito = []
        self.busqueda = ""
        self.vista_inventario = "Existencias"
        self.vista_reporte = "Productos"
        self.periodo = "Mes"
        self.configurar_estilo()
        self.crear_estructura()
        self.mostrar("Inicio")

    def centrar(self, ventana):
        ventana.update_idletasks()
        x = self.root.winfo_rootx() + (self.root.winfo_width() - ventana.winfo_width()) // 2
        y = self.root.winfo_rooty() + (self.root.winfo_height() - ventana.winfo_height()) // 2
        ventana.geometry(f"+{max(x, 0)}+{max(y, 0)}")

    def configurar_estilo(self):
        s = ttk.Style(self.root)
        s.theme_use("clam")
        s.configure("Treeview", background=C["white"], foreground=C["ink"],
                    fieldbackground=C["white"], rowheight=35,
                    bordercolor=C["line"], font=(FONT, 10))
        s.map("Treeview", background=[("selected", C["pale_blue"])],
              foreground=[("selected", C["ink"])])
        s.configure("Treeview.Heading", background=C["header"], foreground=C["ink"],
                    font=(FONT, 10, "bold"), padding=10, relief="flat")
        s.map("Treeview.Heading", background=[("active", C["header"])])
        s.configure("TEntry", padding=6)
        s.configure("TCombobox", padding=6)

    def crear_estructura(self):
        self.sidebar = tk.Frame(self.root, bg=C["nav"], width=242)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        marca = tk.Frame(self.sidebar, bg=C["nav"], padx=24, pady=31)
        marca.pack(fill="x")
        etiqueta(marca, "◈  SGC", "#FFFFFF", 23, True).pack(anchor="w")
        etiqueta(marca, "Gestión Comercial", "#94A3B8", 10).pack(anchor="w", pady=(1, 0))
        tk.Frame(self.sidebar, bg="#2B3953", height=1).pack(fill="x", padx=20, pady=(2, 20))
        self.botones_nav = {}
        self.nombres = ["Inicio", "Productos", "Ventas", "Inventario", "Reportes"]
        simbolos = {"Inicio": "▦", "Productos": "▣", "Ventas": "▤",
                    "Inventario": "▥", "Reportes": "◫"}
        for nombre in self.nombres:
            b = tk.Button(self.sidebar, text=f"  {simbolos[nombre]}    {nombre}",
                          font=(FONT, 11, "bold"), anchor="w", bg=C["nav"], fg="#C8D3E7",
                          activebackground=C["nav_alt"], activeforeground="white",
                          relief="flat", bd=0, highlightthickness=0, padx=22, pady=15, cursor="hand2",
                          command=lambda n=nombre: self.mostrar(n))
            b.pack(fill="x", padx=12, pady=2)
            self.botones_nav[nombre] = b
        tk.Frame(self.sidebar, bg=C["nav"]).pack(fill="both", expand=True)
        abajo = tk.Frame(self.sidebar, bg=C["nav_alt"], padx=15, pady=18)
        abajo.pack(fill="x", padx=12, pady=20)
        etiqueta(abajo, "DATOS GUARDADOS", "#DCE7F9", 9, True).pack(anchor="w")
        etiqueta(abajo, "Se conserva la información", "#A9B8D0", 9).pack(anchor="w", pady=(4, 0))
        etiqueta(abajo, "al cerrar la aplicación.", "#A9B8D0", 9).pack(anchor="w")
        self.area = tk.Frame(self.root, bg=C["background"])
        self.area.pack(side="left", fill="both", expand=True)

    def mostrar(self, pagina):
        self.pagina = pagina
        for nombre, b in self.botones_nav.items():
            b.configure(bg=C["nav_alt"] if nombre == pagina else C["nav"],
                        fg=C["white"] if nombre == pagina else "#C8D3E7")
        for w in self.area.winfo_children():
            w.destroy()
        self.contenido = tk.Frame(self.area, bg=C["background"], padx=30, pady=25)
        self.contenido.pack(fill="both", expand=True)
        if pagina == "Inicio": self.inicio()
        elif pagina == "Productos": self.productos()
        elif pagina == "Ventas": self.ventas()
        elif pagina == "Inventario": self.inventario()
        elif pagina == "Reportes": self.reportes()

    def encabezar(self, titulo, descripcion):
        encabezado = tk.Frame(self.contenido, bg=C["background"])
        encabezado.pack(fill="x", pady=(0, 22))
        etiqueta(encabezado, titulo, size=24, bold=True).pack(anchor="w")
        etiqueta(encabezado, descripcion, "muted", 10).pack(anchor="w", pady=(5, 0))
        return encabezado

    def ejecutar(self, operacion, mensaje=None):
        """Copia para asegurar que un fallo de validación o guardado no deje cambios a medias."""
        nuevo = copy.deepcopy(self.datos)
        resultado = operacion(nuevo)
        guardar_datos(nuevo)
        self.datos = nuevo
        if mensaje:
            messagebox.showinfo("Operación completada", mensaje, parent=self.root)
        self.mostrar(self.pagina)
        return resultado

    def error(self, fn):
        try:
            return fn()
        except (ValueError, OSError) as e:
            messagebox.showerror("No se pudo completar", str(e), parent=self.root)
            return None

    def tarjeta(self, parent, titulo, numero, detalle, color="primary"):
        card = caja(parent, padx=19, pady=17)
        card.pack(side="left", fill="both", expand=True, padx=(0, 12))
        etiqueta(card, titulo, "muted", size=10, bold=True).pack(anchor="w")
        etiqueta(card, numero, color, size=21, bold=True).pack(anchor="w", pady=(12, 5))
        etiqueta(card, detalle, "muted", size=9).pack(anchor="w")
        return card

    def inicio(self):
        head = self.encabezar("Panel principal", "Resumen de productos, existencias y ventas registradas")
        boton(head, "+ Nueva venta", lambda: self.mostrar("Ventas")).pack(side="right")
        cards = tk.Frame(self.contenido, bg=C["background"])
        cards.pack(fill="x", pady=(0, 22))
        self.tarjeta(cards, "PRODUCTOS", str(len(self.datos["productos"])), "Productos registrados")
        self.tarjeta(cards, "VENTAS", str(len(self.datos["ventas"])), "Operaciones completadas", "green")
        self.tarjeta(cards, "INGRESOS", formato_dinero(total_ingresos(self.datos)), "Total con IVA")
        self.tarjeta(cards, "STOCK BAJO", str(len(productos_bajo_minimo(self.datos))), "Necesitan atención", "red")
        panel = caja(self.contenido, padx=22, pady=19)
        panel.pack(fill="both", expand=True)
        titulo = tk.Frame(panel, bg=C["white"])
        titulo.pack(fill="x", pady=(0, 12))
        etiqueta(titulo, "Últimas ventas", size=15, bold=True).pack(side="left")
        boton(titulo, "Ver reportes", lambda: self.mostrar("Reportes"), "neutral").pack(side="right")
        cols = [("numero", "Venta"), ("fecha", "Fecha"), ("items", "Unidades"),
                ("subtotal", "Subtotal"), ("iva", "IVA"), ("total", "Total")]
        tabla = hacer_tabla(panel, cols, [110, 215, 90, 140, 120, 145])
        for v in reversed(self.datos["ventas"][-30:]):
            tabla.insert("", "end", values=(v["numero"], v["fecha"].replace("T", " ")[:19],
                         sum(d["cantidad"] for d in v["detalles"]),
                         formato_dinero(v["subtotal"]), formato_dinero(v["iva"]),
                         formato_dinero(v["total"])))
        self.nota(panel, "Los datos provienen del mismo archivo JSON utilizado por la versión de consola.")

    def nota(self, parent, texto):
        etiqueta(parent, texto, "muted", size=9, wraplength=850, justify="left").pack(anchor="w", pady=(12, 1))

    def productos(self):
        self.encabezar("Gestión de productos", "Registrar, consultar, modificar, activar y desactivar productos")
        panel = caja(self.contenido, padx=20, pady=18)
        panel.pack(fill="both", expand=True)
        barra = tk.Frame(panel, bg=C["white"])
        barra.pack(fill="x", pady=(0, 15))
        etiqueta(barra, "Buscar por código o nombre", "muted", size=10).pack(side="left", padx=(0, 12))
        busq = ttk.Entry(barra, width=23, font=(FONT, 10))
        busq.insert(0, self.busqueda)
        busq.pack(side="left", padx=(0, 10))
        boton(barra, "Buscar", lambda: self.buscar_producto(busq.get()), "neutral").pack(side="left")
        boton(barra, "+ Registrar producto", self.registrar_producto).pack(side="right")
        cols = [("codigo", "Código"), ("nombre", "Nombre"), ("categoria", "Categoría"),
                ("precio", "Precio"), ("cant", "Disponibles"), ("minimo", "Mínimo"),
                ("estado", "Estado")]
        self.product_table = hacer_tabla(panel, cols, [92, 190, 145, 100, 105, 85, 110])
        for p in listar_productos(self.datos):
            if self.busqueda.lower() not in (p["codigo"] + " " + p["nombre"]).lower():
                continue
            tag = "inactivo" if not p["activo"] else ("bajo" if p["cantidad"] <= p["stock_minimo"] else "")
            self.product_table.insert("", "end", iid=p["codigo"], tags=(tag,),
                                      values=(p["codigo"], p["nombre"], p["categoria"],
                                              formato_dinero(p["precio"]), p["cantidad"],
                                              p["stock_minimo"], "Activo" if p["activo"] else "Desactivado"))
        self.product_table.bind("<Double-1>", lambda _event: self.modificar_producto())
        acciones = tk.Frame(panel, bg=C["white"])
        acciones.pack(fill="x", pady=(17, 0))
        boton(acciones, "Modificar seleccionado", self.modificar_producto, "neutral").pack(side="left", padx=(0, 9))
        # Un mismo botón activa o desactiva dependiendo del producto elegido.
        self.boton_estado_producto = boton(acciones, "Activar / desactivar", self.cambiar_estado_producto, "neutral")
        self.boton_estado_producto.pack(side="left")
        self.product_table.bind("<<TreeviewSelect>>", self.actualizar_boton_estado)
        self.nota(panel, "Selecciona un producto y utiliza Activar/Desactivar para cambiar su estado. Las existencias se modifican en Inventario.")

    def buscar_producto(self, texto):
        self.busqueda = texto.strip()
        self.mostrar("Productos")

    def producto_seleccionado(self):
        seleccion = self.product_table.selection()
        if not seleccion:
            raise ValueError("Selecciona primero un producto de la tabla.")
        return consultar_producto(self.datos, seleccion[0])

    def registrar_producto(self):
        campos = [("codigo", "Código *", "", False), ("nombre", "Nombre *", "", False),
                  ("categoria", "Categoría *", "", False), ("precio", "Precio de venta (Q) *", "", False),
                  ("cantidad", "Cantidad inicial *", "0", False),
                  ("minimo", "Stock mínimo *", "0", False)]

        def guardar(v):
            self.ejecutar(lambda datos: registrar_producto(datos, v["codigo"], v["nombre"],
                v["categoria"], precio_valido(v["precio"]), entero(v["cantidad"], "cantidad"),
                entero(v["minimo"], "stock mínimo")))

        Formulario(self, "Registrar producto", campos, guardar)

    def modificar_producto(self):
        p = self.error(self.producto_seleccionado)
        if p is None:
            return
        campos = [("codigo", "Código", p["codigo"], True),
                  ("nombre", "Nombre *", p["nombre"], False),
                  ("categoria", "Categoría *", p["categoria"], False),
                  ("precio", "Precio de venta (Q) *", str(p["precio"]), False),
                  ("minimo", "Stock mínimo *", str(p["stock_minimo"]), False)]

        def guardar(v):
            self.ejecutar(lambda datos: modificar_producto(datos, p["codigo"], v["nombre"],
                v["categoria"], precio_valido(v["precio"]), entero(v["minimo"], "stock mínimo")))

        Formulario(self, "Modificar producto", campos, guardar)

    def actualizar_boton_estado(self, _evento=None):
        """Actualiza el texto del botón según el estado del producto seleccionado."""
        seleccion = self.product_table.selection()
        if not seleccion:
            self.boton_estado_producto.configure(text="Activar / desactivar")
            return
        producto = consultar_producto(self.datos, seleccion[0])
        if producto is not None:
            self.boton_estado_producto.configure(
                text="Desactivar seleccionado" if producto["activo"] else "Activar seleccionado"
            )

    def cambiar_estado_producto(self):
        """Alterna el estado activo/inactivo sin borrar el producto ni sus existencias."""
        producto = self.error(self.producto_seleccionado)
        if producto is None:
            return
        activar = not producto["activo"]
        accion = "activar" if activar else "desactivar"
        aviso = ("Volverá a estar disponible para la venta."
                 if activar else "Ya no se podrá vender hasta que se reactive.")
        if not messagebox.askyesno("Confirmar cambio de estado",
                f"¿Deseas {accion} {producto['codigo']} - {producto['nombre']}?\n{aviso}",
                parent=self.root):
            return

        def cambiar(datos):
            if activar:
                actual = consultar_producto(datos, producto["codigo"])
                if actual is None:
                    raise ValueError("El producto ya no existe.")
                if actual["activo"]:
                    raise ValueError("El producto ya está activo.")
                actual["activo"] = True
                return actual
            return desactivar_producto(datos, producto["codigo"])

        mensaje = f"El producto {producto['codigo']} está ahora {'activo' if activar else 'desactivado'}."
        self.error(lambda: self.ejecutar(cambiar, mensaje))

    def desactivar_producto(self):
        """Mantiene compatibilidad con llamadas existentes a este método."""
        producto = self.error(self.producto_seleccionado)
        if producto is not None and producto["activo"]:
            self.cambiar_estado_producto()

    def ventas(self):
        self.encabezar("Registro de ventas", "Agrega productos al carrito, revisa el total y confirma")
        cab = caja(self.contenido, padx=20, pady=17)
        cab.pack(fill="x", pady=(0, 14))
        fila = tk.Frame(cab, bg=C["white"])
        fila.pack(fill="x")
        etiqueta(fila, "Código de producto", "muted", bold=True).pack(side="left", padx=(0, 8))
        self.codigo_venta = ttk.Entry(fila, width=17)
        self.codigo_venta.pack(side="left", padx=(0, 16))
        etiqueta(fila, "Cantidad", "muted", bold=True).pack(side="left", padx=(0, 8))
        self.cantidad_venta = ttk.Entry(fila, width=7)
        self.cantidad_venta.insert(0, "1")
        self.cantidad_venta.pack(side="left", padx=(0, 14))
        boton(fila, "+ Agregar al carrito", self.agregar_carrito).pack(side="left")
        self.codigo_venta.bind("<Return>", lambda _e: self.agregar_carrito())
        self.cantidad_venta.bind("<Return>", lambda _e: self.agregar_carrito())
        self.nota(cab, "Solo pueden venderse productos activos con existencias suficientes.")

        panel = caja(self.contenido, padx=20, pady=18)
        panel.pack(fill="both", expand=True)
        etiqueta(panel, "Productos de la venta", size=15, bold=True).pack(anchor="w", pady=(0, 12))
        cols = [("codigo", "Código"), ("nombre", "Producto"), ("cant", "Cantidad"),
                ("precio", "Precio unitario"), ("subtotal", "Subtotal")]
        self.tabla_carrito = hacer_tabla(panel, cols, [115, 260, 110, 145, 140], alto=9)
        subtotal = Decimal("0.00")
        for item in self.carrito:
            p = consultar_producto(self.datos, item["codigo"])
            precio = monto(p["precio"]) if p else monto(item.get("precio", 0))
            importe = precio * item["cantidad"]
            subtotal += importe
            self.tabla_carrito.insert("", "end", iid=item["codigo"],
                                      values=(item["codigo"], p["nombre"] if p else "No disponible",
                                              item["cantidad"], formato_dinero(precio), formato_dinero(importe)))
        actions = tk.Frame(panel, bg=C["white"])
        actions.pack(fill="x", pady=(16, 0))
        boton(actions, "Quitar seleccionado", self.quitar_carrito, "neutral").pack(side="left", padx=(0, 9))
        boton(actions, "Vaciar carrito", self.vaciar_carrito, "danger").pack(side="left")
        iva = (subtotal * Decimal("0.12")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        pie = tk.Frame(panel, bg=C["white"])
        pie.pack(fill="x", pady=(16, 0))
        resumen = tk.Frame(pie, bg=C["white"])
        resumen.pack(side="right")
        etiqueta(resumen, f"Subtotal:  {formato_dinero(subtotal)}", "muted", 10).pack(anchor="e")
        etiqueta(resumen, f"IVA 12 %:  {formato_dinero(iva)}", "muted", 10).pack(anchor="e", pady=(3, 0))
        etiqueta(resumen, f"TOTAL:  {formato_dinero(subtotal + iva)}", "green", 18, True).pack(anchor="e", pady=(5, 8))
        boton(resumen, "Confirmar y guardar venta", self.confirmar_venta, "success").pack(anchor="e")

    def agregar_carrito(self):
        try:
            codigo = self.codigo_venta.get().strip().upper()
            cantidad = entero(self.cantidad_venta.get(), "cantidad", 1)
            p = consultar_producto(self.datos, codigo)
            if p is None:
                raise ValueError("El producto no existe. Revisa el código.")
            if not p["activo"]:
                raise ValueError(f"El producto {codigo} está desactivado.")
            ya = sum(i["cantidad"] for i in self.carrito if i["codigo"] == codigo)
            if cantidad + ya > p["cantidad"]:
                raise ValueError(f"Inventario insuficiente para {codigo}: hay {p['cantidad']} y se piden {cantidad + ya}.")
            item = next((i for i in self.carrito if i["codigo"] == codigo), None)
            if item: item["cantidad"] += cantidad
            else: self.carrito.append({"codigo": codigo, "cantidad": cantidad})
            self.mostrar("Ventas")
        except ValueError as e:
            messagebox.showerror("No se puede agregar", str(e), parent=self.root)

    def quitar_carrito(self):
        sel = self.tabla_carrito.selection()
        if not sel:
            messagebox.showwarning("Selecciona un producto", "Selecciona una fila del carrito.", parent=self.root)
            return
        self.carrito = [item for item in self.carrito if item["codigo"] != sel[0]]
        self.mostrar("Ventas")

    def vaciar_carrito(self):
        self.carrito.clear()
        self.mostrar("Ventas")

    def confirmar_venta(self):
        if not self.carrito:
            messagebox.showwarning("Carrito vacío", "Agrega al menos un producto.", parent=self.root)
            return
        if not messagebox.askyesno("Confirmar venta", "¿Guardar la venta y descontar las existencias?", parent=self.root):
            return
        try:
            venta = self.ejecutar(lambda d: registrar_venta(d, self.carrito))
        except (ValueError, OSError) as e:
            messagebox.showerror("Venta rechazada", str(e), parent=self.root)
            return
        self.carrito.clear()
        self.mostrar("Ventas")
        messagebox.showinfo("Venta guardada", f"Venta {venta['numero']} registrada correctamente.\n"
            f"Subtotal: {formato_dinero(venta['subtotal'])}\nIVA 12 %: {formato_dinero(venta['iva'])}\n"
            f"Total: {formato_dinero(venta['total'])}", parent=self.root)

    def inventario(self):
        self.encabezar("Control de inventario", "Existencias, entradas, ajustes y movimientos")
        tabs = tk.Frame(self.contenido, bg=C["background"])
        tabs.pack(fill="x", pady=(0, 13))
        for opcion in ["Existencias", "Stock mínimo", "Movimientos"]:
            boton(tabs, opcion, lambda op=opcion: self.cambiar_inventario(op),
                  "primary" if opcion == self.vista_inventario else "neutral").pack(side="left", padx=(0, 9))
        panel = caja(self.contenido, padx=20, pady=18)
        panel.pack(fill="both", expand=True)
        cab = tk.Frame(panel, bg=C["white"])
        cab.pack(fill="x", pady=(0, 14))
        etiqueta(cab, self.vista_inventario, size=15, bold=True).pack(side="left")
        boton(cab, "+ Entrada", self.entrada_inventario).pack(side="right", padx=(9, 0))
        boton(cab, "Ajustar cantidad", self.ajuste_inventario, "neutral").pack(side="right")
        if self.vista_inventario == "Movimientos":
            cols = [("fecha", "Fecha"), ("codigo", "Código"), ("tipo", "Movimiento"),
                    ("unidades", "Unidades"), ("anterior", "Antes"), ("nuevo", "Después"),
                    ("descripcion", "Descripción")]
            t = hacer_tabla(panel, cols, [185, 90, 140, 85, 80, 90, 250])
            for i, m in enumerate(reversed(historial_movimientos(self.datos))):
                t.insert("", "end", iid=str(i), values=(m["fecha"].replace("T", " ")[:19],
                    m["codigo"], m["tipo"], m["cantidad"], m["existencia_anterior"],
                    m["existencia_nueva"], m["descripcion"]))
        else:
            cols = [("codigo", "Código"), ("nombre", "Nombre"), ("categoria", "Categoría"),
                    ("cant", "Existencias"), ("minimo", "Stock mínimo"), ("estado", "Estado")]
            t = hacer_tabla(panel, cols, [105, 225, 190, 120, 110, 120])
            productos = (productos_bajo_minimo(self.datos) if self.vista_inventario == "Stock mínimo"
                         else existencias(self.datos))
            for p in productos:
                tag = "inactivo" if not p["activo"] else ("bajo" if p["cantidad"] <= p["stock_minimo"] else "")
                t.insert("", "end", iid=p["codigo"], tags=(tag,), values=(p["codigo"], p["nombre"],
                         p["categoria"], p["cantidad"], p["stock_minimo"],
                         "Activo" if p["activo"] else "Desactivado"))
        self.nota(panel, "Los movimientos incluyen fecha, código, tipo, cantidad, existencias anterior y nueva, y motivo.")

    def cambiar_inventario(self, opcion):
        self.vista_inventario = opcion
        self.mostrar("Inventario")

    def entrada_inventario(self):
        campos = [("codigo", "Código de producto *", "", False),
                  ("cantidad", "Unidades que ingresan *", "1", False),
                  ("descripcion", "Motivo o descripción *", "Compra a proveedor", False)]
        def guardar(v):
            self.ejecutar(lambda d: registrar_entrada(d, v["codigo"],
                       entero(v["cantidad"], "cantidad", 1), v["descripcion"]))
        Formulario(self, "Registrar entrada", campos, guardar)

    def ajuste_inventario(self):
        campos = [("codigo", "Código de producto *", "", False),
                  ("cantidad", "Nueva cantidad total *", "0", False),
                  ("descripcion", "Motivo del ajuste *", "Conteo físico", False)]
        def guardar(v):
            self.ejecutar(lambda d: ajustar_existencias(d, v["codigo"],
                        entero(v["cantidad"], "nueva cantidad", 0), v["descripcion"]))
        Formulario(self, "Ajustar existencias", campos, guardar)

    def reportes(self):
        self.encabezar("Reportes y estadísticas", "Indicadores calculados a partir de los datos guardados")
        cards = tk.Frame(self.contenido, bg=C["background"])
        cards.pack(fill="x", pady=(0, 16))
        p = producto_mas_vendido(self.datos)
        self.tarjeta(cards, "INGRESOS", formato_dinero(total_ingresos(self.datos)), "Ventas con IVA")
        self.tarjeta(cards, "VALOR INVENTARIO", formato_dinero(valor_inventario(self.datos)), "Productos activos")
        self.tarjeta(cards, "MÁS VENDIDO", p["codigo"] if p else "—",
                     f"{p['unidades']} unidades" if p else "Sin ventas", "green")
        panel = caja(self.contenido, padx=20, pady=17)
        panel.pack(fill="both", expand=True)
        barra = tk.Frame(panel, bg=C["white"])
        barra.pack(fill="x", pady=(0, 12))
        opciones = ["Productos", "Stock bajo", "Historial ventas", "Promedios", "Matriz ventas"]
        for texto in opciones:
            boton(barra, texto, lambda x=texto: self.cambiar_reporte(x),
                  "primary" if texto == self.vista_reporte else "neutral").pack(side="left", padx=(0, 7))
        fila = tk.Frame(panel, bg=C["white"])
        fila.pack(fill="x", pady=(0, 10))
        etiqueta(fila, self.vista_reporte, size=14, bold=True).pack(side="left")
        boton(fila, "Exportar CSV", self.exportar_reporte, "neutral").pack(side="right")
        if self.vista_reporte == "Promedios":
            etiqueta(fila, "Agrupar por:", "muted").pack(side="left", padx=(20, 9))
            combo = ttk.Combobox(fila, values=["Día", "Mes", "Año"], width=12, state="readonly")
            combo.set(self.periodo)
            combo.pack(side="left")
            combo.bind("<<ComboboxSelected>>", lambda _ev: self.seleccionar_periodo(combo.get()))
        columnas, filas = self.datos_reporte()
        self.columnas_csv = [titulo for _clave, titulo in columnas]
        self.filas_csv = filas
        hacer = hacer_tabla(panel, columnas, alto=12)
        for i, fila in enumerate(filas):
            hacer.insert("", "end", iid=str(i), values=fila)
        if self.vista_reporte == "Promedios":
            self.nota(panel, "Promedio = importe total del período ÷ cantidad de ventas en ese período.")
        elif self.vista_reporte == "Matriz ventas":
            self.nota(panel, "La matriz muestra el subtotal de cada producto sin IVA; el IVA se calcula por venta.")
        else:
            self.nota(panel, "Usa Exportar CSV para guardar una copia del reporte seleccionado.")

    def cambiar_reporte(self, nombre):
        self.vista_reporte = nombre
        self.mostrar("Reportes")

    def seleccionar_periodo(self, nombre):
        self.periodo = nombre
        self.mostrar("Reportes")

    def datos_reporte(self):
        vista = self.vista_reporte
        if vista in ("Productos", "Stock bajo"):
            cols = [("codigo", "Código"), ("nombre", "Nombre"), ("categoria", "Categoría"),
                    ("precio", "Precio"), ("cant", "Existencias"), ("minimo", "Mínimo"),
                    ("estado", "Estado")]
            prods = (productos_bajo_minimo(self.datos) if vista == "Stock bajo" else listar_productos(self.datos))
            filas = [(p["codigo"], p["nombre"], p["categoria"], formato_dinero(p["precio"]),
                     p["cantidad"], p["stock_minimo"], "Activo" if p["activo"] else "Desactivado") for p in prods]
        elif vista == "Historial ventas":
            cols = [("numero", "Venta"), ("fecha", "Fecha"), ("unidades", "Unidades"),
                    ("subtotal", "Subtotal"), ("iva", "IVA"), ("total", "Total")]
            filas = [(v["numero"], v["fecha"].replace("T", " ")[:19],
                      sum(d["cantidad"] for d in v["detalles"]), formato_dinero(v["subtotal"]),
                      formato_dinero(v["iva"]), formato_dinero(v["total"]))
                     for v in reversed(historial_ventas(self.datos))]
        elif vista == "Promedios":
            cols = [("periodo", "Período"), ("ventas", "Ventas"), ("total", "Total"), ("promedio", "Promedio")]
            periodo = {"Día": "dia", "Mes": "mes", "Año": "anio"}[self.periodo]
            filas = [(r["periodo"], r["ventas"], formato_dinero(r["total"]),
                      formato_dinero(r["promedio"])) for r in promedio_ventas_por_periodo(self.datos, periodo)]
        else:
            cols = [("numero", "Venta"), ("codigo", "Código"),
                    ("unidades", "Unidades"), ("subtotal", "Subtotal sin IVA")]
            filas = [(row[0], row[1], row[2], formato_dinero(row[3])) for row in reporte_matriz(self.datos)]
        return cols, filas

    def exportar_reporte(self):
        path = filedialog.asksaveasfilename(title="Guardar reporte CSV", defaultextension=".csv",
            initialfile="reporte_" + self.vista_reporte.lower().replace(" ", "_") + ".csv",
            filetypes=[("CSV", "*.csv")], parent=self.root)
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                out = csv.writer(f)
                out.writerow(self.columnas_csv)
                out.writerows(self.filas_csv)
        except OSError as e:
            messagebox.showerror("No se pudo exportar", str(e), parent=self.root)
            return
        messagebox.showinfo("Reporte guardado", f"Se guardó el archivo:\n{path}", parent=self.root)


def main():
    root = tk.Tk()
    try:
        Aplicacion(root)
    except (ValueError, OSError) as error:
        messagebox.showerror("No se pudieron leer los datos", f"{error}\n\n"
                             f"Archivo de datos:\n{obtener_ruta()}", parent=root)
        root.destroy()
        return
    root.mainloop()


if __name__ == "__main__":
    main()
