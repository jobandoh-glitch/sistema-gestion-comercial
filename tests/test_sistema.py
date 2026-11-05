"""Pruebas automáticas: ejecutar python -m unittest discover -s tests -v."""
import copy
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

RUTA_RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RUTA_RAIZ / "src"))

from archivos import cargar_datos, guardar_datos
from estructuras import datos_iniciales
from productos import (consultar_producto, desactivar_producto,
                       modificar_producto, registrar_producto)
from inventario import (ajustar_existencias, productos_bajo_minimo,
                        registrar_entrada)
from ventas import matriz_ventas, registrar_venta
from reportes import (producto_mas_vendido, promedio_ventas_por_periodo,
                      total_ingresos, valor_inventario)


class PruebasSistema(unittest.TestCase):
    def setUp(self):
        self.datos = datos_iniciales()
        registrar_producto(self.datos, "p001", "Teclado", "Periféricos", 100, 5, 2)
        registrar_producto(self.datos, "p002", "Mouse", "Periféricos", 50, 3, 3)

    def test_01_registro_valido(self):
        self.assertEqual(consultar_producto(self.datos, "P001")["nombre"], "Teclado")
        self.assertEqual(len(self.datos["productos"]), 2)

    def test_02_codigo_duplicado(self):
        with self.assertRaisesRegex(ValueError, "Ya existe"):
            registrar_producto(self.datos, "P001", "Otro", "Varios", 10, 1, 1)
        self.assertEqual(len(self.datos["productos"]), 2)

    def test_03_valores_negativos_y_tipos_invalidos(self):
        for precio, cantidad in [(-1, 4), (2, -5), ("abc", 1)]:
            with self.subTest(precio=precio, cantidad=cantidad):
                with self.assertRaises(ValueError):
                    registrar_producto(self.datos, "X", "Prueba", "A", precio, cantidad, 2)
        with self.assertRaises(ValueError):
            registrar_producto(self.datos, "X", "Prueba", "A", 2, 2.5, 2)
        with self.assertRaises(ValueError):
            registrar_producto(self.datos, "X", "Prueba", "A", 1.999, 2, 2)

    def test_04_consulta_inexistente_y_modificacion(self):
        self.assertIsNone(consultar_producto(self.datos, "NOEXISTE"))
        with self.assertRaisesRegex(ValueError, "No existe"):
            modificar_producto(self.datos, "NOEXISTE", nombre="No")
        modificar_producto(self.datos, "P001", nombre="Teclado USB", precio=120)
        self.assertEqual(consultar_producto(self.datos, "P001")["precio"], 120)

    def test_05_desactivacion(self):
        desactivar_producto(self.datos, "p001")
        with self.assertRaisesRegex(ValueError, "desactivado"):
            registrar_venta(self.datos, [{"codigo": "P001", "cantidad": 1}])

    def test_06_venta_stock_insuficiente_no_modifica_datos(self):
        anterior = copy.deepcopy(self.datos)
        with self.assertRaisesRegex(ValueError, "insuficiente"):
            registrar_venta(self.datos, [{"codigo": "P001", "cantidad": 1},
                                               {"codigo": "P002", "cantidad": 50}])
        self.assertEqual(self.datos, anterior)

    def test_07_iva_subtotal_total_y_descuento_existencias(self):
        venta = registrar_venta(self.datos, [{"codigo": "p001", "cantidad": 2},
                                           {"codigo": "p002", "cantidad": 1}])
        self.assertEqual(venta["numero"], "V0001")
        self.assertEqual(venta["subtotal"], 250)
        self.assertEqual(venta["iva"], 30)
        self.assertEqual(venta["total"], 280)
        self.assertEqual(consultar_producto(self.datos, "P001")["cantidad"], 3)
        self.assertEqual(consultar_producto(self.datos, "P002")["cantidad"], 2)
        self.assertEqual(len(self.datos["movimientos"]), 2)

    def test_08_venta_con_codigos_repetidos_suma_cantidades(self):
        venta = registrar_venta(self.datos, [{"codigo": "P001", "cantidad": 2},
                                           {"codigo": "P001", "cantidad": 3}])
        self.assertEqual(len(venta["detalles"]), 1)
        self.assertEqual(venta["detalles"][0]["cantidad"], 5)
        self.assertEqual(consultar_producto(self.datos, "P001")["cantidad"], 0)

    def test_09_cantidades_de_venta_invalidas(self):
        for valor in (0, -2, "dos", 2.5):
            with self.subTest(valor=valor):
                with self.assertRaises(ValueError):
                    registrar_venta(self.datos, [{"codigo": "P001", "cantidad": valor}])
        self.assertEqual(len(self.datos["ventas"]), 0)

    def test_10_entrada_y_ajuste_con_historial(self):
        registrar_entrada(self.datos, "P001", 3, "Proveedor")
        self.assertEqual(consultar_producto(self.datos, "P001")["cantidad"], 8)
        ajustar_existencias(self.datos, "P001", 7, "Conteo físico")
        self.assertEqual(self.datos["movimientos"][1]["tipo"], "AJUSTE_SALIDA")
        self.assertEqual(self.datos["movimientos"][1]["existencia_nueva"], 7)

    def test_11_alertas_stock_minimo(self):
        bajos = productos_bajo_minimo(self.datos)
        self.assertEqual([producto["codigo"] for producto in bajos], ["P002"])

    def test_12_reportes_dinamicos_y_matriz(self):
        registrar_venta(self.datos, [{"codigo": "P001", "cantidad": 2},
                                           {"codigo": "P002", "cantidad": 1}])
        self.assertEqual(total_ingresos(self.datos), 280)
        self.assertEqual(producto_mas_vendido(self.datos)["codigo"], "P001")
        self.assertEqual(valor_inventario(self.datos), 400)
        self.assertEqual(matriz_ventas(self.datos),
                         [["V0001", "P001", 2, 200], ["V0001", "P002", 1, 50]])

    def test_13_promedio_diario_mensual_anual(self):
        registrar_venta(self.datos, [{"codigo": "P001", "cantidad": 1}])
        registrar_venta(self.datos, [{"codigo": "P002", "cantidad": 1}])
        for periodo in ("dia", "mes", "anio"):
            with self.subTest(periodo=periodo):
                filas = promedio_ventas_por_periodo(self.datos, periodo)
                self.assertEqual(len(filas), 1)
                self.assertEqual(filas[0]["ventas"], 2)
                self.assertEqual(filas[0]["total"], 168)
                self.assertEqual(filas[0]["promedio"], 84)

    def test_14_guardar_y_leer_archivo(self):
        registrar_venta(self.datos, [{"codigo": "P001", "cantidad": 1}])
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "sistema.json"
            guardar_datos(self.datos, ruta)
            recuperados = cargar_datos(ruta)
            self.assertEqual(recuperados, self.datos)
            self.assertEqual(recuperados["ventas"][0]["numero"], "V0001")

    def test_15_archivo_invalido_sin_sobreescribir(self):
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "sistema.json"
            ruta.write_text("{archivo_dañado", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "No se pudo leer"):
                cargar_datos(ruta)
            self.assertEqual(ruta.read_text(encoding="utf-8"), "{archivo_dañado")

    def test_16_menu_invalido_y_salida_controlada(self):
        with tempfile.TemporaryDirectory() as carpeta:
            ambiente = dict(os.environ, SGC_DATA_FILE=str(Path(carpeta) / "datos.json"))
            proceso = subprocess.run([sys.executable, str(RUTA_RAIZ / "src" / "main.py")],
                                     input="99\n5\n", capture_output=True, text=True,
                                     encoding="utf-8", env=ambiente, check=False)
            self.assertEqual(proceso.returncode, 0)
            self.assertIn("Opción inválida", proceso.stdout)
            self.assertIn("Hasta pronto", proceso.stdout)

    def test_17_calculo_iva_redondeo_centavos(self):
        registrar_producto(self.datos, "P003", "Cable", "Cables", 0.05, 20, 1)
        venta = registrar_venta(self.datos, [{"codigo": "P003", "cantidad": 1}])
        self.assertEqual(venta["iva"], 0.01)
        self.assertEqual(venta["total"], 0.06)


if __name__ == "__main__":
    unittest.main()
