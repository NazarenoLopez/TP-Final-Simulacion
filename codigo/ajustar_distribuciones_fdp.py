"""
Script para encontrar la mejor distribución que representa la FDP
de los intervalos entre arribos y generar gráficos para el paper.

Autor: TP Final Simulación
"""

import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
from scipy import optimize
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# Configuración
BASE_DIR = Path(__file__).parent.parent
OUTPUT_DIR = BASE_DIR / "codigo" / "resultados"

# Configuración de matplotlib para gráficos de calidad para paper
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 12
plt.rcParams['axes.labelsize'] = 14
plt.rcParams['axes.titlesize'] = 16
plt.rcParams['xtick.labelsize'] = 12
plt.rcParams['ytick.labelsize'] = 12
plt.rcParams['legend.fontsize'] = 12
plt.rcParams['figure.dpi'] = 300

def cargar_intervalos():
    """Carga los intervalos previamente calculados."""
    archivo_intervalos = OUTPUT_DIR / "intervalos_arribos.npy"
    
    if not archivo_intervalos.exists():
        print(f"⚠️  No se encuentra el archivo de intervalos: {archivo_intervalos}")
        print(f"   Intentando calcular intervalos automáticamente...")
        
        # Importar y ejecutar el cálculo
        import sys
        sys.path.insert(0, str(Path(__file__).parent))
        from calcular_fdp_intervalos import main as calcular_main
        
        print(f"   Esto puede tomar varios minutos...")
        intervalos, stats = calcular_main()
        
        if intervalos is None or len(intervalos) == 0:
            print(f"❌ ERROR: No se pudieron calcular los intervalos")
            return None
        
        return intervalos
    
    intervalos = np.load(archivo_intervalos)
    print(f"✓ Intervalos cargados: {len(intervalos):,} intervalos")
    return intervalos

def filtrar_intervalos_validos(intervalos):
    """Filtra intervalos válidos (elimina negativos y muy grandes)."""
    # Filtrar: entre 0 y 24 horas (1440 minutos)
    intervalos_filtrados = intervalos[(intervalos >= 0) & (intervalos <= 1440)]
    
    print(f"\n📊 Filtrado de intervalos:")
    print(f"   Total: {len(intervalos):,}")
    print(f"   Válidos (0-1440 min): {len(intervalos_filtrados):,}")
    print(f"   Eliminados: {len(intervalos) - len(intervalos_filtrados):,}")
    
    return intervalos_filtrados

def ajustar_distribucion_exponencial(intervalos):
    """Ajusta una distribución exponencial."""
    try:
        # Estimador de máxima verosimilitud
        lambda_est = 1.0 / np.mean(intervalos)
        params = {'scale': 1/lambda_est}
        
        # Test de bondad de ajuste (Kolmogorov-Smirnov)
        ks_stat, ks_pvalue = stats.kstest(intervalos, 
                                          lambda x: stats.expon.cdf(x, scale=params['scale']))
        
        # AIC y BIC
        n = len(intervalos)
        log_likelihood = np.sum(stats.expon.logpdf(intervalos, scale=params['scale']))
        aic = 2 * 1 - 2 * log_likelihood  # 1 parámetro
        bic = 1 * np.log(n) - 2 * log_likelihood
        
        return {
            'nombre': 'Exponencial',
            'dist': stats.expon,
            'params': params,
            'ks_stat': ks_stat,
            'ks_pvalue': ks_pvalue,
            'aic': aic,
            'bic': bic,
            'log_likelihood': log_likelihood
        }
    except Exception as e:
        print(f"   ⚠️  Error ajustando Exponencial: {e}")
        return None

def ajustar_distribucion_gamma(intervalos):
    """Ajusta una distribución Gamma."""
    try:
        # Ajuste por máxima verosimilitud
        alpha, loc, beta = stats.gamma.fit(intervalos, floc=0)
        params = {'a': alpha, 'scale': 1/beta, 'loc': 0}
        
        # Test KS
        ks_stat, ks_pvalue = stats.kstest(intervalos,
                                         lambda x: stats.gamma.cdf(x, a=alpha, scale=1/beta, loc=0))
        
        # AIC y BIC
        n = len(intervalos)
        log_likelihood = np.sum(stats.gamma.logpdf(intervalos, a=alpha, scale=1/beta, loc=0))
        aic = 2 * 2 - 2 * log_likelihood  # 2 parámetros
        bic = 2 * np.log(n) - 2 * log_likelihood
        
        return {
            'nombre': 'Gamma',
            'dist': stats.gamma,
            'params': params,
            'ks_stat': ks_stat,
            'ks_pvalue': ks_pvalue,
            'aic': aic,
            'bic': bic,
            'log_likelihood': log_likelihood,
            'alpha': alpha,
            'beta': beta
        }
    except Exception as e:
        print(f"   ⚠️  Error ajustando Gamma: {e}")
        return None

