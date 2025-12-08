"""
Calculadora de Costos: Calcula costos operativos e inversión
"""

from typing import Dict, Any
from ..core.estado import EstadoSistema
import numpy as np


class CalculadoraCostos:
    """
    Calcula los costos operativos e inversión del sistema.
    """
    
    # Parámetros de costo según el paper
    C_SR_OP = 3000.0  # $/hora
    C_SR_INST = 7000000.0  # $
    C_Q = 95000.0  # $ por uso
    C_INC_OP = 25000.0  # $/día
    C_INC_INST = 1200000.0  # $
    C_MED_MENSUAL = 2000000.0  # $/mes
    C_BONO = 57000.0  # $ por bono
    
    # Dotación base del hospital
    SR_BASE = 24
    I_BASE = 15
    
    def __init__(self, tiempo_simulacion: float):
        """
        Inicializa la calculadora de costos.
        
        Args:
            tiempo_simulacion: Tiempo total de simulación (en minutos)
        """
        self.tiempo_simulacion = tiempo_simulacion
        # Convertir tiempo de simulación a meses (asumiendo 30 días por mes)
        self.meses_simulacion = tiempo_simulacion / (30.0 * 24.0 * 60.0)
    
    def calcular_costos(self, estado: EstadoSistema) -> Dict[str, Any]:
        """
        Calcula todos los costos.
        
        Args:
            estado: Estado final del sistema
            
        Returns:
            Diccionario con todos los costos
        """
        costos = {}
        
        # Costo de médicos
        costos['costo_medicos'] = self._calcular_costo_medicos(estado)
        
        # Costo de quirófano
        costos['costo_quirofano'] = self._calcular_costo_quirofano(estado)
        
        # Costo de salas de recuperación (operación)
        costos['costo_sr_operacion'] = self._calcular_costo_sr_operacion(estado)
        
        # Costo de incubadoras (operación)
        costos['costo_inc_operacion'] = self._calcular_costo_inc_operacion(estado)
        
        # Costo total mensual (CTM)
        costos['CTM'] = (costos['costo_medicos'] + 
                        costos['costo_quirofano'] + 
                        costos['costo_sr_operacion'] + 
                        costos['costo_inc_operacion'])
        
        # Costo inicial de instalaciones (CII)
        costos['CII'] = self._calcular_costo_instalaciones(estado)
        
        return costos
    
    def _calcular_costo_medicos(self, estado: EstadoSistema) -> float:
        """Calcula costo de médicos (salarios + bonos)."""
        # Costo base de salarios
        costo_salarios = estado.G * self.C_MED_MENSUAL * self.meses_simulacion
        
        # Calcular bonos
        # Bono por médico cada 31 pacientes operados (partos)
        total_partos = estado.total_partos_naturales + estado.total_partos_cesarea
        bonos_por_medico = total_partos // 31
        costo_bonos = estado.G * bonos_por_medico * self.C_BONO
        
        return costo_salarios + costo_bonos
    
    def _calcular_costo_quirofano(self, estado: EstadoSistema) -> float:
        """Calcula costo de uso del quirófano."""
        total_partos = estado.total_partos_naturales + estado.total_partos_cesarea
        return total_partos * self.C_Q
    
    def _calcular_costo_sr_operacion(self, estado: EstadoSistema) -> float:
        """Calcula costo de operación de salas de recuperación."""
        # Sumar tiempo de ocupación de todas las salas (en horas)
        tiempo_total_horas = np.sum(estado.tiempo_ocupacion_sr) / 60.0
        return tiempo_total_horas * self.C_SR_OP
    
    def _calcular_costo_inc_operacion(self, estado: EstadoSistema) -> float:
        """Calcula costo de operación de incubadoras."""
        # Sumar tiempo de ocupación de todas las incubadoras (en días)
        tiempo_total_dias = np.sum(estado.tiempo_ocupacion_inc) / (24.0 * 60.0)
        return tiempo_total_dias * self.C_INC_OP
    
    def _calcular_costo_instalaciones(self, estado: EstadoSistema) -> float:
        """Calcula costo inicial de instalaciones (solo si hay ampliación)."""
        costo_sr = 0.0
        costo_inc = 0.0
        
        # Costo de salas adicionales
        if estado.SR > self.SR_BASE:
            costo_sr = (estado.SR - self.SR_BASE) * self.C_SR_INST
        
        # Costo de incubadoras adicionales
        if estado.I > self.I_BASE:
            costo_inc = (estado.I - self.I_BASE) * self.C_INC_INST
        
        return costo_sr + costo_inc

