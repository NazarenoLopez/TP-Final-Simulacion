# 📁 ÍNDICE DE ARCHIVOS - SIMULACIÓN 5 ESCENARIOS

**Hospital Eurnekian - Guardia Gineco-Obstétrica**  
**Fecha de generación:** 15 de Febrero de 2026  
**Simulación:** 10 años, 30 réplicas por escenario (150 totales)

---

## 📄 DOCUMENTOS PRINCIPALES

### 🎯 Documentos para Lectura Rápida

1. **`RESUMEN_EJECUTIVO.md`** ⭐ **EMPEZAR AQUÍ**
   - Resumen de 1 página con conclusiones principales
   - Recomendación final clara
   - Comparación rápida de escenarios
   - Plan de implementación

2. **`reporte_interactivo.html`** 🌐 **VISUALIZACIÓN INTERACTIVA**
   - Dashboard HTML con pestañas navegables
   - Todos los gráficos integrados
   - Tablas comparativas interactivas
   - Abrir en navegador web

3. **`ANALISIS_COMPLETO.md`** 📊 **ANÁLISIS DETALLADO**
   - Documento completo de 20+ páginas
   - Análisis exhaustivo de cada escenario
   - Comparaciones detalladas
   - Recomendaciones fundamentadas
   - Matriz de decisión

### 📊 Reportes de Datos

4. **`reporte_comparativo.txt`**
   - Reporte en formato texto plano
   - Todas las tablas de resultados
   - Variables de resultado (PECC, PECP, PTOSR, PPDSR, CTM, CII)
   - Indicadores de desempeño
   - Análisis y recomendaciones

5. **`comparacion_escenarios.json`**
   - Datos completos en formato JSON
   - Estadísticas de todos los indicadores
   - Media, desviación estándar, IC 95%
   - Configuraciones de cada escenario
   - Para análisis programático

---

## 📈 GRÁFICOS COMPARATIVOS (10 totales)

**Ubicación:** `graficos/`

### Tiempos de Espera

1. **`espera_consultas.png`**
   - Promedio de espera en cola para consultas
   - Con intervalos de confianza
   - Comparación de los 5 escenarios

2. **`espera_partos.png`**
   - Espera en partos: naturales, cesáreas y general
   - Gráfico de barras agrupadas
   - Comparación por tipo de parto

### Derivaciones

3. **`derivaciones_salas.png`**
   - Porcentaje de derivaciones por falta de salas
   - Con intervalos de confianza
   - Indicador crítico de calidad

4. **`derivaciones_totales.png`**
   - Total de derivaciones en 10 años
   - Separado por salas e incubadoras
   - Números absolutos

### Costos y Recursos

5. **`costos_mensuales.png`**
   - Costo total mensual de operación
   - En millones de ARS
   - Con desviación estándar

6. **`tiempo_ocioso_salas.png`**
   - Porcentaje de tiempo ocioso de salas de recuperación
   - Indicador de utilización de capacidad

7. **`utilizacion_recursos.png`**
   - Utilización de médicos y quirófano
   - Comparación por escenario
   - Identificación de cuellos de botella

### Volumen

8. **`volumen_atencion.png`**
   - Pacientes llegados vs. atendidos
   - En miles de pacientes
   - Validación del modelo

### Resúmenes Visuales

9. **`comparacion_radar.png`** ⭐
   - Gráfico de radar multi-indicador
   - Todos los KPIs normalizados
   - Vista 360° de cada escenario

10. **`resumen_indicadores.png`** ⭐
    - Dashboard con 6 subplots
    - Vista rápida de todos los indicadores clave
    - Ideal para presentaciones

---

## 📂 DATOS POR ESCENARIO

Cada escenario tiene su carpeta con:
- `resumen.json` - Estadísticas agregadas
- `replica_01.json` a `replica_30.json` - Datos individuales de cada réplica

### Carpeta `ACTUAL/` (31 archivos)
- Configuración: 2G, 1SC, 19SR, 12I
- 30 réplicas + resumen

### Carpeta `MEJOR_1/` (31 archivos)
- Configuración: 3G, 3SC, 24SR, 15I
- 30 réplicas + resumen