def ajustar_distribucion_weibull(intervalos):
    """Ajusta una distribución Weibull."""
    try:
        # Ajuste por máxima verosimilitud
        c, loc, scale = stats.weibull_min.fit(intervalos, floc=0)
        params = {'c': c, 'scale': scale, 'loc': 0}
        
        # Test KS
        ks_stat, ks_pvalue = stats.kstest(intervalos,
                                         lambda x: stats.weibull_min.cdf(x, c=c, scale=scale, loc=0))
        
        # AIC y BIC
        n = len(intervalos)
        log_likelihood = np.sum(stats.weibull_min.logpdf(intervalos, c=c, scale=scale, loc=0))
        aic = 2 * 2 - 2 * log_likelihood  # 2 parámetros
        bic = 2 * np.log(n) - 2 * log_likelihood
        
        return {
            'nombre': 'Weibull',
            'dist': stats.weibull_min,
            'params': params,
            'ks_stat': ks_stat,
            'ks_pvalue': ks_pvalue,
            'aic': aic,
            'bic': bic,
            'log_likelihood': log_likelihood,
            'c': c,
            'scale': scale
        }
    except Exception as e:
        print(f"   ⚠️  Error ajustando Weibull: {e}")
        return None

def ajustar_distribucion_lognormal(intervalos):
    """Ajusta una distribución Lognormal."""
    try:
        # Ajuste por máxima verosimilitud
        s, loc, scale = stats.lognorm.fit(intervalos, floc=0)
        params = {'s': s, 'scale': scale, 'loc': 0}
        
        # Test KS
        ks_stat, ks_pvalue = stats.kstest(intervalos,
                                         lambda x: stats.lognorm.cdf(x, s=s, scale=scale, loc=0))
        
        # AIC y BIC
        n = len(intervalos)
        log_likelihood = np.sum(stats.lognorm.logpdf(intervalos, s=s, scale=scale, loc=0))
        aic = 2 * 2 - 2 * log_likelihood  # 2 parámetros
        bic = 2 * np.log(n) - 2 * log_likelihood
        
        return {
            'nombre': 'Lognormal',
            'dist': stats.lognorm,
            'params': params,
            'ks_stat': ks_stat,
            'ks_pvalue': ks_pvalue,
            'aic': aic,
            'bic': bic,
            'log_likelihood': log_likelihood,
            's': s,
            'scale': scale
        }
    except Exception as e:
        print(f"   ⚠️  Error ajustando Lognormal: {e}")
        return None

def ajustar_todas_distribuciones(intervalos):
    """Ajusta todas las distribuciones y compara."""
    print(f"\n🔬 Ajustando distribuciones teóricas...")
    
    distribuciones = []
    
    # Ajustar cada distribución
    print(f"   Ajustando Exponencial...")
    exp = ajustar_distribucion_exponencial(intervalos)
    if exp:
        distribuciones.append(exp)
        print(f"      ✓ Exponencial ajustada")
    
    print(f"   Ajustando Gamma...")
    gamma = ajustar_distribucion_gamma(intervalos)
    if gamma:
        distribuciones.append(gamma)
        print(f"      ✓ Gamma ajustada")
    
    print(f"   Ajustando Weibull...")
    weibull = ajustar_distribucion_weibull(intervalos)
    if weibull:
        distribuciones.append(weibull)
        print(f"      ✓ Weibull ajustada")
    
    print(f"   Ajustando Lognormal...")
    lognorm = ajustar_distribucion_lognormal(intervalos)
    if lognorm:
        distribuciones.append(lognorm)
        print(f"      ✓ Lognormal ajustada")
    
    return distribuciones

