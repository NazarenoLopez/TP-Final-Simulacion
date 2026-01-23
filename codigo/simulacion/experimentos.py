"""
Diseño y Ejecución de Experimentos: Ejecuta múltiples escenarios y réplicas
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Tuple
import numpy as np
from multiprocessing import Pool, cpu_count
from functools import partial
import sys

from .simulador import Simulador


def _ejecutar_replica_individual(args: Tuple[int, int, int, int, int, int, int, str]) -> Tuple[int, Dict[str, Any]]:
    """
    Función auxiliar para ejecutar una réplica individual.
    Necesaria para multiprocessing (debe ser picklable).
    
    Args:
        args: Tupla con (replica, G, SR, I, SC, semilla, directorio_escenario_str, nombre_escenario)
        
    Returns:
        Tupla (replica, resultados)
    """
    replica, G, SR, I, SC, semilla, directorio_escenario_str, nombre_escenario = args
    directorio_escenario = Path(directorio_escenario_str)
    
    # Crear y ejecutar simulador
    simulador = Simulador(G=G, SR=SR, I=I, SC=SC, semilla=semilla)
    resultados = simulador.ejecutar(mostrar_progreso=False)
    
    # Guardar réplica individual
    archivo_replica = directorio_escenario / f"replica_{replica:02d}.json"
    with open(archivo_replica, 'w', encoding='utf-8') as f:
        json.dump(resultados, f, indent=2, ensure_ascii=False)
    
    return (replica, resultados)


class Experimento:
    """
    Maneja el diseño y ejecución de experimentos de simulación.
    """
    
    def __init__(self, directorio_resultados: str = "resultados_simulacion"):
        """
        Inicializa el experimento.
        
        Args:
            directorio_resultados: Directorio donde guardar resultados
        """
        self.directorio_resultados = Path(directorio_resultados)
        self.directorio_resultados.mkdir(parents=True, exist_ok=True)
    
    def generar_escenarios(self) -> List[Tuple[int, int, int, int]]:
        """
        Genera todos los escenarios a evaluar.
        Incluye escenarios con menos recursos que la dotación actual.
        
        Returns:
            Lista de tuplas (G, SR, I, SC)
        """
        escenarios = []
        
        # Grid ajustado según pedido
        # G (médicos): [2, 3, 4]
        # SC (consultorios): [2, 3, 4, 5]
        # SR (salas recuperación): [15, 24, 30]
        # I (incubadoras): [10, 15, 20]
        for G in [2, 3, 4]:
            for SC in [2, 3, 4, 5]:
                for SR in [15, 24, 30]:
                    for I in [10, 15, 20]:
                        escenarios.append((G, SR, I, SC))
        
        return escenarios
    
    def ejecutar_escenario(
        self,
        G: int,
        SR: int,
        I: int,
        SC: int,
        num_replicas: int = 30,
        semilla_base: int = 42,
        mostrar_progreso: bool = False,
        num_procesos: int = None
    ) -> Dict[str, Any]:
        """
        Ejecuta un escenario completo con múltiples réplicas en paralelo.
        
        Args:
            G: Cantidad de médicos
            SR: Cantidad de salas de recuperación
            I: Cantidad de incubadoras
            SC: Cantidad de salas de consultorio
            num_replicas: Número de réplicas a ejecutar
            semilla_base: Semilla base para generar semillas únicas
            mostrar_progreso: Si mostrar progreso por consola
            num_procesos: Número de procesos paralelos (None = usar todos los núcleos)
            
        Returns:
            Diccionario con resultados agregados del escenario
        """
        nombre_escenario = f"G{G}_SR{SR}_I{I}_SC{SC}"
        directorio_escenario = self.directorio_resultados / nombre_escenario
        directorio_escenario.mkdir(parents=True, exist_ok=True)
        
        # Determinar número de procesos
        # Limitar a un máximo razonable para evitar problemas de memoria en Windows
        if num_procesos is None:
            num_procesos = cpu_count()
        
        # Preparar argumentos para cada réplica
        args_replicas = []
        for replica in range(1, num_replicas + 1):
            semilla = semilla_base + replica * 1000 + G * 100 + SR * 10 + I + SC
            args_replicas.append((
                replica, G, SR, I, SC, semilla, 
                str(directorio_escenario), nombre_escenario
            ))
        
        # Ejecutar réplicas en paralelo
        if mostrar_progreso:
            print(f"  Ejecutando {num_replicas} réplicas en paralelo ({num_procesos} procesos)...")
        
        replicas_dict = {}
        try:
            with Pool(processes=num_procesos) as pool:
                resultados_paralelos = pool.map(_ejecutar_replica_individual, args_replicas)
        except Exception as e:
            if mostrar_progreso:
                print(f"  Error en paralelización: {e}")
                print(f"  Reintentando con menos procesos...")
            # Reintentar con menos procesos si falla
            num_procesos_reducido = max(1, num_procesos // 2)
            with Pool(processes=num_procesos_reducido) as pool:
                resultados_paralelos = pool.map(_ejecutar_replica_individual, args_replicas)
        
        # Organizar resultados por número de réplica
        for replica, resultados in resultados_paralelos:
            replicas_dict[replica] = resultados
        
        # Convertir a lista ordenada
        replicas = [replicas_dict[i] for i in range(1, num_replicas + 1)]
        
        if mostrar_progreso:
            print(f"  ✓ Réplicas completadas para {nombre_escenario}")
        
        # Calcular estadísticas agregadas
        estadisticas = self._calcular_estadisticas(replicas)
        
        # Guardar resumen del escenario
        archivo_resumen = directorio_escenario / "resumen_escenario.json"
        with open(archivo_resumen, 'w', encoding='utf-8') as f:
            json.dump(estadisticas, f, indent=2, ensure_ascii=False)
        
        return estadisticas
    
    def ejecutar_todos_escenarios(
        self,
        num_replicas: int = 30,
        semilla_base: int = 42,
        mostrar_progreso: bool = True,
        num_procesos: int = None
    ) -> List[Dict[str, Any]]:
        """
        Ejecuta todos los escenarios usando procesamiento paralelo.
        
        Args:
            num_replicas: Número de réplicas por escenario
            semilla_base: Semilla base para generar semillas únicas
            mostrar_progreso: Si mostrar progreso por consola
            num_procesos: Número de procesos paralelos (None = usar todos los núcleos)
            
        Returns:
            Lista con resultados de todos los escenarios
        """
        escenarios = self.generar_escenarios()
        resultados_todos = []
        
        # Determinar número de procesos
        # Limitar a un máximo razonable para evitar problemas de memoria en Windows
        if num_procesos is None:
            num_procesos = cpu_count()
        
        print(f"\n{'='*80}")
        print(f"EJECUTANDO EXPERIMENTOS (PARALELO)")
        print(f"{'='*80}")
        print(f"Total de escenarios: {len(escenarios)}")
        print(f"Réplicas por escenario: {num_replicas}")
        print(f"Total de simulaciones: {len(escenarios) * num_replicas}")
        print(f"Procesos paralelos: {num_procesos} (de {cpu_count()} núcleos disponibles)")
        print(f"{'='*80}\n")
        
        for idx, (G, SR, I, SC) in enumerate(escenarios, 1):
            print(f"\n[{idx}/{len(escenarios)}] Escenario: G={G}, SR={SR}, I={I}, SC={SC}")
            
            estadisticas = self.ejecutar_escenario(
                G=G,
                SR=SR,
                I=I,
                SC=SC,
                num_replicas=num_replicas,
                semilla_base=semilla_base,
                mostrar_progreso=mostrar_progreso,
                num_procesos=num_procesos
            )
            
            resultados_todos.append(estadisticas)
        
        # Guardar resumen general
        self._guardar_resumen_general(resultados_todos)
        
        return resultados_todos
    
    def _calcular_estadisticas(self, replicas: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calcula estadísticas agregadas de múltiples réplicas.
        
        Args:
            replicas: Lista de resultados de réplicas
            
        Returns:
            Diccionario con estadísticas (media, desv. est., IC 95%)
        """
        if len(replicas) == 0:
            return {}
        
        # Obtener parámetros del primer resultado
        primer_resultado = replicas[0]
        G = primer_resultado['G']
        SR = primer_resultado['SR']
        I = primer_resultado['I']
        SC = primer_resultado['SC']
        
        # Indicadores a analizar
        indicadores = [
            'PEC_consultas', 'PEC_partos_nat', 'PEC_partos_ces', 'PEC_general',
            'UT_med', 'UT_Q', 'PTOSR_promedio',
            'PPDSR', 'PPDINC',
            'CTM', 'CII'
        ]
        
        estadisticas = {
            'G': G,
            'SR': SR,
            'I': I,
            'SC': SC,
            'num_replicas': len(replicas)
        }
        
        # Calcular estadísticas para cada indicador
        for indicador in indicadores:
            valores = [r[indicador] for r in replicas if indicador in r]
            
            if len(valores) > 0:
                media = np.mean(valores)
                desv_est = np.std(valores, ddof=1)
                
                # Intervalo de confianza al 95% (t-student)
                from scipy import stats
                n = len(valores)
                t_critico = stats.t.ppf(0.975, n - 1)
                margen_error = t_critico * (desv_est / np.sqrt(n))
                
                estadisticas[f'{indicador}_media'] = media
                estadisticas[f'{indicador}_desv'] = desv_est
                estadisticas[f'{indicador}_ic_inf'] = media - margen_error
                estadisticas[f'{indicador}_ic_sup'] = media + margen_error
        
        return estadisticas
    
    def _guardar_resumen_general(self, resultados: List[Dict[str, Any]]):
        """
        Guarda un resumen general de todos los escenarios.
        
        Args:
            resultados: Lista de resultados de todos los escenarios
        """
        import csv
        
        archivo_csv = self.directorio_resultados / "resumen_escenarios.csv"
        
        # Obtener todas las columnas
        columnas = ['G', 'SR', 'I', 'SC', 'num_replicas']
        indicadores = [
            'PEC_consultas', 'PEC_partos_nat', 'PEC_partos_ces', 'PEC_general',
            'UT_med', 'UT_Q', 'PTOSR_promedio',
            'PPDSR', 'PPDINC',
            'CTM', 'CII'
        ]
        
        for indicador in indicadores:
            columnas.extend([
                f'{indicador}_media',
                f'{indicador}_desv',
                f'{indicador}_ic_inf',
                f'{indicador}_ic_sup'
            ])
        
        # Escribir CSV
        with open(archivo_csv, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=columnas)
            writer.writeheader()
            
            for resultado in resultados:
                # Filtrar solo las columnas que existen
                fila = {col: resultado.get(col, '') for col in columnas}
                writer.writerow(fila)
        
        print(f"\n✓ Resumen general guardado: {archivo_csv}")