### Carpeta `MEJOR_2/` (31 archivos)
- Configuración: 3G, 2SC, 20SR, 13I
- 30 réplicas + resumen

### Carpeta `PEOR_1/` (31 archivos)
- Configuración: 1G, 1SC, 15SR, 10I
- 30 réplicas + resumen

### Carpeta `PEOR_2/` (31 archivos)
- Configuración: 2G, 1SC, 16SR, 11I
- 30 réplicas + resumen

**Total de archivos de datos:** 155 archivos JSON

---

## 🗂️ ESTRUCTURA COMPLETA DE DIRECTORIOS

```
resultados_cinco_escenarios/
│
├── 📄 RESUMEN_EJECUTIVO.md ⭐ [EMPEZAR AQUÍ]
├── 📄 ANALISIS_COMPLETO.md [Análisis detallado]
├── 🌐 reporte_interactivo.html [Dashboard interactivo]
├── 📄 reporte_comparativo.txt [Reporte texto]
├── 📊 comparacion_escenarios.json [Datos JSON]
├── 📄 INDICE_ARCHIVOS.md [Este archivo]
│
├── 📁 graficos/ (10 gráficos PNG)
│   ├── espera_consultas.png
│   ├── espera_partos.png
│   ├── derivaciones_salas.png
│   ├── derivaciones_totales.png
│   ├── costos_mensuales.png
│   ├── tiempo_ocioso_salas.png
│   ├── utilizacion_recursos.png
│   ├── volumen_atencion.png
│   ├── comparacion_radar.png ⭐
│   └── resumen_indicadores.png ⭐
│
├── 📁 ACTUAL/ (31 archivos)
│   ├── resumen.json
│   ├── replica_01.json
│   ├── replica_02.json
│   └── ... (hasta replica_30.json)
│
├── 📁 MEJOR_1/ (31 archivos)
│   ├── resumen.json
│   ├── replica_01.json
│   └── ... (hasta replica_30.json)
│
├── 📁 MEJOR_2/ (31 archivos)
│   ├── resumen.json
│   ├── replica_01.json
│   └── ... (hasta replica_30.json)
│
├── 📁 PEOR_1/ (31 archivos)
│   ├── resumen.json
│   ├── replica_01.json
│   └── ... (hasta replica_30.json)
│
└── 📁 PEOR_2/ (31 archivos)
    ├── resumen.json
    ├── replica_01.json
    └── ... (hasta replica_30.json)
```

**Total de archivos:** 171 archivos

---

## 🎯 GUÍA DE USO SEGÚN NECESIDAD

### Para Directivos / Toma de Decisiones
1. Leer **`RESUMEN_EJECUTIVO.md`** (5 min)
2. Revisar **`reporte_interactivo.html`** en navegador (10 min)
3. Ver gráficos clave:
   - `comparacion_radar.png`
   - `resumen_indicadores.png`
   - `costos_mensuales.png`
   - `derivaciones_salas.png`

### Para Análisis Técnico Detallado
1. Leer **`ANALISIS_COMPLETO.md`** (30 min)
2. Revisar **`reporte_comparativo.txt`** (15 min)
3. Analizar todos los gráficos en `graficos/`
4. Revisar datos JSON si es necesario

### Para Presentaciones
1. Usar **`reporte_interactivo.html`** (proyección directa)
2. Exportar slides desde:
   - `resumen_indicadores.png` (overview)
   - `comparacion_radar.png` (comparación)
   - Gráficos específicos según tema

### Para Análisis Estadístico / Programático
1. Cargar **`comparacion_escenarios.json`**
2. Acceder a réplicas individuales en carpetas de escenarios
3. Procesar con Python/R según necesidad

---

## 📊 INDICADORES DISPONIBLES

### Variables de Resultado (según propuesta formal)
- **PECC** - Promedio de Espera en Cola para Consulta (minutos)
- **PECP** - Promedio de Espera en Cola para Parto (minutos)
  - Naturales, Cesáreas, General
