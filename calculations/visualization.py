
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.lines import Line2D

def visualize_stress_block(B, H, x, c, fcd, fyd, n_bars_sup, n_bars_inf, phi_sup, phi_inf, results):
    fig, ax = plt.subplots(1,1, figsize=(8,6))

    # grid and stress map
    n_points_x = 50
    n_points_y = 50
    x_mesh = np.linspace(0, B, n_points_x)
    y_mesh = np.linspace(0, H, n_points_y)
    X, Y = np.meshgrid(x_mesh, y_mesh)
    stress_map = np.zeros_like(Y)

    y_compression_top = H
    y_compression_active = H - 0.8 * x
    mask_active_compression = (Y <= y_compression_top) & (Y >= y_compression_active)
    stress_map[mask_active_compression] = fcd

    im = ax.imshow(stress_map, extent=[0,B,0,H], vmin=0, vmax=fcd, cmap='Reds', alpha=0.7, origin='lower', aspect='equal')
    fig.colorbar(im, ax=ax, label='Tensione [MPa]', shrink=0.8)

    # section outline and neutral axis
    section_rect = patches.Rectangle((0,0), B, H, linewidth=1.5, edgecolor='black', facecolor='none')
    ax.add_patch(section_rect)
    ax.axhline(y=H-x, color='blue', linestyle='--', linewidth=2, label=f'Asse neutro (x = {x:.1f} mm)')

    sigma_s_inf = results.get('sigma_s_inf', 0.0)
    sigma_s_sup = results.get('sigma_s_sup', 0.0)
    is_inf_yielded = results.get('steel_yielding', {}).get('teso', False)
    is_sup_yielded = results.get('steel_yielding', {}).get('compresso', False)

    # draw reinforcement
    if n_bars_sup > 0:
        y_sup = H - c
        color_sup = 'darkred' if is_sup_yielded else 'orange'
        for i in range(int(n_bars_sup)):
            x_pos = (i+1)*B/(int(n_bars_sup)+1)
            circle_sup = patches.Circle((x_pos, y_sup), phi_sup/2, facecolor=color_sup, edgecolor='black', linewidth=1.2, alpha=0.9)
            ax.add_patch(circle_sup)

    if n_bars_inf > 0:
        y_inf = c
        color_inf = 'darkred' if is_inf_yielded else 'orange'
        for i in range(int(n_bars_inf)):
            x_pos = (i+1)*B/(int(n_bars_inf)+1)
            circle_inf = patches.Circle((x_pos, y_inf), phi_inf/2, facecolor=color_inf, edgecolor='black', linewidth=1.2, alpha=0.9)
            ax.add_patch(circle_inf)

    # annotations and legend
    if x>0:
        ax.annotate('', xy=(B+20,H), xytext=(B+20,H-x), arrowprops=dict(arrowstyle='<->', color='blue', lw=1.2))
        ax.text(B+40, H-x/2, f'x = {x:.1f} mm', rotation=90, ha='center', va='center', color='blue')

    info_text = f"Acciaio sup: {sigma_s_sup:.1f} MPa\nAcciaio inf: {sigma_s_inf:.1f} MPa\nCalcestruzzo: {fcd:.1f} MPa"
    fig.text(0.02, 0.95, info_text, verticalalignment='top', fontsize=9, bbox=dict(boxstyle='round,pad=0.4', facecolor='lightgray', alpha=0.8))

    legend_elements = [
        Line2D([0],[0], marker='o', color='w', markerfacecolor='darkred', markersize=8, label='Acciaio snervato'),
        Line2D([0],[0], marker='o', color='w', markerfacecolor='orange', markersize=8, label='Acciaio elastico'),
        Line2D([0],[0], color='blue', linestyle='--', label='Asse neutro')
    ]
    ax.legend(handles=legend_elements, bbox_to_anchor=(-0.15,0), loc='lower right')
    ax.set_xlim(-25, B+25)
    ax.set_ylim(-25, H+25)
    ax.set_xlabel('Larghezza [mm]')
    ax.set_ylabel('Altezza [mm]')
    ax.set_title('Stress Block')
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return fig

def visualize_strain_diagram(x, d, H, results):
    fig, ax = plt.subplots(1,1, figsize=(7,6))
    epsilon_s_inf = results.get('epsilon_s_inf', 0.0)
    epsilon_s_sup = - results.get('epsilon_s_sup', 0.0)
    c = H - d
    y_def = [H, H-c, H-x, H-d]
    epsilon_cu = -0.0035
    epsilon_yd = 0.0186
    epsilon_def = [epsilon_cu, epsilon_s_sup, 0, epsilon_s_inf]
    ax.plot([e*1000 for e in epsilon_def], y_def, '-', color='red', linewidth=2)
    ax.axhline(y=H-x, color='blue', linestyle='--', linewidth=2, label='Asse neutro')
    ax.set_xlabel('Deformazione (‰)')
    ax.set_ylabel('Altezza [mm]')
    ax.set_title('Diagramma deformazioni')
    ax.grid(True)
    fig.tight_layout()
    return fig
