
import numpy as np

def calc_shear_capacity(B, d, fcd, fyd, phi_staffe, n_bracci, passo_staffe, V_Ed, z=None):
    """Calcolo della resistenza a taglio VRd"""
    nu = 0.5
    alpha_c = 1.0
    s = passo_staffe * 10  # cm → mm
    z = z or 0.9 * d
    Asw = n_bracci * np.pi * (phi_staffe / 2)**2

    # 1. Calcolo percentuale meccanica armatura trasversale
    omega_sw = (Asw * fyd) / (B * s * fcd + 1e-12)

    denom = nu * alpha_c / omega_sw - 1

    if denom <= 0:
        return {'V_Rd': 0.0, 'theta_deg': 0.0, 'caso': 'Armatura insufficiente', 'verifica_ok': False, 'omega_sw': omega_sw, 'Asw': Asw, 'passo': s, 'rapporto_taglio': 0.0}

    cot_theta_opt = np.sqrt(denom)
    theta_deg = np.degrees(np.arctan(1 / cot_theta_opt))

    if 1.0 <= cot_theta_opt <= 2.5:
        V_Rcd = (B * d * alpha_c * nu * fcd) / (cot_theta_opt + 1 / cot_theta_opt)
        caso = f"Ottimale (θ = {theta_deg:.1f}°)"
    elif cot_theta_opt > 2.5:
        cot_theta_opt = 2.5
        theta_deg = np.degrees(np.arctan(1 / cot_theta_opt))
        V_Rcd = (B * d * alpha_c * nu * fcd) / (cot_theta_opt + 1 / cot_theta_opt)
        caso = f"Crisi staffe (θ = {theta_deg:.1f}°)"
    else:
        cot_theta_opt = 1.0
        V_Rcd = (Asw * fyd * d * cot_theta_opt) / s
        caso = "Crisi bielle compresse (θ = 45°)"

    V_Rd = V_Rcd / 1000.0  # N -> kN

    return {
        'V_Rd': V_Rd,
        'theta_deg': theta_deg,
        'caso': caso,
        'verifica_ok': V_Rd >= V_Ed,
        'omega_sw': omega_sw,
        'Asw': Asw,
        'passo': s,
        'rapporto_taglio': V_Rd / V_Ed if V_Ed>0 else float('inf')
    }