def encontrar_mejor_distribucion(distribuciones):
    """Encuentra la mejor distribución basándose en AIC, BIC y p-value de KS."""
    if len(distribuciones) == 0:
        return None
    
    print(f"\n📊 Comparación de distribuciones:")
    print(f"{'='*80}")
    print(f"{'Distribución':<15} {'AIC':<15} {'BIC':<15} {'KS Stat':<15} {'KS p-value':<15}")
    print(f"{'-'*80}")
    
    for dist in distribuciones:
        print(f"{dist['nombre']:<15} {dist['aic']:<15.2f} {dist['bic']:<15.2f} "
              f"{dist['ks_stat']:<15.6f} {dist['ks_pvalue']:<15.6f}")
    
    # Encontrar la mejor según AIC (menor es mejor)
    mejor_aic = min(distribuciones, key=lambda x: x['aic'])
    
    # Encontrar la mejor según BIC (menor es mejor)
    mejor_bic = min(distribuciones, key=lambda x: x['bic'])
    
    # Encontrar la mejor según p-value de KS (mayor es mejor)
    mejor_ks = max(distribuciones, key=lambda x: x['ks_pvalue'])
    
    print(f"\n🏆 Mejor distribución según AIC: {mejor_aic['nombre']} (AIC = {mejor_aic['aic']:.2f})")
    print(f"🏆 Mejor distribución según BIC: {mejor_bic['nombre']} (BIC = {mejor_bic['bic']:.2f})")
    print(f"🏆 Mejor distribución según KS p-value: {mejor_ks['nombre']} (p = {mejor_ks['ks_pvalue']:.6f})")
    
    # Decidir la mejor (priorizar AIC, luego p-value)
    mejor = mejor_aic
    if mejor_ks['ks_pvalue'] > 0.05 and mejor_ks['nombre'] != mejor_aic['nombre']:
        # Si hay una con p-value significativo y diferente, considerar ambas
        print(f"\n💡 Recomendación: {mejor_aic['nombre']} tiene el mejor AIC")
        if mejor_ks['ks_pvalue'] > mejor_aic['ks_pvalue']:
            print(f"   Pero {mejor_ks['nombre']} tiene mejor p-value de KS")
    
    return mejor, distribuciones

