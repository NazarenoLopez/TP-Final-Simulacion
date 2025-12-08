# PLAN DE IMPLEMENTACIÓN - SIMULACIÓN DE EVENTOS DISCRETOS
## Guardia Gineco-Obstétrica - Hospital Eurnekian

---

## 1. ARQUITECTURA GENERAL DEL SISTEMA

### 1.1. Metodología
- **Tipo**: Simulación de eventos discretos con avance evento a evento
- **Motor**: Tabla de Eventos Futuros (TEF) implementada como cola de prioridad
- **Unidad de tiempo**: Minutos (para precisión en arribos y servicios)
- **Horizonte**: 1 año calendario = 365 × 24 × 60 = 525,600 minutos

### 1.2. Componentes Principales
1. **Generador de Variables Aleatorias**: Módulo para todas las FDP
2. **Estado del Sistema**: Variables de estado dinámicas
3. **Tabla de Eventos Futuros (TEF)**: Cola de prioridad ordenada por tiempo
4. **Colas de Pacientes**: Tres colas con prioridades
5. **Recursos**: Médicos, Quirófano, Salas de Recuperación, Incubadoras
6. **Acumuladores**: Para calcular indicadores de desempeño
7. **Calculadora de Costos**: Módulo para costos operativos e inversión

---

## 2. ESTRUCTURA DE DATOS

### 2.1. Estado del Sistema (Variables de Estado)
```python
Estado = {
    # Colas de pacientes
    'cola_consultas': deque(),           # Cola de consultas ginecológicas
    'cola_partos_naturales': deque(),   # Cola de partos naturales (mayor prioridad)
    'cola_partos_cesarea': deque(),     # Cola de cesáreas
    
    # Recursos disponibles
    'medicos_disponibles': int,          # MD: médicos libres
    'quirofano_disponible': bool,        # True si quirófano libre
    'salas_recuperacion_libres': int,    # SR - NSR
    'incubadoras_libres': int,           # I - NSI
    
    # Recursos ocupados
    'salas_recuperacion_ocupadas': int,  # NSR
    'incubadoras_ocupadas': int,         # NSI
    
    # Reloj de simulación
    'tiempo_actual': float,              # En minutos desde inicio
    
    # Contadores acumulados para indicadores
    'total_pacientes_atendidos': int,
    'total_consultas': int,
    'total_partos_naturales': int,
    'total_partos_cesarea': int,
    'total_derivaciones_sr': int,
    'total_derivaciones_inc': int,
    'tiempo_total_espera_consultas': float,
    'tiempo_total_espera_partos_nat': float,
    'tiempo_total_espera_partos_ces': float,
    'tiempo_ocupacion_medicos': float,
    'tiempo_ocupacion_quirofano': float,
    'tiempo_ocupacion_sr': [float] * SR,  # Por sala
    'tiempo_inactividad_sr': [float] * SR, # Por sala
}
```

### 2.2. Evento (Estructura)
```python
Evento = {
    'tipo': str,              # 'llegada', 'fin_consulta', 'inicio_parto', 
                              # 'fin_parto', 'fin_reposo', 'fin_incubacion'
    'tiempo': float,          # Tiempo programado (minutos)
    'paciente_id': int,       # ID único del paciente (opcional)
    'datos_extra': dict       # Información adicional según tipo de evento
}
```

### 2.3. Paciente (Estructura)
```python
Paciente = {
    'id': int,
    'tipo': str,              # 'consulta', 'parto_natural', 'parto_cesarea'
    'tiempo_llegada': float,  # Tiempo de arribo a guardia
    'tiempo_inicio_atencion': float,  # Cuando comenzó a ser atendido
    'requiere_incubadora': bool,      # Solo para neonatos
}
```

---

## 3. FUNCIONES DE DENSIDAD DE PROBABILIDAD (FDP)

### 3.1. Intervalo entre Arribos (IAG)
- **Distribución**: Lognormal
- **Parámetros**: s=1.362189, scale=23.268083, loc=0
- **Media aproximada**: ~50 minutos (según paper)
- **Unidad**: Minutos

