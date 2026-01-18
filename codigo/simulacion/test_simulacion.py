"""
Script de Prueba: Ejecuta una réplica simple para verificar que todo funciona
"""

import sys
from pathlib import Path

# Agregar directorio padre al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from simulacion.simulador import Simulador


def main():
    """Ejecuta una réplica de prueba."""
    print("\n" + "="*80)
    print("PRUEBA DE SIMULACIÓN - UNA RÉPLICA")
    print("="*80)
    
    # Parámetros de prueba (escenario base)
    G = 3  # 3 médicos
    SR = 24  # 24 salas de recuperación (dotación base)
    I = 15  # 15 incubadoras (dotación base)
    
    print(f"\nParámetros:")
    print(f"  G (médicos): {G}")
    print(f"  SR (salas recuperación): {SR}")
    print(f"  I (incubadoras): {I}")
    print(f"\nEjecutando simulación (10 años = 5,256,000 minutos)...")
    print("Esto puede tomar unos minutos...\n")
    
    # Crear y ejecutar simulador
    simulador = Simulador(G=G, SR=SR, I=I, semilla=42)
    resultados = simulador.ejecutar(mostrar_progreso=True)
    
    # Mostrar resultados principales
    print(f"\n{'='*80}")
    print("RESULTADOS DE LA SIMULACIÓN")
    print(f"{'='*80}\n")
    
    print(f"Pacientes llegados: {resultados['total_pacientes_llegados']:,}")
    print(f"Pacientes atendidos: {resultados['total_pacientes_atendidos']:,}")
    print(f"  - Consultas: {resultados['total_consultas']:,}")
    print(f"  - Partos naturales: {resultados['total_partos_naturales']:,}")
    print(f"  - Cesáreas: {resultados['total_partos_cesarea']:,}")
    print(f"\nDerivaciones:")
    print(f"  - Por falta de salas de recuperación: {resultados['total_derivaciones_sr']:,}")
    print(f"  - Por falta de incubadoras: {resultados['total_derivaciones_inc']:,}")
    
    print(f"\nTiempos promedio de espera:")
    print(f"  - Consultas: {resultados['PEC_consultas']:.2f} minutos")
    print(f"  - Partos naturales: {resultados['PEC_partos_nat']:.2f} minutos")
    print(f"  - Cesáreas: {resultados['PEC_partos_ces']:.2f} minutos")
    print(f"  - General: {resultados['PEC_general']:.2f} minutos")
    
    print(f"\nUtilizaciones:")
    print(f"  - Médicos: {resultados['UT_med']:.2f}%")
    print(f"  - Quirófano: {resultados['UT_Q']:.2f}%")
    print(f"  - Salas de recuperación (promedio ocioso): {resultados['PTOSR_promedio']:.2f}%")
    
    print(f"\nDerivaciones (%):")
    print(f"  - Por falta de salas de recuperación: {resultados['PPDSR']:.2f}%")
    print(f"  - Por falta de incubadoras: {resultados['PPDINC']:.2f}%")
    
    print(f"\nCostos:")
    print(f"  - Costo Total Mensual (CTM): ${resultados['CTM']:,.0f}")
    print(f"  - Costo Inicial de Instalaciones (CII): ${resultados['CII']:,.0f}")
    
    print(f"\n{'='*80}")
    print("✓ PRUEBA COMPLETADA")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    main()

