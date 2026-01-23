"""
Script Principal: Ejecuta la simulación completa
"""

import sys
from pathlib import Path

# Agregar directorio padre al path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configurar multiprocessing para Windows ANTES de importar otros módulos
if sys.platform == 'win32':
    import multiprocessing
    try:
        multiprocessing.set_start_method('spawn', force=True)
    except RuntimeError:
        pass  # Ya está configurado

from simulacion.experimentos import Experimento
from simulacion.analisis_resultados import AnalizadorResultados
import argparse


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
    
    # Argumentos CLI
    parser = argparse.ArgumentParser(description="Simulación Guardia Gineco-Obstétrica")
    parser.add_argument("--replicas", type=int, default=5, help="Número de réplicas por escenario (default: 5)")
    parser.add_argument("--procesos", type=int, default=None, help="Número de procesos paralelos (default: todos los núcleos)")
    parser.add_argument("--yes", action="store_true", help="Saltar confirmación y ejecutar directamente")
    args = parser.parse_args()

    # Mostrar información de escenarios
    escenarios = experimento.generar_escenarios()
    print(f"\n{'='*80}")
    print("CONFIGURACIÓN DE EXPERIMENTOS")
    print(f"{'='*80}")
    import multiprocessing
    
    num_nucleos = multiprocessing.cpu_count()
    replicas = args.replicas
    print(f"Total de escenarios: {len(escenarios)}")
    print(f"Réplicas por escenario: {replicas}")
    print(f"Total de simulaciones: {len(escenarios) * replicas}")
    print(f"Núcleos disponibles: {num_nucleos}")
    print(f"Modo: PARALELO (usando todos los núcleos para réplicas)")
    print(f"\nEscenarios incluyen:")
    print(f"  - G (médicos): [2, 3, 4]")
    print(f"  - SC (salas de consultorio): [2, 3, 4, 5]")
    print(f"  - SR (salas recuperación): [15, 24, 30]")
    print(f"  - I (incubadoras): [10, 15, 20]")
    print(f"{'='*80}")
    
    if not args.yes:
        print("\n¿Deseas ejecutar todos los escenarios?")
        print("Esto puede tomar tiempo dependiendo de tu hardware...")
        respuesta = input("¿Continuar? (s/n): ").lower().strip()
        if respuesta != 's':
            print("Ejecución cancelada.")
            return
    
    resultados = experimento.ejecutar_todos_escenarios(
        num_replicas=replicas,
        semilla_base=42,
        mostrar_progreso=True,
        num_procesos=(args.procesos or num_nucleos)
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
        
        # Mostrar resultados por escenario (variables de resultado solicitadas)
        analizador.mostrar_resultados_por_escenario(df)
        
        # Elegir y mostrar las mejores opciones
        mejores = analizador.elegir_mejores_opciones(df)
        
        # Generar gráficos generales
        print("\nGenerando gráficos comparativos generales...")
        analizador.generar_graficos_comparativos(df)
        
        # Generar gráficos de las mejores 4 opciones
        print("\nGenerando gráficos comparativos de las mejores 4 opciones...")
        analizador.generar_graficos_mejores_4(df)

        # Generar gráficos de los casos destacados solicitados
        casos_destacados = [
            {'G': 4, 'SR': 15, 'I': 15},  # menor PEC
            {'G': 2, 'SR': 30, 'I': 10},  # menor PPDSR
            {'G': 2, 'SR': 15, 'I': 15},  # menor PPDINC
            {'G': 2, 'SR': 15, 'I': 20},  # menor CTM
        ]
        print("\nGenerando gráfico de casos destacados...")
        analizador.generar_graficos_casos_destacados(df, casos_destacados)
        
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

