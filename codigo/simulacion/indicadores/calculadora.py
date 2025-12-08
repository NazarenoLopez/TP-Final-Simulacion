"""
Calculadora de Indicadores: Calcula todos los indicadores de desempeño
"""

from typing import Dict, Any
from ..core.estado import EstadoSistema
import numpy as np


class CalculadoraIndicadores:
    """
    Calcula los indicadores de desempeño del sistema.
    """
    
    def __init__(self, tiempo_simulacion: float, tiempo_calentamiento: float = 0.0):
        """
        Inicializa la calculadora.
        
        Args:
            tiempo_simulacion: Tiempo total de simulación (en minutos)
            tiempo_calentamiento: Tiempo de calentamiento a descartar (en minutos)
        """
        self.tiempo_simulacion = tiempo_simulacion
        self.tiempo_calentamiento = tiempo_calentamiento
        self.tiempo_efectivo = tiempo_simulacion - tiempo_calentamiento
    
    def calcular_todos(self, estado: EstadoSistema) -> Dict[str, Any]:
        """
        Calcula todos los indicadores de desempeño.
        
        Args:
            estado: Estado final del sistema
            
        Returns:
            Diccionario con todos los indicadores
        """
        indicadores = {}
        
        # Tiempos promedio de espera (PEC)
        indicadores['PEC_consultas'] = self._calcular_pec_consultas(estado)
        indicadores['PEC_partos_nat'] = self._calcular_pec_partos_nat(estado)
        indicadores['PEC_partos_ces'] = self._calcular_pec_partos_ces(estado)
        indicadores['PEC_general'] = self._calcular_pec_general(estado)
        
        # Utilizaciones
        indicadores['UT_med'] = self._calcular_utilizacion_medicos(estado)
        indicadores['UT_Q'] = self._calcular_utilizacion_quirofano(estado)
        
        # Porcentaje de tiempo ocioso de salas de recuperación
        indicadores['PTOSR'] = self._calcular_ptosr(estado)
        indicadores['PTOSR_promedio'] = np.mean(indicadores['PTOSR']) if len(indicadores['PTOSR']) > 0 else 0.0
        
        # Porcentajes de derivación
        indicadores['PPDSR'] = self._calcular_ppdsr(estado)
        indicadores['PPDINC'] = self._calcular_ppdinc(estado)
        
        # Contadores adicionales
        indicadores['total_pacientes_llegados'] = estado.total_pacientes_llegados
        indicadores['total_pacientes_atendidos'] = estado.total_pacientes_atendidos
        indicadores['total_consultas'] = estado.total_consultas
        indicadores['total_partos_naturales'] = estado.total_partos_naturales
        indicadores['total_partos_cesarea'] = estado.total_partos_cesarea
        indicadores['total_derivaciones_sr'] = estado.total_derivaciones_sr
        indicadores['total_derivaciones_inc'] = estado.total_derivaciones_inc
        indicadores['total_partos'] = estado.total_partos_naturales + estado.total_partos_cesarea
        
        return indicadores
    
    def _calcular_pec_consultas(self, estado: EstadoSistema) -> float:
        """Calcula tiempo promedio de espera para consultas."""
        if estado.total_consultas == 0:
            return 0.0
        return estado.tiempo_total_espera_consultas / estado.total_consultas
    
    def _calcular_pec_partos_nat(self, estado: EstadoSistema) -> float:
        """Calcula tiempo promedio de espera para partos naturales."""
        if estado.total_partos_naturales == 0:
            return 0.0
        return estado.tiempo_total_espera_partos_nat / estado.total_partos_naturales
    
    def _calcular_pec_partos_ces(self, estado: EstadoSistema) -> float:
        """Calcula tiempo promedio de espera para cesáreas."""
        if estado.total_partos_cesarea == 0:
            return 0.0
        return estado.tiempo_total_espera_partos_ces / estado.total_partos_cesarea
    
    def _calcular_pec_general(self, estado: EstadoSistema) -> float:
        """Calcula tiempo promedio de espera general."""
        if estado.total_pacientes_atendidos == 0:
            return 0.0
        tiempo_total = (estado.tiempo_total_espera_consultas + 
                       estado.tiempo_total_espera_partos_nat + 
                       estado.tiempo_total_espera_partos_ces)
        return tiempo_total / estado.total_pacientes_atendidos
    
    def _calcular_utilizacion_medicos(self, estado: EstadoSistema) -> float:
        """Calcula utilización promedio de médicos."""
        if self.tiempo_efectivo == 0:
            return 0.0
        tiempo_total_disponible = estado.G * self.tiempo_efectivo
        if tiempo_total_disponible == 0:
            return 0.0
        return (estado.tiempo_ocupacion_medicos / tiempo_total_disponible) * 100.0
    
    def _calcular_utilizacion_quirofano(self, estado: EstadoSistema) -> float:
        """Calcula utilización del quirófano."""
        if self.tiempo_efectivo == 0:
            return 0.0
        return (estado.tiempo_ocupacion_quirofano / self.tiempo_efectivo) * 100.0
    
    def _calcular_ptosr(self, estado: EstadoSistema) -> list:
        """Calcula porcentaje de tiempo ocioso por sala de recuperación."""
        ptosr = []
        for i in range(estado.SR):
            if self.tiempo_efectivo == 0:
                ptosr.append(0.0)
            else:
                porcentaje = (estado.tiempo_inactividad_sr[i] / self.tiempo_efectivo) * 100.0
                ptosr.append(porcentaje)
        return ptosr
    
    def _calcular_ppdsr(self, estado: EstadoSistema) -> float:
        """Calcula porcentaje de pacientes derivados por falta de salas de recuperación."""
        total_partos = estado.total_partos_naturales + estado.total_partos_cesarea
        if total_partos == 0:
            return 0.0
        return (estado.total_derivaciones_sr / total_partos) * 100.0
    
    def _calcular_ppdinc(self, estado: EstadoSistema) -> float:
        """Calcula porcentaje de neonatos derivados por falta de incubadoras."""
        if estado.total_neonatos_requieren_inc == 0:
            return 0.0
        return (estado.total_derivaciones_inc / estado.total_neonatos_requieren_inc) * 100.0

