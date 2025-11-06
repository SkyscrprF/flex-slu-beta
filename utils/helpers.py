
import numpy as np

def steel_stress(x, d, d_sup, fyd):
    Es = 210000.0
    eps_cu = 0.0035
    eps_y = fyd / Es if Es!=0 else 0.0

    if x <= 0:
        return {'epsilon_inf':0.0, 'epsilon_sup':0.0, 'sigma_inf':0.0, 'sigma_sup':0.0, 'yield_inf':False, 'yield_sup':False}

    eps_inf = eps_cu * (d - x) / x
    eps_sup = eps_cu * (x - d_sup) / x if x > d_sup else 0.0

    sigma_inf = min(fyd, Es * eps_inf)
    sigma_sup = min(fyd, Es * eps_sup)

    return {
        'epsilon_inf': eps_inf,
        'epsilon_sup': eps_sup,
        'sigma_inf': sigma_inf,
        'sigma_sup': sigma_sup,
        'yield_inf': eps_inf >= eps_y,
        'yield_sup': eps_sup >= eps_y
    }

def find_neutral_axis(B, As_inf, As_sup, fcd, fyd, d, d_sup):
    Es = 210000.0
    eps_cu = 0.0035
    a = 0.8 * B * fcd
    b = As_sup * Es * eps_cu - As_inf * fyd
    c = -As_sup * Es * eps_cu * d_sup

    disc = b**2 - 4 * a * c
    if disc < 0:
        return 0.2 * d

    x1 = (-b + np.sqrt(disc)) / (2 * a)
    x2 = (-b - np.sqrt(disc)) / (2 * a)
    for x in (x1, x2):
        if d_sup < x < d:
            return x
    return 0.2 * d

def validate_section(B, H, c):
    if B <= 0 or H <= 0:
        return False, "Errore: dimensioni non valide."
    if H - c <= c:
        return False, "Errore: l'altezza utile deve essere maggiore del copriferro superiore."
    return True, ""
