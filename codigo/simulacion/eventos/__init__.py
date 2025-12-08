"""
Módulo eventos: Rutinas de manejo de eventos
"""

from .llegada import procesar_llegada
from .consulta import procesar_inicio_consulta, procesar_fin_consulta
from .parto import procesar_inicio_parto, procesar_fin_parto
from .reposo import procesar_fin_reposo
from .incubacion import procesar_fin_incubacion

__all__ = [
    'procesar_llegada',
    'procesar_inicio_consulta',
    'procesar_fin_consulta',
    'procesar_inicio_parto',
    'procesar_fin_parto',
    'procesar_fin_reposo',
    'procesar_fin_incubacion'
]