### 3.2. Tiempo de Atención de Consultas (TAC)
- **Distribución**: Uniforme
- **Rango**: [5, 23] minutos

### 3.3. Tiempo de Atención de Partos (TAP)
- **Distribución**: Uniforme
- **Rango**: [50, 70] minutos
- **Aplica a**: Partos naturales y cesáreas (mismo tiempo)

### 3.4. Tiempo de Reposo en Salas de Recuperación (TREP)
- **Distribución**: Uniforme
- **Rango**: [24, 36] horas = [1440, 2160] minutos

### 3.5. Tiempo de Internación en Incubadora (TINC)
- **Distribución**: Determinístico
- **Valor**: 4 días = 5760 minutos

### 3.6. Probabilidades Categóricas
- **p_parto**: 0.30 (probabilidad de que llegue para parto)
- **p_consulta**: 0.70 (probabilidad de que llegue para consulta)
- **p_nat**: 0.57 (probabilidad de parto natural dado que es parto)
- **p_ces**: 0.43 (probabilidad de cesárea dado que es parto)
- **p_inc**: 0.10 (probabilidad de que neonato requiera incubadora)

---

## 4. FLUJO DE EVENTOS DETALLADO

### 4.1. INICIALIZACIÓN
```
1. Reloj de simulación = 0
2. Inicializar estado del sistema:
   - Colas vacías
   - Todos los recursos disponibles
   - Contadores en 0
3. Cargar parámetros:
   - G (médicos), SR (salas recuperación), I (incubadoras)
   - Parámetros de FDP
   - Costos
4. Programar primera llegada de paciente:
   - Generar IAG (lognormal)
   - Crear evento 'llegada' en tiempo = IAG
   - Insertar en TEF
```

### 4.2. EVENTO: LLEGADA DE PACIENTE
```
1. Generar tipo de paciente:
   - Si random() < p_parto (0.30):
     - Si random() < p_nat (0.57): tipo = 'parto_natural'
     - Sino: tipo = 'parto_cesarea'
   - Sino: tipo = 'consulta'

2. Crear objeto Paciente con:
   - ID único
   - Tipo
   - Tiempo de llegada = tiempo_actual

3. Encolar según tipo:
   - Consulta → cola_consultas
   - Parto natural → cola_partos_naturales
   - Cesárea → cola_partos_cesarea

4. Intentar asignar recursos inmediatamente:
   - Llamar a función asignar_recursos()

5. Programar próxima llegada:
   - Generar nuevo IAG (lognormal)
   - Crear evento 'llegada' en tiempo = tiempo_actual + IAG
   - Insertar en TEF
```

### 4.3. FUNCIÓN: ASIGNAR RECURSOS
```
Esta función se llama cuando:
- Llega un nuevo paciente
- Se libera un médico
- Se libera el quirófano

Lógica de asignación (respetando prioridades):
1. Verificar si hay médicos disponibles (MD > 0)
2. Prioridad 1: Partos naturales
   - Si hay paciente en cola_partos_naturales Y MD > 0 Y quirófano_disponible:
     - Asignar médico y quirófano (ambos tipos de partos usan quirófano)
     - Programar evento 'inicio_parto' (inmediato)
3. Prioridad 2: Cesáreas
   - Si hay paciente en cola_partos_cesarea Y MD > 0 Y quirófano_disponible:
     - Asignar médico y quirófano
     - Programar evento 'inicio_parto' (inmediato)
4. Prioridad 3: Consultas
   - Si hay paciente en cola_consultas Y MD > 0:
     - Asignar médico
     - Programar evento 'inicio_consulta' (inmediato)
```

### 4.4. EVENTO: INICIO DE CONSULTA
```
1. Extraer paciente de cola_consultas
2. Registrar tiempo_inicio_atencion = tiempo_actual
3. Calcular tiempo de espera = tiempo_actual - tiempo_llegada
4. Acumular tiempo_total_espera_consultas += tiempo_espera
5. Generar TAC (uniforme [5, 23])
6. Programar evento 'fin_consulta' en tiempo = tiempo_actual + TAC
7. Insertar en TEF
```

