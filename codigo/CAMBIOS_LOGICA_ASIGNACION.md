# CORRECCIÓN DE LÓGICA DE ASIGNACIÓN DE RECURSOS

**Fecha:** 23 de Enero de 2026  
**Problema identificado:** Tiempos de espera anómalos (consultas esperan MÁS que partos a pesar de tener menor prioridad)

---

## 🔴 PROBLEMA ORIGINAL

### Lógica INCORRECTA (con elif):
```python
if hay_partos_naturales_y_recursos:
    asignar_parto_natural()
elif hay_cesareas_y_recursos:      # ❌ Solo si NO hay partos naturales
    asignar_cesarea()
elif hay_consultas_y_recursos:     # ❌ Solo si NO hay partos
    asignar_consulta()
```

### ¿Por qué fallaba?

1. **Bloqueaba asignaciones subsecuentes:** El `elif` impedía revisar otras colas si la primera condición era falsa
2. **No aprovechaba múltiples médicos:** Con 3 médicos disponibles, solo asignaba 1 recurso por llamada
3. **Consultas se acumulaban:** Mientras atendía partos largos (50-70 min), llegaban múltiples consultas sin poder asignarse

### Resultados ANTES de la corrección:

| Escenario | PECC (consultas) | PECP Natural | PECP Cesárea |
|-----------|------------------|--------------|--------------|
| ACTUAL    | **83.95 min** ❌ | 21.77 min ✓  | 39.87 min ✓  |
| MEJOR     | 0.08 min         | 19.46 min    | 35.25 min    |
| PEOR      | 1.40 min         | 19.34 min    | 35.45 min    |

**Anomalía:** Consultas esperaban 4x más que partos naturales, cuando deberían esperar MENOS (tienen menor prioridad pero son más rápidas y frecuentes).

---

## ✅ SOLUCIÓN IMPLEMENTADA (Opción 2)

### Nueva lógica (con loop iterativo):

```python
continuar = True
while continuar:
    continuar = False
    
    # Intentar parto natural
    if hay_parto_natural_y_recursos:
        asignar_parto_natural()
        continuar = True  # Seguir intentando
        continue          # Revisar prioridades desde inicio
    
    # Intentar cesárea
    if hay_cesarea_y_recursos:
        asignar_cesarea()
        continuar = True
        continue
    
    # Intentar consulta (SOLO si no hay partos esperando)
    if hay_consulta_y_recursos AND no_hay_partos_en_cola:
        asignar_consulta()
        continuar = True
```

### Mejoras implementadas:

1. ✅ **Loop iterativo:** Intenta asignar recursos hasta que no pueda más
2. ✅ **Múltiples asignaciones:** Con 3 médicos disponibles, puede asignar 3 pacientes simultáneamente
3. ✅ **Respeto estricto de prioridades:** Consultas SOLO se asignan si NO hay partos esperando
4. ✅ **Aprovecha recursos disponibles:** Si hay 3 médicos y 3 consultorios, atiende 3 consultas en paralelo

---

## 📊 CAMBIOS ESPERADOS

### Escenario ACTUAL (G=1, SC=1, SR=24, I=15)

**ANTES:**
- PECC: 83.95 min (consultas esperan mucho)
- Problema: Médico único crea cuello de botella severo

**DESPUÉS (esperado):**
- PECC: Debería REDUCIRSE (mejor aprovechamiento del médico)
- PECP: Podría AUMENTAR ligeramente (prioridad más estricta)
- **Trade-off:** Partos esperan un poco más, consultas MUCHO menos

### Escenario MEJOR (G=3, SC=3, SR=24, I=15)

**ANTES:**
- PECC: 0.08 min (ya casi perfecto)
- PECP: ~20 min

**DESPUÉS (esperado):**
- Similar o ligeramente mejor
- Mayor aprovechamiento de los 3 médicos disponibles

### Escenario PEOR (G=2, SC=2, SR=15, I=10)

**ANTES:**
- PECC: 1.40 min
- PECP: ~19-35 min

**DESPUÉS (esperado):**
- Mejor balance entre consultas y partos
- Menor acumulación en cola de consultas

---

## 🧪 VALIDACIÓN

Para validar que la corrección funciona, verificaremos:

1. ✅ **Prioridades respetadas:** PECP debería ser MENOR que PECC (o similar)
2. ✅ **Mejor utilización:** Con múltiples médicos, la utilización debería aumentar
3. ✅ **Coherencia matemática:** Los tiempos de espera deben ser consistentes con:
   - Tasa de arribos: ~1 cada 50 min
   - Tiempos de servicio: 5-23 min (consultas), 50-70 min (partos)
   - Recursos disponibles: G médicos, SC consultorios

---

## 🎯 PRÓXIMOS PASOS

1. ✅ Implementar lógica mejorada (COMPLETADO)
2. ⏳ Re-ejecutar simulaciones de 3 escenarios (30 réplicas c/u)
3. ⏳ Comparar resultados antes/después
4. ⏳ Validar que las prioridades se respetan correctamente
5. ⏳ Actualizar reporte final

---

## 📝 NOTAS TÉCNICAS

### Cambios en el código:

**Archivo modificado:** `simulacion/recursos/asignacion.py`

**Función:** `asignar_recursos()`

**Líneas modificadas:** 11-95

**Complejidad:** O(n) donde n = número de pacientes en colas (vs. O(1) antes)
- Impacto: Negligible dado que las colas rara vez superan 10-20 pacientes

### Compatibilidad:
- ✅ Compatible con código existente
- ✅ No requiere cambios en eventos
- ✅ No afecta generadores de variables aleatorias
- ✅ Mantiene interface de la función

---

**Implementado por:** GitHub Copilot  
**Fecha de implementación:** 2026-01-23 19:15
