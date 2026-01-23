# PLAN DE SIMULACIÓN - 10 AÑOS
## Hospital Eurnekian - Guardia Gineco-Obstétrica

**Fecha:** 23 de Enero de 2026  
**Horizonte de Simulación:** 10 años de operación  
**Estado:** ✅ En Ejecución

---

## 🎯 OBJETIVO

Simular 10 años de operación del Hospital Eurnekian comparando tres escenarios de configuración:

1. **ACTUAL**: Configuración actual del hospital según propuesta formal
2. **MEJOR**: Configuración optimizada que minimiza costos manteniendo calidad
3. **PEOR**: Configuración subóptima con recursos insuficientes (para contrastar)

---

## 📊 VARIABLES DE RESULTADO (según Propuesta Formal)

Las siguientes variables se calcularán y compararán para cada escenario:

### Variables Principales
- **PECC**: Promedio de espera en cola para CONSULTA (minutos)
- **PECP**: Promedio de espera en cola para PARTO (minutos)
  - Para partos naturales
  - Para cesáreas
- **PTOSR**: Porcentaje de tiempo ocioso de salas de recuperación (%)
- **PPDSR**: Porcentaje de pacientes derivados por falta de salas de recuperación (%)
- **CTM**: Costo Total Mensual de operación (ARS $)
- **CII**: Costo Inicial de Instalaciones (ARS $)

### Variables Adicionales
- Utilización de médicos (%)
- Utilización de quirófano (%)
- Total de pacientes atendidos
- Total de derivaciones por incubadoras

---

## ⚙️ CONFIGURACIONES EVALUADAS

### 🏥 ESCENARIO ACTUAL
**Configuración según propuesta formal del hospital:**
- Médicos (G): **1**
- Salas de Consultorio (SC): **1**
- Salas de Recuperación (SR): **24**
- Incubadoras (I): **15**

**Descripción:** Esta es la configuración operativa actual del hospital según la propuesta formal entregada.

---

### ⭐ ESCENARIO MEJOR (Optimizado)
**Configuración optimizada basada en análisis previos:**
- Médicos (G): **3**
- Salas de Consultorio (SC): **3**
- Salas de Recuperación (SR): **24**
- Incubadoras (I): **15**

**Descripción:** Configuración que busca minimizar costos operativos mientras mantiene un nivel de servicio adecuado. Se aumentan médicos y consultorios para reducir tiempos de espera y mejorar flujo.

**Justificación:**
- Más médicos permiten atender consultas y partos en paralelo
- Más consultorios reducen cuellos de botella en atención ambulatoria
- Mantiene salas de recuperación e incubadoras en nivel actual (suficiente según análisis)

---

### ⚠️ ESCENARIO PEOR (Subóptimo)
**Configuración con recursos deliberadamente insuficientes:**
- Médicos (G): **2**
- Salas de Consultorio (SC): **2**
- Salas de Recuperación (SR): **15**
- Incubadoras (I): **10**

**Descripción:** Configuración con recursos reducidos para contrastar con los otros escenarios y mostrar el impacto de la falta de recursos.

**Impacto esperado:**
- Alto nivel de derivaciones por falta de salas de recuperación
- Tiempos de espera elevados
- Posible saturación del sistema

---

## 💰 COSTOS UTILIZADOS (según Propuesta Formal)

### Costos Operativos Mensuales
| Concepto | Costo | Unidad |
|----------|-------|--------|
| Médico Gineco-Obstetra | $2,000,000 | /mes |
| Bono por médico | $57,000 | cada 31 pacientes operados |
| Uso de quirófano | $95,000 | por uso |
| Sala de recuperación | $3,000 | /hora por paciente |
| Incubadora | $25,000 | /día por bebé |

### Costos de Instalación (Inversión Inicial)
| Concepto | Costo | Unidad |
|----------|-------|--------|
| Sala de consultorio | $10,000,000 | por sala |
| Sala de recuperación | $7,000,000 | por sala |
| Incubadora | $1,200,000 | por unidad |

**Nota:** Los costos de instalación solo se aplican a recursos adicionales sobre la dotación base del hospital.

---

## 🎲 FUNCIONES DE DENSIDAD DE PROBABILIDAD (FDP)

### FDP Utilizadas (ya calculadas y validadas)

#### 1. Intervalo entre Arribos (IAG)
- **Distribución:** Lognormal
- **Parámetros:**
  - s (sigma): 1.362189
  - scale: 23.268083
  - loc: 0.0
- **Fuente:** `resultados/mejor_distribucion.txt`
- **Validación:** AIC=1462528.42, KS p-value < 0.05

#### 2. Tiempo de Atención para Parto (TAP)
- **Distribución:** Uniforme continua
- **Parámetros:** min=50, max=70 minutos
- **Fuente:** Propuesta formal

#### 3. Tiempo de Atención para Consulta (TAC)
- **Distribución:** Uniforme continua
- **Parámetros:** min=5, max=23 minutos
- **Fuente:** Propuesta formal

#### 4. Tiempo de Reposo Post-Parto (TREP)
- **Distribución:** Uniforme continua
- **Parámetros:** min=24, max=36 horas
- **Fuente:** Propuesta formal (política del hospital)

### Probabilidades Utilizadas
- **Tipo de paciente:**
  - 30% llegan para parto
  - 70% llegan para consulta
  
- **Tipo de parto:**
  - 57% parto natural
  - 43% cesárea
  
- **Requiere incubadora:**
  - 10% de los recién nacidos (1 de cada 10 partos)
  - Tiempo de incubación: 4 días fijos

---

## 🔬 METODOLOGÍA DE SIMULACIÓN

