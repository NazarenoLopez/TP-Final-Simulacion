"""
Script para actualizar el HTML interactivo con los nombres nuevos de casos
y eliminar los gráficos y secciones no deseadas.
"""

import re
from pathlib import Path

def actualizar_html():
    """Actualiza el HTML con los cambios solicitados."""
    
    html_path = Path("resultados_cinco_escenarios/reporte_interactivo.html")
    
    # Leer el archivo
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Reemplazos de nombres
    reemplazos = [
        ('MEJOR_1', 'CASO 1'),
        ('MEJOR_2', 'CASO 2'),
        ('PEOR_1', 'CASO 3'),
        ('PEOR_2', 'CASO 4'),
    ]
    
    for viejo, nuevo in reemplazos:
        html_content = html_content.replace(viejo, nuevo)
    
    # Eliminar gráficos no deseados del tab de gráficos
    # 1. Utilización de recursos
    pattern_util = r'<div class="graph-container">.*?<h3>📈 Utilización de Recursos</h3>.*?</div>\s*</div>'
    html_content = re.sub(pattern_util, '', html_content, flags=re.DOTALL)
    
    # 2. Volumen de atención
    pattern_vol = r'<div class="graph-container">.*?<h3>👥 Volumen de Atención</h3>.*?</div>\s*</div>'
    html_content = re.sub(pattern_vol, '', html_content, flags=re.DOTALL)
    
    # 3. Comparación Radar
    pattern_radar = r'<div class="graph-container"[^>]*>.*?<h3>🕸️ Comparación Multi-Indicador \(Radar\)</h3>.*?</div>\s*</div>'
    html_content = re.sub(pattern_radar, '', html_content, flags=re.DOTALL)
    
    # Agregar leyenda de configuraciones en la sección de gráficos
    leyenda = '''
                <div class="summary-box" style="background: #f0f9ff; border-left: 5px solid #2E86AB; margin-bottom: 30px;">
                    <h4 style="color: #2E86AB;">📋 Referencias de Configuración</h4>
                    <table style="width: 100%; margin-top: 10px;">
                        <tr style="border-bottom: 1px solid #e0e0e0;">
                            <td style="padding: 8px; font-weight: 600;">ACTUAL:</td>
                            <td style="padding: 8px;">2 Médicos, 1 Consultorio, 19 Salas Recuperación, 12 Incubadoras</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #e0e0e0;">
                            <td style="padding: 8px; font-weight: 600;">CASO 1:</td>
                            <td style="padding: 8px;">3 Médicos, 3 Consultorios, 24 Salas Recuperación, 15 Incubadoras</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #e0e0e0;">
                            <td style="padding: 8px; font-weight: 600;">CASO 2:</td>
                            <td style="padding: 8px;">3 Médicos, 2 Consultorios, 20 Salas Recuperación, 13 Incubadoras</td>
                        </tr>
                        <tr style="border-bottom: 1px solid #e0e0e0;">
                            <td style="padding: 8px; font-weight: 600;">CASO 3:</td>
                            <td style="padding: 8px;">1 Médico, 1 Consultorio, 15 Salas Recuperación, 10 Incubadoras</td>
                        </tr>
                        <tr>
                            <td style="padding: 8px; font-weight: 600;">CASO 4:</td>
                            <td style="padding: 8px;">2 Médicos, 1 Consultorio, 16 Salas Recuperación, 11 Incubadoras</td>
                        </tr>
                    </table>
                </div>
'''
    
    # Insertar la leyenda después del título de gráficos
    html_content = html_content.replace(
        '<h2 style="color: #2E86AB; margin-bottom: 20px;">📈 Gráficos Comparativos</h2>',
        '<h2 style="color: #2E86AB; margin-bottom: 20px;">📈 Gráficos Comparativos</h2>\n' + leyenda
    )
    
    # Guardar el archivo actualizado
    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✓ HTML actualizado correctamente: {html_path}")
    print("\nCambios realizados:")
    print("  - MEJOR_1 → CASO 1")
    print("  - MEJOR_2 → CASO 2")
    print("  - PEOR_1 → CASO 3")
    print("  - PEOR_2 → CASO 4")
    print("  - Eliminado gráfico de Utilización de Recursos")
    print("  - Eliminado gráfico de Volumen de Atención")
    print("  - Eliminado gráfico de Comparación Radar")
    print("  - Agregada tabla de referencias de configuración")

if __name__ == "__main__":
    actualizar_html()
