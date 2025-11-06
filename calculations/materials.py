
def get_concrete_properties(classe_cls):
    """Restituisce le proprietà del calcestruzzo per SLU"""
    concrete_props = {
        'C20/25': {'fck': 20, 'fctm': 2.2},
        'C25/30': {'fck': 25, 'fctm': 2.6},
        'C28/35': {'fck': 28, 'fctm': 2.9},
        'C30/37': {'fck': 30, 'fctm': 2.9},
        'C32/40': {'fck': 32, 'fctm': 3.2},
        'C35/45': {'fck': 35, 'fctm': 3.5},
        'C40/50': {'fck': 40, 'fctm': 3.5},
        'C45/55': {'fck': 45, 'fctm': 4.0},
        'C50/60': {'fck': 50, 'fctm': 4.1}
    }
    return concrete_props.get(classe_cls, concrete_props['C25/30'])
