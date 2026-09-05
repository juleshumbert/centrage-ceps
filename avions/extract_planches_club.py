"""Extrait des notebooks de planches (reference/notebooks/) les valeurs masse et centrage
utilisees par le club, vers avions/<type>/planches_club.json.

Rien n'est recopie a la main : les cellules 0 a 5 des notebooks sont executees (comme dans
heuristique_remplissage/caravan_model.py) et les constantes de la cellule de configuration
sont lues par expression reguliere. Relancer apres tout rafraichissement de reference/notebooks/.

    python3 avions/extract_planches_club.py
"""
import json
import re
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
NB_DIR = ROOT / 'reference' / 'notebooks'
sys.path.insert(0, str(ROOT / 'heuristique_remplissage'))

LBS2KG = 2.20462
GAL2L = 3.78541


def load(name):
    nb = json.loads((NB_DIR / name).read_text())
    cells = [''.join(c['source']) for c in nb['cells']]
    ns = {}
    for src in cells[:6]:
        exec(src, ns)
    consts = {}
    for src in cells:
        for line in src.splitlines():
            m = re.match(r'\s*(EW_LBS|EW_KG|EW_MOMENT|MTOW_LBS|MTOW_KG|DATUM_LINE|MAC|'
                         r'TARGET_CG_IN|TARGET_CG_M|IMMAT|FUEL_PER_ROTATION|FUEL_RESERVE)\s*=\s*([^#]+)', line)
            if m:
                try:   # la derniere affectation litterale gagne (cellule de configuration)
                    consts[m.group(1)] = eval(m.group(2).strip(), {})
                except NameError:
                    pass
    return ns, consts


def fuel_table_from_source(src):
    """Lit le tableau `data = np.array([...])` de compute_moment (gal, masse, moment)."""
    block = re.search(r'data = np\.array\(\[(.*?)\]\)', src, re.S).group(1)
    rows = re.findall(r'\[([^\]]+)\]', block)
    return [[float(v) for v in r.split(',')] for r in rows]


def caravan():
    ns_bk, c_bk = load('planche_c208b_A.ipynb')
    _, c_la = load('planche_c208b_B.ipynb')
    import caravan_model as cm   # relit le notebook BK, meme geometrie
    src1 = ''.join(json.loads((NB_DIR / 'planche_c208b_A.ipynb').read_text())['cells'][1]['source'])
    fuel = fuel_table_from_source(src1)
    fuel_rows = [{'gal': g, 'lb': w, 'moment_1000': m, 'arm_in': round(m * 1000 / w, 2)} for g, w, m in fuel]
    zones = ns_bk['get_slots_bk']()[3]
    mtow = c_bk['MTOW_LBS']
    return {
        'aircraft': 'Cessna 208B Grand Caravan',
        'source': 'reference/notebooks/planche_c208b_A.ipynb et _LA.ipynb (planches club CEPS Ariege)',
        'units': {'weight': 'lb', 'arm': 'in', 'moment': 'lb.in/1000'},
        'datum': 'datum POH Cessna 208B (100 in en avant de la face avant de la cloison pare-feu, a confirmer dans avions/c208b/notes.md)',
        'mac': {'lemac_in': c_bk['DATUM_LINE'], 'length_in': c_bk['MAC'],
                'formula': '%MAC = (CG_in - lemac_in) / length_in * 100'},
        'limits': {'mtow_lb': mtow, 'target_cg_in': c_bk['TARGET_CG_IN']},
        'registrations': {
            c_bk['IMMAT']: {'ew_lb': c_bk['EW_LBS'], 'ew_moment_1000': c_bk['EW_MOMENT'],
                            'ew_cg_in': round(c_bk['EW_MOMENT'] * 1000 / c_bk['EW_LBS'], 2)},
            c_la['IMMAT']: {'ew_lb': c_la['EW_LBS'], 'ew_moment_1000': c_la['EW_MOMENT'],
                            'ew_cg_in': round(c_la['EW_MOMENT'] * 1000 / c_la['EW_LBS'], 2)},
        },
        'envelopes': [{
            'name': 'planches club (limite avant lineaire par morceaux, limite arriere constante)',
            'vertices': [[float(w), float(a)] for w, a in
                         [(0, 179.6), (5500, 179.6), (8000, 193.37), (mtow, 199.15), (mtow, 204.35), (0, 204.35)]],
            'note': 'le sommet a masse 0 vaut EW_LBS dans le notebook (bord bas du trace), la limite ne depend pas de la masse sous 5500 lb',
            'forward_limit': {'weight_lb': [5500, 8000, mtow], 'arm_in': [179.6, 193.37, 199.15]},
            'aft_limit_in': 204.35,
        }],
        'stations': [{'name': 'pilote', 'arm_in': 135.5}] + [
            {'name': z['label'], 'x0_in': z['x0'], 'x1_in': z['x1'], 'arm_in': z['arm'], 'width_in': z['height']}
            for z in zones],
        'fixed_seats_n20': [{'idx': s.idx, 'arm_in': s.x, 'lateral_in': s.y, 'row': s.row} for s in cm.SLOTS],
        'fuel': {'capacity_usable_gal': 332, 'capacity_usable_lb': 2224, 'density_lb_per_gal': 6.7,
                 'per_rotation_lb': c_bk['FUEL_PER_ROTATION'], 'reserve_lb': c_bk['FUEL_RESERVE'],
                 'table': fuel_rows},
        'forfaits_kg': {'para_militaire': 90, 'para_civil': 80, 'pilote_militaire': 80, 'pilote_civil': 86},
    }