- **PTOSR** - Porcentaje de Tiempo Ocioso de Salas de Recuperación (%)
- **PPDSR** - Porcentaje de Pacientes Derivados por Falta de Salas (%)
- **CTM** - Costo Total Mensual de Operación (ARS $)
- **CII** - Costo Inicial de Instalaciones (ARS $)

### Indicadores Adicionales
- **UT_med** - Utilización de Médicos (%)
- **UT_Q** - Utilización de Quirófano (%)
- **total_derivaciones_sr** - Total derivaciones por salas (10 años)
- **total_derivaciones_inc** - Total derivaciones por incubadoras (10 años)
- **total_pacientes_llegados** - Volumen de llegadas (10 años)
- **total_pacientes_atendidos** - Volumen atendido (10 años)

---

## 🔍 METADATOS DE LA SIMULACIÓN

### Configuración de Ejecución
- **Horizonte temporal:** 10 años por réplica
- **Número de réplicas:** 30 por escenario
- **Total de réplicas:** 150 (5 escenarios × 30)
- **Semilla base:** 42 (reproducible)
- **Método:** Simulación de eventos discretos
- **Nivel de confianza:** 95% (IC)

### Escenarios Simulados
1. **ACTUAL** - Base actual: 2G, 1SC, 19SR, 12I
2. **MEJOR_1** - Óptimo calidad: 3G, 3SC, 24SR, 15I
3. **MEJOR_2** - Balance: 3G, 2SC, 20SR, 13I
4. **PEOR_1** - Mínimo: 1G, 1SC, 15SR, 10I
5. **PEOR_2** - Subóptimo: 2G, 1SC, 16SR, 11I

### Tiempo de Ejecución
- **Inicio:** 2026-02-15 12:00:02
- **Finalización:** 2026-02-15 12:16:28
- **Duración total:** ~16 minutos
- **Tiempo por réplica:** ~6.4 segundos promedio

---

## ⚡ ACCESO RÁPIDO

### Principales Conclusiones
👉 **Ver:** `RESUMEN_EJECUTIVO.md` - Sección "DECISIÓN FINAL RECOMENDADA"

### Mejor Escenario
👉 **MEJOR_2** es la opción recomendada
👉 **Ver:** `ANALISIS_COMPLETO.md` - Sección "Opción 2: ACTUALIZAR A MEJOR_2"

### Comparación Directa ACTUAL vs. MEJOR_2
👉 **Ver:** `reporte_comparativo.txt` - Líneas 85-165
👉 **Gráfico:** `graficos/resumen_indicadores.png`

### ROI y Costos
👉 **Ver:** `ANALISIS_COMPLETO.md` - Sección "Análisis Comparativo Detallado"
👉 **Gráfico:** `graficos/costos_mensuales.png`

### Plan de Implementación
👉 **Ver:** `RESUMEN_EJECUTIVO.md` - Sección "PLAN DE IMPLEMENTACIÓN"
👉 **Ver:** `ANALISIS_COMPLETO.md` - Sección "Plan de Implementación Sugerido"

---

## 📞 SOPORTE Y CONSULTAS

Para preguntas sobre:
- **Metodología:** Ver código en `simulacion/simulacion_cinco_escenarios.py`
- **Datos específicos:** Revisar archivos JSON en carpetas de escenarios
- **Interpretación:** Consultar `ANALISIS_COMPLETO.md`
- **Visualización:** Abrir `reporte_interactivo.html`

---

## 🔄 ACTUALIZACIONES

**Versión:** 2.0  
**Fecha:** 15 de Febrero de 2026  
**Cambios desde v1.0:**
- ✅ Actualización de configuración ACTUAL (2G, 19SR, 12I, 1SC)
- ✅ Comparación de 5 escenarios (vs. 3 en v1.0)
- ✅ 2 mejores + 2 peores escenarios adicionales
- ✅ 10 gráficos comparativos (vs. 0 en v1.0)
- ✅ Dashboard interactivo HTML
- ✅ Análisis detallado de ROI y balance costo-beneficio

---

**Documento generado:** 15 de Febrero de 2026  
**Simulación:** Hospital Eurnekian - Sistema de Simulación v2.0  
**Total de años simulados:** 1,500 años (150 réplicas × 10 años c/u)
