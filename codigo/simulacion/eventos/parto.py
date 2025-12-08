"""
Rutinas de eventos: Inicio y fin de parto
"""

from ..core.estado import EstadoSistema
from ..core.evento import Evento
from ..generadores.variables_aleatorias import GeneradorVariablesAleatorias
from ..recursos.asignacion import asignar_recursos


def procesar_inicio_parto(
    estado: EstadoSistema,
    evento: Evento,
    tef,
    generador: GeneradorVariablesAleatorias
):
    """
    Procesa el inicio de atención de un parto (natural o cesárea).
    
    Pasos:
    1. Obtener paciente del evento
    2. Registrar tiempo de inicio de atención
    3. Calcular y acumular tiempo de espera
    4. Generar tiempo de atención (TAP)
    5. Programar fin de parto
    
    Args:
        estado: Estado actual del sistema
        evento: Evento de inicio de parto
        tef: Tabla de Eventos Futuros
        generador: Generador de variables aleatorias
    """
    paciente = evento.datos_extra['paciente']
    tipo_parto = evento.datos_extra['tipo_parto']
    
    # Registrar tiempo de inicio de atención
    paciente.tiempo_inicio_atencion = estado.tiempo_actual
    
    # Calcular tiempo de espera
    tiempo_espera = paciente.calcular_tiempo_espera(estado.tiempo_actual)
    
    # Acumular tiempo de espera según tipo
    if tipo_parto == 'natural':
        estado.tiempo_total_espera_partos_nat += tiempo_espera
    else:  # cesarea
        estado.tiempo_total_espera_partos_ces += tiempo_espera
    
    # Generar tiempo de atención
    tap = generador.generar_tiempo_atencion_parto()
    
    # Programar fin de parto
    evento_fin = Evento(
        tipo='fin_parto',
        tiempo=estado.tiempo_actual + tap,
        paciente_id=paciente.id,
        datos_extra={
            'paciente': paciente,
            'tipo_parto': tipo_parto,
            'tap': tap
        }
    )
    tef.insertar(evento_fin)


def procesar_fin_parto(
    estado: EstadoSistema,
    evento: Evento,
    tef,
    generador: GeneradorVariablesAleatorias
):
    """
    Procesa el fin de un parto (natural o cesárea).
    
    Pasos:
    1. Obtener datos del evento
    2. Liberar médico y quirófano
    3. Actualizar contadores y tiempo de ocupación
    4. Procesar madre (asignar sala de recuperación o derivar)
    5. Procesar neonato (asignar incubadora o derivar)
    6. Intentar asignar recursos a siguiente paciente
    
    Args:
        estado: Estado actual del sistema
        evento: Evento de fin de parto
        tef: Tabla de Eventos Futuros
        generador: Generador de variables aleatorias
    """
    paciente = evento.datos_extra['paciente']
    tipo_parto = evento.datos_extra['tipo_parto']
    tap = evento.datos_extra['tap']
    
    # Liberar médico y quirófano (ambos tipos de partos usan quirófano)
    estado.medicos_disponibles += 1
    estado.quirofano_disponible = True
    
    # Actualizar tiempo de ocupación del quirófano
    estado.tiempo_ocupacion_quirofano += tap
    
    # Actualizar contadores
    if tipo_parto == 'natural':
        estado.total_partos_naturales += 1
    else:
        estado.total_partos_cesarea += 1
    
    estado.total_pacientes_atendidos += 1
    
    # Actualizar tiempo de ocupación de médicos
    estado.tiempo_ocupacion_medicos += tap
    
    # PROCESAR MADRE: Asignar sala de recuperación
    sala_id = estado.asignar_sala_recuperacion()
    
    if sala_id >= 0:
        # Hay sala disponible
        paciente.sala_recuperacion_asignada = sala_id
        trep = generador.generar_tiempo_reposo()
        
        # Programar fin de reposo
        evento_reposo = Evento(
            tipo='fin_reposo',
            tiempo=estado.tiempo_actual + trep,
            paciente_id=paciente.id,
            datos_extra={
                'paciente': paciente,
                'sala_id': sala_id,
                'trep': trep
            }
        )
        tef.insertar(evento_reposo)
    else:
        # No hay sala disponible - derivar
        estado.total_derivaciones_sr += 1
    
    # PROCESAR NEONATO: Verificar si requiere incubadora
    requiere_inc = generador.requiere_incubadora()
    
    if requiere_inc:
        estado.total_neonatos_requieren_inc += 1
        inc_id = estado.asignar_incubadora()
        
        if inc_id >= 0:
            # Hay incubadora disponible
            paciente.incubadora_asignada = inc_id
            tinc = generador.generar_tiempo_incubacion()
            
            # Programar fin de incubación
            evento_inc = Evento(
                tipo='fin_incubacion',
                tiempo=estado.tiempo_actual + tinc,
                paciente_id=paciente.id,
                datos_extra={
                    'paciente': paciente,
                    'inc_id': inc_id,
                    'tinc': tinc
                }
            )
            tef.insertar(evento_inc)
        else:
            # No hay incubadora disponible - derivar
            estado.total_derivaciones_inc += 1
    
    # Intentar asignar recursos a siguiente paciente
    asignar_recursos(estado, tef, generador)

