"""
Clase Evento: Representa un evento en la simulación
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class Evento:
    """
    Representa un evento en la simulación de eventos discretos.
    
    Atributos:
        tipo: Tipo de evento ('llegada', 'fin_consulta', 'inicio_parto', 
              'fin_parto', 'fin_reposo', 'fin_incubacion')
        tiempo: Tiempo programado del evento (en minutos)
        paciente_id: ID del paciente asociado (opcional)
        datos_extra: Información adicional del evento
    """
    tipo: str
    tiempo: float
    paciente_id: Optional[int] = None
    datos_extra: Optional[Dict[str, Any]] = None
    
    def __lt__(self, other):
        """Permite ordenar eventos por tiempo (para cola de prioridad)"""
        return self.tiempo < other.tiempo
    
    def __eq__(self, other):
        """Comparación de igualdad"""
        if not isinstance(other, Evento):
            return False
        return (self.tipo == other.tipo and 
                self.tiempo == other.tiempo and
                self.paciente_id == other.paciente_id)
    
    def __repr__(self):
        return f"Evento(tipo='{self.tipo}', tiempo={self.tiempo:.2f}, paciente_id={self.paciente_id})"

