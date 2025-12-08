"""
Tabla de Eventos Futuros (TEF): Cola de prioridad para eventos
"""

import heapq
from typing import List, Optional
from .evento import Evento


class TablaEventosFuturos:
    """
    Implementa la Tabla de Eventos Futuros como una cola de prioridad.
    Los eventos se ordenan por tiempo (el más próximo primero).
    """
    
    def __init__(self):
        """Inicializa la TEF vacía."""
        self.eventos: List[Evento] = []
        self.contador_tiebreak = 0  # Para desempatar eventos con mismo tiempo
    
    def insertar(self, evento: Evento):
        """
        Inserta un evento en la TEF.
        
        Args:
            evento: Evento a insertar
        """
        # Usar contador como tiebreak para mantener orden estable
        heapq.heappush(self.eventos, (evento.tiempo, self.contador_tiebreak, evento))
        self.contador_tiebreak += 1
    
    def extraer_proximo(self) -> Optional[Evento]:
        """
        Extrae y retorna el evento más próximo (menor tiempo).
        
        Returns:
            El evento más próximo, o None si la TEF está vacía
        """
        if len(self.eventos) == 0:
            return None
        
        _, _, evento = heapq.heappop(self.eventos)
        return evento
    
    def esta_vacia(self) -> bool:
        """
        Verifica si la TEF está vacía.
        
        Returns:
            True si está vacía, False en caso contrario
        """
        return len(self.eventos) == 0
    
    def tamaño(self) -> int:
        """
        Retorna el número de eventos en la TEF.
        
        Returns:
            Cantidad de eventos
        """
        return len(self.eventos)
    
    def ver_proximo(self) -> Optional[Evento]:
        """
        Retorna el próximo evento sin extraerlo.
        
        Returns:
            El evento más próximo, o None si la TEF está vacía
        """
        if len(self.eventos) == 0:
            return None
        
        _, _, evento = self.eventos[0]
        return evento
    
    def limpiar(self):
        """Limpia todos los eventos de la TEF."""
        self.eventos = []
        self.contador_tiebreak = 0

