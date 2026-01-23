"""
Rutinas de eventos: Inicio y fin de consulta
"""

from ..core.estado import EstadoSistema
from ..core.evento import Evento
from ..generadores.variables_aleatorias import GeneradorVariablesAleatorias
from ..recursos.asignacion import asignar_recursos


def procesar_inicio_consulta(
    estado: EstadoSistema,
    evento: Evento,
    tef,
    generador: GeneradorVariablesAleatorias
):
    """
    Procesa el inicio de atención de una consulta.
    
    Pasos:
    1. Obtener paciente del evento
    2. Registrar tiempo de inicio de atención
    3. Calcular y acumular tiempo de espera
    4. Generar tiempo de atención (TAC)
    5. Programar fin de consulta
    
    Args:
        estado: Estado actual del sistema
        evento: Evento de inicio de consulta
        tef: Tabla de Eventos Futuros
        generador: Generador de variables aleatorias
    """
    paciente = evento.datos_extra['paciente']
    consultorio_id = evento.datos_extra.get('consultorio_id', -1)
    
    # Registrar tiempo de inicio de atención
    paciente.tiempo_inicio_atencion = estado.tiempo_actual
    
    # Calcular tiempo de espera
    tiempo_espera = paciente.calcular_tiempo_espera(estado.tiempo_actual)
    estado.tiempo_total_espera_consultas += tiempo_espera
    
    # Generar tiempo de atención
    tac = generador.generar_tiempo_atencion_consulta()
    
    # Programar fin de consulta
    evento_fin = Evento(
        tipo='fin_consulta',
        tiempo=estado.tiempo_actual + tac,
        paciente_id=paciente.id,
        datos_extra={
            'paciente': paciente,
            'tac': tac,
            'consultorio_id': consultorio_id
        }
    )
    tef.insertar(evento_fin)


def procesar_fin_consulta(
    estado: EstadoSistema,
    evento: Evento,
    tef,
    generador: GeneradorVariablesAleatorias
):
    """
    Procesa el fin de atención de una consulta.
    
    Pasos:
    1. Obtener datos del evento
    2. Liberar médico
    3. Actualizar contadores
    4. Actualizar tiempo de ocupación de médicos
    5. Intentar asignar recursos a siguiente paciente
    
    Args:
        estado: Estado actual del sistema
        evento: Evento de fin de consulta
        tef: Tabla de Eventos Futuros
        generador: Generador de variables aleatorias
    """
    paciente = evento.datos_extra['paciente']
    tac = evento.datos_extra['tac']
    consultorio_id = evento.datos_extra.get('consultorio_id', -1)
    
    # Liberar médico y consultorio
    estado.medicos_disponibles += 1
    if consultorio_id >= 0:
        estado.liberar_consultorio(consultorio_id, tac)
    
    # Actualizar contadores
    estado.total_consultas += 1
    estado.total_pacientes_atendidos += 1
    
    # Actualizar tiempo de ocupación de médicos
    estado.tiempo_ocupacion_medicos += tac
    
    # Intentar asignar recursos a siguiente paciente
    asignar_recursos(estado, tef, generador)

