"""
Generador de Variables Aleatorias: Implementa todas las FDP del modelo
"""

import numpy as np
from scipy import stats
from typing import Optional


class GeneradorVariablesAleatorias:
    """
    Generador de variables aleatorias según las FDP definidas en el modelo.
    """
    
    def __init__(self, semilla: Optional[int] = None):
        """
        Inicializa el generador.
        
        Args:
            semilla: Semilla para reproducibilidad (opcional)
        """
        if semilla is not None:
            np.random.seed(semilla)
        
        # Parámetros de FDP según el paper y análisis previo
        # Intervalo entre arribos: Lognormal
        self.iag_s = 1.362189
        self.iag_scale = 23.268083
        self.iag_loc = 0.0
        
        # Tiempo de atención de consultas: Uniforme [5, 23]
        self.tac_min = 5.0
        self.tac_max = 23.0
        
        # Tiempo de atención de partos: Uniforme [50, 70]
        self.tap_min = 50.0
        self.tap_max = 70.0
        
        # Tiempo de reposo en salas de recuperación: Uniforme [24, 36] horas
        self.trep_min = 24.0 * 60.0  # Convertir a minutos
        self.trep_max = 36.0 * 60.0
        
        # Tiempo de internación en incubadora: Determinístico 4 días
        self.tinc = 4.0 * 24.0 * 60.0  # 4 días en minutos
        
        # Probabilidades categóricas
        self.p_parto = 0.30
        self.p_consulta = 0.70
        self.p_nat = 0.57  # Probabilidad de parto natural dado que es parto
        self.p_ces = 0.43  # Probabilidad de cesárea dado que es parto
        self.p_inc = 0.10  # Probabilidad de que neonato requiera incubadora
    
    def generar_intervalo_arribo(self) -> float:
        """
        Genera un intervalo entre arribos (IAG) usando distribución lognormal.
        
        Returns:
            Intervalo en minutos
        """
        intervalo = stats.lognorm.rvs(
            s=self.iag_s,
            scale=self.iag_scale,
            loc=self.iag_loc
        )
        # Asegurar que sea positivo
        return max(0.1, intervalo)
    
    def generar_tiempo_atencion_consulta(self) -> float:
        """
        Genera un tiempo de atención de consulta (TAC) usando distribución uniforme.
        
        Returns:
            Tiempo en minutos
        """
        return np.random.uniform(self.tac_min, self.tac_max)
    
    def generar_tiempo_atencion_parto(self) -> float:
        """
        Genera un tiempo de atención de parto (TAP) usando distribución uniforme.
        Aplica tanto a partos naturales como cesáreas.
        
        Returns:
            Tiempo en minutos
        """
        return np.random.uniform(self.tap_min, self.tap_max)
    
    def generar_tiempo_reposo(self) -> float:
        """
        Genera un tiempo de reposo en sala de recuperación (TREP) usando distribución uniforme.
        
        Returns:
            Tiempo en minutos
        """
        return np.random.uniform(self.trep_min, self.trep_max)
    
    def generar_tiempo_incubacion(self) -> float:
        """
        Genera un tiempo de internación en incubadora (TINC) - determinístico.
        
        Returns:
            Tiempo en minutos (4 días)
        """
        return self.tinc
    
    def determinar_tipo_paciente(self) -> str:
        """
        Determina el tipo de paciente según las probabilidades categóricas.
        
        Returns:
            'consulta', 'parto_natural', o 'parto_cesarea'
        """
        r = np.random.random()
        
        if r < self.p_parto:
            # Es un parto
            r2 = np.random.random()
            if r2 < self.p_nat:
                return 'parto_natural'
            else:
                return 'parto_cesarea'
        else:
            # Es una consulta
            return 'consulta'
    
    def requiere_incubadora(self) -> bool:
        """
        Determina si un neonato requiere incubadora.
        
        Returns:
            True si requiere incubadora, False en caso contrario
        """
        return np.random.random() < self.p_inc
    
    def set_semilla(self, semilla: int):
        """
        Establece una nueva semilla para reproducibilidad.
        
        Args:
            semilla: Semilla aleatoria
        """
        np.random.seed(semilla)

