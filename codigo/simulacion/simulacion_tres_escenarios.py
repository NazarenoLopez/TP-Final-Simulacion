"""
Script de Simulación: Comparación de Tres Escenarios
Hospital Eurnekian - Guardia Gineco-Obstétrica

Compara:
1. Configuración ACTUAL del hospital
2. Configuración MEJOR (optimizada)
3. Configuración PEOR (subóptima)
"""

import sys
from pathlib import Path
import json
import numpy as np
from datetime import datetime

# Agregar directorio padre al path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Configurar multiprocessing para Windows
if sys.platform == 'win32':
    import multiprocessing
    try:
        multiprocessing.set_start_method('spawn', force=True)
    except RuntimeError:
        pass

from simulacion.simulador import Simulador


class ComparadorEscenarios:
    """Ejecuta y compara tres escenarios de configuración."""
    
    def __init__(self, directorio_resultados: str = "resultados_comparacion"):
        self.directorio_resultados = Path(directorio_resultados)
        self.directorio_resultados.mkdir(parents=True, exist_ok=True)
        
    def definir_escenarios(self):
        """
        Define los tres escenarios a comparar.
        
        Returns:
            Dict con nombre, configuración y descripción de cada escenario
        """
        escenarios = {
            'ACTUAL': {
                'G': 1,   # 1 médico (según propuesta formal)
                'SC': 1,  # 1 sala consultorio (según propuesta)
                'SR': 24, # 24 salas recuperación (según propuesta)
                'I': 15,  # 15 incubadoras (según propuesta)
                'descripcion': 'Configuración actual del hospital según propuesta formal'
            },
            'MEJOR': {
                'G': 3,   # Mejor configuración basada en experimentos previos
                'SC': 3,  # Balance óptimo costo-servicio
                'SR': 24, # Suficiente para evitar derivaciones
                'I': 15,  # Adecuado para demanda de neonatología
                'descripcion': 'Configuración optimizada que minimiza costos manteniendo calidad'
            },
            'PEOR': {
                'G': 2,   # Recursos insuficientes
                'SC': 2,  # Pocas salas
                'SR': 15, # Salas insuficientes (alta derivación)
                'I': 10,  # Incubadoras insuficientes
                'descripcion': 'Configuración subóptima con recursos insuficientes'
            }
        }
        return escenarios
    
    def ejecutar_escenario(self, nombre: str, config: dict, num_replicas: int = 30, 
                          semilla_base: int = 42):
        """
        Ejecuta un escenario con múltiples réplicas.
        
        Args:
            nombre: Nombre del escenario
            config: Configuración (G, SC, SR, I)
            num_replicas: Número de réplicas
            semilla_base: Semilla base
            
        Returns:
            Estadísticas agregadas del escenario
        """
        print(f"\n{'='*80}")
        print(f"EJECUTANDO ESCENARIO: {nombre}")
        print(f"{'='*80}")
        print(f"Configuración:")
        print(f"  - Médicos (G): {config['G']}")
        print(f"  - Salas Consultorio (SC): {config['SC']}")
        print(f"  - Salas Recuperación (SR): {config['SR']}")
        print(f"  - Incubadoras (I): {config['I']}")
        print(f"\nDescripción: {config['descripcion']}")
        print(f"\nEjecutando {num_replicas} réplicas...")
        print(f"{'='*80}\n")
        
        # Directorio para este escenario
        dir_escenario = self.directorio_resultados / nombre
        dir_escenario.mkdir(parents=True, exist_ok=True)
        
        # Ejecutar réplicas
        replicas = []
        for replica in range(1, num_replicas + 1):
            semilla = semilla_base + replica * 1000 + config['G'] * 100
            
            # Crear y ejecutar simulador
            simulador = Simulador(
                G=config['G'],
                SR=config['SR'],
                I=config['I'],
                SC=config['SC'],
                semilla=semilla
            )
            
            resultados = simulador.ejecutar(mostrar_progreso=False)
            replicas.append(resultados)
            
            # Guardar réplica individual
            archivo_replica = dir_escenario / f"replica_{replica:02d}.json"
            with open(archivo_replica, 'w', encoding='utf-8') as f:
                json.dump(resultados, f, indent=2, ensure_ascii=False)
            
            # Progreso
            if replica % 5 == 0 or replica == num_replicas:
                print(f"  Progreso: {replica}/{num_replicas} réplicas completadas")
        
        print(f"\n✓ Escenario {nombre} completado\n")
        
        # Calcular estadísticas
        estadisticas = self._calcular_estadisticas(nombre, config, replicas)
        
        # Guardar resumen
        archivo_resumen = dir_escenario / "resumen.json"
        with open(archivo_resumen, 'w', encoding='utf-8') as f:
            json.dump(estadisticas, f, indent=2, ensure_ascii=False)
        
        return estadisticas
    
    def _calcular_estadisticas(self, nombre: str, config: dict, 
                               replicas: list) -> dict:
        """Calcula estadísticas agregadas de las réplicas."""
        
        # Indicadores a analizar
        indicadores = [
            'PEC_consultas', 'PEC_partos_nat', 'PEC_partos_ces', 'PEC_general',
            'UT_med', 'UT_Q', 'PTOSR_promedio',
            'PPDSR', 'PPDINC',
            'CTM', 'CII',
            'total_pacientes_llegados', 'total_pacientes_atendidos',
            'total_derivaciones_sr', 'total_derivaciones_inc'
        ]
        
        estadisticas = {
            'nombre': nombre,
            'configuracion': config,
            'num_replicas': len(replicas),
            'indicadores': {}
        }
        
        # Calcular media, desv.est. e IC 95% para cada indicador
        for indicador in indicadores:
            valores = [r[indicador] for r in replicas]
            media = np.mean(valores)
            std = np.std(valores, ddof=1)
            
            # Intervalo de confianza 95%
            n = len(valores)
            error_est = 1.96 * std / np.sqrt(n)
            ic_inf = media - error_est
            ic_sup = media + error_est
            
            estadisticas['indicadores'][indicador] = {
                'media': float(media),
                'std': float(std),
                'ic_95': [float(ic_inf), float(ic_sup)],
                'min': float(np.min(valores)),
                'max': float(np.max(valores))
            }
        
        return estadisticas
    
    def ejecutar_comparacion(self, num_replicas: int = 30, semilla_base: int = 42):
        """
        Ejecuta la comparación completa de los tres escenarios.
        
        Args:
            num_replicas: Número de réplicas por escenario
            semilla_base: Semilla base
        """
        print("\n" + "="*80)
        print("SIMULACIÓN DE 10 AÑOS - HOSPITAL EURNEKIAN")
        print("Comparación de Tres Escenarios")
        print("="*80)
        print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Horizonte: 10 años de operación")
        print(f"Réplicas por escenario: {num_replicas}")
        print("="*80)
        
        # Definir escenarios
        escenarios = self.definir_escenarios()
        
        # Ejecutar cada escenario
        resultados = {}
        for nombre, config in escenarios.items():
            resultados[nombre] = self.ejecutar_escenario(
                nombre, config, num_replicas, semilla_base
            )
        
        # Generar reporte comparativo
        self._generar_reporte_comparativo(resultados)
        
        print("\n" + "="*80)
        print("✓ COMPARACIÓN COMPLETADA")
        print("="*80)
        print(f"\nResultados guardados en: {self.directorio_resultados}")
        print("\nArchivos generados:")
        print("  - reporte_comparativo.txt: Reporte detallado")
        print("  - comparacion_escenarios.json: Datos JSON")
        print("  - [ACTUAL/MEJOR/PEOR]/: Resultados de cada escenario")
        print("="*80 + "\n")
    
    def _generar_reporte_comparativo(self, resultados: dict):
        """Genera reporte comparativo en texto y JSON."""
        
        # Guardar JSON
        archivo_json = self.directorio_resultados / "comparacion_escenarios.json"
        with open(archivo_json, 'w', encoding='utf-8') as f:
            json.dump(resultados, f, indent=2, ensure_ascii=False)
        
        # Generar reporte en texto
        archivo_txt = self.directorio_resultados / "reporte_comparativo.txt"
        
        with open(archivo_txt, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("REPORTE COMPARATIVO DE ESCENARIOS\n")
            f.write("Hospital Eurnekian - Guardia Gineco-Obstétrica\n")
            f.write("Simulación de 10 años de operación\n")
            f.write("="*80 + "\n\n")
            f.write(f"Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Resumen de configuraciones
            f.write("="*80 + "\n")
            f.write("CONFIGURACIONES EVALUADAS\n")
            f.write("="*80 + "\n\n")
            
            for nombre in ['ACTUAL', 'MEJOR', 'PEOR']:
                config = resultados[nombre]['configuracion']
                f.write(f"{nombre}:\n")
                f.write(f"  Médicos (G): {config['G']}\n")
                f.write(f"  Salas Consultorio (SC): {config['SC']}\n")
                f.write(f"  Salas Recuperación (SR): {config['SR']}\n")
                f.write(f"  Incubadoras (I): {config['I']}\n")
                f.write(f"  Descripción: {config['descripcion']}\n\n")
            
            # Variables de resultado (según propuesta formal)
            f.write("="*80 + "\n")
            f.write("VARIABLES DE RESULTADO (según propuesta formal)\n")
            f.write("="*80 + "\n\n")
            
            # PECC - Promedio de espera en cola para consulta
            f.write("-"*80 + "\n")
            f.write("PECC - Promedio de Espera en Cola para CONSULTA (minutos)\n")
            f.write("-"*80 + "\n")
            f.write(f"{'Escenario':<15} {'Media':<15} {'Desv.Est':<15} {'IC 95%':<30}\n")
            f.write("-"*80 + "\n")
            for nombre in ['ACTUAL', 'MEJOR', 'PEOR']:
                ind = resultados[nombre]['indicadores']['PEC_consultas']
                f.write(f"{nombre:<15} {ind['media']:<15.2f} {ind['std']:<15.2f} "
                       f"[{ind['ic_95'][0]:.2f}, {ind['ic_95'][1]:.2f}]\n")
            f.write("\n")
            
            # PECP - Promedio de espera en cola para parto
            f.write("-"*80 + "\n")
            f.write("PECP - Promedio de Espera en Cola para PARTO (minutos)\n")
            f.write("-"*80 + "\n")
            f.write(f"{'Escenario':<15} {'Naturales':<15} {'Cesáreas':<15} {'General':<15}\n")
            f.write("-"*80 + "\n")
            for nombre in ['ACTUAL', 'MEJOR', 'PEOR']:
                pec_nat = resultados[nombre]['indicadores']['PEC_partos_nat']['media']
                pec_ces = resultados[nombre]['indicadores']['PEC_partos_ces']['media']
                pec_gen = resultados[nombre]['indicadores']['PEC_general']['media']
                f.write(f"{nombre:<15} {pec_nat:<15.2f} {pec_ces:<15.2f} {pec_gen:<15.2f}\n")
            f.write("\n")
            
            # PTOSR - Porcentaje de tiempo ocioso salas recuperación
            f.write("-"*80 + "\n")
            f.write("PTOSR - Porcentaje de Tiempo Ocioso de Salas de Recuperación (%)\n")
            f.write("-"*80 + "\n")
            f.write(f"{'Escenario':<15} {'Media':<15} {'Desv.Est':<15} {'IC 95%':<30}\n")
            f.write("-"*80 + "\n")
            for nombre in ['ACTUAL', 'MEJOR', 'PEOR']:
                ind = resultados[nombre]['indicadores']['PTOSR_promedio']
                # Convertir de fracción a porcentaje
                f.write(f"{nombre:<15} {ind['media']*100:<15.2f} {ind['std']*100:<15.2f} "
                       f"[{ind['ic_95'][0]*100:.2f}, {ind['ic_95'][1]*100:.2f}]\n")
            f.write("\n")
            
            # PPDSR - Porcentaje de pacientes derivados por falta de salas
            f.write("-"*80 + "\n")
            f.write("PPDSR - Porcentaje de Pacientes Derivados por Falta de Salas (%)\n")
            f.write("-"*80 + "\n")
            f.write(f"{'Escenario':<15} {'Media':<15} {'Desv.Est':<15} {'IC 95%':<30}\n")
            f.write("-"*80 + "\n")
            for nombre in ['ACTUAL', 'MEJOR', 'PEOR']:
                ind = resultados[nombre]['indicadores']['PPDSR']
                # Convertir de fracción a porcentaje
                f.write(f"{nombre:<15} {ind['media']*100:<15.2f} {ind['std']*100:<15.2f} "
                       f"[{ind['ic_95'][0]*100:.2f}, {ind['ic_95'][1]*100:.2f}]\n")
            f.write("\n")
            
            # CTM - Costo Total Mensual
            f.write("-"*80 + "\n")
            f.write("CTM - Costo Total Mensual de Operación (ARS $)\n")
            f.write("-"*80 + "\n")
            f.write(f"{'Escenario':<15} {'Media':<20} {'Desv.Est':<20}\n")
            f.write("-"*80 + "\n")
            for nombre in ['ACTUAL', 'MEJOR', 'PEOR']:
                ind = resultados[nombre]['indicadores']['CTM']
                f.write(f"{nombre:<15} ${ind['media']:<19,.2f} ${ind['std']:<19,.2f}\n")
            f.write("\n")
            
            # CII - Costo Inicial de Instalaciones
            f.write("-"*80 + "\n")
            f.write("CII - Costo Inicial de Instalaciones (ARS $)\n")
            f.write("-"*80 + "\n")
            f.write(f"{'Escenario':<15} {'Costo':<20}\n")
            f.write("-"*80 + "\n")
            for nombre in ['ACTUAL', 'MEJOR', 'PEOR']:
                ind = resultados[nombre]['indicadores']['CII']
                f.write(f"{nombre:<15} ${ind['media']:<19,.2f}\n")
            f.write("\n")
            
            # Indicadores adicionales
            f.write("="*80 + "\n")
            f.write("INDICADORES ADICIONALES DE DESEMPEÑO\n")
            f.write("="*80 + "\n\n")
            
            # Utilización de recursos
            f.write("-"*80 + "\n")
            f.write("Utilización de Recursos (%)\n")
            f.write("-"*80 + "\n")
            f.write(f"{'Escenario':<15} {'Médicos':<15} {'Quirófano':<15}\n")
            f.write("-"*80 + "\n")
            for nombre in ['ACTUAL', 'MEJOR', 'PEOR']:
                # Ya vienen como fracción (0-1), multiplicar por 100 para %
                ut_med = resultados[nombre]['indicadores']['UT_med']['media'] * 100
                ut_q = resultados[nombre]['indicadores']['UT_Q']['media'] * 100
                f.write(f"{nombre:<15} {ut_med:<15.2f} {ut_q:<15.2f}\n")
            f.write("\n")
            
            # Derivaciones
            f.write("-"*80 + "\n")
            f.write("Total de Derivaciones (10 años)\n")
            f.write("-"*80 + "\n")
            f.write(f"{'Escenario':<15} {'Salas Recup.':<20} {'Incubadoras':<20}\n")
            f.write("-"*80 + "\n")
            for nombre in ['ACTUAL', 'MEJOR', 'PEOR']:
                deriv_sr = resultados[nombre]['indicadores']['total_derivaciones_sr']['media']
                deriv_inc = resultados[nombre]['indicadores']['total_derivaciones_inc']['media']
                f.write(f"{nombre:<15} {deriv_sr:<20.0f} {deriv_inc:<20.0f}\n")
            f.write("\n")
            
            # Volumen de atención
            f.write("-"*80 + "\n")
            f.write("Volumen de Atención (10 años)\n")
            f.write("-"*80 + "\n")
            f.write(f"{'Escenario':<15} {'Pacientes Llegados':<25} {'Pacientes Atendidos':<25}\n")
            f.write("-"*80 + "\n")
            for nombre in ['ACTUAL', 'MEJOR', 'PEOR']:
                llegados = resultados[nombre]['indicadores']['total_pacientes_llegados']['media']
                atendidos = resultados[nombre]['indicadores']['total_pacientes_atendidos']['media']
                f.write(f"{nombre:<15} {llegados:<25.0f} {atendidos:<25.0f}\n")
            f.write("\n")
            
            # Análisis y recomendaciones
            f.write("="*80 + "\n")
            f.write("ANÁLISIS Y RECOMENDACIONES\n")
            f.write("="*80 + "\n\n")
            
            # Determinar mejor escenario
            ctm_actual = resultados['ACTUAL']['indicadores']['CTM']['media']
            ctm_mejor = resultados['MEJOR']['indicadores']['CTM']['media']
            ctm_peor = resultados['PEOR']['indicadores']['CTM']['media']
            
            ppdsr_actual = resultados['ACTUAL']['indicadores']['PPDSR']['media']
            ppdsr_mejor = resultados['MEJOR']['indicadores']['PPDSR']['media']
            
            f.write("Comparación de Costos Mensuales (promedio):\n")
            f.write(f"  - Actual: ${ctm_actual:,.2f}\n")
            f.write(f"  - Mejor: ${ctm_mejor:,.2f}\n")
            f.write(f"  - Peor: ${ctm_peor:,.2f}\n\n")
            
            # Calcular diferencia de costos
            diff_mejor_actual = ctm_mejor - ctm_actual
            diff_peor_actual = ctm_peor - ctm_actual
            
            if diff_mejor_actual > 0:
                f.write(f"Costo adicional con configuración MEJOR:\n")
                f.write(f"  - Mensual: ${diff_mejor_actual:,.2f} (+{diff_mejor_actual/ctm_actual*100:.1f}%)\n")
                f.write(f"  - Anual: ${diff_mejor_actual*12:,.2f}\n\n")
            elif diff_mejor_actual < 0:
                f.write(f"Ahorro potencial con configuración MEJOR:\n")
                f.write(f"  - Mensual: ${abs(diff_mejor_actual):,.2f} ({abs(diff_mejor_actual)/ctm_actual*100:.1f}%)\n")
                f.write(f"  - Anual: ${abs(diff_mejor_actual)*12:,.2f}\n\n")
            
            f.write(f"Nivel de servicio (% de derivaciones por falta de salas):\n")
            # Convertir de fracción a porcentaje
            f.write(f"  - Actual: {ppdsr_actual*100:.2f}%\n")
            f.write(f"  - Mejor: {ppdsr_mejor*100:.2f}%\n\n")
            
            f.write("RECOMENDACIÓN:\n")
            if diff_mejor_actual < 0 and ppdsr_mejor*100 <= ppdsr_actual*100:
                f.write(f"Se recomienda adoptar la configuración MEJOR que permite:\n")
                f.write(f"  - Reducir costos en ${abs(diff_mejor_actual):,.2f}/mes\n")
                f.write(f"  - Mantener o mejorar el nivel de servicio\n")
                f.write(f"  - Optimizar la utilización de recursos\n")
            elif diff_mejor_actual > 0:
                # MEJOR cuesta más
                mejora_espera_consultas = (resultados['ACTUAL']['indicadores']['PEC_consultas']['media'] - 
                                          resultados['MEJOR']['indicadores']['PEC_consultas']['media'])
                f.write(f"La configuración MEJOR implica mayor costo pero mejora significativamente el servicio:\n")
                f.write(f"  - Costo adicional: ${diff_mejor_actual:,.2f}/mes (+{diff_mejor_actual/ctm_actual*100:.1f}%)\n")
                f.write(f"  - Reduce espera en consultas en {mejora_espera_consultas:.1f} minutos (de {resultados['ACTUAL']['indicadores']['PEC_consultas']['media']:.1f} a {resultados['MEJOR']['indicadores']['PEC_consultas']['media']:.1f} min)\n")
                f.write(f"  - Inversión inicial requerida: ${resultados['MEJOR']['indicadores']['CII']['media']:,.0f}\n")
                f.write(f"\nDECISIÓN: Evaluar si la mejora en calidad de servicio justifica el incremento de costo.\n")
            elif ppdsr_actual*100 > 5:
                f.write(f"Se requiere evaluar ampliación de recursos:\n")
                f.write(f"  - Alto nivel de derivaciones: {ppdsr_actual*100:.2f}%\n")
                f.write(f"  - Esto impacta negativamente en la calidad del servicio\n")
            else:
                f.write(f"La configuración ACTUAL mantiene un balance adecuado entre costo y servicio:\n")
                f.write(f"  - Nivel de derivaciones aceptable: {ppdsr_actual*100:.2f}%\n")
                f.write(f"  - Costo operativo competitivo\n")
                f.write(f"  - Considerar la configuración MEJOR solo si se busca reducir tiempos de espera\n")
            
            f.write("\n" + "="*80 + "\n")
            f.write("FIN DEL REPORTE\n")
            f.write("="*80 + "\n")


def main():
    """Función principal."""
    print("\n" + "="*80)
    print("COMPARACIÓN DE ESCENARIOS - HOSPITAL EURNEKIAN")
    print("="*80)
    
    comparador = ComparadorEscenarios()
    comparador.ejecutar_comparacion(num_replicas=30, semilla_base=42)


if __name__ == '__main__':
    main()
