"""
Análisis de Resultados: Análisis estadístico y visualización de resultados
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import List, Dict, Any
import json
import glob


class AnalizadorResultados:
    """
    Analiza y visualiza los resultados de las simulaciones.
    """
    
    def __init__(self, directorio_resultados: str = "resultados_simulacion"):
        """
        Inicializa el analizador.
        
        Args:
            directorio_resultados: Directorio donde están los resultados
        """
        self.directorio_resultados = Path(directorio_resultados)
    
    def cargar_resultados(self) -> pd.DataFrame:
        """
        Carga todos los resultados desde el CSV de resumen.
        
        Returns:
            DataFrame con todos los resultados
        """
        archivo_csv = self.directorio_resultados / "resumen_escenarios.csv"
        
        if not archivo_csv.exists():
            raise FileNotFoundError(f"No se encuentra el archivo: {archivo_csv}")
        
        df = pd.read_csv(archivo_csv)
        return df
    
    def generar_graficos_comparativos(self, df: pd.DataFrame, output_dir: Path = None):
        """
        Genera gráficos comparativos de los resultados.
        
        Args:
            df: DataFrame con resultados
            output_dir: Directorio donde guardar gráficos
        """
        if output_dir is None:
            output_dir = self.directorio_resultados
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuración de matplotlib
        plt.rcParams['figure.figsize'] = (14, 8)
        plt.rcParams['font.size'] = 10
        
        print("\nGenerando gráficos comparativos...")
        
        # Gráfico 1: Tiempos de espera promedio
        print("  - Tiempos de espera...")
        self._grafico_tiempos_espera(df, output_dir)
        
        # Gráfico 2: Utilizaciones
        print("  - Utilizaciones...")
        self._grafico_utilizaciones(df, output_dir)
        
        # Gráfico 3: Derivaciones
        print("  - Derivaciones...")
        self._grafico_derivaciones(df, output_dir)
        
        # Gráfico 4: Costos
        print("  - Costos...")
        self._grafico_costos(df, output_dir)
        
        # Gráfico 5: Análisis por recursos (nuevo)
        print("  - Análisis por recursos...")
        self._grafico_analisis_recursos(df, output_dir)
        
        # Gráfico 6: Comparación costo-beneficio (nuevo)
        print("  - Análisis costo-beneficio...")
        self._grafico_costo_beneficio(df, output_dir)
        
        print(f"\n✓ Gráficos guardados en: {output_dir}")
    
    def _grafico_tiempos_espera(self, df: pd.DataFrame, output_dir: Path):
        """Genera gráfico de tiempos de espera promedio."""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        axes = axes.flatten()
        
        indicadores = [
            ('PEC_consultas_media', 'Tiempo Promedio de Espera - Consultas (min)'),
            ('PEC_partos_nat_media', 'Tiempo Promedio de Espera - Partos Naturales (min)'),
            ('PEC_partos_ces_media', 'Tiempo Promedio de Espera - Cesáreas (min)'),
            ('PEC_general_media', 'Tiempo Promedio de Espera - General (min)')
        ]
        
        for idx, (col, titulo) in enumerate(indicadores):
            ax = axes[idx]
            
            # Agrupar por G y promediar
            datos = df.groupby('G')[col].mean()
            
            ax.bar(datos.index, datos.values, alpha=0.7, color='steelblue')
            ax.set_xlabel('Cantidad de Médicos (G)')
            ax.set_ylabel('Tiempo (minutos)')
            ax.set_title(titulo)
            ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_dir / "tiempos_espera.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def _grafico_utilizaciones(self, df: pd.DataFrame, output_dir: Path):
        """Genera gráfico de utilizaciones."""
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        
        # Utilización de médicos
        datos_med = df.groupby('G')['UT_med_media'].mean()
        axes[0].bar(datos_med.index, datos_med.values, alpha=0.7, color='green')
        axes[0].set_xlabel('Cantidad de Médicos (G)')
        axes[0].set_ylabel('Utilización (%)')
        axes[0].set_title('Utilización Promedio de Médicos')
        axes[0].grid(True, alpha=0.3)
        
        # Utilización de quirófano
        datos_q = df.groupby('G')['UT_Q_media'].mean()
        axes[1].bar(datos_q.index, datos_q.values, alpha=0.7, color='red')
        axes[1].set_xlabel('Cantidad de Médicos (G)')
        axes[1].set_ylabel('Utilización (%)')
        axes[1].set_title('Utilización del Quirófano')
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_dir / "utilizaciones.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def _grafico_derivaciones(self, df: pd.DataFrame, output_dir: Path):
        """Genera gráfico de derivaciones."""
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        
        # Derivaciones por salas de recuperación
        datos_sr = df.groupby('SR')['PPDSR_media'].mean()
        axes[0].bar(datos_sr.index, datos_sr.values, alpha=0.7, color='orange')
        axes[0].set_xlabel('Cantidad de Salas de Recuperación (SR)')
        axes[0].set_ylabel('Porcentaje de Derivaciones (%)')
        axes[0].set_title('Derivaciones por Falta de Salas de Recuperación')
        axes[0].grid(True, alpha=0.3)
        
        # Derivaciones por incubadoras
        datos_inc = df.groupby('I')['PPDINC_media'].mean()
        axes[1].bar(datos_inc.index, datos_inc.values, alpha=0.7, color='purple')
        axes[1].set_xlabel('Cantidad de Incubadoras (I)')
        axes[1].set_ylabel('Porcentaje de Derivaciones (%)')
        axes[1].set_title('Derivaciones por Falta de Incubadoras')
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_dir / "derivaciones.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def _grafico_costos(self, df: pd.DataFrame, output_dir: Path):
        """Genera gráfico de costos."""
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        
        # Costo Total Mensual
        datos_ctm = df.groupby('G')['CTM_media'].mean()
        axes[0].bar(datos_ctm.index, datos_ctm.values / 1e6, alpha=0.7, color='darkblue')
        axes[0].set_xlabel('Cantidad de Médicos (G)')
        axes[0].set_ylabel('Costo (millones de $)')
        axes[0].set_title('Costo Total Mensual (CTM)')
        axes[0].grid(True, alpha=0.3)
        
        # Costo Inicial de Instalaciones
        datos_cii = df.groupby(['SR', 'I'])['CII_media'].mean()
        # Simplificado: mostrar solo algunos casos
        casos_especiales = df[df['CII_media'] > 0]
        if len(casos_especiales) > 0:
            axes[1].bar(range(len(casos_especiales)), 
                       casos_especiales['CII_media'].values / 1e6, 
                       alpha=0.7, color='darkred')
            axes[1].set_xlabel('Escenario')
            axes[1].set_ylabel('Costo (millones de $)')
            axes[1].set_title('Costo Inicial de Instalaciones (CII)')
            axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_dir / "costos.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def _grafico_analisis_recursos(self, df: pd.DataFrame, output_dir: Path):
        """Genera gráficos de análisis por recursos."""
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1. Tiempo de espera vs cantidad de médicos
        datos = df.groupby('G')['PEC_general_media'].mean()
        axes[0, 0].plot(datos.index, datos.values, marker='o', linewidth=2, markersize=8, color='steelblue')
        axes[0, 0].set_xlabel('Cantidad de Médicos (G)')
        axes[0, 0].set_ylabel('Tiempo Promedio de Espera (min)')
        axes[0, 0].set_title('Efecto de la Cantidad de Médicos en Tiempo de Espera')
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. Derivaciones vs cantidad de salas de recuperación
        datos_sr = df.groupby('SR')['PPDSR_media'].mean()
        axes[0, 1].plot(datos_sr.index, datos_sr.values, marker='s', linewidth=2, markersize=8, color='orange')
        axes[0, 1].axvline(x=24, color='red', linestyle='--', linewidth=1.5, label='Dotación actual (24)')
        axes[0, 1].set_xlabel('Cantidad de Salas de Recuperación (SR)')
        axes[0, 1].set_ylabel('Porcentaje de Derivaciones (%)')
        axes[0, 1].set_title('Efecto de Salas de Recuperación en Derivaciones')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
        
        # 3. Derivaciones vs cantidad de incubadoras
        datos_inc = df.groupby('I')['PPDINC_media'].mean()
        axes[1, 0].plot(datos_inc.index, datos_inc.values, marker='^', linewidth=2, markersize=8, color='purple')
        axes[1, 0].axvline(x=15, color='red', linestyle='--', linewidth=1.5, label='Dotación actual (15)')
        axes[1, 0].set_xlabel('Cantidad de Incubadoras (I)')
        axes[1, 0].set_ylabel('Porcentaje de Derivaciones (%)')
        axes[1, 0].set_title('Efecto de Incubadoras en Derivaciones')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # 4. Costo total mensual vs cantidad de médicos
        datos_ctm = df.groupby('G')['CTM_media'].mean()
        axes[1, 1].plot(datos_ctm.index, datos_ctm.values / 1e6, marker='D', linewidth=2, markersize=8, color='darkblue')
        axes[1, 1].set_xlabel('Cantidad de Médicos (G)')
        axes[1, 1].set_ylabel('Costo Total Mensual (millones de $)')
        axes[1, 1].set_title('Efecto de la Cantidad de Médicos en Costos')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_dir / "analisis_recursos.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def _grafico_costo_beneficio(self, df: pd.DataFrame, output_dir: Path):
        """Genera gráfico de análisis costo-beneficio."""
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        
        # 1. Costo vs Derivaciones (trade-off)
        # Agrupar por G y promediar
        datos_g = df.groupby('G').agg({
            'CTM_media': 'mean',
            'PPDSR_media': 'mean',
            'PPDINC_media': 'mean'
        }).reset_index()
        
        scatter = axes[0].scatter(
            datos_g['PPDSR_media'] + datos_g['PPDINC_media'],
            datos_g['CTM_media'] / 1e6,
            s=200,
            c=datos_g['G'],
            cmap='viridis',
            alpha=0.7,
            edgecolors='black',
            linewidth=1
        )
        axes[0].set_xlabel('Derivaciones Totales (%)')
        axes[0].set_ylabel('Costo Total Mensual (millones de $)')
        axes[0].set_title('Trade-off: Costo vs Derivaciones (por cantidad de médicos)')
        axes[0].grid(True, alpha=0.3)
        cbar = plt.colorbar(scatter, ax=axes[0])
        cbar.set_label('Cantidad de Médicos (G)')
        
        # 2. Costo vs Tiempo de Espera
        scatter2 = axes[1].scatter(
            datos_g['CTM_media'] / 1e6,
            df.groupby('G')['PEC_general_media'].mean(),
            s=200,
            c=datos_g['G'],
            cmap='plasma',
            alpha=0.7,
            edgecolors='black',
            linewidth=1
        )
        axes[1].set_xlabel('Costo Total Mensual (millones de $)')
        axes[1].set_ylabel('Tiempo Promedio de Espera (min)')
        axes[1].set_title('Trade-off: Costo vs Tiempo de Espera')
        axes[1].grid(True, alpha=0.3)
        cbar2 = plt.colorbar(scatter2, ax=axes[1])
        cbar2.set_label('Cantidad de Médicos (G)')
        
        plt.tight_layout()
        plt.savefig(output_dir / "costo_beneficio.png", dpi=300, bbox_inches='tight')
        plt.close()
    
    def generar_reporte(self, df: pd.DataFrame, output_file: str = "reporte_analisis.txt"):
        """
        Genera un reporte de análisis en texto.
        
        Args:
            df: DataFrame con resultados
            output_file: Nombre del archivo de salida
        """
        archivo = self.directorio_resultados / output_file
        
        with open(archivo, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("REPORTE DE ANÁLISIS DE RESULTADOS\n")
            f.write("="*80 + "\n\n")
            
            f.write(f"Total de escenarios analizados: {len(df)}\n\n")
            
            # Mejores escenarios por indicador
            f.write("MEJORES ESCENARIOS:\n")
            f.write("-"*80 + "\n\n")
            
            # Menor tiempo de espera general
            mejor_pec = df.loc[df['PEC_general_media'].idxmin()]
            f.write(f"Menor tiempo de espera general:\n")
            f.write(f"  G={mejor_pec['G']}, SR={mejor_pec['SR']}, I={mejor_pec['I']}\n")
            f.write(f"  PEC_general: {mejor_pec['PEC_general_media']:.2f} min\n\n")
            
            # Menor porcentaje de derivaciones SR
            mejor_sr = df.loc[df['PPDSR_media'].idxmin()]
            f.write(f"Menor porcentaje de derivaciones SR:\n")
            f.write(f"  G={mejor_sr['G']}, SR={mejor_sr['SR']}, I={mejor_sr['I']}\n")
            f.write(f"  PPDSR: {mejor_sr['PPDSR_media']:.2f}%\n\n")
            
            # Menor porcentaje de derivaciones INC
            mejor_inc = df.loc[df['PPDINC_media'].idxmin()]
            f.write(f"Menor porcentaje de derivaciones INC:\n")
            f.write(f"  G={mejor_inc['G']}, SR={mejor_inc['SR']}, I={mejor_inc['I']}\n")
            f.write(f"  PPDINC: {mejor_inc['PPDINC_media']:.2f}%\n\n")
            
            # Menor costo total mensual
            mejor_costo = df.loc[df['CTM_media'].idxmin()]
            f.write(f"Menor costo total mensual:\n")
            f.write(f"  G={mejor_costo['G']}, SR={mejor_costo['SR']}, I={mejor_costo['I']}\n")
            f.write(f"  CTM: ${mejor_costo['CTM_media']:,.0f}\n\n")
        
        print(f"✓ Reporte guardado: {archivo}")

    def generar_graficos_casos_destacados(self, df: pd.DataFrame, casos: list, output_dir: Path = None):
        """Genera gráficos comparativos para casos destacados específicos.

        Args:
            df: DataFrame con resultados agregados.
            casos: Lista de dicts con claves 'G', 'SR', 'I'. SC se inferirá del df.
            output_dir: Directorio de salida para los gráficos.
        """
        if output_dir is None:
            output_dir = self.directorio_resultados
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        filas = []
        etiquetas = []
        for caso in casos:
            sub = df[(df['G'] == caso['G']) & (df['SR'] == caso['SR']) & (df['I'] == caso['I'])]
            if sub.empty:
                continue
            # Si hay varias SC para mismos G, SR, I, tomar la de mejor PEC general
            sub_sorted = sub.sort_values('PEC_general_media')
            fila = sub_sorted.iloc[0]
            filas.append(fila)
            etiquetas.append(f"G{int(fila['G'])}_SR{int(fila['SR'])}_I{int(fila['I'])}_SC{int(fila['SC'])}")

        if not filas:
            print("No se encontraron casos destacados en el DataFrame.")
            return

        datos = pd.DataFrame(filas, index=etiquetas)

        # Métricas a comparar
        metricas = {
            'PEC_general_media': 'PEC general (min)',
            'PPDSR_media': 'Derivaciones SR (%)',
            'PPDINC_media': 'Derivaciones INC (%)',
            'CTM_media': 'CTM ($)',
            'CII_media': 'CII ($)',
            'UT_med_media': 'Utilización médicos (%)',
            'UT_Q_media': 'Utilización quirófano (%)',
            'PTOSR_promedio_media': 'PTOSR promedio (%)'
        }

        # Crear figura de múltiples subplots
        fig, axes = plt.subplots(2, 4, figsize=(18, 8))
        axes = axes.flatten()

        for ax, (col, titulo) in zip(axes, metricas.items()):
            valores = datos[col]
            ax.bar(valores.index, valores.values, color='steelblue', alpha=0.8)
            ax.set_title(titulo)
            ax.tick_params(axis='x', rotation=35)
            ax.grid(True, alpha=0.2)

        plt.tight_layout()
        salida = output_dir / "casos_destacados.png"
        plt.savefig(salida, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✓ Gráfico de casos destacados guardado en: {salida}")
    
    def mostrar_resultados_por_escenario(self, df: pd.DataFrame):
        """
        Muestra los resultados específicos solicitados para cada escenario.
        
        Variables de resultado mostradas:
        - PEC: Promedio de espera en cola para ser atendido en guardia
        - PTOSR[i]: Porcentaje de tiempo ocioso de la sala de recuperación i
        - PPDSR: Porcentaje de pacientes derivados por falta de salas de recuperación
        - CTM: Costo total de operación mensual
        - CII: Costo inicial de instalaciones
        
        Args:
            df: DataFrame con resultados de todos los escenarios
        """
        print("\n" + "="*100)
        print("RESULTADOS POR ESCENARIO - VARIABLES DE RESULTADO")
        print("="*100)
        
        # Ordenar por G, SR, I para mejor visualización
        df_ordenado = df.sort_values(['G', 'SR', 'I'])
        
        for idx, row in df_ordenado.iterrows():
            print(f"\n{'─'*100}")
            print(f"ESCENARIO: G={int(row['G'])}, SR={int(row['SR'])}, I={int(row['I'])}, SC={int(row['SC'])}")
            print(f"{'─'*100}")
            
            # PEC - Promedio de espera en cola
            pec_media = row.get('PEC_general_media', 0)
            pec_ic_inf = row.get('PEC_general_ic_inf', 0)
            pec_ic_sup = row.get('PEC_general_ic_sup', 0)
            print(f"\nPEC (Promedio de espera en cola):")
            print(f"  Media: {pec_media:.2f} minutos")
            print(f"  IC 95%: [{pec_ic_inf:.2f}, {pec_ic_sup:.2f}] minutos")
            
            # PTOSR[i] - Porcentaje de tiempo ocioso por sala
            ptosr_media = row.get('PTOSR_promedio_media', 0)
            ptosr_ic_inf = row.get('PTOSR_promedio_ic_inf', 0)
            ptosr_ic_sup = row.get('PTOSR_promedio_ic_sup', 0)
            print(f"\nPTOSR (Porcentaje de tiempo ocioso de salas de recuperación):")
            print(f"  Promedio de las {int(row['SR'])} salas: {ptosr_media:.2f}%")
            print(f"  IC 95%: [{ptosr_ic_inf:.2f}%, {ptosr_ic_sup:.2f}%]")
            
            # Intentar cargar PTOSR por sala desde las réplicas si están disponibles
            nombre_escenario = f"G{int(row['G'])}_SR{int(row['SR'])}_I{int(row['I'])}_SC{int(row['SC'])}"
            directorio_escenario = self.directorio_resultados / nombre_escenario
            if directorio_escenario.exists():
                try:
                    # Cargar algunas réplicas para mostrar distribución por sala
                    archivos_replicas = sorted(glob.glob(str(directorio_escenario / "replica_*.json")))[:5]  # Primeras 5 réplicas
                    if archivos_replicas:
                        ptosr_por_sala = []
                        for archivo in archivos_replicas:
                            with open(archivo, 'r', encoding='utf-8') as f:
                                replica = json.load(f)
                                if 'PTOSR' in replica and isinstance(replica['PTOSR'], list):
                                    if len(ptosr_por_sala) == 0:
                                        ptosr_por_sala = [[] for _ in range(len(replica['PTOSR']))]
                                    for i, valor in enumerate(replica['PTOSR']):
                                        if i < len(ptosr_por_sala):
                                            ptosr_por_sala[i].append(valor)
                        
                        if ptosr_por_sala:
                            print(f"  Distribución por sala (muestra de {len(archivos_replicas)} réplicas):")
                            for i, valores_sala in enumerate(ptosr_por_sala[:10]):  # Mostrar primeras 10 salas
                                if valores_sala:
                                    promedio_sala = np.mean(valores_sala)
                                    print(f"    Sala {i+1}: {promedio_sala:.2f}%")
                            if len(ptosr_por_sala) > 10:
                                print(f"    ... (y {len(ptosr_por_sala) - 10} salas más)")
                except Exception:
                    pass  # Si falla, solo mostrar el promedio
            
            # PPDSR - Porcentaje de derivaciones por falta de salas
            ppdsr_media = row.get('PPDSR_media', 0)
            ppdsr_ic_inf = row.get('PPDSR_ic_inf', 0)
            ppdsr_ic_sup = row.get('PPDSR_ic_sup', 0)
            print(f"\nPPDSR (Porcentaje de pacientes derivados por falta de salas de recuperación):")
            print(f"  Media: {ppdsr_media:.2f}%")
            print(f"  IC 95%: [{ppdsr_ic_inf:.2f}%, {ppdsr_ic_sup:.2f}%]")
            
            # CTM - Costo total mensual
            ctm_media = row.get('CTM_media', 0)
            ctm_ic_inf = row.get('CTM_ic_inf', 0)
            ctm_ic_sup = row.get('CTM_ic_sup', 0)
            print(f"\nCTM (Costo total de operación mensual):")
            print(f"  Media: ${ctm_media:,.0f}")
            print(f"  IC 95%: [${ctm_ic_inf:,.0f}, ${ctm_ic_sup:,.0f}]")
            
            # CII - Costo inicial de instalaciones
            cii_media = row.get('CII_media', 0)
            cii_ic_inf = row.get('CII_ic_inf', 0)
            cii_ic_sup = row.get('CII_ic_sup', 0)
            print(f"\nCII (Costo inicial de instalaciones):")
            print(f"  Media: ${cii_media:,.0f}")
            print(f"  IC 95%: [${cii_ic_inf:,.0f}, ${cii_ic_sup:,.0f}]")
        
        print(f"\n{'='*100}\n")
    
    def elegir_mejores_opciones(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Elige las mejores opciones basándose en los criterios especificados.
        
        Criterios de optimización:
        - PEC: Minimizar (menor tiempo de espera)
        - PTOSR: Maximizar (mayor tiempo ocioso = mejor utilización de recursos)
        - PPDSR: Minimizar (menor porcentaje de derivaciones)
        - CTM: Minimizar (menor costo operativo)
        - CII: Minimizar (menor costo de inversión)
        
        Args:
            df: DataFrame con resultados de todos los escenarios
            
        Returns:
            Diccionario con las mejores opciones según cada criterio
        """
        mejores = {}
        
        print("\n" + "="*100)
        print("MEJORES OPCIONES POR CRITERIO")
        print("="*100)
        
        # 1. Menor PEC (mejor tiempo de espera)
        mejor_pec_idx = df['PEC_general_media'].idxmin()
        mejor_pec = df.loc[mejor_pec_idx]
        mejores['menor_PEC'] = {
            'G': int(mejor_pec['G']),
            'SR': int(mejor_pec['SR']),
            'I': int(mejor_pec['I']),
            'SC': int(mejor_pec['SC']),
            'valor': mejor_pec['PEC_general_media']
        }
        print(f"\n1. MENOR PEC (Mejor tiempo de espera):")
        print(f"   Escenario: G={mejores['menor_PEC']['G']}, SR={mejores['menor_PEC']['SR']}, I={mejores['menor_PEC']['I']}, SC={mejores['menor_PEC']['SC']}")
        print(f"   PEC: {mejores['menor_PEC']['valor']:.2f} minutos")
        
        # 2. Mayor PTOSR promedio (mejor utilización de recursos - menos ocio)
        # Nota: Mayor ocio puede ser bueno o malo según perspectiva
        # Aquí asumimos que queremos un balance, pero mostramos el mayor
        mejor_ptosr_idx = df['PTOSR_promedio_media'].idxmax()
        mejor_ptosr = df.loc[mejor_ptosr_idx]
        mejores['mayor_PTOSR'] = {
            'G': int(mejor_ptosr['G']),
            'SR': int(mejor_ptosr['SR']),
            'I': int(mejor_ptosr['I']),
            'SC': int(mejor_ptosr['SC']),
            'valor': mejor_ptosr['PTOSR_promedio_media']
        }
        print(f"\n2. MAYOR PTOSR (Mayor tiempo ocioso - puede indicar sobrecapacidad):")
        print(f"   Escenario: G={mejores['mayor_PTOSR']['G']}, SR={mejores['mayor_PTOSR']['SR']}, I={mejores['mayor_PTOSR']['I']}, SC={mejores['mayor_PTOSR']['SC']}")
        print(f"   PTOSR promedio: {mejores['mayor_PTOSR']['valor']:.2f}%")
        
        # 3. Menor PPDSR (menor derivación por falta de salas)
        mejor_ppdsr_idx = df['PPDSR_media'].idxmin()
        mejor_ppdsr = df.loc[mejor_ppdsr_idx]
        mejores['menor_PPDSR'] = {
            'G': int(mejor_ppdsr['G']),
            'SR': int(mejor_ppdsr['SR']),
            'I': int(mejor_ppdsr['I']),
            'SC': int(mejor_ppdsr['SC']),
            'valor': mejor_ppdsr['PPDSR_media']
        }
        print(f"\n3. MENOR PPDSR (Menor derivación por falta de salas):")
        print(f"   Escenario: G={mejores['menor_PPDSR']['G']}, SR={mejores['menor_PPDSR']['SR']}, I={mejores['menor_PPDSR']['I']}, SC={mejores['menor_PPDSR']['SC']}")
        print(f"   PPDSR: {mejores['menor_PPDSR']['valor']:.2f}%")
        
        # 4. Menor CTM (menor costo operativo)
        mejor_ctm_idx = df['CTM_media'].idxmin()
        mejor_ctm = df.loc[mejor_ctm_idx]
        mejores['menor_CTM'] = {
            'G': int(mejor_ctm['G']),
            'SR': int(mejor_ctm['SR']),
            'I': int(mejor_ctm['I']),
            'SC': int(mejor_ctm['SC']),
            'valor': mejor_ctm['CTM_media']
        }
        print(f"\n4. MENOR CTM (Menor costo operativo mensual):")
        print(f"   Escenario: G={mejores['menor_CTM']['G']}, SR={mejores['menor_CTM']['SR']}, I={mejores['menor_CTM']['I']}, SC={mejores['menor_CTM']['SC']}")
        print(f"   CTM: ${mejores['menor_CTM']['valor']:,.0f}")
        
        # 5. Menor CII (menor costo de inversión)
        mejor_cii_idx = df['CII_media'].idxmin()
        mejor_cii = df.loc[mejor_cii_idx]
        mejores['menor_CII'] = {
            'G': int(mejor_cii['G']),
            'SR': int(mejor_cii['SR']),
            'I': int(mejor_cii['I']),
            'SC': int(mejor_cii['SC']),
            'valor': mejor_cii['CII_media']
        }
        print(f"\n5. MENOR CII (Menor costo inicial de instalaciones):")
        print(f"   Escenario: G={mejores['menor_CII']['G']}, SR={mejores['menor_CII']['SR']}, I={mejores['menor_CII']['I']}, SC={mejores['menor_CII']['SC']}")
        print(f"   CII: ${mejores['menor_CII']['valor']:,.0f}")
        
        # 6. Opción balanceada (combinando criterios)
        # Normalizar valores para comparación
        df_norm = df.copy()
        df_norm['PEC_norm'] = (df['PEC_general_media'] - df['PEC_general_media'].min()) / (df['PEC_general_media'].max() - df['PEC_general_media'].min() + 1e-10)
        df_norm['PPDSR_norm'] = (df['PPDSR_media'] - df['PPDSR_media'].min()) / (df['PPDSR_media'].max() - df['PPDSR_media'].min() + 1e-10)
        df_norm['CTM_norm'] = (df['CTM_media'] - df['CTM_media'].min()) / (df['CTM_media'].max() - df['CTM_media'].min() + 1e-10)
        df_norm['CII_norm'] = (df['CII_media'] - df['CII_media'].min()) / (df['CII_media'].max() - df['CII_media'].min() + 1e-10)
        
        # Score combinado (menor es mejor para todos)
        df_norm['score_combinado'] = (df_norm['PEC_norm'] + df_norm['PPDSR_norm'] + 
                                      df_norm['CTM_norm'] + df_norm['CII_norm'])
        
        mejor_balanceado_idx = df_norm['score_combinado'].idxmin()
        mejor_balanceado = df.loc[mejor_balanceado_idx]
        mejores['balanceado'] = {
            'G': int(mejor_balanceado['G']),
            'SR': int(mejor_balanceado['SR']),
            'I': int(mejor_balanceado['I']),
            'SC': int(mejor_balanceado['SC']),
            'PEC': mejor_balanceado['PEC_general_media'],
            'PPDSR': mejor_balanceado['PPDSR_media'],
            'CTM': mejor_balanceado['CTM_media'],
            'CII': mejor_balanceado['CII_media']
        }
        print(f"\n6. OPCIÓN BALANCEADA (Mejor combinación de criterios):")
        print(f"   Escenario: G={mejores['balanceado']['G']}, SR={mejores['balanceado']['SR']}, I={mejores['balanceado']['I']}, SC={mejores['balanceado']['SC']}")
        print(f"   PEC: {mejores['balanceado']['PEC']:.2f} min")
        print(f"   PPDSR: {mejores['balanceado']['PPDSR']:.2f}%")
        print(f"   CTM: ${mejores['balanceado']['CTM']:,.0f}")
        print(f"   CII: ${mejores['balanceado']['CII']:,.0f}")
        
        print(f"\n{'='*100}\n")
        
        return mejores
    
    def identificar_mejores_4_escenarios(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Identifica las mejores 4 opciones basándose en un score combinado.
        
        El score combina:
        - PEC (minimizar)
        - PPDSR (minimizar)
        - CTM (minimizar)
        - CII (minimizar)
        - PTOSR (considerar balance - no demasiado ocioso ni demasiado ocupado)
        
        Args:
            df: DataFrame con resultados de todos los escenarios
            
        Returns:
            DataFrame con las 4 mejores opciones
        """
        df_score = df.copy()
        
        # Normalizar valores (0-1) donde menor es mejor para PEC, PPDSR, CTM, CII
        df_score['PEC_norm'] = (df['PEC_general_media'] - df['PEC_general_media'].min()) / (df['PEC_general_media'].max() - df['PEC_general_media'].min() + 1e-10)
        df_score['PPDSR_norm'] = (df['PPDSR_media'] - df['PPDSR_media'].min()) / (df['PPDSR_media'].max() - df['PPDSR_media'].min() + 1e-10)
        df_score['CTM_norm'] = (df['CTM_media'] - df['CTM_media'].min()) / (df['CTM_media'].max() - df['CTM_media'].min() + 1e-10)
        df_score['CII_norm'] = (df['CII_media'] - df['CII_media'].min()) / (df['CII_media'].max() - df['CII_media'].min() + 1e-10)
        
        # Para PTOSR, idealmente queremos un valor moderado (ni muy alto ni muy bajo)
        # Penalizar valores extremos (muy altos = sobrecapacidad, muy bajos = sobrecarga)
        ptosr_medio = df['PTOSR_promedio_media'].median()
        df_score['PTOSR_norm'] = abs(df['PTOSR_promedio_media'] - ptosr_medio) / (df['PTOSR_promedio_media'].max() - df['PTOSR_promedio_media'].min() + 1e-10)
        
        # Score combinado (menor es mejor)
        # Pesos: PEC (30%), PPDSR (25%), CTM (25%), CII (10%), PTOSR (10%)
        df_score['score_combinado'] = (
            0.30 * df_score['PEC_norm'] +
            0.25 * df_score['PPDSR_norm'] +
            0.25 * df_score['CTM_norm'] +
            0.10 * df_score['CII_norm'] +
            0.10 * df_score['PTOSR_norm']
        )
        
        # Seleccionar las 4 mejores (menor score)
        mejores_4 = df_score.nsmallest(4, 'score_combinado')
        
        return mejores_4
    
    def generar_graficos_mejores_4(self, df: pd.DataFrame, output_dir: Path = None):
        """
        Genera gráficos comparativos de las mejores 4 opciones.
        
        Muestra las variables de resultado solicitadas:
        - PEC: Promedio de espera en cola
        - PTOSR: Porcentaje de tiempo ocioso de salas
        - PPDSR: Porcentaje de derivaciones
        - CTM: Costo total mensual
        - CII: Costo inicial de instalaciones
        
        Args:
            df: DataFrame con resultados de todos los escenarios
            output_dir: Directorio donde guardar gráficos
        """
        if output_dir is None:
            output_dir = self.directorio_resultados
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Identificar las mejores 4 opciones
        mejores_4 = self.identificar_mejores_4_escenarios(df)
        
        print("\nGenerando gráficos comparativos de las mejores 4 opciones...")
        print(f"Mejores 4 escenarios identificados:")
        for idx, row in mejores_4.iterrows():
            print(f"  - G={int(row['G'])}, SR={int(row['SR'])}, I={int(row['I'])}")
        
        # Crear etiquetas para los escenarios
        etiquetas = []
        for idx, row in mejores_4.iterrows():
            etiquetas.append(f"G{int(row['G'])}_SR{int(row['SR'])}_I{int(row['I'])}_SC{int(row['SC'])}")
        
        # Configuración de matplotlib
        plt.rcParams['figure.figsize'] = (16, 10)
        plt.rcParams['font.size'] = 11
        
        # Gráfico 1: Comparación de todas las variables de resultado
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        axes = axes.flatten()
        
        # 1. PEC - Promedio de espera en cola
        ax = axes[0]
        valores = mejores_4['PEC_general_media'].values
        errores = [mejores_4['PEC_general_media'].values - mejores_4['PEC_general_ic_inf'].values,
                   mejores_4['PEC_general_ic_sup'].values - mejores_4['PEC_general_media'].values]
        bars = ax.bar(range(len(etiquetas)), valores, alpha=0.7, color='steelblue', yerr=errores, capsize=5)
        ax.set_xlabel('Escenario')
        ax.set_ylabel('Tiempo (minutos)')
        ax.set_title('PEC - Promedio de Espera en Cola', fontweight='bold')
        ax.set_xticks(range(len(etiquetas)))
        ax.set_xticklabels(etiquetas, rotation=45, ha='right')
        ax.grid(True, alpha=0.3, axis='y')
        # Agregar valores en las barras
        for i, (bar, val) in enumerate(zip(bars, valores)):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + errores[1][i],
                   f'{val:.2f}', ha='center', va='bottom', fontsize=9)
        
        # 2. PTOSR - Porcentaje de tiempo ocioso
        ax = axes[1]
        valores = mejores_4['PTOSR_promedio_media'].values
        errores = [mejores_4['PTOSR_promedio_media'].values - mejores_4['PTOSR_promedio_ic_inf'].values,
                   mejores_4['PTOSR_promedio_ic_sup'].values - mejores_4['PTOSR_promedio_media'].values]
        bars = ax.bar(range(len(etiquetas)), valores, alpha=0.7, color='green', yerr=errores, capsize=5)
        ax.set_xlabel('Escenario')
        ax.set_ylabel('Porcentaje (%)')
        ax.set_title('PTOSR - Porcentaje de Tiempo Ocioso (Promedio)', fontweight='bold')
        ax.set_xticks(range(len(etiquetas)))
        ax.set_xticklabels(etiquetas, rotation=45, ha='right')
        ax.grid(True, alpha=0.3, axis='y')
        for i, (bar, val) in enumerate(zip(bars, valores)):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + errores[1][i],
                   f'{val:.2f}%', ha='center', va='bottom', fontsize=9)
        
        # 3. PPDSR - Porcentaje de derivaciones
        ax = axes[2]
        valores = mejores_4['PPDSR_media'].values
        errores = [mejores_4['PPDSR_media'].values - mejores_4['PPDSR_ic_inf'].values,
                   mejores_4['PPDSR_ic_sup'].values - mejores_4['PPDSR_media'].values]
        bars = ax.bar(range(len(etiquetas)), valores, alpha=0.7, color='orange', yerr=errores, capsize=5)
        ax.set_xlabel('Escenario')
        ax.set_ylabel('Porcentaje (%)')
        ax.set_title('PPDSR - Porcentaje de Derivaciones por Falta de Salas', fontweight='bold')
        ax.set_xticks(range(len(etiquetas)))
        ax.set_xticklabels(etiquetas, rotation=45, ha='right')
        ax.grid(True, alpha=0.3, axis='y')
        for i, (bar, val) in enumerate(zip(bars, valores)):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + errores[1][i],
                   f'{val:.2f}%', ha='center', va='bottom', fontsize=9)
        
        # 4. CTM - Costo total mensual
        ax = axes[3]
        valores = mejores_4['CTM_media'].values / 1e6  # Convertir a millones
        errores = [(mejores_4['CTM_media'].values - mejores_4['CTM_ic_inf'].values) / 1e6,
                   (mejores_4['CTM_ic_sup'].values - mejores_4['CTM_media'].values) / 1e6]
        bars = ax.bar(range(len(etiquetas)), valores, alpha=0.7, color='darkblue', yerr=errores, capsize=5)
        ax.set_xlabel('Escenario')
        ax.set_ylabel('Costo (millones de $)')
        ax.set_title('CTM - Costo Total de Operación Mensual', fontweight='bold')
        ax.set_xticks(range(len(etiquetas)))
        ax.set_xticklabels(etiquetas, rotation=45, ha='right')
        ax.grid(True, alpha=0.3, axis='y')
        for i, (bar, val) in enumerate(zip(bars, valores)):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + errores[1][i],
                   f'${val:.1f}M', ha='center', va='bottom', fontsize=9)
        
        # 5. CII - Costo inicial de instalaciones
        ax = axes[4]
        valores = mejores_4['CII_media'].values / 1e6  # Convertir a millones
        errores = [(mejores_4['CII_media'].values - mejores_4['CII_ic_inf'].values) / 1e6,
                   (mejores_4['CII_ic_sup'].values - mejores_4['CII_media'].values) / 1e6]
        bars = ax.bar(range(len(etiquetas)), valores, alpha=0.7, color='darkred', yerr=errores, capsize=5)
        ax.set_xlabel('Escenario')
        ax.set_ylabel('Costo (millones de $)')
        ax.set_title('CII - Costo Inicial de Instalaciones', fontweight='bold')
        ax.set_xticks(range(len(etiquetas)))
        ax.set_xticklabels(etiquetas, rotation=45, ha='right')
        ax.grid(True, alpha=0.3, axis='y')
        for i, (bar, val) in enumerate(zip(bars, valores)):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + errores[1][i],
                   f'${val:.1f}M' if val > 0 else '$0', ha='center', va='bottom', fontsize=9)
        
        # 6. Resumen comparativo (radar chart o tabla)
        ax = axes[5]
        ax.axis('off')
        
        # Crear tabla comparativa
        tabla_datos = []
        for idx, row in mejores_4.iterrows():
            tabla_datos.append([
                f"G{int(row['G'])}_SR{int(row['SR'])}_I{int(row['I'])}_SC{int(row['SC'])}",
                f"{row['PEC_general_media']:.2f} min",
                f"{row['PTOSR_promedio_media']:.2f}%",
                f"{row['PPDSR_media']:.2f}%",
                f"${row['CTM_media']/1e6:.1f}M",
                f"${row['CII_media']/1e6:.1f}M"
            ])
        
        tabla = ax.table(
            cellText=tabla_datos,
            colLabels=['Escenario', 'PEC', 'PTOSR', 'PPDSR', 'CTM', 'CII'],
            cellLoc='center',
            loc='center',
            bbox=[0, 0, 1, 1]
        )
        tabla.auto_set_font_size(False)
        tabla.set_fontsize(9)
        tabla.scale(1, 2)
        
        # Estilo de la tabla
        for i in range(len(tabla_datos) + 1):
            for j in range(6):
                if i == 0:  # Encabezado
                    tabla[(i, j)].set_facecolor('#4CAF50')
                    tabla[(i, j)].set_text_props(weight='bold', color='white')
                else:
                    tabla[(i, j)].set_facecolor('#f0f0f0' if i % 2 == 0 else 'white')
        
        ax.set_title('Resumen Comparativo - Mejores 4 Escenarios', fontweight='bold', pad=20)
        
        plt.tight_layout()
        plt.savefig(output_dir / "mejores_4_escenarios.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        # Gráfico 2: Comparación lado a lado (grouped bar chart)
        fig, ax = plt.subplots(figsize=(14, 8))
        
        x = np.arange(len(etiquetas))
        width = 0.15
        
        # Normalizar valores para comparación (0-1)
        pec_norm = (mejores_4['PEC_general_media'].values - mejores_4['PEC_general_media'].min()) / (mejores_4['PEC_general_media'].max() - mejores_4['PEC_general_media'].min() + 1e-10)
        ptosr_norm = (mejores_4['PTOSR_promedio_media'].values - mejores_4['PTOSR_promedio_media'].min()) / (mejores_4['PTOSR_promedio_media'].max() - mejores_4['PTOSR_promedio_media'].min() + 1e-10)
        ppdsr_norm = (mejores_4['PPDSR_media'].values - mejores_4['PPDSR_media'].min()) / (mejores_4['PPDSR_media'].max() - mejores_4['PPDSR_media'].min() + 1e-10)
        ctm_norm = (mejores_4['CTM_media'].values - mejores_4['CTM_media'].min()) / (mejores_4['CTM_media'].max() - mejores_4['CTM_media'].min() + 1e-10)
        cii_norm = (mejores_4['CII_media'].values - mejores_4['CII_media'].min()) / (mejores_4['CII_media'].max() - mejores_4['CII_media'].min() + 1e-10)
        
        ax.bar(x - 2*width, pec_norm, width, label='PEC (normalizado)', alpha=0.7, color='steelblue')
        ax.bar(x - width, ptosr_norm, width, label='PTOSR (normalizado)', alpha=0.7, color='green')
        ax.bar(x, ppdsr_norm, width, label='PPDSR (normalizado)', alpha=0.7, color='orange')
        ax.bar(x + width, ctm_norm, width, label='CTM (normalizado)', alpha=0.7, color='darkblue')
        ax.bar(x + 2*width, cii_norm, width, label='CII (normalizado)', alpha=0.7, color='darkred')
        
        ax.set_xlabel('Escenario')
        ax.set_ylabel('Valor Normalizado (0-1)')
        ax.set_title('Comparación Normalizada de Variables de Resultado - Mejores 4 Escenarios', fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(etiquetas, rotation=45, ha='right')
        ax.legend(loc='upper left')
        ax.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        plt.savefig(output_dir / "mejores_4_escenarios_normalizado.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✓ Gráficos de mejores 4 escenarios guardados en: {output_dir}")

