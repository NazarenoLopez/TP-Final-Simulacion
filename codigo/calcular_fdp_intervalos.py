"""
Script para calcular la FDP (Función de Densidad de Probabilidad) 
de los intervalos entre arribos de pacientes al hospital.
"""

import pandas as pd
import numpy as np
import os
from pathlib import Path
from datetime import datetime, timedelta
import warnings
import random
warnings.filterwarnings('ignore')

# Configuración
BASE_DIR = Path(__file__).parent.parent

DATA_DIR = BASE_DIR / "fdp" / "artificial_hes_ae_202302_v1_full"

CHUNK_SIZE = 50000  
OUTPUT_DIR = BASE_DIR / "codigo" / "resultados"
PROCESAR_SOLO_PRIMER_ARCHIVO = False  
MUESTREO_FRACCION = 0.01  

def crear_timestamp(fecha_str, hora_str):
    """
    Combina fecha y hora en un timestamp.
    
    Args:
        fecha_str: Fecha en formato YYYY-MM-DD
        hora_str: Hora en formato HHMM (4 dígitos)
    
    Returns:
        datetime object o None si hay error
    """
    try:
        # Parsear fecha
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
        
        # Parsear hora (formato HHMM)
        if pd.isna(hora_str) or hora_str == '' or str(hora_str).strip() == '':
            return None
        
        hora_str = str(hora_str).zfill(4)  # Asegurar 4 dígitos
        
        if len(hora_str) == 4 and hora_str.isdigit():
            hora = int(hora_str[:2])
            minuto = int(hora_str[2:])
            
            if 0 <= hora <= 23 and 0 <= minuto <= 59:
                return fecha.replace(hour=hora, minute=minuto)
        
        return None
    except:
        return None

def procesar_archivo_csv(archivo_path, mostrar_progreso=True):
    """
    Procesa un archivo CSV y extrae los timestamps de llegada.
    
    Args:
        archivo_path: Ruta al archivo CSV
        mostrar_progreso: Si mostrar progreso por consola
    
    Returns:
        Lista de timestamps válidos
    """
    timestamps = []
    total_chunks = 0
    registros_totales = 0
    registros_validos = 0
    registros_invalidos = 0
    
    if mostrar_progreso:
        print(f"\n{'='*60}")
        print(f"Procesando: {archivo_path.name}")
        print(f"{'='*60}")
    
    try:
        # Leer archivo en chunks
        for chunk in pd.read_csv(archivo_path, chunksize=CHUNK_SIZE, low_memory=False):
            total_chunks += 1
            registros_totales += len(chunk)
            
            # Extraer columnas relevantes
            if 'ARRIVALDATE' not in chunk.columns or 'ARRIVALTIME' not in chunk.columns:
                print(f"⚠️  ADVERTENCIA: Archivo {archivo_path.name} no tiene las columnas necesarias")
                continue
            
            # Procesar cada fila
            for idx, row in chunk.iterrows():
                fecha = row['ARRIVALDATE']
                hora = row['ARRIVALTIME']
                
                timestamp = crear_timestamp(fecha, hora)
                
                if timestamp is not None:
                    timestamps.append(timestamp)
                    registros_validos += 1
                else:
                    registros_invalidos += 1
            
            # Mostrar progreso cada 10 chunks
            if mostrar_progreso and total_chunks % 10 == 0:
                print(f"  Chunks procesados: {total_chunks} | "
                      f"Registros: {registros_totales:,} | "
                      f"Válidos: {registros_validos:,} | "
                      f"Inválidos: {registros_invalidos:,}")
        
        if mostrar_progreso:
            print(f"\n✓ Archivo completado:")
            print(f"  - Total registros: {registros_totales:,}")
            print(f"  - Registros válidos: {registros_validos:,}")
            print(f"  - Registros inválidos: {registros_invalidos:,}")
            print(f"  - Tasa de éxito: {registros_validos/registros_totales*100:.2f}%")
    
    except Exception as e:
        print(f"❌ ERROR procesando {archivo_path.name}: {str(e)}")
        return []
    
    return timestamps

