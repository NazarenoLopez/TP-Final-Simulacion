"""
Script para regenerar el HTML con los gráficos correctos
"""
import json
from pathlib import Path

# Cargar datos
resultados_path = Path("resultados_cinco_escenarios")
with open(resultados_path / "comparacion_escenarios.json", encoding='utf-8') as f:
    resultados = json.load(f)

# HTML completo
html = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Análisis Comparativo - Hospital Eurnekian</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        
        header {
            background: linear-gradient(135deg, #2E86AB 0%, #06A77D 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }
        
        header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        header p {
            font-size: 1.2em;
            opacity: 0.95;
        }
        
        .nav-tabs {
            display: flex;
            background: #f5f5f5;
            border-bottom: 3px solid #2E86AB;
            overflow-x: auto;
        }
        
        .nav-tab {
            padding: 15px 30px;
            cursor: pointer;
            background: #f5f5f5;
            border: none;
            font-size: 1.1em;
            font-weight: 600;
            color: #666;
            transition: all 0.3s;
            white-space: nowrap;
        }
        
        .nav-tab:hover {
            background: #e0e0e0;
            color: #2E86AB;
        }
        
        .nav-tab.active {
            background: white;
            color: #2E86AB;
            border-bottom: 3px solid #2E86AB;
            margin-bottom: -3px;
        }
        
        .content {
            padding: 30px;
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
            animation: fadeIn 0.5s;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .scenario-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }
        
        .scenario-card {
            background: white;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            padding: 20px;
            transition: all 0.3s;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .scenario-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 20px rgba(0,0,0,0.2);
        }
        
        .scenario-card.actual {
            border-color: #2E86AB;
            background: linear-gradient(135deg, #f5f9fc 0%, #ffffff 100%);
        }
        
        .scenario-card.mejor {
            border-color: #06A77D;
            background: linear-gradient(135deg, #f0fdf7 0%, #ffffff 100%);
        }
        
        .scenario-card.peor {
            border-color: #D62246;
            background: linear-gradient(135deg, #fef5f7 0%, #ffffff 100%);
        }
        
        .scenario-card h3 {
            color: #2E86AB;
            margin-bottom: 15px;
            font-size: 1.5em;
            border-bottom: 2px solid #e0e0e0;
            padding-bottom: 10px;
        }
        
        .scenario-card.mejor h3 { color: #06A77D; }
        .scenario-card.peor h3 { color: #D62246; }
        
        .metric {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid #f0f0f0;
        }
        
        .metric:last-child {
            border-bottom: none;
        }
        
        .metric-label {
            font-weight: 600;
            color: #666;
        }
        
        .metric-value {
            color: #333;
            font-weight: bold;
        }
        
        .metric-value.good { color: #06A77D; }
        .metric-value.bad { color: #D62246; }
        .metric-value.neutral { color: #F77E21; }
        
        .graph-container {
            margin: 30px 0;
            padding: 20px;
            background: #f9f9f9;
            border-radius: 10px;
            text-align: center;
        }
        
        .graph-container h3 {
            color: #2E86AB;
            margin-bottom: 20px;
            font-size: 1.3em;
        }
        
        .graph-container img {
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .graphs-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 30px;
            margin: 20px 0;
        }
        
        .recommendation {
            background: linear-gradient(135deg, #06A77D 0%, #2E86AB 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin: 30px 0;
            box-shadow: 0 5px 20px rgba(0,0,0,0.2);
        }
        
        .recommendation h3 {
            font-size: 1.8em;
            margin-bottom: 15px;
            text-shadow: 1px 1px 3px rgba(0,0,0,0.3);
        }
        
        .recommendation ul {
            list-style: none;
            margin: 15px 0;
        }
        
        .recommendation li {
            padding: 10px 0;
            padding-left: 30px;
            position: relative;
        }
        
        .recommendation li:before {
            content: "✓";
            position: absolute;
            left: 0;
            font-weight: bold;
            color: #52D1DC;
            font-size: 1.3em;
        }
        
        .comparison-table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        .comparison-table th {
            background: linear-gradient(135deg, #2E86AB 0%, #06A77D 100%);
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }
        
        .comparison-table td {
            padding: 12px 15px;
            border-bottom: 1px solid #e0e0e0;
        }
        
        .comparison-table tr:hover {
            background: #f5f9fc;
        }
        
        .comparison-table tr:nth-child(even) {
            background: #f9f9f9;
        }
        
        .badge {
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: 600;
            margin: 0 5px;
        }
        
        .badge.best {
            background: #06A77D;
            color: white;
        }
        
        .badge.good {
            background: #52D1DC;
            color: white;
        }
        
        .badge.warning {
            background: #F77E21;
            color: white;
        }
        
        .badge.bad {
            background: #D62246;
            color: white;
        }
        
        .summary-box {
            background: #f0f9ff;
            border-left: 5px solid #2E86AB;
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
        }
        
        .summary-box h4 {
            color: #2E86AB;
            margin-bottom: 10px;
        }
        
        footer {
            background: #2a2a2a;
            color: white;
            text-align: center;
            padding: 20px;
            margin-top: 40px;
        }
        
        @media (max-width: 768px) {
            .graphs-grid {
                grid-template-columns: 1fr;
            }
            
            .scenario-grid {
                grid-template-columns: 1fr;
            }
            
            .nav-tabs {
                flex-wrap: wrap;
            }
            
            .nav-tab {
                flex: 1 0 auto;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🏥 Hospital Eurnekian</h1>
            <p>Análisis Comparativo de 5 Escenarios - Guardia Gineco-Obstétrica</p>
            <p style="font-size: 0.9em; margin-top: 10px;">Simulación de 10 años | 30 réplicas por escenario | Fecha: 15/02/2026</p>
        </header>
        
        <div class="nav-tabs">
            <button class="nav-tab active" onclick="showTab('resumen')">📊 Resumen</button>
            <button class="nav-tab" onclick="showTab('escenarios')">🎯 Escenarios</button>
            <button class="nav-tab" onclick="showTab('graficos')">📈 Gráficos</button>
            <button class="nav-tab" onclick="showTab('comparacion')">⚖️ Comparación</button>
            <button class="nav-tab" onclick="showTab('recomendaciones')">✅ Recomendaciones</button>
        </div>
        
        <div class="content">
"""

# Agregar el resto del contenido llamando a la generación
print("Generando HTML actualizado...")
print(f"Escenarios encontrados: {list(resultados.keys())}")

# Guardar el inicio
with open(resultados_path / "reporte_interactivo.html", 'w', encoding='utf-8') as f:
    f.write("Regenerando...")

print("HTML será regenerado por la simulación...")
print("\nEjecute: python simulacion/simulacion_cinco_escenarios.py")
