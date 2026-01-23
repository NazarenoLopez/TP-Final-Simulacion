# Simulación de Eventos Discretos - Guardia Gineco-Obstétrica

Sistema de simulación de eventos discretos para analizar la operación de la guardia gineco-obstétrica del Hospital Eurnekian.

## Estructura del Código

```
codigo/simulacion/
├── core/                    # Clases base
│   ├── evento.py           # Clase Evento
│   ├── paciente.py         # Clase Paciente
│   ├── estado.py           # Clase EstadoSistema
│   └── tef.py              # Tabla de Eventos Futuros
│
├── generadores/             # Generadores de variables aleatorias
│   └── variables_aleatorias.py
│
├── eventos/                 # Rutinas de manejo de eventos
│   ├── llegada.py
│   ├── consulta.py
│   ├── parto.py
│   ├── reposo.py
│   └── incubacion.py
│
├── recursos/                # Lógica de asignación de recursos
│   └── asignacion.py
│
├── indicadores/             # Cálculo de indicadores y costos
│   ├── calculadora.py
│   └── costos.py
│
├── simulador.py             # Motor principal de simulación
├── experimentos.py           # Diseño y ejecución de experimentos
├── analisis_resultados.py  # Análisis estadístico
├── main.py                  # Script principal
└── resultados_simulacion/   # Directorio de salida
```

## Configuración

### Parámetros del Sistema

- **Horizonte de simulación**: 10 años = 5,256,000 minutos
- **Período de calentamiento**: 1 mes = 43,200 minutos
- **Número de réplicas por escenario**: 20
- **Escenarios**: 108 combinaciones (grid ajustado)
  - G (médicos): [2, 3, 4]
  - SC (salas de consultorio): [2, 3, 4, 5]
  - SR (salas recuperación): [15, 24, 30]
    - Dotación actual: 24
  - I (incubadoras): [10, 15, 20]
    - Dotación actual: 15

### Funciones de Densidad de Probabilidad (FDP)

- **Intervalo entre arribos (IAG)**: Lognormal (s=1.362189, scale=23.268083)
- **Tiempo de atención de consultas (TAC)**: Uniforme [5, 23] minutos
- **Tiempo de atención de partos (TAP)**: Uniforme [50, 70] minutos
- **Tiempo de reposo (TREP)**: Uniforme [24, 36] horas
- **Tiempo de incubación (TINC)**: Determinístico 4 días

### Probabilidades

- **p_parto**: 0.30
- **p_consulta**: 0.70
- **p_nat**: 0.57 (parto natural dado que es parto)
- **p_ces**: 0.43 (cesárea dado que es parto)
- **p_inc**: 0.10 (neonato requiere incubadora)

## Uso

### Ejecutar Simulación Completa

```bash
cd codigo/simulacion
# Ejecuta con valores por defecto (grid actual, 5 réplicas por escenario)
python main.py

# Ajustar rápidamente réplicas y procesos
python main.py --replicas 5 --procesos 8 --yes
```

Esto ejecutará:
- 108 escenarios (grid actual)
- Réplicas configurables (default: 5)
- Total: escenarios × réplicas



### Ejecutar un Escenario Específico

```python
from simulacion.experimentos import Experimento

experimento = Experimento()
resultados = experimento.ejecutar_escenario(
  G=3,
  SR=26,
  I=17,
  SC=3,
  num_replicas=30
)
```

### Ejecutar una Réplica Individual

```python
from simulacion.simulador import Simulador

simulador = Simulador(G=3, SR=26, I=17, SC=3, semilla=42)
resultados = simulador.ejecutar(mostrar_progreso=True)
```

## Resultados

Los resultados se guardan en `resultados_simulacion/`:

- **Por escenario**: `G{G}_SR{SR}_I{I}/`
  - `replica_01.json`, `replica_02.json`, ...
  - `resumen_escenario.json`
- **Resumen general**: `resumen_escenarios.csv`
- **Gráficos**: 
  - `tiempos_espera.png`: Tiempos promedio de espera
  - `utilizaciones.png`: Utilización de médicos y quirófano
  - `derivaciones.png`: Porcentajes de derivaciones
  - `costos.png`: Costos totales mensuales e iniciales
  - `analisis_recursos.png`: Análisis del efecto de cada recurso
  - `costo_beneficio.png`: Análisis costo-beneficio (trade-offs)
- **Reporte**: `reporte_analisis.txt`

## Indicadores Calculados

1. **PEC_consultas**: Tiempo promedio de espera para consultas (minutos)
2. **PEC_partos_nat**: Tiempo promedio de espera para partos naturales (minutos)
3. **PEC_partos_ces**: Tiempo promedio de espera para cesáreas (minutos)
4. **PEC_general**: Tiempo promedio de espera general (minutos)
5. **UT_med**: Utilización promedio de médicos (%)
6. **UT_Q**: Utilización del quirófano (%)
7. **PTOSR_promedio**: Porcentaje promedio de tiempo ocioso de salas de recuperación (%)
8. **PPDSR**: Porcentaje de pacientes derivados por falta de salas de recuperación (%)
9. **PPDINC**: Porcentaje de neonatos derivados por falta de incubadoras (%)
10. **CTM**: Costo total mensual ($)
11. **CII**: Costo inicial de instalaciones ($)

## Análisis de Resultados

```python
from simulacion.analisis_resultados import AnalizadorResultados

analizador = AnalizadorResultados()
df = analizador.cargar_resultados()
analizador.generar_graficos_comparativos(df)
analizador.generar_reporte(df)
```

## Notas Importantes

1. **Quirófano**: Tanto partos naturales como cesáreas requieren el quirófano en este hospital.
2. **Dotación base**: 24 salas de recuperación y 15 incubadoras.
3. **Período de calentamiento**: Los primeros 30 días se descartan para el cálculo de indicadores.
4. **Semillas**: Cada réplica usa una semilla única para garantizar independencia estadística.

## Requisitos

Ver `requirements.txt` en el directorio padre (`codigo/requirements.txt`).

## Autor

TP Final Simulación - 2024

