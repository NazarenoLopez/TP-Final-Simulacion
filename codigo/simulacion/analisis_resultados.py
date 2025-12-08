"""
Análisis de Resultados: Análisis estadístico y visualización de resultados
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from typing import List, Dict, Any
import json


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

