"""
Motor Principal de Simulación: Ejecuta la simulación de eventos discretos
"""

from typing import Dict, Any, Optional
from .core.estado import EstadoSistema
from .core.tef import TablaEventosFuturos
from .core.evento import Evento
from .generadores.variables_aleatorias import GeneradorVariablesAleatorias
from .indicadores.calculadora import CalculadoraIndicadores
from .indicadores.costos import CalculadoraCostos

# Importar rutinas de eventos
from .eventos import (
    procesar_llegada,
    procesar_inicio_consulta,
    procesar_fin_consulta,
    procesar_inicio_parto,
    procesar_fin_parto,
    procesar_fin_reposo,
    procesar_fin_incubacion
)


class Simulador:
    """
    Motor principal de simulación de eventos discretos.
    """
    
    # Horizonte de simulación: 1 año = 365 × 24 × 60 = 525,600 minutos
    TIEMPO_SIMULACION = 365 * 24 * 60
    
    # Período de calentamiento: 1 mes = 30 × 24 × 60 = 43,200 minutos
    TIEMPO_CALENTAMIENTO = 30 * 24 * 60
    
    def __init__(self, G: int, SR: int, I: int, semilla: Optional[int] = None):
        """
        Inicializa el simulador.
        
        Args:
            G: Cantidad de médicos de guardia
            SR: Cantidad de salas de recuperación
            I: Cantidad de incubadoras
            semilla: Semilla para reproducibilidad (opcional)
        """
        self.G = G
        self.SR = SR
        self.I = I
        self.semilla = semilla
        
        # Inicializar componentes
        self.estado = EstadoSistema(G, SR, I)
        self.tef = TablaEventosFuturos()
        self.generador = GeneradorVariablesAleatorias(semilla=semilla)
        
        # Calculadoras
        self.calculadora_indicadores = CalculadoraIndicadores(
            tiempo_simulacion=self.TIEMPO_SIMULACION,
            tiempo_calentamiento=self.TIEMPO_CALENTAMIENTO
        )
        self.calculadora_costos = CalculadoraCostos(
            tiempo_simulacion=self.TIEMPO_SIMULACION
        )
    
    def inicializar(self):
        """Inicializa la simulación."""
        # Resetear estado
        self.estado = EstadoSistema(self.G, self.SR, self.I)
        self.tef = TablaEventosFuturos()
        
        # Resetear generador si hay semilla
        if self.semilla is not None:
            self.generador.set_semilla(self.semilla)
        
        # Programar primera llegada
        intervalo = self.generador.generar_intervalo_arribo()
        primera_llegada = Evento(
            tipo='llegada',
            tiempo=intervalo
        )
        self.tef.insertar(primera_llegada)
    
    def ejecutar(self, mostrar_progreso: bool = False) -> Dict[str, Any]:
        """
        Ejecuta la simulación completa.
        
        Args:
            mostrar_progreso: Si mostrar progreso por consola
            
        Returns:
            Diccionario con todos los resultados (indicadores + costos)
        """
        # Inicializar
        self.inicializar()
        
        # Contador de eventos procesados
        eventos_procesados = 0
        
        # Ciclo principal
        while not self.tef.esta_vacia():
            # Extraer próximo evento
            evento = self.tef.extraer_proximo()
            
            if evento is None:
                break
            
            # Avanzar reloj
            self.estado.tiempo_actual = evento.tiempo
            
            # Verificar si estamos en período de calentamiento
            en_calentamiento = self.estado.tiempo_actual < self.TIEMPO_CALENTAMIENTO
            
            # Procesar evento según tipo
            self._procesar_evento(evento, en_calentamiento)
            
            eventos_procesados += 1
            
            # Mostrar progreso cada 10000 eventos
            if mostrar_progreso and eventos_procesados % 10000 == 0:
                progreso = (self.estado.tiempo_actual / self.TIEMPO_SIMULACION) * 100
                print(f"Progreso: {progreso:.1f}% - Eventos: {eventos_procesados:,} - "
                      f"Tiempo: {self.estado.tiempo_actual:.0f} min")
            
            # Verificar condición de término
            if self.estado.tiempo_actual >= self.TIEMPO_SIMULACION:
                break
        
        # Calcular indicadores y costos
        indicadores = self.calculadora_indicadores.calcular_todos(self.estado)
        costos = self.calculadora_costos.calcular_costos(self.estado)
        
        # Combinar resultados
        resultados = {
            **indicadores,
            **costos,
            'eventos_procesados': eventos_procesados,
            'tiempo_simulacion': self.estado.tiempo_actual,
            'G': self.G,
            'SR': self.SR,
            'I': self.I
        }
        
        return resultados
    
    def _procesar_evento(self, evento: Evento, en_calentamiento: bool):
        """
        Procesa un evento según su tipo.
        
        Args:
            evento: Evento a procesar
            en_calentamiento: Si estamos en período de calentamiento
        """
        tipo = evento.tipo
        
        # Diccionario de rutinas de eventos
        rutinas = {
            'llegada': procesar_llegada,
            'inicio_consulta': procesar_inicio_consulta,
            'fin_consulta': procesar_fin_consulta,
            'inicio_parto': procesar_inicio_parto,
            'fin_parto': procesar_fin_parto,
            'fin_reposo': procesar_fin_reposo,
            'fin_incubacion': procesar_fin_incubacion
        }
        
        # Ejecutar rutina correspondiente
        if tipo in rutinas:
            rutina = rutinas[tipo]
            
            # Algunas rutinas necesitan el evento, otras no
            if tipo in ['inicio_consulta', 'fin_consulta', 'inicio_parto', 
                       'fin_parto', 'fin_reposo', 'fin_incubacion']:
                rutina(self.estado, evento, self.tef, self.generador)
            else:  # llegada
                rutina(self.estado, self.tef, self.generador)
        
        # Si estamos en calentamiento, resetear contadores acumulados
        if en_calentamiento and self.estado.tiempo_actual >= self.TIEMPO_CALENTAMIENTO:
            # Al finalizar calentamiento, resetear acumuladores
            self._resetear_acumuladores()
    
    def _resetear_acumuladores(self):
        """Resetea los acumuladores al finalizar el período de calentamiento."""
        # No resetear contadores de llegadas (para calcular derivaciones correctamente)
        # Solo resetear acumuladores de tiempo
        self.estado.tiempo_total_espera_consultas = 0.0
        self.estado.tiempo_total_espera_partos_nat = 0.0
        self.estado.tiempo_total_espera_partos_ces = 0.0
        self.estado.tiempo_ocupacion_medicos = 0.0
        self.estado.tiempo_ocupacion_quirofano = 0.0
        self.estado.tiempo_ocupacion_sr = self.estado.tiempo_ocupacion_sr * 0.0
        self.estado.tiempo_inactividad_sr = self.estado.tiempo_inactividad_sr * 0.0
        self.estado.tiempo_ocupacion_inc = self.estado.tiempo_ocupacion_inc * 0.0
        
        # Resetear contadores de atención (pero mantener llegadas)
        self.estado.total_pacientes_atendidos = 0
        self.estado.total_consultas = 0
        self.estado.total_partos_naturales = 0
        self.estado.total_partos_cesarea = 0
        self.estado.total_derivaciones_sr = 0
        self.estado.total_derivaciones_inc = 0
        self.estado.total_neonatos_requieren_inc = 0

