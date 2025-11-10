
import numpy as np
from utils.helpers import find_neutral_axis, steel_stress

def calc_flexural_capacity(B, H, c, n_inf, phi_inf, n_sup, phi_sup,
                           fck, fyk, M_Ed, gamma_c=1.5, gamma_s=1.15,
                           alpha_cc=0.85):
    """Calcolo completo della resistenza a flessione MRd"""
    fcd = alpha_cc * fck / gamma_c
    fyd = fyk / gamma_s
    d = H - c
    d_sup = c

    As_inf = n_inf * np.pi * (phi_inf / 2)**2
    As_sup = n_sup * np.pi * (phi_sup / 2)**2

    x = find_neutral_axis(B, As_inf, As_sup, fcd, fyd, d, d_sup)
    steel = steel_stress(x, d, d_sup, fyd)

    Cc = 0.8 * B * x * fcd
    Cs = As_sup * steel['sigma_sup']
    Ts = As_inf * steel['sigma_inf']
    z = d - 0.4 * x
    M_Rd = (Cc * z + Cs * (d - d_sup)) / 1e6  # kNm

    # optional: also provide internal lever arm for shear module
    z_concrete = z

    return {
        'fcd': fcd, 'fyd': fyd, 'd': d, 'x': x,
        'As_inf': As_inf, 'As_sup': As_sup,
        'M_Rd': M_Rd,
        'z_concrete': z_concrete,
        'verifica_ok': M_Rd >= M_Ed,
        'rapporto_sicurezza': M_Rd / M_Ed if M_Ed > 0 else float('inf'),
        **{
            'sigma_s_inf': steel['sigma_inf'],
            'sigma_s_sup': steel['sigma_sup'],
            'epsilon_s_inf': steel['epsilon_inf'],
            'epsilon_s_sup': steel['epsilon_sup'],
            'steel_yielding': {'teso': steel['yield_inf'], 'compresso': steel['yield_sup']}
        }
    }