def distribuir_timestamps_duplicados_uniformemente(timestamps):
    """
    Distribuye timestamps duplicados (mismo minuto) uniformemente dentro del minuto.
    Esto evita intervalos de 0 minutos y genera una FDP más realista.
    Los arribos del mismo minuto se distribuyen uniformemente en segundos (0-59).
    
    Args:
        timestamps: Lista de timestamps ordenados
    
    Returns:
        Lista de timestamps con segundos distribuidos uniformemente
    """
    from collections import defaultdict
    
    # Agrupar timestamps por minuto (sin segundos)
    timestamps_por_minuto = defaultdict(list)
    for ts in timestamps:
        # Redondear al minuto (sin segundos)
        ts_minuto = ts.replace(second=0, microsecond=0)
        timestamps_por_minuto[ts_minuto].append(ts)
    
    # Distribuir segundos uniformemente para cada grupo
    timestamps_distribuidos = []
    total_afectados = 0
    
    for ts_minuto, grupo in sorted(timestamps_por_minuto.items()):
        if len(grupo) == 1:
            # Solo un timestamp, mantenerlo pero agregar segundos aleatorios
            ts_original = grupo[0]
            # Agregar segundos aleatorios entre 0-59 para variabilidad
            segundo = random.randint(0, 59)
            ts_nuevo = ts_minuto.replace(second=segundo)
            timestamps_distribuidos.append(ts_nuevo)
        else:
            # Múltiples timestamps en el mismo minuto
            total_afectados += len(grupo)
            # Distribuir uniformemente los segundos (0-59)
            # Dividir el minuto en N partes iguales
            n = len(grupo)
            if n <= 60:
                # Si hay 60 o menos arribos, distribuir uniformemente
                segundos = np.linspace(0, 59, n, dtype=int)
            else:
                # Si hay más de 60 arribos, algunos tendrán el mismo segundo
                # pero distribuidos lo más uniformemente posible
                segundos = (np.arange(n) * 60 / n).astype(int) % 60
            
            # Aleatorizar ligeramente para evitar patrones artificiales
            np.random.shuffle(segundos)
            
            for i, ts_original in enumerate(grupo):
                ts_nuevo = ts_minuto.replace(second=int(segundos[i]))
                timestamps_distribuidos.append(ts_nuevo)
    
    return timestamps_distribuidos, total_afectados

def calcular_intervalos(timestamps):
    """
    Calcula los intervalos entre arribos consecutivos.
    ESTRATEGIA PERFECTA: Ordena TODOS los timestamps juntos antes de calcular intervalos.
    Distribuye timestamps duplicados uniformemente para evitar intervalos de 0 minutos.
    
    Args:
        timestamps: Lista de timestamps (pueden estar desordenados)
    
    Returns:
        Array de intervalos en minutos
    """
    if len(timestamps) < 2:
        return np.array([])
    
    print(f"\n   📊 Ordenando {len(timestamps):,} timestamps...")
    print(f"   (Esto asegura orden cronológico correcto entre todos los archivos)")
    
    # CRÍTICO: Ordenar TODOS los timestamps juntos
    # Esto es esencial para calcular intervalos correctos entre archivos
    timestamps_ordenados = sorted(timestamps)
    
    print(f"   ✓ Ordenamiento completado")
    print(f"\n   📅 Rango temporal completo:")
    print(f"      Primer timestamp: {timestamps_ordenados[0]}")
    print(f"      Último timestamp: {timestamps_ordenados[-1]}")
    rango_horas = (timestamps_ordenados[-1] - timestamps_ordenados[0]).total_seconds() / 3600
    rango_dias = rango_horas / 24
    print(f"      Rango: {rango_horas:.2f} horas ({rango_dias:.2f} días)")
    
    # Verificar y distribuir duplicados uniformemente
    timestamps_unicos = len(set(timestamps_ordenados))
    duplicados = len(timestamps_ordenados) - timestamps_unicos
    if duplicados > 0:
        porcentaje_dup = (duplicados / len(timestamps_ordenados)) * 100
        print(f"\n   ⚠️  Timestamps duplicados detectados: {duplicados:,} ({porcentaje_dup:.2f}%)")
        print(f"      Distribuyendo segundos uniformemente dentro de cada minuto...")
        print(f"      (Esto genera intervalos más realistas y evita valores de 0 minutos)")
        
        # Distribuir timestamps duplicados uniformemente
        timestamps_distribuidos, total_afectados = distribuir_timestamps_duplicados_uniformemente(timestamps_ordenados)
        timestamps_ordenados = sorted(timestamps_distribuidos)
        
        print(f"      ✓ Distribución completada: {total_afectados:,} timestamps redistribuidos")
        print(f"      Timestamps finales: {len(timestamps_ordenados):,}")
        print(f"      (Los arribos del mismo minuto ahora tienen segundos diferentes)")
    else:
        print(f"\n   ✓ No hay timestamps duplicados")
    
    # Validar orden (verificar que no haya timestamps desordenados)
    print(f"\n   🔍 Validando orden cronológico...")
    desordenados = 0
    for i in range(1, min(1000, len(timestamps_ordenados))):  # Verificar primeros 1000
        if timestamps_ordenados[i] < timestamps_ordenados[i-1]:
            desordenados += 1
    
    if desordenados == 0:
        print(f"   ✓ Orden cronológico validado correctamente")
    else:
        print(f"   ❌ ERROR: Se encontraron {desordenados} timestamps desordenados")
    
    # Calcular diferencias
    print(f"\n   ⏱️  Calculando intervalos entre arribos consecutivos...")
    intervalos = []
    
    # Usar numpy para eficiencia con grandes cantidades
    for i in range(1, len(timestamps_ordenados)):
        diff = (timestamps_ordenados[i] - timestamps_ordenados[i-1]).total_seconds() / 60.0  # en minutos
        intervalos.append(diff)
        
        # Mostrar progreso cada 100k intervalos
        if i % 100000 == 0:
            print(f"      Procesados: {i:,} / {len(timestamps_ordenados)-1:,} intervalos")
    
    intervalos_array = np.array(intervalos)
    print(f"   ✓ Cálculo completado: {len(intervalos_array):,} intervalos")
    
    return intervalos_array

