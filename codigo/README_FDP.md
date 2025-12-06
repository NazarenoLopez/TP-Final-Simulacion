# Cálculo de FDP para Intervalos entre Arribos

Este conjunto de scripts permite calcular la Función de Densidad de Probabilidad (FDP) de los intervalos entre arribos de pacientes al hospital a partir de los datos de atención de emergencias.

## Estructura de Archivos

```
codigo/
├── calcular_fdp_intervalos.py    # Script principal: procesa datos y calcula intervalos
├── generar_fdp_visualizacion.py  # Script secundario: genera FDP y visualizaciones
├── requirements.txt              # Dependencias de Python
└── resultados/                   # Directorio de salida (se crea automáticamente)
    ├── intervalos_arribos.npy
    ├── estadisticas_intervalos.txt
    ├── fdp_intervalos_arribos.png
    ├── qq_plots_intervalos.png
    └── parametros_distribuciones.txt
```

## Requisitos

- Python 3.8 o superior
- Librerías listadas en `requirements.txt`

## Instalación

1. Instalar las dependencias:
```bash
pip install -r requirements.txt
```

## Uso

### Paso 1: Calcular Intervalos

Ejecuta el script principal para procesar todos los archivos CSV y calcular los intervalos:

```bash
python calcular_fdp_intervalos.py
```

**¿Qué hace este script?**
- Lee todos los archivos CSV del directorio `fdp/artificial_hes_ae_202302_v1_full/`
- Procesa los datos en chunks para no cargar todo en memoria
- Extrae las columnas `ARRIVALDATE` y `ARRIVALTIME`
- Combina fecha y hora en timestamps
- Calcula los intervalos entre arribos consecutivos
- Genera estadísticas descriptivas
- Guarda los resultados en `codigo/resultados/`

**Salida esperada:**
- `intervalos_arribos.npy`: Array numpy con todos los intervalos
- `estadisticas_intervalos.txt`: Estadísticas descriptivas

**Progreso por consola:**
El script muestra el progreso en tiempo real:
- Archivos procesados
- Chunks procesados
- Registros válidos vs inválidos
- Estadísticas finales

### Paso 2: Generar FDP y Visualizaciones

Una vez calculados los intervalos, ejecuta el script de visualización:

```bash
python generar_fdp_visualizacion.py
```

**¿Qué hace este script?**
- Carga los intervalos previamente calculados
- Filtra intervalos válidos (0-1440 minutos)
- Ajusta distribuciones teóricas:
  - Exponencial
  - Gamma
  - Weibull
  - Lognormal
- Genera histogramas de la FDP empírica
- Superpone las distribuciones teóricas ajustadas
- Genera Q-Q plots para evaluar el ajuste
- Guarda todas las visualizaciones

**Salida esperada:**
- `fdp_intervalos_arribos.png`: Histograma de FDP con distribuciones superpuestas
- `qq_plots_intervalos.png`: Q-Q plots para evaluar ajustes
- `parametros_distribuciones.txt`: Parámetros de las distribuciones ajustadas

## Columnas Utilizadas

Los scripts utilizan las siguientes columnas de los archivos CSV:

- **ARRIVALDATE**: Fecha de llegada (formato: YYYY-MM-DD)
- **ARRIVALTIME**: Hora de llegada (formato: HHMM, 4 dígitos)

## Consideraciones

### Procesamiento Eficiente
- Los archivos se procesan en chunks de 50,000 registros
- No se carga todo en memoria simultáneamente
- Progreso visible por consola

### Filtrado de Datos
- Se eliminan registros con fechas/horas inválidas
- Se filtran intervalos negativos o mayores a 24 horas
- Se mantienen estadísticas de registros válidos vs inválidos

### Intervalos
- Los intervalos se calculan en **minutos**
- Se ordenan cronológicamente antes de calcular diferencias
- Se guardan para análisis posteriores

## Ejemplo de Salida

### Estadísticas Descriptivas
```
Total de intervalos: 15,234,567
Intervalos válidos: 15,123,456
Intervalos anómalos: 111,111

Media: 12.34 minutos
Mediana: 8.76 minutos
Desviación estándar: 15.67 minutos
Mínimo: 0.01 minutos
Máximo: 1,234.56 minutos

Percentiles:
  P25: 3.45 minutos
  P75: 15.67 minutos
  P95: 45.23 minutos
  P99: 123.45 minutos
```

### Distribuciones Ajustadas
```
Exponencial: λ = 0.081234
Gamma: α = 1.2345, β = 0.098765
Weibull: c = 0.8765, scale = 14.5678
Lognormal: s = 1.2345, scale = 8.9012
```

## Solución de Problemas

### Error: "No se encuentra el directorio de datos"
- Verifica que la ruta `fdp/artificial_hes_ae_202302_v1_full/` existe
- Verifica que contiene archivos CSV

### Error: "No se encuentra el archivo de intervalos"
- Ejecuta primero `calcular_fdp_intervalos.py`
- Verifica que el directorio `codigo/resultados/` se creó correctamente

### Memoria insuficiente
- Reduce el `CHUNK_SIZE` en `calcular_fdp_intervalos.py`
- Procesa archivos de forma individual modificando el script

### Visualizaciones no se generan
- Verifica que matplotlib está instalado correctamente
- Verifica que hay suficientes intervalos válidos (>100)

## Notas Técnicas

- Los timestamps se crean combinando `ARRIVALDATE` y `ARRIVALTIME`
- La hora debe estar en formato HHMM (4 dígitos)
- Se valida que las horas estén en rango 00:00-23:59
- Los intervalos se calculan como diferencia entre arribos consecutivos ordenados
- Las distribuciones se ajustan usando máxima verosimilitud (scipy.stats)

## Autor

TP Final Simulación - 2024

