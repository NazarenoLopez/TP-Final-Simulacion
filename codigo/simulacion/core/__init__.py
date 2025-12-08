"""
Módulo core: Clases base del sistema de simulación
"""

from .evento import Evento
from .paciente import Paciente
from .estado import EstadoSistema
from .tef import TablaEventosFuturos

__all__ = ['Evento', 'Paciente', 'EstadoSistema', 'TablaEventosFuturos']

