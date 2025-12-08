"""
Rutina de evento: Llegada de paciente a la guardia
"""

from ..core.estado import EstadoSistema
from ..core.evento import Evento
from ..core.paciente import Paciente
from ..generadores.variables_aleatorias import GeneradorVariablesAleatorias
from ..recursos.asignacion import asignar_recursos


def procesar_llegada(
    estado: EstadoSistema,
    tef,
    generador: GeneradorVariablesAleatorias
):
    """
    Procesa el evento de llegada de un paciente a la guardia.
    
    Pasos:
    1. Determinar tipo de paciente (consulta, parto natural, cesárea)
    2. Crear objeto Paciente
    3. Encolar según tipo
    4. Intentar asignar recursos inmediatamente
    5. Programar próxima llegada
    
    Args:
        estado: Estado actual del sistema
        tef: Tabla de Eventos Futuros
        generador: Generador de variables aleatorias
    """
    # 1. Determinar tipo de paciente
    tipo = generador.determinar_tipo_paciente()
    
    # 2. Crear paciente
    paciente = Paciente(
        id=estado.total_pacientes_llegados,
        tipo=tipo,
        tiempo_llegada=estado.tiempo_actual
    )
    
    estado.total_pacientes_llegados += 1
    
    # 3. Encolar según tipo
    if tipo == 'consulta':
        estado.cola_consultas.append(paciente)
    elif tipo == 'parto_natural':
        estado.cola_partos_naturales.append(paciente)
    elif tipo == 'parto_cesarea':
        estado.cola_partos_cesarea.append(paciente)
    
    # 4. Intentar asignar recursos inmediatamente
    asignar_recursos(estado, tef, generador)
    
    # 5. Programar próxima llegada
    intervalo = generador.generar_intervalo_arribo()
    proxima_llegada = Evento(
        tipo='llegada',
        tiempo=estado.tiempo_actual + intervalo
    )
    tef.insertar(proxima_llegada)

