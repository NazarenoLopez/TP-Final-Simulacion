"""
Script para verificar los valores de PPDSR en el JSON
"""
import json
from pathlib import Path

# Cargar datos
resultados_path = Path("resultados_cinco_escenarios")
comparacion_file = resultados_path / "comparacion_escenarios.json"

with open(comparacion_file, 'r', encoding='utf-8') as f:
    datos = json.load(f)

print("="*60)
print("VALORES DE PPDSR EN EL JSON")
print("="*60)
for nombre in ['ACTUAL', 'CASO 1', 'CASO 2', 'CASO 3', 'CASO 4']:
    ppdsr = datos[nombre]['indicadores']['PPDSR']['media']
    ppdsr_pct = ppdsr * 100
    print(f"{nombre:10s}: {ppdsr:.6f} → {ppdsr_pct:.2f}%")

print("\n" + "="*60)
print("VALORES DE PTOSR_promedio EN EL JSON")
print("="*60)
for nombre in ['ACTUAL', 'CASO 1', 'CASO 2', 'CASO 3', 'CASO 4']:
    ptosr = datos[nombre]['indicadores']['PTOSR_promedio']['media']
    ptosr_pct = ptosr * 100
    print(f"{nombre:10s}: {ptosr:.6f} → {ptosr_pct:.2f}%")