def generar_histograma_fdp(intervalos, distribuciones, mejor_dist):
    """Genera histograma de la FDP con distribuciones superpuestas."""
    print(f"\n📈 Generando histograma de FDP...")
    
    # Filtrar para visualización (hasta 200 minutos)
    intervalos_vis = intervalos[intervalos <= 200]
    
    fig, axes = plt.subplots(2, 1, figsize=(14, 10))
    
    # Histograma 1: Vista general
    ax1 = axes[0]
    n, bins, patches = ax1.hist(intervalos_vis, bins=100, density=True, 
                                alpha=0.7, color='steelblue', 
                                edgecolor='black', linewidth=0.5,
                                label='FDP Empírica')
    
    # Superponer distribuciones teóricas
    x = np.linspace(0, 200, 1000)
    
    for dist_info in distribuciones:
        try:
            if dist_info['nombre'] == 'Exponencial':
                y = stats.expon.pdf(x, scale=dist_info['params']['scale'])
                estilo = '--' if dist_info['nombre'] != mejor_dist['nombre'] else '-'
                grosor = 2 if dist_info['nombre'] == mejor_dist['nombre'] else 1.5
                color = 'red' if dist_info['nombre'] == mejor_dist['nombre'] else 'gray'
            elif dist_info['nombre'] == 'Gamma':
                y = stats.gamma.pdf(x, a=dist_info['params']['a'], 
                                   scale=dist_info['params']['scale'], loc=0)
                estilo = '--' if dist_info['nombre'] != mejor_dist['nombre'] else '-'
                grosor = 2 if dist_info['nombre'] == mejor_dist['nombre'] else 1.5
                color = 'red' if dist_info['nombre'] == mejor_dist['nombre'] else 'gray'
            elif dist_info['nombre'] == 'Weibull':
                y = stats.weibull_min.pdf(x, c=dist_info['params']['c'], 
                                         scale=dist_info['params']['scale'], loc=0)
                estilo = '--' if dist_info['nombre'] != mejor_dist['nombre'] else '-'
                grosor = 2 if dist_info['nombre'] == mejor_dist['nombre'] else 1.5
                color = 'red' if dist_info['nombre'] == mejor_dist['nombre'] else 'gray'
            elif dist_info['nombre'] == 'Lognormal':
                y = stats.lognorm.pdf(x, s=dist_info['params']['s'], 
                                     scale=dist_info['params']['scale'], loc=0)
                estilo = '--' if dist_info['nombre'] != mejor_dist['nombre'] else '-'
                grosor = 2 if dist_info['nombre'] == mejor_dist['nombre'] else 1.5
                color = 'red' if dist_info['nombre'] == mejor_dist['nombre'] else 'gray'
            else:
                continue
            
            label = f"{dist_info['nombre']}"
            if dist_info['nombre'] == mejor_dist['nombre']:
                label += " (Mejor ajuste)"
            
            ax1.plot(x, y, estilo, linewidth=grosor, label=label, 
                    color=color, alpha=0.8)
        except:
            continue
    
    ax1.set_xlabel('Intervalo entre arribos (minutos)', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Densidad de Probabilidad', fontsize=14, fontweight='bold')
    ax1.set_title('Función de Densidad de Probabilidad - Intervalos entre Arribos', 
                  fontsize=16, fontweight='bold', pad=20)
    ax1.legend(fontsize=11, loc='upper right', framealpha=0.9)
    ax1.grid(True, alpha=0.3, linestyle='--')
    ax1.set_xlim(0, 200)
    
    # Histograma 2: Escala logarítmica
    ax2 = axes[1]
    ax2.hist(intervalos_vis, bins=100, density=True, alpha=0.7, 
            color='steelblue', edgecolor='black', linewidth=0.5,
            label='FDP Empírica')
    
    # Superponer distribuciones en escala log
    for dist_info in distribuciones:
        try:
            if dist_info['nombre'] == 'Exponencial':
                y = stats.expon.pdf(x, scale=dist_info['params']['scale'])
            elif dist_info['nombre'] == 'Gamma':
                y = stats.gamma.pdf(x, a=dist_info['params']['a'], 
                                   scale=dist_info['params']['scale'], loc=0)
            elif dist_info['nombre'] == 'Weibull':
                y = stats.weibull_min.pdf(x, c=dist_info['params']['c'], 
                                         scale=dist_info['params']['scale'], loc=0)
            elif dist_info['nombre'] == 'Lognormal':
                y = stats.lognorm.pdf(x, s=dist_info['params']['s'], 
                                     scale=dist_info['params']['scale'], loc=0)
            else:
                continue
            
            estilo = '--' if dist_info['nombre'] != mejor_dist['nombre'] else '-'
            grosor = 2 if dist_info['nombre'] == mejor_dist['nombre'] else 1.5
            color = 'red' if dist_info['nombre'] == mejor_dist['nombre'] else 'gray'
            
            label = f"{dist_info['nombre']}"
            if dist_info['nombre'] == mejor_dist['nombre']:
                label += " (Mejor ajuste)"
            
            ax2.plot(x, y, estilo, linewidth=grosor, label=label, 
                    color=color, alpha=0.8)
        except:
            continue
    
    ax2.set_xlabel('Intervalo entre arribos (minutos)', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Densidad de Probabilidad (escala log)', fontsize=14, fontweight='bold')
    ax2.set_title('FDP - Escala Logarítmica (detalle de cola)', 
                  fontsize=16, fontweight='bold', pad=20)
    ax2.set_yscale('log')
    ax2.legend(fontsize=11, loc='upper right', framealpha=0.9)
    ax2.grid(True, alpha=0.3, linestyle='--', which='both')
    ax2.set_xlim(0, 200)
    
    plt.tight_layout()
    
    # Guardar figura
    archivo_fig = OUTPUT_DIR / "fdp_intervalos_paper.png"
    plt.savefig(archivo_fig, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"   ✓ Figura guardada: {archivo_fig}")
    
    plt.close()

def generar_qq_plots(intervalos, distribuciones, mejor_dist):
    """Genera Q-Q plots para evaluar el ajuste de las distribuciones."""
    print(f"\n📊 Generando Q-Q plots...")
    
    n_dist = len(distribuciones)
    if n_dist == 0:
        return
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 14))
    axes = axes.flatten()
    
    for idx, dist_info in enumerate(distribuciones):
        if idx >= 4:
            break
        
        ax = axes[idx]
        
        try:
            if dist_info['nombre'] == 'Exponencial':
                stats.probplot(intervalos, dist=stats.expon, 
                              sparams=(0, dist_info['params']['scale']), plot=ax)
            elif dist_info['nombre'] == 'Gamma':
                stats.probplot(intervalos, dist=stats.gamma, 
                              sparams=(dist_info['params']['a'], 0, 
                                      dist_info['params']['scale']), plot=ax)
            elif dist_info['nombre'] == 'Weibull':
                stats.probplot(intervalos, dist=stats.weibull_min, 
                              sparams=(dist_info['params']['c'], 0, 
                                      dist_info['params']['scale']), plot=ax)
            elif dist_info['nombre'] == 'Lognormal':
                stats.probplot(intervalos, dist=stats.lognorm, 
                              sparams=(dist_info['params']['s'], 0, 
                                      dist_info['params']['scale']), plot=ax)
            else:
                continue
            
            titulo = f"Q-Q Plot: {dist_info['nombre']}"
            if dist_info['nombre'] == mejor_dist['nombre']:
                titulo += " (Mejor ajuste)"
            
            ax.set_title(titulo, fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3, linestyle='--')
        except Exception as e:
            ax.text(0.5, 0.5, f'Error: {str(e)}', ha='center', va='center')
            ax.set_title(f'Q-Q Plot: {dist_info["nombre"]}', fontsize=14)
    
    # Ocultar ejes no usados
    for idx in range(len(distribuciones), 4):
        axes[idx].axis('off')
    
    plt.tight_layout()
    
    # Guardar figura
    archivo_fig = OUTPUT_DIR / "qq_plots_paper.png"
    plt.savefig(archivo_fig, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"   ✓ Figura guardada: {archivo_fig}")
    
    plt.close()

