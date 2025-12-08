"""
Rutina de evento: Fin de internación en incubadora
"""

from ..core.estado import EstadoSistema
from ..core.evento import Evento


def procesar_fin_incubacion(
    estado: EstadoSistema,
    evento: Evento,
    tef,
    generador
):
    """
    Procesa el fin de la internación en incubadora.
    
    Pasos:
    1. Obtener datos del evento
    2. Liberar incubadora
    3. El neonato es dado de alta (no se programa más eventos)
    
    Args:
        estado: Estado actual del sistema
        evento: Evento de fin de incubación
        tef: Tabla de Eventos Futuros (no usado aquí)
        generador: Generador de variables aleatorias (no usado aquí)
    """
    paciente = evento.datos_extra['paciente']
    inc_id = evento.datos_extra['inc_id']
    tinc = evento.datos_extra['tinc']
    
    # Liberar incubadora
    estado.liberar_incubadora(inc_id, tinc)
    
    # El neonato es dado de alta (no se programa más eventos)

