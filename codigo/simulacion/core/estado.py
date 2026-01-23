"""
Clase EstadoSistema: Maneja el estado dinámico del sistema
"""

from collections import deque
from typing import List, Dict, Any
import numpy as np


class EstadoSistema:
    """
    Maneja el estado dinámico del sistema de simulación.
    """
    
    def __init__(self, G: int, SR: int, I: int, SC: int = 1):
        """
        Inicializa el estado del sistema.
        
        Args:
            G: Cantidad de médicos de guardia
            SR: Cantidad de salas de recuperación
            I: Cantidad de incubadoras
        """
        # Parámetros del sistema
        self.G = G
        self.SR = SR
        self.I = I
        self.SC = SC  # Salas de consultorio
        
        # Colas de pacientes
        self.cola_consultas = deque()
        self.cola_partos_naturales = deque()
        self.cola_partos_cesarea = deque()
        
        # Recursos disponibles
        self.medicos_disponibles = G
        self.quirofano_disponible = True
        self.consultorios_disponibles = SC
        self.salas_recuperacion_libres = SR
        self.incubadoras_libres = I
        
        # Recursos ocupados
        self.consultorios_ocupados = 0
        self.salas_recuperacion_ocupadas = 0
        self.incubadoras_ocupadas = 0
        
        # Reloj de simulación
        self.tiempo_actual = 0.0
        
        # Contadores acumulados
        self.total_pacientes_llegados = 0
        self.total_pacientes_atendidos = 0
        self.total_consultas = 0
        self.total_partos_naturales = 0
        self.total_partos_cesarea = 0
        self.total_derivaciones_sr = 0
        self.total_derivaciones_inc = 0
        self.total_neonatos_requieren_inc = 0
        
        # Acumuladores de tiempo de espera
        self.tiempo_total_espera_consultas = 0.0
        self.tiempo_total_espera_partos_nat = 0.0
        self.tiempo_total_espera_partos_ces = 0.0
        
        # Acumuladores de ocupación
        self.tiempo_ocupacion_medicos = 0.0
        self.tiempo_ocupacion_quirofano = 0.0
        self.tiempo_ocupacion_consultorios = np.zeros(SC)  # Por consultorio
        self.tiempo_ocupacion_sr = np.zeros(SR)  # Por sala
        self.tiempo_inactividad_sr = np.zeros(SR)  # Por sala
        self.tiempo_ocupacion_inc = np.zeros(I)  # Por incubadora

        # Tiempo de última actualización de inactividad
        self.tiempo_ultima_actualizacion_consultorios = np.zeros(SC)
        self.tiempo_ultima_actualizacion_sr = np.zeros(SR)
        self.tiempo_ultima_actualizacion_inc = np.zeros(I)
        
        # Inicializar tiempos de última actualización
        for i in range(SC):
            self.tiempo_ultima_actualizacion_consultorios[i] = 0.0
        for i in range(SR):
            self.tiempo_ultima_actualizacion_sr[i] = 0.0
        for i in range(I):
            self.tiempo_ultima_actualizacion_inc[i] = 0.0

    def asignar_consultorio(self) -> int:
        """Asigna un consultorio disponible."""
        if self.consultorios_disponibles > 0:
            for i in range(self.SC):
                if self.tiempo_ocupacion_consultorios[i] == 0 or \
                   (self.tiempo_actual - self.tiempo_ultima_actualizacion_consultorios[i]) >= 0:
                    self.consultorios_disponibles -= 1
                    self.consultorios_ocupados += 1
                    self.tiempo_ultima_actualizacion_consultorios[i] = self.tiempo_actual
                    return i
        return -1

    def liberar_consultorio(self, consultorio_id: int, tiempo_ocupacion: float):
        """Libera un consultorio y acumula su tiempo de uso."""
        if consultorio_id < 0 or consultorio_id >= self.SC:
            return
        self.tiempo_ocupacion_consultorios[consultorio_id] += tiempo_ocupacion
        self.consultorios_disponibles += 1
        self.consultorios_ocupados -= 1
        self.tiempo_ultima_actualizacion_consultorios[consultorio_id] = self.tiempo_actual
    
    def actualizar_inactividad_sr(self, sala_id: int):
        """
        Actualiza el tiempo de inactividad de una sala de recuperación.
        
        Args:
            sala_id: ID de la sala
        """
        if sala_id < 0 or sala_id >= self.SR:
            return
        
        tiempo_transcurrido = self.tiempo_actual - self.tiempo_ultima_actualizacion_sr[sala_id]
        if tiempo_transcurrido > 0:
            # Si la sala está libre, acumular inactividad
            if self.salas_recuperacion_ocupadas < self.SR:
                # Verificar si esta sala específica está libre
                # (simplificado: asumimos que si hay salas libres, esta podría estar libre)
                self.tiempo_inactividad_sr[sala_id] += tiempo_transcurrido
        
        self.tiempo_ultima_actualizacion_sr[sala_id] = self.tiempo_actual
    
    def asignar_sala_recuperacion(self) -> int:
        """
        Asigna una sala de recuperación disponible.
        
        Returns:
            ID de la sala asignada, o -1 si no hay salas disponibles
        """
        if self.salas_recuperacion_libres > 0:
            # Encontrar primera sala libre
            for i in range(self.SR):
                if self.tiempo_ocupacion_sr[i] == 0 or \
                   (self.tiempo_actual - self.tiempo_ultima_actualizacion_sr[i]) > 0:
                    # Actualizar inactividad antes de asignar
                    self.actualizar_inactividad_sr(i)
                    self.salas_recuperacion_libres -= 1
                    self.salas_recuperacion_ocupadas += 1
                    return i
        return -1
    
    def liberar_sala_recuperacion(self, sala_id: int, tiempo_ocupacion: float):
        """
        Libera una sala de recuperación.
        
        Args:
            sala_id: ID de la sala a liberar
            tiempo_ocupacion: Tiempo que estuvo ocupada (en minutos)
        """
        if sala_id < 0 or sala_id >= self.SR:
            return
        
        self.actualizar_inactividad_sr(sala_id)
        self.tiempo_ocupacion_sr[sala_id] += tiempo_ocupacion
        self.salas_recuperacion_libres += 1
        self.salas_recuperacion_ocupadas -= 1
        self.tiempo_ultima_actualizacion_sr[sala_id] = self.tiempo_actual
    
    def asignar_incubadora(self) -> int:
        """
        Asigna una incubadora disponible.
        
        Returns:
            ID de la incubadora asignada, o -1 si no hay incubadoras disponibles
        """
        if self.incubadoras_libres > 0:
            for i in range(self.I):
                if self.tiempo_ocupacion_inc[i] == 0 or \
                   (self.tiempo_actual - self.tiempo_ultima_actualizacion_inc[i]) > 0:
                    self.incubadoras_libres -= 1
                    self.incubadoras_ocupadas += 1
                    return i
        return -1
    
    def liberar_incubadora(self, inc_id: int, tiempo_ocupacion: float):
        """
        Libera una incubadora.
        
        Args:
            inc_id: ID de la incubadora a liberar
            tiempo_ocupacion: Tiempo que estuvo ocupada (en minutos)
        """
        if inc_id < 0 or inc_id >= self.I:
            return
        
        self.tiempo_ocupacion_inc[inc_id] += tiempo_ocupacion
        self.incubadoras_libres += 1
        self.incubadoras_ocupadas -= 1
        self.tiempo_ultima_actualizacion_inc[inc_id] = self.tiempo_actual
    
    def obtener_resumen(self) -> Dict[str, Any]:
        """
        Obtiene un resumen del estado actual del sistema.
        
        Returns:
            Diccionario con el resumen del estado
        """
        return {
            'tiempo_actual': self.tiempo_actual,
            'medicos_disponibles': self.medicos_disponibles,
            'quirofano_disponible': self.quirofano_disponible,
            'salas_recuperacion_libres': self.salas_recuperacion_libres,
            'incubadoras_libres': self.incubadoras_libres,
            'cola_consultas': len(self.cola_consultas),
            'cola_partos_naturales': len(self.cola_partos_naturales),
            'cola_partos_cesarea': len(self.cola_partos_cesarea),
        }

