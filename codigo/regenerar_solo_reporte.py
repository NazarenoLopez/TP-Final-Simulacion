"""
Script para regenerar SOLO el HTML interactivo usando los datos ya existentes
"""
import json
from pathlib import Path
import sys

# Agregar el path de simulación
sys.path.insert(0, str(Path(__file__).parent / "simulacion"))

from simulacion_cinco_escenarios import ComparadorCincoEscenarios

# Crear comparador
comparador = ComparadorCincoEscenarios("resultados_cinco_escenarios")

# Cargar resultados existentes
archivo_consolidado = comparador.directorio_resultados / "comparacion_escenarios.json"
with open(archivo_consolidado, 'r', encoding='utf-8') as f:
    resultados = json.load(f)

print("Regenerando HTML interactivo...")
print(f"Datos cargados: {list(resultados.keys())}")

# Generar reporte comparativo
comparador._generar_reporte_comparativo(resultados)

print("\n✓ Reporte comparativo regenerado exitosamente")
print(f"Ubicación: {comparador.directorio_resultados / 'reporte_comparativo.txt'}")
