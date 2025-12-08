"""
Rutina de evento: Fin de reposo en sala de recuperación
"""

from ..core.estado import EstadoSistema
from ..core.evento import Evento


def procesar_fin_reposo(
    estado: EstadoSistema,
    evento: Evento,
    tef,
    generador
):
    """
    Procesa el fin del reposo en sala de recuperación.
    
    Pasos:
    1. Obtener datos del evento
    2. Liberar sala de recuperación
    3. La madre es dada de alta (no se programa más eventos)
    
    Args:
        estado: Estado actual del sistema
        evento: Evento de fin de reposo
        tef: Tabla de Eventos Futuros (no usado aquí)
        generador: Generador de variables aleatorias (no usado aquí)
    """
    paciente = evento.datos_extra['paciente']
    sala_id = evento.datos_extra['sala_id']
    trep = evento.datos_extra['trep']
    
    # Liberar sala de recuperación
    estado.liberar_sala_recuperacion(sala_id, trep)
    
    # La madre es dada de alta (no se programa más eventos)