### 4.5. EVENTO: FIN DE CONSULTA
```
1. Liberar médico (MD += 1)
2. Incrementar contador total_consultas
3. Incrementar total_pacientes_atendidos
4. Actualizar tiempo_ocupacion_medicos += TAC
5. Intentar asignar recursos a siguiente paciente:
   - Llamar a asignar_recursos()
```

### 4.6. EVENTO: INICIO DE PARTO
```
1. Extraer paciente de cola correspondiente (natural o cesárea)
2. Registrar tiempo_inicio_atencion = tiempo_actual
3. Calcular tiempo de espera = tiempo_actual - tiempo_llegada
4. Acumular tiempo de espera según tipo
5. Marcar quirófano como ocupado (tanto naturales como cesáreas usan quirófano)
6. Generar TAP (uniforme [50, 70])
7. Programar evento 'fin_parto' en tiempo = tiempo_actual + TAP
8. Insertar en TEF
```

### 4.7. EVENTO: FIN DE PARTO
```
1. Liberar médico (MD += 1)
2. Liberar quirófano (tanto naturales como cesáreas usan quirófano)
3. Actualizar tiempo_ocupacion_quirofano += TAP
4. Incrementar contador según tipo de parto
5. Incrementar total_pacientes_atendidos

5. PROCESAR MADRE:
   - Verificar si hay sala de recuperación libre:
     - Si SÍ:
       - Asignar sala (NSR += 1)
       - Generar TREP (uniforme [1440, 2160])
       - Programar evento 'fin_reposo' en tiempo = tiempo_actual + TREP
       - Actualizar tiempo_ocupacion_sr[sala] += TREP
     - Si NO:
       - Incrementar total_derivaciones_sr
       - Registrar derivación (madre se va a otro hospital)

6. PROCESAR NEONATO:
   - Generar si requiere incubadora: random() < p_inc (0.10)
   - Si requiere incubadora:
     - Verificar si hay incubadora libre:
       - Si SÍ:
         - Asignar incubadora (NSI += 1)
         - Programar evento 'fin_incubacion' en tiempo = tiempo_actual + 5760
       - Si NO:
         - Incrementar total_derivaciones_inc
         - Registrar derivación (neonato se va a otro hospital)

7. Intentar asignar recursos a siguiente paciente:
   - Llamar a asignar_recursos()
```

### 4.8. EVENTO: FIN DE REPOSO EN SALA DE RECUPERACIÓN
```
1. Liberar sala de recuperación (NSR -= 1)
2. Calcular tiempo de ocupación real
3. Actualizar tiempo_inactividad_sr[sala] si corresponde
4. La madre es dada de alta (no se programa más eventos)
```

### 4.9. EVENTO: FIN DE INTERNACIÓN EN INCUBADORA
```
1. Liberar incubadora (NSI -= 1)
2. El neonato es dado de alta (no se programa más eventos)
```

---

## 5. CÁLCULO DE INDICADORES

### 5.1. Tiempo Promedio de Espera en Cola (PEC)
```
PEC_consultas = tiempo_total_espera_consultas / total_consultas
PEC_partos_nat = tiempo_total_espera_partos_nat / total_partos_naturales
PEC_partos_ces = tiempo_total_espera_partos_ces / total_partos_cesarea
PEC_general = (tiempo_total_espera_consultas + 
               tiempo_total_espera_partos_nat + 
               tiempo_total_espera_partos_ces) / total_pacientes_atendidos
```

### 5.2. Utilización de Médicos (UT_med)
```
UT_med = (tiempo_ocupacion_medicos / (G × tiempo_simulacion)) × 100
```

### 5.3. Utilización de Quirófano (UT_Q)
```
UT_Q = (tiempo_ocupacion_quirofano / tiempo_simulacion) × 100
```