def guardar_resultados(mejor_dist, todas_distribuciones):
    """Guarda los resultados del análisis."""
    archivo_resultados = OUTPUT_DIR / "mejor_distribucion.txt"
    
    with open(archivo_resultados, 'w', encoding='utf-8') as f:
        f.write("ANÁLISIS DE DISTRIBUCIONES - INTERVALOS ENTRE ARRIBOS\n")
        f.write("="*80 + "\n\n")
        
        f.write(f"MEJOR DISTRIBUCIÓN: {mejor_dist['nombre']}\n")
        f.write("-"*80 + "\n")
        f.write(f"AIC: {mejor_dist['aic']:.4f}\n")
        f.write(f"BIC: {mejor_dist['bic']:.4f}\n")
        f.write(f"KS Statistic: {mejor_dist['ks_stat']:.6f}\n")
        f.write(f"KS p-value: {mejor_dist['ks_pvalue']:.6f}\n")
        f.write(f"Log-Likelihood: {mejor_dist['log_likelihood']:.4f}\n")
        f.write(f"\nParámetros:\n")
        for key, value in mejor_dist['params'].items():
            f.write(f"  {key}: {value:.6f}\n")
        
        f.write(f"\n\nCOMPARACIÓN DE TODAS LAS DISTRIBUCIONES\n")
        f.write("="*80 + "\n")
        f.write(f"{'Distribución':<15} {'AIC':<15} {'BIC':<15} {'KS Stat':<15} {'KS p-value':<15}\n")
        f.write("-"*80 + "\n")
        
        for dist in todas_distribuciones:
            f.write(f"{dist['nombre']:<15} {dist['aic']:<15.4f} {dist['bic']:<15.4f} "
                   f"{dist['ks_stat']:<15.6f} {dist['ks_pvalue']:<15.6f}\n")
    
    print(f"   ✓ Resultados guardados: {archivo_resultados}")

def main():
    """Función principal."""
    print("\n" + "="*80)
    print("ANÁLISIS DE DISTRIBUCIONES PARA FDP DE INTERVALOS ENTRE ARRIBOS")
    print("="*80)
    
    # Cargar intervalos
    intervalos = cargar_intervalos()
    if intervalos is None:
        return
    
    # Filtrar intervalos válidos
    intervalos_filtrados = filtrar_intervalos_validos(intervalos)
    
    if len(intervalos_filtrados) == 0:
        print("❌ ERROR: No hay intervalos válidos para analizar")
        return
    
    # Ajustar todas las distribuciones
    distribuciones = ajustar_todas_distribuciones(intervalos_filtrados)
    
    if len(distribuciones) == 0:
        print("⚠️  ADVERTENCIA: No se pudieron ajustar distribuciones")
        return
    
    # Encontrar la mejor distribución
    mejor_dist, todas_dist = encontrar_mejor_distribucion(distribuciones)
    
    if mejor_dist is None:
        print("❌ ERROR: No se pudo determinar la mejor distribución")
        return
    
    # Guardar resultados
    guardar_resultados(mejor_dist, todas_dist)
    
    # Generar visualizaciones
    generar_histograma_fdp(intervalos_filtrados, distribuciones, mejor_dist)
    generar_qq_plots(intervalos_filtrados, distribuciones, mejor_dist)
    
    print(f"\n{'='*80}")
    print("✓ PROCESO COMPLETADO")
    print(f"{'='*80}\n")
    print(f"📁 Resultados guardados en: {OUTPUT_DIR}")
    print(f"   - mejor_distribucion.txt: Análisis completo")
    print(f"   - fdp_intervalos_paper.png: Histograma de FDP")
    print(f"   - qq_plots_paper.png: Q-Q plots de ajuste")

if __name__ == "__main__":
    main()