def analizar_intervalos(intervalos):
    """
    Analiza los intervalos y genera estadísticas descriptivas.
    
    Args:
        intervalos: Array de intervalos en minutos
    
    Returns:
        Diccionario con estadísticas
    """
    if len(intervalos) == 0:
        return {}
    
    stats = {
        'total_intervalos': len(intervalos),
        'media': np.mean(intervalos),
        'mediana': np.median(intervalos),
        'desviacion_estandar': np.std(intervalos),
        'minimo': np.min(intervalos),
        'maximo': np.max(intervalos),
        'percentil_25': np.percentile(intervalos, 25),
        'percentil_75': np.percentile(intervalos, 75),
        'percentil_95': np.percentile(intervalos, 95),
        'percentil_99': np.percentile(intervalos, 99),
    }
    
    # Filtrar intervalos anómalos (negativos o muy grandes)
    intervalos_validos = intervalos[(intervalos >= 0) & (intervalos <= 1440)]  # máximo 24 horas
    stats['intervalos_validos'] = len(intervalos_validos)
    stats['intervalos_anomalos'] = len(intervalos) - len(intervalos_validos)
    
    return stats

def main():
    """
    Función principal que orquesta todo el proceso.
    """
    print("\n" + "="*60)
    print("CÁLCULO DE FDP PARA INTERVALOS ENTRE ARRIBOS")
    print("="*60)
    
    # Verificar directorio de datos
    if not DATA_DIR.exists():
        print(f"❌ ERROR: No se encuentra el directorio de datos: {DATA_DIR}")
        return
    
    # Crear directorio de resultados
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    # Buscar archivos CSV
    archivos_csv = sorted(DATA_DIR.glob("*.csv"))
    
    if len(archivos_csv) == 0:
        print(f"❌ ERROR: No se encontraron archivos CSV en {DATA_DIR}")
        return
    
    # Si solo procesar primer archivo, limitar la lista
    if PROCESAR_SOLO_PRIMER_ARCHIVO:
        archivos_csv = archivos_csv[:1]
        print(f"\n⚠️  MODO: Procesando SOLO el primer archivo (para análisis)")
        print(f"   Cambiar PROCESAR_SOLO_PRIMER_ARCHIVO = False para procesar todos")
    else:
        print(f"\n⚠️  MODO: Procesando TODOS los archivos")
    
    print(f"\n📁 Archivos a procesar: {len(archivos_csv)}")
    for archivo in archivos_csv:
        tamaño_mb = archivo.stat().st_size / (1024 * 1024)
        print(f"   - {archivo.name} ({tamaño_mb:.1f} MB)")
    
    # Procesar archivos
    print(f"\n🚀 Iniciando procesamiento...")
    print(f"   Chunk size: {CHUNK_SIZE:,} registros")
    print(f"   Estrategia: Procesar archivos → Acumular timestamps → Ordenar TODO → Calcular intervalos")
    
    todos_timestamps = []
    estadisticas_archivos = []
    
    # Aplicar muestreo si está configurado
    if MUESTREO_FRACCION < 1.0:
        print(f"\n⚠️  MODO MUESTREO: Procesando solo el {MUESTREO_FRACCION*100:.1f}% de los datos")
        print(f"   Esto genera una densidad similar al primer archivo (10k arribos/año)")
        np.random.seed(42)  # Semilla para reproducibilidad
    
    for i, archivo in enumerate(archivos_csv, 1):
        print(f"\n[{i}/{len(archivos_csv)}] Procesando archivo...")
        timestamps = procesar_archivo_csv(archivo, mostrar_progreso=True)
        
        if len(timestamps) > 0:
            # Aplicar muestreo si está configurado
            if MUESTREO_FRACCION < 1.0:
                n_muestra = max(1, int(len(timestamps) * MUESTREO_FRACCION))
                timestamps_muestra = np.random.choice(timestamps, size=n_muestra, replace=False).tolist()
                timestamps = [datetime.fromtimestamp(ts.timestamp()) if isinstance(ts, np.datetime64) else ts 
                             for ts in timestamps_muestra]
                print(f"   📊 Muestreo: {len(timestamps):,} de {len(timestamps) + n_muestra - len(timestamps):,} timestamps")
            
            # Guardar estadísticas del archivo
            stats_archivo = {
                'archivo': archivo.name,
                'timestamps': len(timestamps),
                'primer_ts': min(timestamps),
                'ultimo_ts': max(timestamps)
            }
            estadisticas_archivos.append(stats_archivo)
            
            todos_timestamps.extend(timestamps)
            print(f"   ✓ Archivo procesado: {len(timestamps):,} timestamps")
            print(f"   Total acumulado: {len(todos_timestamps):,} timestamps válidos")
        else:
            print(f"   ⚠️  Archivo sin timestamps válidos")
    
    # Mostrar resumen de archivos procesados
    if len(estadisticas_archivos) > 0:
        print(f"\n{'='*60}")
        print("RESUMEN DE ARCHIVOS PROCESADOS")
        print(f"{'='*60}")
        print(f"Total de archivos: {len(estadisticas_archivos)}")
        print(f"Total de timestamps acumulados: {len(todos_timestamps):,}")
        
        # Mostrar rango temporal de cada archivo
        if len(estadisticas_archivos) <= 20:  # Solo mostrar si hay pocos archivos
            print(f"\nRango temporal por archivo:")
            for stats in estadisticas_archivos:
                rango = (stats['ultimo_ts'] - stats['primer_ts']).total_seconds() / 3600
                print(f"  {stats['archivo']}: {stats['timestamps']:,} timestamps, "
                      f"rango {rango:.1f}h ({stats['primer_ts']} a {stats['ultimo_ts']})")
    
    # Calcular intervalos
    print(f"\n{'='*60}")
    print("CALCULANDO INTERVALOS ENTRE ARRIBOS")
    print(f"{'='*60}")
    print(f"Total de timestamps acumulados: {len(todos_timestamps):,}")
    
    if len(todos_timestamps) < 2:
        print("❌ ERROR: No hay suficientes timestamps para calcular intervalos")
        return
    
    # CRÍTICO: Ordenar TODOS los timestamps juntos antes de calcular intervalos
    # Esto asegura que los intervalos entre archivos sean correctos
    print(f"\n⚠️  IMPORTANTE: Se ordenarán TODOS los timestamps juntos")
    print(f"   Esto garantiza que los intervalos entre archivos sean correctos")
    
    intervalos = calcular_intervalos(todos_timestamps)
    print(f"\n✓ Total de intervalos calculados: {len(intervalos):,}")
    
    # Analizar intervalos
    print(f"\n{'='*60}")
    print("ANÁLISIS DE INTERVALOS")
    print(f"{'='*60}")
    stats = analizar_intervalos(intervalos)
    
    if stats:
        print(f"\n📊 Estadísticas descriptivas (intervalos en minutos):")
        print(f"   Total de intervalos: {stats['total_intervalos']:,}")
        print(f"   Intervalos válidos: {stats['intervalos_validos']:,}")
        print(f"   Intervalos anómalos: {stats['intervalos_anomalos']:,}")
        print(f"\n   Media: {stats['media']:.2f} minutos")
        print(f"   Mediana: {stats['mediana']:.2f} minutos")
        print(f"   Desviación estándar: {stats['desviacion_estandar']:.2f} minutos")
        print(f"   Mínimo: {stats['minimo']:.2f} minutos")
        print(f"   Máximo: {stats['maximo']:.2f} minutos")
        print(f"\n   Percentiles:")
        print(f"     P25: {stats['percentil_25']:.2f} minutos")
        print(f"     P75: {stats['percentil_75']:.2f} minutos")
        print(f"     P95: {stats['percentil_95']:.2f} minutos")
        print(f"     P99: {stats['percentil_99']:.2f} minutos")
        
        # Guardar intervalos
        archivo_intervalos = OUTPUT_DIR / "intervalos_arribos.npy"
        np.save(archivo_intervalos, intervalos)
        print(f"\n💾 Intervalos guardados en: {archivo_intervalos}")
        
        # Guardar estadísticas
        archivo_stats = OUTPUT_DIR / "estadisticas_intervalos.txt"
        with open(archivo_stats, 'w', encoding='utf-8') as f:
            f.write("ESTADÍSTICAS DE INTERVALOS ENTRE ARRIBOS\n")
            f.write("="*60 + "\n\n")
            for key, value in stats.items():
                if isinstance(value, float):
                    f.write(f"{key}: {value:.4f}\n")
                else:
                    f.write(f"{key}: {value}\n")
        print(f"💾 Estadísticas guardadas en: {archivo_stats}")
    
    print(f"\n{'='*60}")
    print("✓ PROCESO COMPLETADO")
    print(f"{'='*60}\n")
    
    return intervalos, stats

if __name__ == "__main__":
    intervalos, stats = main()