### 5.4. Porcentaje de Tiempo Ocioso de Salas de Recuperación (PTOSR[i])
```
Para cada sala i:
PTOSR[i] = (tiempo_inactividad_sr[i] / tiempo_simulacion) × 100
PTOSR_promedio = promedio de todas las salas
```

### 5.5. Porcentaje de Pacientes Derivados (PPDSR, PPDINC)
```
PPDSR = (total_derivaciones_sr / total_partos) × 100
PPDINC = (total_derivaciones_inc / total_neonatos_requieren_inc) × 100
```

---

## 6. CÁLCULO DE COSTOS

### 6.1. Parámetros de Costo (según paper)
```
c_SR_op = 3,000 $/hora (costo operativo por sala de recuperación)
c_SR_inst = 7,000,000 $ (costo instalación nueva sala)
c_Q = 95,000 $ (costo por uso de quirófano)
c_INC_op = 25,000 $/día (costo operativo por incubadora)
c_INC_inst = 1,200,000 $ (costo adquisición incubadora)
c_med_mensual = 2,000,000 $/mes (costo mensual por médico)
c_bono = 57,000 $ (bono por médico cada 31 pacientes operados)
```

### 6.2. Costo Total Mensual (CTM)
```
CTM = costo_medicos + costo_quirofano + costo_sr_operacion + costo_inc_operacion

Donde:
- costo_medicos = G × c_med_mensual + bonos
- bonos = G × floor(total_pacientes_operados / 31) × c_bono
- costo_quirofano = total_partos × c_Q
- costo_sr_operacion = sum(tiempo_ocupacion_sr[i] / 60) × c_SR_op
- costo_inc_operacion = sum(tiempo_ocupacion_inc[i] / 1440) × c_INC_op
```

### 6.3. Costo Inicial de Instalaciones (CII)
```
CII = (SR - SR_base) × c_SR_inst + (I - I_base) × c_INC_inst

Donde:
- SR_base = 24 (dotación actual del hospital)
- I_base = 15 (dotación actual del hospital)
```

---

## 7. DISEÑO DE EXPERIMENTOS

### 7.1. Escenarios a Evaluar
```
Variar las variables de control:
- G (médicos): [2, 3, 4]
- SR (salas recuperación): [24, 26, 28, 30]
- I (incubadoras): [15, 17, 19, 21]

Total de escenarios: 3 × 4 × 4 = 48 escenarios
```

### 7.2. Configuración de Réplicas
```
- Horizonte de simulación: 1 año = 525,600 minutos
- Número de réplicas por escenario: 30
- Semillas aleatorias: diferentes para cada réplica
- Período de calentamiento: 43,200 minutos (30 días = 1 mes) - descartar resultados
```

### 7.3. Indicadores a Medir por Escenario
```
1. PEC_consultas (minutos)
2. PEC_partos_nat (minutos)
3. PEC_partos_ces (minutos)
4. UT_med (%)
5. UT_Q (%)
6. PTOSR_promedio (%)
7. PPDSR (%)
8. PPDINC (%)
9. CTM ($)
10. CII ($)
```

### 7.4. Análisis Estadístico
```
Para cada indicador:
- Calcular media de las 30 réplicas
- Calcular desviación estándar
- Calcular intervalo de confianza al 95%
- Guardar en tabla de resultados
```

---

## 8. ESTRUCTURA DE ARCHIVOS PROPUESTA

