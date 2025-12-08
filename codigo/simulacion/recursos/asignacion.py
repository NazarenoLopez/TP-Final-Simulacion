"""
Lógica de asignación de recursos según prioridades
"""

from typing import Optional
from ..core.estado import EstadoSistema
from ..core.evento import Evento
from ..core.paciente import Paciente
from ..generadores.variables_aleatorias import GeneradorVariablesAleatorias


def asignar_recursos(
    estado: EstadoSistema,
    tef,
    generador: GeneradorVariablesAleatorias
) -> bool:
    """
    Asigna recursos a pacientes en cola según las prioridades definidas.
    
    Prioridades:
    1. Partos naturales (mayor prioridad)
    2. Cesáreas
    3. Consultas (menor prioridad)
    
    Args:
        estado: Estado actual del sistema
        tef: Tabla de Eventos Futuros
        generador: Generador de variables aleatorias
        
    Returns:
        True si se asignó algún recurso, False en caso contrario
    """
    recursos_asignados = False
    
    # Prioridad 1: Partos naturales
    # Requieren: médico + quirófano
    if (len(estado.cola_partos_naturales) > 0 and 
        estado.medicos_disponibles > 0 and 
        estado.quirofano_disponible):
        
        paciente = estado.cola_partos_naturales.popleft()
        estado.medicos_disponibles -= 1
        estado.quirofano_disponible = False
        
        # Programar inicio de parto (inmediato)
        evento = Evento(
            tipo='inicio_parto',
            tiempo=estado.tiempo_actual,
            paciente_id=paciente.id,
            datos_extra={'tipo_parto': 'natural', 'paciente': paciente}
        )
        tef.insertar(evento)
        recursos_asignados = True
    
    # Prioridad 2: Cesáreas
    # Requieren: médico + quirófano
    elif (len(estado.cola_partos_cesarea) > 0 and 
          estado.medicos_disponibles > 0 and 
          estado.quirofano_disponible):
        
        paciente = estado.cola_partos_cesarea.popleft()
        estado.medicos_disponibles -= 1
        estado.quirofano_disponible = False
        
        # Programar inicio de parto (inmediato)
        evento = Evento(
            tipo='inicio_parto',
            tiempo=estado.tiempo_actual,
            paciente_id=paciente.id,
            datos_extra={'tipo_parto': 'cesarea', 'paciente': paciente}
        )
        tef.insertar(evento)
        recursos_asignados = True
    
    # Prioridad 3: Consultas
    # Requieren: solo médico
    elif (len(estado.cola_consultas) > 0 and 
          estado.medicos_disponibles > 0):
        
        paciente = estado.cola_consultas.popleft()
        estado.medicos_disponibles -= 1
        
        # Programar inicio de consulta (inmediato)
        evento = Evento(
            tipo='inicio_consulta',
            tiempo=estado.tiempo_actual,
            paciente_id=paciente.id,
            datos_extra={'paciente': paciente}
        )
        tef.insertar(evento)
        recursos_asignados = True
    
    return recursos_asignados

