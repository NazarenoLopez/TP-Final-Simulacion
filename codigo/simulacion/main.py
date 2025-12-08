"""
Script Principal: Ejecuta la simulación completa
"""

import sys
from pathlib import Path

# Agregar directorio padre al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from simulacion.experimentos import Experimento
from simulacion.analisis_resultados import AnalizadorResultados


def main():
    """Función principal."""
    print("\n" + "="*80)
    print("SIMULACIÓN DE EVENTOS DISCRETOS - GUARDIA GINECO-OBSTÉTRICA")
    print("Hospital Eurnekian")
    print("="*80)
    
    # Directorio de resultados
    directorio_resultados = Path(__file__).parent / "resultados_simulacion"
    
    # Crear experimento
    experimento = Experimento(directorio_resultados=str(directorio_resultados))
    
    # Mostrar información de escenarios
    escenarios = experimento.generar_escenarios()
    print(f"\n{'='*80}")
    print("CONFIGURACIÓN DE EXPERIMENTOS")
    print(f"{'='*80}")
    print(f"Total de escenarios: {len(escenarios)}")
    print(f"Réplicas por escenario: 30")
    print(f"Total de simulaciones: {len(escenarios) * 30}")
    print(f"\nEscenarios incluyen:")
    print(f"  - G (médicos): [2, 3, 4]")
    print(f"  - SR (salas recuperación): [20, 22, 24, 26, 28, 30]")
    print(f"    * Dotación actual: 24")
    print(f"    * Incluye casos con MENOS recursos: 20, 22")
    print(f"  - I (incubadoras): [11, 13, 15, 17, 19, 21]")
    print(f"    * Dotación actual: 15")
    print(f"    * Incluye casos con MENOS recursos: 11, 13")
    print(f"{'='*80}")
    
    print("\n¿Deseas ejecutar todos los escenarios?")
    print("Esto puede tomar varias horas dependiendo de tu hardware...")
    respuesta = input("¿Continuar? (s/n): ").lower().strip()
    
    if respuesta != 's':
        print("Ejecución cancelada.")
        return
    
    resultados = experimento.ejecutar_todos_escenarios(
        num_replicas=30,
        semilla_base=42,
        mostrar_progreso=True
    )
    
    print(f"\n{'='*80}")
    print("✓ SIMULACIONES COMPLETADAS")
    print(f"{'='*80}\n")
    
    # Analizar resultados
    print("Analizando resultados...")
    analizador = AnalizadorResultados(directorio_resultados=str(directorio_resultados))
    
    try:
        df = analizador.cargar_resultados()
        print(f"✓ Resultados cargados: {len(df)} escenarios")
        
        # Generar gráficos
        print("\nGenerando gráficos...")
        analizador.generar_graficos_comparativos(df)
        
        # Generar reporte
        print("\nGenerando reporte...")
        analizador.generar_reporte(df)
        
        print(f"\n{'='*80}")
        print("✓ ANÁLISIS COMPLETADO")
        print(f"{'='*80}\n")
        print(f"Resultados guardados en: {directorio_resultados}")
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
        print("Asegúrate de que las simulaciones se hayan completado correctamente.")


if __name__ == "__main__":
    main()