```
codigo/simulacion/
├── __init__.py
├── PLAN_SIMULACION.md (este archivo)
│
├── core/
│   ├── __init__.py
│   ├── evento.py              # Clase Evento
│   ├── paciente.py             # Clase Paciente
│   ├── estado.py               # Clase EstadoSistema
│   └── tef.py                  # Tabla de Eventos Futuros
│
├── generadores/
│   ├── __init__.py
│   └── variables_aleatorias.py # Todas las FDP
│
├── eventos/
│   ├── __init__.py
│   ├── llegada.py              # Manejo evento llegada
│   ├── consulta.py             # Manejo eventos consulta
│   ├── parto.py                # Manejo eventos parto
│   ├── reposo.py               # Manejo evento fin reposo
│   └── incubacion.py           # Manejo evento fin incubación
│
├── recursos/
│   ├── __init__.py
│   └── asignacion.py           # Lógica de asignación de recursos
│
├── indicadores/
│   ├── __init__.py
│   ├── calculadora.py          # Cálculo de todos los indicadores
│   └── costos.py               # Cálculo de costos
│
├── simulador.py                # Motor principal de simulación
├── experimentos.py             # Diseño y ejecución de experimentos
├── analisis_resultados.py     # Análisis estadístico de resultados
│
└── resultados_simulacion/     # Directorio de salida
    ├── escenario_G2_SR24_I15/
    │   ├── replica_01.json
    │   ├── replica_02.json
    │   └── ...
    ├── escenario_G3_SR26_I17/
    │   └── ...
    ├── resumen_escenarios.csv
    └── analisis_final.xlsx
```

---

## 9. FLUJO DE EJECUCIÓN

### 9.1. Ejecución de una Réplica
```
1. Inicializar simulador con parámetros (G, SR, I)
2. Inicializar estado del sistema
3. Programar primera llegada
4. Ciclo principal:
   a. Extraer evento más próximo de TEF
   b. Avanzar reloj a tiempo del evento
   c. Ejecutar rutina del evento
   d. Actualizar acumuladores
   e. Si tiempo_actual < tiempo_final: continuar
   f. Sino: terminar
5. Calcular indicadores finales
6. Retornar resultados
```

### 9.2. Ejecución de un Escenario
```
1. Para cada réplica (1 a 30):
   a. Ejecutar simulación con semilla diferente
   b. Guardar resultados de la réplica
2. Calcular estadísticas agregadas (media, desv. est., IC 95%)
3. Guardar resumen del escenario
```

### 9.3. Ejecución de Todos los Escenarios
```
1. Generar lista de todos los escenarios (48 combinaciones)
2. Para cada escenario:
   a. Ejecutar 30 réplicas
   b. Calcular estadísticas
   c. Guardar resultados
3. Generar tabla comparativa de todos los escenarios
4. Generar gráficos comparativos
```

---

## 10. VALIDACIONES Y VERIFICACIONES

### 10.1. Validación de Lógica
- [ ] Verificar que las prioridades se respetan (partos naturales > cesáreas > consultas)
- [ ] Verificar que un médico no atiende dos pacientes simultáneamente
- [ ] Verificar que el quirófano solo se usa para cesáreas
- [ ] Verificar que las derivaciones ocurren solo cuando no hay recursos

### 10.2. Validación de Conservación de Flujos
- [ ] Total de pacientes que llegan = Total atendidos + Total derivados
- [ ] Total de partos = Total de madres que pasan a recuperación + Total derivadas
- [ ] Total de neonatos que requieren incubadora = Total internados + Total derivados

### 10.3. Validación de Indicadores
- [ ] Utilizaciones entre 0% y 100%
- [ ] Tiempos de espera no negativos
- [ ] Porcentajes de derivación entre 0% y 100%
- [ ] Costos no negativos

---

## 11. PREGUNTAS PARA ACLARAR

1. **Bono médico**: ¿Se cuenta "pacientes operados" como todos los partos (naturales + cesáreas)?
2. **Salas de consultorio**: El paper menciona 2 salas, ¿se modelan explícitamente o solo los médicos?
3. **Derivaciones**: ¿Se registran pero no se programan más eventos para esos pacientes?

---

## 12. PRÓXIMOS PASOS

Una vez aprobado este plan:
1. Implementar módulos base (Evento, Paciente, Estado, TEF)
2. Implementar generadores de variables aleatorias
3. Implementar rutinas de eventos
4. Implementar motor de simulación
5. Implementar cálculo de indicadores y costos
6. Implementar diseño de experimentos
7. Ejecutar simulaciones
8. Analizar resultados

---

**¿Estás de acuerdo con este plan? ¿Hay algo que quieras modificar o aclarar antes de comenzar la implementación?**

