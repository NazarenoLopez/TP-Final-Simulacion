"""
Diseño y Ejecución de Experimentos: Ejecuta múltiples escenarios y réplicas
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Tuple
import numpy as np

from .simulador import Simulador


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
    
    def generar_escenarios(self) -> List[Tuple[int, int, int]]:
        """
        Genera todos los escenarios a evaluar.
        Incluye escenarios con menos recursos que la dotación actual.
        
        Returns:
            Lista de tuplas (G, SR, I)
        """
        escenarios = []
        
        # G (médicos): [2, 3, 4]
        # SR (salas recuperación): [20, 22, 24, 26, 28, 30]
        #   - Dotación actual: 24
        #   - Incluye casos con menos recursos: 20, 22
        # I (incubadoras): [11, 13, 15, 17, 19, 21]
        #   - Dotación actual: 15
        #   - Incluye casos con menos recursos: 11, 13
        
        for G in [2, 3, 4]:
            for SR in [20, 22, 24, 26, 28, 30]:
                for I in [11, 13, 15, 17, 19, 21]:
                    escenarios.append((G, SR, I))
        
        return escenarios
    
    def ejecutar_escenario(
        self, 
        G: int, 
        SR: int, 
        I: int, 
        num_replicas: int = 30,
        semilla_base: int = 42,
        mostrar_progreso: bool = False
    ) -> Dict[str, Any]:
        """
        Ejecuta un escenario completo con múltiples réplicas.
        
        Args:
            G: Cantidad de médicos
            SR: Cantidad de salas de recuperación
            I: Cantidad de incubadoras
            num_replicas: Número de réplicas a ejecutar
            semilla_base: Semilla base para generar semillas únicas
            mostrar_progreso: Si mostrar progreso por consola
            
        Returns:
            Diccionario con resultados agregados del escenario
        """
        nombre_escenario = f"G{G}_SR{SR}_I{I}"
        directorio_escenario = self.directorio_resultados / nombre_escenario
        directorio_escenario.mkdir(parents=True, exist_ok=True)
        
        replicas = []
        
        # Ejecutar réplicas
        for replica in range(1, num_replicas + 1):
            semilla = semilla_base + replica * 1000 + G * 100 + SR * 10 + I
            
            if mostrar_progreso:
                print(f"\nEjecutando réplica {replica}/{num_replicas} - Escenario: {nombre_escenario}")
            
            # Crear y ejecutar simulador
            simulador = Simulador(G=G, SR=SR, I=I, semilla=semilla)
            resultados = simulador.ejecutar(mostrar_progreso=mostrar_progreso)
            
            # Guardar réplica individual
            archivo_replica = directorio_escenario / f"replica_{replica:02d}.json"
            with open(archivo_replica, 'w', encoding='utf-8') as f:
                json.dump(resultados, f, indent=2, ensure_ascii=False)
            
            replicas.append(resultados)
        
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
        mostrar_progreso: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Ejecuta todos los escenarios.
        
        Args:
            num_replicas: Número de réplicas por escenario
            semilla_base: Semilla base para generar semillas únicas
            mostrar_progreso: Si mostrar progreso por consola
            
        Returns:
            Lista con resultados de todos los escenarios
        """
        escenarios = self.generar_escenarios()
        resultados_todos = []
        
        print(f"\n{'='*80}")
        print(f"EJECUTANDO EXPERIMENTOS")
        print(f"{'='*80}")
        print(f"Total de escenarios: {len(escenarios)}")
        print(f"Réplicas por escenario: {num_replicas}")
        print(f"Total de simulaciones: {len(escenarios) * num_replicas}")
        print(f"{'='*80}\n")
        
        for idx, (G, SR, I) in enumerate(escenarios, 1):
            print(f"\n[{idx}/{len(escenarios)}] Escenario: G={G}, SR={SR}, I={I}")
            
            estadisticas = self.ejecutar_escenario(
                G=G,
                SR=SR,
                I=I,
                num_replicas=num_replicas,
                semilla_base=semilla_base,
                mostrar_progreso=False  # No mostrar progreso de réplicas individuales
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
        columnas = ['G', 'SR', 'I', 'num_replicas']
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