def pilatus():
    ns, c_pil = load('planche_pc6_A.ipynb')
    _, c_yry = load('planche_pc6_B.ipynb')
    src1 = ''.join(json.loads((NB_DIR / 'planche_pc6_A.ipynb').read_text())['cells'][1]['source'])
    fuel = fuel_table_from_source(src1)
    fuel_rows = [{'gal': g, 'l': round(g * GAL2L, 1), 'kg': w, 'moment_kgm': m,
                  'arm_m': round(m / w, 3) if w else None} for g, w, m in fuel]
    top, bot = ns['get_slots_pil']()
    mtow = c_pil['MTOW_KG']
    return {
        'aircraft': 'Pilatus PC-6/B2-H4 Turbo Porter',
        'source': 'reference/notebooks/planche_pc6_A.ipynb et _yry.ipynb (planches club CEPS Ariege)',
        'units': {'weight': 'kg', 'arm': 'm', 'moment': 'kg.m'},
        'datum': 'datum AFM Pilatus (a confirmer dans avions/pc6-b2h4/notes.md)',
        'mac': {'lemac_m': c_pil['DATUM_LINE'], 'length_m': c_pil['MAC'],
                'formula': '%MAC = (CG_m - lemac_m) / length_m * 100'},
        'limits': {'mtow_kg': mtow, 'target_cg_m': c_pil['TARGET_CG_M']},
        'registrations': {
            c_pil['IMMAT']: {'ew_kg': c_pil['EW_KG'], 'ew_moment_kgm': c_pil['EW_MOMENT'],
                             'ew_cg_m': round(c_pil['EW_MOMENT'] / c_pil['EW_KG'], 3)},
            c_yry['IMMAT']: {'ew_kg': c_yry['EW_KG'], 'ew_moment_kgm': c_yry['EW_MOMENT'],
                             'ew_cg_m': round(c_yry['EW_MOMENT'] / c_yry['EW_KG'], 3)},
        },
        'envelopes': [{
            'name': 'planches club',
            'vertices': [[float(w), float(a)] for w, a in
                         [(0, 3.209), (1450, 3.209), (mtow, 3.608), (mtow, 3.722), (0, 3.722)]],
            'note': 'le sommet a masse 0 vaut EW_KG dans le notebook (bord bas du trace)',
            'forward_limit': {'weight_kg': [1450, mtow], 'arm_m': [3.209, 3.608]},
            'aft_limit_m': 3.722,
        }],
        'stations': [{'name': 'pilote', 'arm_m': 3.05}],
        'fixed_seats': {'rangee_haute_m': [round(x, 3) for x in top], 'rangee_basse_m': [round(x, 3) for x in bot]},
        'fuel': {'capacity_l': 640, 'per_rotation_l': c_pil['FUEL_PER_ROTATION'], 'reserve_l': c_pil['FUEL_RESERVE'],
                 'table': fuel_rows},
        'forfaits_kg': {'para_militaire': 90, 'para_civil': 80, 'pilote_militaire': 80, 'pilote_civil': 86},
    }


if __name__ == '__main__':
    for sub, data in [('c208b', caravan()), ('pc6-b2h4', pilatus())]:
        out = ROOT / 'avions' / sub / 'planches_club.json'
        out.write_text(json.dumps(data, indent=1, ensure_ascii=False) + '\n')
        print('ecrit', out.relative_to(ROOT))
