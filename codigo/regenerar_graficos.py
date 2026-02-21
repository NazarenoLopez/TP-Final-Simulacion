"""
Script para regenerar solo los gráficos con porcentajes corregidos
"""
import json
from pathlib import Path
import sys

# Agregar el directorio de simulación al path
sys.path.insert(0, str(Path(__file__).parent))

from simulacion.simulacion_cinco_escenarios import ComparadorCincoEscenarios

def regenerar_graficos():
    """Regenera los gráficos usando los datos JSON existentes."""
    
    # Cargar datos existentes
    resultados_path = Path("resultados_cinco_escenarios")
    comparacion_file = resultados_path / "comparacion_escenarios.json"
    
    if not comparacion_file.exists():
        print(f"❌ Error: No se encontró {comparacion_file}")
        return
    
    print("📊 Regenerando gráficos con porcentajes corregidos...")
    print(f"   Leyendo datos de: {comparacion_file}")
    
    with open(comparacion_file, 'r', encoding='utf-8') as f:
        datos = json.load(f)
    
    # Crear instancia del comparador con el directorio correcto
    comparador = ComparadorCincoEscenarios(str(resultados_path))
    
    # Generar los gráficos
    print("\n🎨 Generando gráficos...")
    comparador._generar_graficos_comparativos(datos)
    
    print("\n✅ ¡Gráficos regenerados exitosamente!")
    print(f"   Los gráficos están en: {resultados_path / 'graficos'}")
    print("\n💡 Ahora puedes abrir el reporte_interactivo.html para ver los cambios")

if __name__ == "__main__":
    regenerar_graficos()