### Tipo de Simulación
- **Modelo:** Simulación de Eventos Discretos (DES)
- **Enfoque:** Monte Carlo con múltiples réplicas
- **Horizonte:** 10 años = 5,256,000 minutos
- **Período de calentamiento:** 1 mes = 43,200 minutos

### Experimento
- **Réplicas por escenario:** 30
- **Total de simulaciones:** 90 (3 escenarios × 30 réplicas)
- **Semilla base:** 42 (para reproducibilidad)
- **Nivel de confianza:** 95% para intervalos de confianza

### Eventos Modelados
1. **Llegada de paciente** → Entra en cola según tipo
2. **Inicio de consulta** → Asignación de consultorio y médico
3. **Fin de consulta** → Liberación de recursos
4. **Inicio de parto** → Asignación de quirófano y médico
5. **Fin de parto** → Asignación de sala de recuperación o derivación
6. **Fin de reposo** → Liberación de sala de recuperación
7. **Fin de incubación** → Liberación de incubadora o derivación

### Colas del Sistema
1. **Cola de consultas** (prioridad baja)
2. **Cola de partos por cesárea** (prioridad media)
3. **Cola de partos naturales** (prioridad alta)

---

## 📈 INDICADORES CALCULADOS

### Por cada escenario se calcula:

#### Tiempos de Espera
- Media, desviación estándar, IC 95%
- Por tipo de atención (consultas, partos)

#### Utilización de Recursos
- Médicos (% tiempo ocupado)
- Quirófano (% tiempo ocupado)
- Salas de recuperación (% tiempo ocioso)
- Consultorios (% tiempo ocupado)

#### Nivel de Servicio
- % de derivaciones por falta de salas
- % de derivaciones por falta de incubadoras
- Total de pacientes atendidos vs. llegados

#### Costos
- Costo mensual promedio (CTM)
- Costo inicial de instalaciones (CII)
- Desglose por concepto

---

## 📂 ESTRUCTURA DE RESULTADOS

```
resultados_comparacion/
│
├── reporte_comparativo.txt          # Reporte principal en texto
├── comparacion_escenarios.json      # Datos en formato JSON
│
├── ACTUAL/
│   ├── resumen.json                 # Estadísticas agregadas
│   ├── replica_01.json              # Resultados réplica 1
│   ├── replica_02.json              # Resultados réplica 2
│   └── ...                          # Réplicas 3-30
│
├── MEJOR/
│   ├── resumen.json
│   ├── replica_01.json
│   └── ...
│
└── PEOR/
    ├── resumen.json
    ├── replica_01.json
    └── ...
```

---

## 🚀 EJECUCIÓN

### Comando
```bash
python -m simulacion.simulacion_tres_escenarios
```

### Proceso
1. **Escenario ACTUAL** (30 réplicas) → ~10-15 minutos
2. **Escenario MEJOR** (30 réplicas) → ~10-15 minutos
3. **Escenario PEOR** (30 réplicas) → ~10-15 minutos
4. **Generación de reportes** → ~1 minuto

**Tiempo total estimado:** 30-45 minutos

---

## 📊 ANÁLISIS ESPERADO

Al finalizar la simulación, el reporte comparativo incluirá:

### 1. Comparación de Costos
- Costo mensual de cada escenario
- Ahorro potencial vs. configuración actual
- Costo de inversión inicial requerido

### 2. Comparación de Nivel de Servicio
- Tiempos de espera en cada escenario
- Porcentaje de derivaciones
- Capacidad de atención

### 3. Eficiencia Operativa
- Utilización de recursos
- Cuellos de botella identificados
- Balance costo-servicio

### 4. Recomendaciones
- Mejor configuración según criterios de optimización
- Trade-offs entre costo y calidad de servicio
- Escenarios de ampliación/reducción de recursos

---

## ✅ CHECKLIST DE IMPLEMENTACIÓN

- [x] Actualizar costos según nueva propuesta formal
- [x] Incluir costo de salas de consultorio
- [x] Definir configuración ACTUAL según propuesta
- [x] Definir configuración MEJOR (optimizada)
- [x] Definir configuración PEOR (subóptima)
- [x] Crear script de comparación de tres escenarios
- [x] Configurar horizonte de simulación a 10 años
- [x] Configurar 30 réplicas por escenario
- [x] Implementar generación de reportes comparativos
- [x] Iniciar ejecución de simulaciones
- [ ] Verificar resultados de escenario ACTUAL
- [ ] Verificar resultados de escenario MEJOR
- [ ] Verificar resultados de escenario PEOR
- [ ] Revisar reporte comparativo final
- [ ] Validar recomendaciones

---

## 📝 NOTAS IMPORTANTES

1. **Dotación Base:** La configuración ACTUAL (G=1, SC=1, SR=24, I=15) se considera la dotación base del hospital. Solo se cobran costos de instalación para recursos adicionales.

2. **FDP Pre-calculadas:** Se utilizan las distribuciones ya ajustadas y validadas en `resultados/mejor_distribucion.txt` y los parámetros de la propuesta formal.

3. **Período de Calentamiento:** Se descarta el primer mes de simulación para eliminar bias de condiciones iniciales.

4. **Reproducibilidad:** Todas las simulaciones usan semillas deterministas para permitir reproducción exacta de resultados.

5. **Validación Estadística:** Los intervalos de confianza al 95% permiten evaluar la significancia estadística de las diferencias entre escenarios.

---

## 🔍 PRÓXIMOS PASOS

1. ✅ Ejecutar las 90 simulaciones (en progreso)
2. ⏳ Esperar finalización (~30-45 minutos)
3. ⏳ Revisar `reporte_comparativo.txt`
4. ⏳ Analizar resultados y validar recomendaciones
5. ⏳ Preparar presentación de resultados

---

**Archivo generado:** 23/01/2026  
**Última actualización:** 23/01/2026 18:44
