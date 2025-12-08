"""
Clase Paciente: Representa un paciente en el sistema
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Paciente:
    """
    Representa un paciente en el sistema de simulación.
    
    Atributos:
        id: Identificador único del paciente
        tipo: Tipo de atención ('consulta', 'parto_natural', 'parto_cesarea')
        tiempo_llegada: Tiempo de arribo a la guardia (en minutos)
        tiempo_inicio_atencion: Tiempo en que comenzó a ser atendido (en minutos)
        requiere_incubadora: Si el neonato requiere incubadora (solo para partos)
        sala_recuperacion_asignada: ID de la sala de recuperación asignada (si aplica)
        incubadora_asignada: ID de la incubadora asignada (si aplica)
    """
    id: int
    tipo: str
    tiempo_llegada: float
    tiempo_inicio_atencion: Optional[float] = None
    requiere_incubadora: bool = False
    sala_recuperacion_asignada: Optional[int] = None
    incubadora_asignada: Optional[int] = None
    
    def calcular_tiempo_espera(self, tiempo_actual: float) -> float:
        """
        Calcula el tiempo de espera en cola.
        
        Args:
            tiempo_actual: Tiempo actual de la simulación
            
        Returns:
            Tiempo de espera en minutos
        """
        if self.tiempo_inicio_atencion is None:
            return tiempo_actual - self.tiempo_llegada
        return self.tiempo_inicio_atencion - self.tiempo_llegada
    
    def es_parto(self) -> bool:
        """Verifica si el paciente es un parto (natural o cesárea)"""
        return self.tipo in ['parto_natural', 'parto_cesarea']
    
    def __repr__(self):
        return f"Paciente(id={self.id}, tipo='{self.tipo}', llegada={self.tiempo_llegada:.2f})"

