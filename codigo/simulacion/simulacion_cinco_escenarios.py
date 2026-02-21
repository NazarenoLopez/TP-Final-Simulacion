"""
Script de Simulación: Comparación de Cinco Escenarios
Hospital Eurnekian - Guardia Gineco-Obstétrica

Compara:
1. Configuración ACTUAL (actualizada: 2G, 19SR, 12I, 1SC)
2. Configuración MEJOR_1 (optimizada)
3. Configuración MEJOR_2 (optimizada alternativa)
4. Configuración PEOR_1 (recursos mínimos)
5. Configuración PEOR_2 (subóptima)
"""

import sys
from pathlib import Path
import json
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Backend sin interfaz gráfica

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


class ComparadorCincoEscenarios:
    """Ejecuta y compara cinco escenarios de configuración."""
    
    def __init__(self, directorio_resultados: str = "resultados_cinco_escenarios"):
        self.directorio_resultados = Path(directorio_resultados)
        self.directorio_resultados.mkdir(parents=True, exist_ok=True)
        
    def definir_escenarios(self):
        """
        Define los cinco escenarios a comparar.
        
        Returns:
            Dict con nombre, configuración y descripción de cada escenario
        """
        escenarios = {
            'ACTUAL': {
                'G': 2,   # 2 médicos (actualizado)
                'SC': 1,  # 1 sala consultorio
                'SR': 19, # 19 salas recuperación (actualizado)
                'I': 12,  # 12 incubadoras (actualizado)
                'descripcion': 'Configuración actual actualizada del hospital'
            },
            'CASO 1': {
                'G': 3,   # Óptimo balance costo-servicio
                'SC': 3,  # Suficientes consultorios
                'SR': 24, # Amplio margen para partos
                'I': 15,  # Adecuado para neonatología
                'descripcion': 'Configuración optimizada principal - maximiza calidad de servicio'
            },
            'CASO 2': {
                'G': 3,   # Misma cantidad de médicos
                'SC': 2,  # Menos consultorios pero suficientes
                'SR': 20, # Reducción moderada en salas
                'I': 13,  # Incubadoras suficientes
                'descripcion': 'Configuración optimizada alternativa - balance costo-calidad'
            },
            'CASO 3': {
                'G': 1,   # Recursos mínimos
                'SC': 1,  # Mínimo posible
                'SR': 15, # Salas insuficientes (alta derivación)
                'I': 10,  # Incubadoras insuficientes
                'descripcion': 'Configuración mínima - alta probabilidad de derivaciones'
            },
            'CASO 4': {
                'G': 2,   # Recursos limitados
                'SC': 1,  # Consultorio único
                'SR': 16, # Salas apenas suficientes
                'I': 11,  # Incubadoras ajustadas
                'descripcion': 'Configuración subóptima - servicio comprometido'
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
        Ejecuta la comparación completa de los cinco escenarios.
        
        Args:
            num_replicas: Número de réplicas por escenario
            semilla_base: Semilla base
        """
        print("\n" + "="*80)
        print("SIMULACIÓN DE 10 AÑOS - HOSPITAL EURNEKIAN")
        print("Comparación de Cinco Escenarios (ACTUAL + 2 MEJORES + 2 PEORES)")
        print("="*80)
        print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Horizonte: 10 años de operación")
        print(f"Réplicas por escenario: {num_replicas}")
        print("="*80)
        
        # Definir escenarios
        escenarios = self.definir_escenarios()
        
        # Ejecutar cada escenario
        resultados_escenarios = {}
        for nombre, config in escenarios.items():
            estadisticas = self.ejecutar_escenario(nombre, config, num_replicas, semilla_base)
            resultados_escenarios[nombre] = estadisticas
        
        # Guardar resultados consolidados
        archivo_consolidado = self.directorio_resultados / "comparacion_escenarios.json"
        with open(archivo_consolidado, 'w', encoding='utf-8') as f:
            json.dump(resultados_escenarios, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Resultados consolidados guardados en: {archivo_consolidado}")
        
        # Generar reporte comparativo
        self._generar_reporte_comparativo(resultados_escenarios)
        
        # Generar gráficos
        self._generar_graficos_comparativos(resultados_escenarios)
        
        return resultados_escenarios
    
    def _generar_reporte_comparativo(self, resultados: dict):
        """Genera reporte comparativo en formato texto."""
        
        archivo_reporte = self.directorio_resultados / "reporte_comparativo.txt"
        
        with open(archivo_reporte, 'w', encoding='utf-8') as f:
            # Encabezado
            f.write("="*80 + "\n")
            f.write("REPORTE COMPARATIVO DE CINCO ESCENARIOS\n")
            f.write("Hospital Eurnekian - Guardia Gineco-Obstétrica\n")
            f.write("Simulación de 10 años de operación\n")
            f.write("="*80 + "\n\n")
            f.write(f"Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Configuraciones
            f.write("="*80 + "\n")
            f.write("CONFIGURACIONES EVALUADAS\n")
            f.write("="*80 + "\n\n")
            
            for nombre, datos in resultados.items():
                config = datos['configuracion']
                f.write(f"{nombre}:\n")
                f.write(f"  Médicos (G): {config['G']}\n")
                f.write(f"  Salas Consultorio (SC): {config['SC']}\n")
                f.write(f"  Salas Recuperación (SR): {config['SR']}\n")
                f.write(f"  Incubadoras (I): {config['I']}\n")
                f.write(f"  Descripción: {config['descripcion']}\n\n")
            
            # Variables de resultado
            f.write("="*80 + "\n")
            f.write("VARIABLES DE RESULTADO (según propuesta formal)\n")
            f.write("="*80 + "\n\n")
            
            # PECC - Promedio de Espera en Cola para CONSULTA
            f.write("-"*80 + "\n")
            f.write("PECC - Promedio de Espera en Cola para CONSULTA (minutos)\n")
            f.write("-"*80 + "\n")
            f.write(f"{'Escenario':<15} {'Media':<15} {'Desv.Est':<15} {'IC 95%':<30}\n")
            f.write("-"*80 + "\n")
            for nombre, datos in resultados.items():
                ind = datos['indicadores']['PEC_consultas']
                f.write(f"{nombre:<15} {ind['media']:<15.2f} {ind['std']:<15.2f} "
                       f"[{ind['ic_95'][0]:.2f}, {ind['ic_95'][1]:.2f}]\n")
            
            # PECP - Promedio de Espera en Cola para PARTO
            f.write("\n" + "-"*80 + "\n")
            f.write("PECP - Promedio de Espera en Cola para PARTO (minutos)\n")
            f.write("-"*80 + "\n")
            f.write(f"{'Escenario':<15} {'Naturales':<15} {'Cesáreas':<15} {'General':<15}\n")
            f.write("-"*80 + "\n")
            for nombre, datos in resultados.items():
                nat = datos['indicadores']['PEC_partos_nat']['media']
                ces = datos['indicadores']['PEC_partos_ces']['media']
                gen = datos['indicadores']['PEC_general']['media']
                f.write(f"{nombre:<15} {nat:<15.2f} {ces:<15.2f} {gen:<15.2f}\n")
            
            # PTOSR - Porcentaje de Tiempo Ocioso de Salas de Recuperación
            f.write("\n" + "-"*80 + "\n")
            f.write("PTOSR - Porcentaje de Tiempo Ocioso de Salas de Recuperación (%)\n")
            f.write("-"*80 + "\n")
            f.write(f"{'Escenario':<15} {'Media':<15} {'Desv.Est':<15} {'IC 95%':<30}\n")
            f.write("-"*80 + "\n")
            for nombre, datos in resultados.items():
                ind = datos['indicadores']['PTOSR_promedio']
                f.write(f"{nombre:<15} {ind['media']:<15.2f} {ind['std']:<15.2f} "
                       f"[{ind['ic_95'][0]:.2f}, {ind['ic_95'][1]:.2f}]\n")
            
            # PPDSR - Porcentaje de Pacientes Derivados por Falta de Salas
            f.write("\n" + "-"*80 + "\n")
            f.write("PPDSR - Porcentaje de Pacientes Derivados por Falta de Salas (%)\n")
            f.write("-"*80 + "\n")
            f.write(f"{'Escenario':<15} {'Media':<15} {'Desv.Est':<15} {'IC 95%':<30}\n")
            f.write("-"*80 + "\n")
            for nombre, datos in resultados.items():
                ind = datos['indicadores']['PPDSR']
                f.write(f"{nombre:<15} {ind['media']:<15.2f} {ind['std']:<15.2f} "
                       f"[{ind['ic_95'][0]:.2f}, {ind['ic_95'][1]:.2f}]\n")
            
            # CTM - Costo Total Mensual de Operación
            f.write("\n" + "-"*80 + "\n")
            f.write("CTM - Costo Total Mensual de Operación (ARS $)\n")
            f.write("-"*80 + "\n")
            f.write(f"{'Escenario':<15} {'Media':<25} {'Desv.Est':<20}\n")
            f.write("-"*80 + "\n")
            for nombre, datos in resultados.items():
                ind = datos['indicadores']['CTM']
                f.write(f"{nombre:<15} ${ind['media']:>20,.2f}    ${ind['std']:>15,.2f}\n")
            
            # CII - Costo Inicial de Instalaciones
            f.write("\n" + "-"*80 + "\n")
            f.write("CII - Costo Inicial de Instalaciones (ARS $)\n")
            f.write("-"*80 + "\n")
            f.write(f"{'Escenario':<15} {'Costo':<20}\n")
            f.write("-"*80 + "\n")
            for nombre, datos in resultados.items():
                ind = datos['indicadores']['CII']
                f.write(f"{nombre:<15} ${ind['media']:>15,.2f}\n")
            
            # Indicadores adicionales
            f.write("\n" + "="*80 + "\n")
            f.write("INDICADORES ADICIONALES DE DESEMPEÑO\n")
            f.write("="*80 + "\n\n")
            
            # Utilización de Recursos
            f.write("-"*80 + "\n")
            f.write("Utilización de Recursos (%)\n")
            f.write("-"*80 + "\n")
            f.write(f"{'Escenario':<15} {'Médicos':<15} {'Quirófano':<15}\n")
            f.write("-"*80 + "\n")
            for nombre, datos in resultados.items():
                ut_med = datos['indicadores']['UT_med']['media']
                ut_q = datos['indicadores']['UT_Q']['media']
                f.write(f"{nombre:<15} {ut_med:<15.2f} {ut_q:<15.2f}\n")
            
            # Total de Derivaciones
            f.write("\n" + "-"*80 + "\n")
            f.write("Total de Derivaciones (10 años)\n")
            f.write("-"*80 + "\n")
            f.write(f"{'Escenario':<15} {'Salas Recup.':<25} {'Incubadoras':<20}\n")
            f.write("-"*80 + "\n")
            for nombre, datos in resultados.items():
                der_sr = datos['indicadores']['total_derivaciones_sr']['media']
                der_inc = datos['indicadores']['total_derivaciones_inc']['media']
                f.write(f"{nombre:<15} {der_sr:<25.0f} {der_inc:<20.0f}\n")
            
            # Volumen de Atención
            f.write("\n" + "-"*80 + "\n")
            f.write("Volumen de Atención (10 años)\n")
            f.write("-"*80 + "\n")
            f.write(f"{'Escenario':<15} {'Pacientes Llegados':<25} {'Pacientes Atendidos':<25}\n")
            f.write("-"*80 + "\n")
            for nombre, datos in resultados.items():
                llegados = datos['indicadores']['total_pacientes_llegados']['media']
                atendidos = datos['indicadores']['total_pacientes_atendidos']['media']
                f.write(f"{nombre:<15} {llegados:<25.0f} {atendidos:<25.0f}\n")
            
            # Análisis y Recomendaciones
            f.write("\n" + "="*80 + "\n")
            f.write("ANÁLISIS Y RECOMENDACIONES\n")
            f.write("="*80 + "\n\n")
            
            # Comparación de costos con ACTUAL
            actual = resultados['ACTUAL']
            ctm_actual = actual['indicadores']['CTM']['media']
            
            f.write("Comparación de Costos Mensuales vs. ACTUAL:\n")
            for nombre, datos in resultados.items():
                if nombre == 'ACTUAL':
                    continue
                ctm = datos['indicadores']['CTM']['media']
                diff = ctm - ctm_actual
                pct = (diff / ctm_actual) * 100
                f.write(f"  - {nombre}: ${ctm:,.2f} ({diff:+,.2f}, {pct:+.1f}%)\n")
            
            f.write("\n")
            
            # Nivel de servicio
            f.write("Nivel de Servicio (% de derivaciones por falta de salas):\n")
            for nombre, datos in resultados.items():
                ppdsr = datos['indicadores']['PPDSR']['media']
                f.write(f"  - {nombre}: {ppdsr:.2f}%\n")
            
            f.write("\n")
            
            # Recomendaciones
            f.write("RECOMENDACIONES:\n\n")
            
            # Encontrar mejor y peor en términos de servicio (menor derivación)
            mejor_servicio = min(resultados.items(), 
                               key=lambda x: x[1]['indicadores']['PPDSR']['media'])
            peor_servicio = max(resultados.items(), 
                              key=lambda x: x[1]['indicadores']['PPDSR']['media'])
            
            # Encontrar más económico
            mas_economico = min(resultados.items(), 
                              key=lambda x: x[1]['indicadores']['CTM']['media'])
            
            f.write(f"1. MEJOR CALIDAD DE SERVICIO: {mejor_servicio[0]}\n")
            f.write(f"   - Derivaciones: {mejor_servicio[1]['indicadores']['PPDSR']['media']:.2f}%\n")
            f.write(f"   - Espera consultas: {mejor_servicio[1]['indicadores']['PEC_consultas']['media']:.1f} min\n")
            f.write(f"   - Costo mensual: ${mejor_servicio[1]['indicadores']['CTM']['media']:,.2f}\n\n")
            
            f.write(f"2. MÁS ECONÓMICO: {mas_economico[0]}\n")
            f.write(f"   - Costo mensual: ${mas_economico[1]['indicadores']['CTM']['media']:,.2f}\n")
            f.write(f"   - Derivaciones: {mas_economico[1]['indicadores']['PPDSR']['media']:.2f}%\n")
            f.write(f"   - Espera consultas: {mas_economico[1]['indicadores']['PEC_consultas']['media']:.1f} min\n\n")
            
            f.write(f"3. PEOR DESEMPEÑO: {peor_servicio[0]}\n")
            f.write(f"   - Derivaciones: {peor_servicio[1]['indicadores']['PPDSR']['media']:.2f}%\n")
            f.write(f"   - NO RECOMENDADO debido a alto nivel de derivaciones\n\n")
            
            # Análisis ACTUAL
            actual_ppdsr = actual['indicadores']['PPDSR']['media']
            actual_pec = actual['indicadores']['PEC_consultas']['media']
            
            f.write("EVALUACIÓN DE CONFIGURACIÓN ACTUAL:\n")
            if actual_ppdsr < 1.0:
                f.write(f"✓ Nivel de derivaciones ACEPTABLE ({actual_ppdsr:.2f}%)\n")
            elif actual_ppdsr < 3.0:
                f.write(f"⚠ Nivel de derivaciones MODERADO ({actual_ppdsr:.2f}%) - considerar mejora\n")
            else:
                f.write(f"✗ Nivel de derivaciones ALTO ({actual_ppdsr:.2f}%) - requiere mejora urgente\n")
            
            if actual_pec < 30:
                f.write(f"✓ Tiempo de espera en consultas EXCELENTE ({actual_pec:.1f} min)\n")
            elif actual_pec < 60:
                f.write(f"✓ Tiempo de espera en consultas ACEPTABLE ({actual_pec:.1f} min)\n")
            else:
                f.write(f"⚠ Tiempo de espera en consultas ELEVADO ({actual_pec:.1f} min)\n")
            
            f.write("\n" + "="*80 + "\n")
            f.write("FIN DEL REPORTE\n")
            f.write("="*80 + "\n")
        
        print(f"\n✓ Reporte comparativo generado: {archivo_reporte}")
    
    def _generar_graficos_comparativos(self, resultados: dict):
        """Genera gráficos comparativos de todos los indicadores."""
        
        print("\n" + "="*80)
        print("GENERANDO GRÁFICOS COMPARATIVOS")
        print("="*80)
        
        dir_graficos = self.directorio_resultados / "graficos"
        dir_graficos.mkdir(parents=True, exist_ok=True)
        
        # Colores para cada escenario
        colores = {
            'ACTUAL': '#2E86AB',      # Azul
            'CASO 1': '#06A77D',      # Verde
            'CASO 2': '#52D1DC',      # Cyan
            'CASO 3': '#D62246',      # Rojo
            'CASO 4': '#F77E21'       # Naranja
        }
        
        nombres = list(resultados.keys())
        
        # 1. Espera en Consultas
        self._grafico_barras_con_ic(
            resultados, 'PEC_consultas',
            'Promedio de Espera en Cola para CONSULTA',
            'Tiempo (minutos)',
            dir_graficos / 'espera_consultas.png',
            colores
        )
        
        # 2. Espera en Partos (Naturales, Cesáreas, General)
        self._grafico_partos(resultados, dir_graficos / 'espera_partos.png', colores)
        
        # 3. Porcentaje de Derivaciones por Salas
        self._grafico_barras_con_ic(
            resultados, 'PPDSR',
            'Porcentaje de Pacientes Derivados por Falta de Salas',
            'Porcentaje (%)',
            dir_graficos / 'derivaciones_salas.png',
            colores
        )
        
        # 4. Tiempo Ocioso de Salas de Recuperación
        self._grafico_barras_con_ic(
            resultados, 'PTOSR_promedio',
            'Porcentaje de Tiempo Ocioso - Salas de Recuperación',
            'Porcentaje (%)',
            dir_graficos / 'tiempo_ocioso_salas.png',
            colores
        )
        
        # 5. Costo Total Mensual
        self._grafico_costos(resultados, dir_graficos / 'costos_mensuales.png', colores)
        
        # 6. Total de Derivaciones (Salas e Incubadoras)
        self._grafico_derivaciones_totales(
            resultados, 
            dir_graficos / 'derivaciones_totales.png', 
            colores
        )
        
        # 7. Resumen de indicadores clave
        self._grafico_resumen_indicadores(
            resultados, 
            dir_graficos / 'resumen_indicadores.png', 
            colores
        )
        
        print(f"\n✓ Gráficos generados en: {dir_graficos}")
    
    def _crear_referencias_config(self, resultados: dict) -> str:
        """
        Crea el texto de referencias de configuración para los gráficos.
        
        Returns:
            String con las configuraciones en formato "Nombre: XG, YSC, ZSR, WI"
        """
        referencias = []
        for nombre, datos in resultados.items():
            config = datos['configuracion']
            ref = f"{nombre}: {config['G']}G, {config['SC']}SC, {config['SR']}SR, {config['I']}I"
            referencias.append(ref)
        
        return " | ".join(referencias)
    
    def _grafico_barras_con_ic(self, resultados, indicador, titulo, ylabel, 
                                archivo, colores):
        """Genera gráfico de barras con intervalos de confianza."""
        
        nombres = list(resultados.keys())
        medias = [resultados[n]['indicadores'][indicador]['media'] for n in nombres]
        stds = [resultados[n]['indicadores'][indicador]['std'] for n in nombres]
        
        # Detectar si son porcentajes (valores típicamente < 1) y convertir a escala 0-100
        es_porcentaje = ylabel.startswith('Porcentaje')
        if es_porcentaje:
            medias = [m * 100 for m in medias]
            stds = [s * 100 for s in stds]
        
        fig, ax = plt.subplots(figsize=(12, 7))
        
        x = np.arange(len(nombres))
        bars = ax.bar(x, medias, color=[colores[n] for n in nombres], 
                     alpha=0.8, edgecolor='black', linewidth=1.5)
        ax.errorbar(x, medias, yerr=stds, fmt='none', ecolor='black', 
                   capsize=5, capthick=2, alpha=0.7)
        
        ax.set_xlabel('Escenario', fontsize=12, fontweight='bold')
        ax.set_ylabel(ylabel, fontsize=12, fontweight='bold')
        ax.set_title(titulo, fontsize=14, fontweight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(nombres, fontsize=11)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Añadir valores en las barras
        for i, (bar, media) in enumerate(zip(bars, medias)):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{media:.2f}',
                   ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        # Agregar referencias de configuración
        referencias = self._crear_referencias_config(resultados)
        fig.text(0.5, 0.01, referencias, ha='center', fontsize=8, style='italic', 
                wrap=True, color='gray')
        
        plt.tight_layout(rect=[0, 0.03, 1, 1])
        plt.savefig(archivo, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  ✓ Generado: {archivo.name}")
    
    def _grafico_partos(self, resultados, archivo, colores):
        """Gráfico de espera en partos (naturales, cesáreas, general)."""
        
        nombres = list(resultados.keys())
        x = np.arange(len(nombres))
        width = 0.25
        
        naturales = [resultados[n]['indicadores']['PEC_partos_nat']['media'] 
                    for n in nombres]
        cesareas = [resultados[n]['indicadores']['PEC_partos_ces']['media'] 
                   for n in nombres]
        general = [resultados[n]['indicadores']['PEC_general']['media'] 
                  for n in nombres]
        
        fig, ax = plt.subplots(figsize=(14, 7))
        
        bars1 = ax.bar(x - width, naturales, width, label='Partos Naturales',
                      color='#06A77D', alpha=0.8, edgecolor='black', linewidth=1.5)
        bars2 = ax.bar(x, cesareas, width, label='Cesáreas',
                      color='#F77E21', alpha=0.8, edgecolor='black', linewidth=1.5)
        bars3 = ax.bar(x + width, general, width, label='General',
                      color='#2E86AB', alpha=0.8, edgecolor='black', linewidth=1.5)
        
        ax.set_xlabel('Escenario', fontsize=12, fontweight='bold')
        ax.set_ylabel('Tiempo (minutos)', fontsize=12, fontweight='bold')
        ax.set_title('Promedio de Espera en Cola para PARTO', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(nombres, fontsize=11)
        ax.legend(fontsize=11, loc='upper right')
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Añadir valores
        for bars in [bars1, bars2, bars3]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.1f}',
                       ha='center', va='bottom', fontsize=9)
        
        # Agregar referencias de configuración
        referencias = self._crear_referencias_config(resultados)
        fig.text(0.5, 0.01, referencias, ha='center', fontsize=8, style='italic', 
                wrap=True, color='gray')
        
        plt.tight_layout(rect=[0, 0.03, 1, 1])
        plt.savefig(archivo, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  ✓ Generado: {archivo.name}")
    
    def _grafico_costos(self, resultados, archivo, colores):
        """Gráfico de costos mensuales."""
        
        nombres = list(resultados.keys())
        medias = [resultados[n]['indicadores']['CTM']['media'] / 1e6 for n in nombres]
        stds = [resultados[n]['indicadores']['CTM']['std'] / 1e6 for n in nombres]
        
        fig, ax = plt.subplots(figsize=(12, 7))
        
        x = np.arange(len(nombres))
        bars = ax.bar(x, medias, color=[colores[n] for n in nombres], 
                     alpha=0.8, edgecolor='black', linewidth=1.5)
        ax.errorbar(x, medias, yerr=stds, fmt='none', ecolor='black', 
                   capsize=5, capthick=2, alpha=0.7)
        
        ax.set_xlabel('Escenario', fontsize=12, fontweight='bold')
        ax.set_ylabel('Costo (Millones de ARS $)', fontsize=12, fontweight='bold')
        ax.set_title('Costo Total Mensual de Operación', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(nombres, fontsize=11)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Añadir valores
        for bar, media in zip(bars, medias):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'${media:.2f}M',
                   ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        # Agregar referencias de configuración
        referencias = self._crear_referencias_config(resultados)
        fig.text(0.5, 0.01, referencias, ha='center', fontsize=8, style='italic', 
                wrap=True, color='gray')
        
        plt.tight_layout(rect=[0, 0.03, 1, 1])
        plt.savefig(archivo, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  ✓ Generado: {archivo.name}")
    
    def _grafico_utilizacion(self, resultados, archivo, colores):
        """Gráfico de utilización de recursos."""
        
        nombres = list(resultados.keys())
        x = np.arange(len(nombres))
        width = 0.35
        
        ut_med = [resultados[n]['indicadores']['UT_med']['media'] for n in nombres]
        ut_q = [resultados[n]['indicadores']['UT_Q']['media'] for n in nombres]
        
        fig, ax = plt.subplots(figsize=(12, 7))
        
        bars1 = ax.bar(x - width/2, ut_med, width, label='Médicos',
                      color='#06A77D', alpha=0.8, edgecolor='black', linewidth=1.5)
        bars2 = ax.bar(x + width/2, ut_q, width, label='Quirófano',
                      color='#2E86AB', alpha=0.8, edgecolor='black', linewidth=1.5)
        
        ax.set_xlabel('Escenario', fontsize=12, fontweight='bold')
        ax.set_ylabel('Utilización (%)', fontsize=12, fontweight='bold')
        ax.set_title('Utilización de Recursos', fontsize=14, fontweight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(nombres, fontsize=11)
        ax.legend(fontsize=11)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        ax.set_ylim(0, 100)
        
        # Añadir valores
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.1f}%',
                       ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        plt.savefig(archivo, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  ✓ Generado: {archivo.name}")
    
    def _grafico_derivaciones_totales(self, resultados, archivo, colores):
        """Gráfico de derivaciones totales."""
        
        nombres = list(resultados.keys())
        x = np.arange(len(nombres))
        width = 0.35
        
        der_sr = [resultados[n]['indicadores']['total_derivaciones_sr']['media'] 
                 for n in nombres]
        der_inc = [resultados[n]['indicadores']['total_derivaciones_inc']['media'] 
                  for n in nombres]
        
        fig, ax = plt.subplots(figsize=(12, 7))
        
        bars1 = ax.bar(x - width/2, der_sr, width, label='Salas Recuperación',
                      color='#D62246', alpha=0.8, edgecolor='black', linewidth=1.5)
        bars2 = ax.bar(x + width/2, der_inc, width, label='Incubadoras',
                      color='#F77E21', alpha=0.8, edgecolor='black', linewidth=1.5)
        
        ax.set_xlabel('Escenario', fontsize=12, fontweight='bold')
        ax.set_ylabel('Número de Derivaciones', fontsize=12, fontweight='bold')
        ax.set_title('Total de Derivaciones en 10 Años', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(nombres, fontsize=11)
        ax.legend(fontsize=11)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Añadir valores
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{int(height)}',
                           ha='center', va='bottom', fontsize=9)
        
        # Agregar referencias de configuración
        referencias = self._crear_referencias_config(resultados)
        fig.text(0.5, 0.01, referencias, ha='center', fontsize=8, style='italic', 
                wrap=True, color='gray')
        
        plt.tight_layout(rect=[0, 0.03, 1, 1])
        plt.savefig(archivo, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  ✓ Generado: {archivo.name}")
    
    def _grafico_volumen_atencion(self, resultados, archivo, colores):
        """Gráfico de volumen de atención."""
        
        nombres = list(resultados.keys())
        x = np.arange(len(nombres))
        width = 0.35
        
        llegados = [resultados[n]['indicadores']['total_pacientes_llegados']['media'] / 1000
                   for n in nombres]
        atendidos = [resultados[n]['indicadores']['total_pacientes_atendidos']['media'] / 1000
                    for n in nombres]
        
        fig, ax = plt.subplots(figsize=(12, 7))
        
        bars1 = ax.bar(x - width/2, llegados, width, label='Pacientes Llegados',
                      color='#52D1DC', alpha=0.8, edgecolor='black', linewidth=1.5)
        bars2 = ax.bar(x + width/2, atendidos, width, label='Pacientes Atendidos',
                      color='#06A77D', alpha=0.8, edgecolor='black', linewidth=1.5)
        
        ax.set_xlabel('Escenario', fontsize=12, fontweight='bold')
        ax.set_ylabel('Pacientes (miles)', fontsize=12, fontweight='bold')
        ax.set_title('Volumen de Atención en 10 Años', 
                    fontsize=14, fontweight='bold', pad=20)
        ax.set_xticks(x)
        ax.set_xticklabels(nombres, fontsize=11)
        ax.legend(fontsize=11)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Añadir valores
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.1f}k',
                       ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        plt.savefig(archivo, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  ✓ Generado: {archivo.name}")
    
    def _grafico_radar(self, resultados, archivo, colores):
        """Gráfico de radar para comparación multi-indicador."""
        
        # Indicadores a incluir (normalizados)
        categorias = [
            'Espera\nConsultas',
            'Derivaciones\nSalas',
            'Utilización\nMédicos',
            'Tiempo Ocioso\nSalas',
            'Costo\nMensual'
        ]
        
        nombres = list(resultados.keys())
        
        # Normalizar indicadores (invertir donde menor es mejor)
        def normalizar_inverso(valores):
            """Normaliza valores donde MENOR es MEJOR (0-100 donde 100 es mejor)."""
            min_val = min(valores)
            max_val = max(valores)
            if max_val == min_val:
                return [50] * len(valores)
            return [100 - (v - min_val) / (max_val - min_val) * 100 for v in valores]
        
        def normalizar_directo(valores):
            """Normaliza valores donde MAYOR es MEJOR (0-100)."""
            min_val = min(valores)
            max_val = max(valores)
            if max_val == min_val:
                return [50] * len(valores)
            return [(v - min_val) / (max_val - min_val) * 100 for v in valores]
        
        # Extraer datos
        espera_cons = [resultados[n]['indicadores']['PEC_consultas']['media'] 
                      for n in nombres]
        derivaciones = [resultados[n]['indicadores']['PPDSR']['media'] 
                       for n in nombres]
        ut_med = [resultados[n]['indicadores']['UT_med']['media'] 
                 for n in nombres]
        tiempo_ocioso = [resultados[n]['indicadores']['PTOSR_promedio']['media'] 
                        for n in nombres]
        costos = [resultados[n]['indicadores']['CTM']['media'] 
                 for n in nombres]
        
        # Normalizar (convertir a escala 0-100 donde 100 es mejor)
        espera_norm = normalizar_inverso(espera_cons)  # Menor es mejor
        deriv_norm = normalizar_inverso(derivaciones)   # Menor es mejor
        ut_norm = normalizar_directo(ut_med)            # Mayor es mejor
        ocioso_norm = normalizar_directo(tiempo_ocioso) # Mayor es mejor (más disponibilidad)
        costo_norm = normalizar_inverso(costos)         # Menor es mejor
        
        # Preparar datos para radar
        num_vars = len(categorias)
        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
        angles += angles[:1]  # Cerrar el círculo
        
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
        
        for i, nombre in enumerate(nombres):
            valores = [
                espera_norm[i],
                deriv_norm[i],
                ut_norm[i],
                ocioso_norm[i],
                costo_norm[i]
            ]
            valores += valores[:1]  # Cerrar el polígono
            
            ax.plot(angles, valores, 'o-', linewidth=2, 
                   label=nombre, color=colores[nombre], alpha=0.7)
            ax.fill(angles, valores, alpha=0.15, color=colores[nombre])
        
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(categorias, fontsize=10)
        ax.set_ylim(0, 100)
        ax.set_yticks([20, 40, 60, 80, 100])
        ax.set_yticklabels(['20', '40', '60', '80', '100'], fontsize=8)
        ax.set_title('Comparación Multi-indicador (Normalizado)\n100 = Mejor Desempeño', 
                    fontsize=14, fontweight='bold', pad=30)
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=10)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(archivo, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  ✓ Generado: {archivo.name}")
    
    def _grafico_resumen_indicadores(self, resultados, archivo, colores):
        """Gráfico de resumen con múltiples subplots."""
        
        nombres = list(resultados.keys())
        
        fig = plt.figure(figsize=(16, 10))
        gs = fig.add_gridspec(2, 3, hspace=0.3, wspace=0.3)
        
        # 1. Espera Consultas
        ax1 = fig.add_subplot(gs[0, 0])
        medias = [resultados[n]['indicadores']['PEC_consultas']['media'] for n in nombres]
        ax1.bar(range(len(nombres)), medias, color=[colores[n] for n in nombres], alpha=0.8)
        ax1.set_title('Espera en Consultas (min)', fontweight='bold')
        ax1.set_xticks(range(len(nombres)))
        ax1.set_xticklabels(nombres, rotation=45, ha='right', fontsize=9)
        ax1.grid(axis='y', alpha=0.3)
        
        # 2. Derivaciones
        ax2 = fig.add_subplot(gs[0, 1])
        medias = [resultados[n]['indicadores']['PPDSR']['media'] for n in nombres]
        ax2.bar(range(len(nombres)), medias, color=[colores[n] for n in nombres], alpha=0.8)
        ax2.set_title('Derivaciones Salas (%)', fontweight='bold')
        ax2.set_xticks(range(len(nombres)))
        ax2.set_xticklabels(nombres, rotation=45, ha='right', fontsize=9)
        ax2.grid(axis='y', alpha=0.3)
        
        # 3. Costos
        ax3 = fig.add_subplot(gs[0, 2])
        medias = [resultados[n]['indicadores']['CTM']['media'] / 1e6 for n in nombres]
        ax3.bar(range(len(nombres)), medias, color=[colores[n] for n in nombres], alpha=0.8)
        ax3.set_title('Costo Mensual (Millones ARS)', fontweight='bold')
        ax3.set_xticks(range(len(nombres)))
        ax3.set_xticklabels(nombres, rotation=45, ha='right', fontsize=9)
        ax3.grid(axis='y', alpha=0.3)
        
        # 4. Espera Partos
        ax4 = fig.add_subplot(gs[1, 0])
        medias = [resultados[n]['indicadores']['PEC_general']['media'] for n in nombres]
        ax4.bar(range(len(nombres)), medias, color=[colores[n] for n in nombres], alpha=0.8)
        ax4.set_title('Espera Partos (min)', fontweight='bold')
        ax4.set_xticks(range(len(nombres)))
        ax4.set_xticklabels(nombres, rotation=45, ha='right', fontsize=9)
        ax4.grid(axis='y', alpha=0.3)
        
        # 5. Tiempo Ocioso Salas
        ax5 = fig.add_subplot(gs[1, 1])
        medias = [resultados[n]['indicadores']['PTOSR_promedio']['media'] for n in nombres]
        ax5.bar(range(len(nombres)), medias, color=[colores[n] for n in nombres], alpha=0.8)
        ax5.set_title('Tiempo Ocioso Salas (%)', fontweight='bold')
        ax5.set_xticks(range(len(nombres)))
        ax5.set_xticklabels(nombres, rotation=45, ha='right', fontsize=9)
        ax5.grid(axis='y', alpha=0.3)
        
        # 6. Total Derivaciones
        ax6 = fig.add_subplot(gs[1, 2])
        der_sr = [resultados[n]['indicadores']['total_derivaciones_sr']['media'] 
                 for n in nombres]
        der_inc = [resultados[n]['indicadores']['total_derivaciones_inc']['media'] 
                  for n in nombres]
        width = 0.35
        x = np.arange(len(nombres))
        ax6.bar(x - width/2, der_sr, width, label='Salas', color='#D62246', alpha=0.8)
        ax6.bar(x + width/2, der_inc, width, label='Incubadoras', color='#F77E21', alpha=0.8)
        ax6.set_title('Derivaciones Totales (10 años)', fontweight='bold')
        ax6.set_xticks(range(len(nombres)))
        ax6.set_xticklabels(nombres, rotation=45, ha='right', fontsize=9)
        ax6.legend(fontsize=8)
        ax6.grid(axis='y', alpha=0.3)
        
        fig.suptitle('Resumen de Indicadores Clave - Comparación de Escenarios',
                    fontsize=16, fontweight='bold', y=0.995)
        
        # Agregar referencias de configuración
        referencias = self._crear_referencias_config(resultados)
        fig.text(0.5, 0.01, referencias, ha='center', fontsize=9, style='italic', 
                wrap=True, color='gray')
        
        plt.savefig(archivo, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"  ✓ Generado: {archivo.name}")


def main():
    """Ejecuta la comparación de cinco escenarios."""
    
    comparador = ComparadorCincoEscenarios(
        directorio_resultados="resultados_cinco_escenarios"
    )
    
    # Ejecutar comparación
    resultados = comparador.ejecutar_comparacion(num_replicas=30, semilla_base=42)
    
    print("\n" + "="*80)
    print("SIMULACIÓN COMPLETADA")
    print("="*80)
    print(f"\nResultados guardados en: {comparador.directorio_resultados}")
    print("\nArchivos generados:")
    print(f"  - {comparador.directorio_resultados}/comparacion_escenarios.json")
    print(f"  - {comparador.directorio_resultados}/reporte_comparativo.txt")
    print(f"  - {comparador.directorio_resultados}/graficos/ (10 gráficos)")
    print("\n" + "="*80)


if __name__ == "__main__":
    main()
