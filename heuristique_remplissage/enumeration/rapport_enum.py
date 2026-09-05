"""Lecture de output.json (enumerateur Rust) : tableaux de comptage et verification
des meilleurs ordres avec le banc Python (masses uniformes ET individuelles).

Usage : python3 rapport_enum.py  (apres prepare.py, enumere)
"""
import json
import math
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from caravan_model import SLOTS, LBS2KG
from scenarios import all_scenarios
from fast import Bench
from ordre_origine import legacy_slots, original_order_arms, FILLING_ORDER

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / 'output'
res = json.loads((HERE / 'output.json').read_text())
BY = {r['name']: r for r in res}
TOTAL_SUBSETS = 2 ** 20 - 1
TOTAL_ORDERS = math.factorial(20)
ARMS = {'legacy': legacy_slots('C208B-A'), 'n20': [s.x for s in SLOTS]}

lines = ['# Enumeration exhaustive des configurations (Rust, enumeration/)\n',
         f'Places : 20, donc {TOTAL_SUBSETS:,} configurations non vides (sous-ensembles), '
         f'C(20,N) par N (max C(20,10) = 184 756), et 20! = {TOTAL_ORDERS:.3e} ordres de remplissage possibles. '
         'Masses uniformes (forfait ou poids moyen de la rotation) : une configuration = un sous-ensemble '
         'de places, un ordre = une chaine de sous-ensembles emboites.\n']


def fmt_n(v):
    return ' '.join(f'{x}' for x in v)


def row(name):
    r = BY[name]
    n_orders = int(r['orders_per_n'][19])
    nmax = r['n_max']
    reach20 = r['reach_per_n'][19]
    return r, n_orders, nmax, reach20


print(f'{TOTAL_SUBSETS:,} configurations non vides, {TOTAL_ORDERS:.3e} ordres possibles\n')
hdr = f'{"places":7s} {"avion":11s} {"domaine":46s} {"critere":18s} {"valides N=10":>12s} {"valides N=20":>12s} {"N max":>5s} {"ordres valides":>16s} {"part":>9s} {"marge min (in bras moyen)":>26s}'
print(hdr)
lines.append('| places | avion | domaine | critere | configs valides N=10 (sur 184 756) | N max atteignable | ordres valides (sur 2,43e18) | marge min du meilleur ordre (in de bras moyen) |')
lines.append('|---|---|---|---|---|---|---|---|')
for r in res:
    sl, av, dom, crit = [t.strip() for t in r['name'].split('|')]
    n_orders = int(r['orders_per_n'][19]) if r['n_max'] == 20 else 0
    nmax = r['n_max']
    v10 = r['valid_per_n'][9]
    bm = r['best_margins']
    mm = min(bm) if bm else float('nan')
    part = n_orders / TOTAL_ORDERS
    print(f'{sl:7s} {av:11s} {dom:46s} {crit:18s} {v10:12d} {r["valid_per_n"][19]:12d} {nmax:5d} {n_orders:16.3e} {part:9.2e} {mm:26.2f}')
    lines.append(f'| {sl} | {av} | {dom} | {crit} | {v10:,} | {nmax} | {n_orders:.2e} ({100*part:.4f} %) | {mm:+.2f} |')

# --- verification des meilleurs ordres avec le banc Python (scenarios uniformes + individuels)
print('\nVerification au banc Python (masses uniformes de la grille + tirages individuels) :')
scs, _ = all_scenarios(seed=0, k_per_cell=6)
B = Bench(scs)
feas = B.feasible
fuel = np.array([s.fuel_lbs for s in scs]); mean_kg = np.array([np.mean(s.weights_kg) for s in scs])
immat = np.array([s.immat for s in scs]); pil = np.array([s.pilot_kg for s in scs])
uniform = np.array([s.family.startswith('uniforme') for s in scs])


def margins_arms(order, arms_by_immat):
    """Marge CG (in) par scenario pour un ordre sur des bras dependant de l avion."""
    m = np.zeros(len(scs))
    for im, arms in arms_by_immat.items():
        sel = immat == im
        xs = np.array(arms)[np.asarray(order)]
        m[sel] = B.W_desc[sel] @ xs / 1000
    return np.minimum(m - B.r_lo, B.r_hi - m) * 1000 / B.mass


def arms_for(slotset):
    if slotset == 'legacy':
        return {'C208B-A': legacy_slots('C208B-A'), 'C208B-B': legacy_slots('C208B-B')}
    return {'C208B-A': ARMS['n20'], 'C208B-B': ARMS['n20']}


DOM_MASKS = {
    'forfait 90 kg, pilote 80': (mean_kg == 90) & uniform & (pil == 80),
    'forfait 80 kg, pilote 86': (mean_kg == 80) & uniform & (pil == 86),
    'moyen 70-110 kg, pilotes 80/86': (mean_kg >= 70) & (mean_kg <= 110) & np.isin(pil, [80, 86]),
    'moyen 60-120 kg, pilotes 80/86': np.isin(pil, [80, 86]),
    'moyen 70-110 kg, pilotes 65-110': (mean_kg >= 70) & (mean_kg <= 110),
    'moyen 70-110 kg, pilotes 80/86, fuel 320-1900': (mean_kg >= 70) & (mean_kg <= 110) & np.isin(pil, [80, 86]) & (fuel >= 320) & (fuel <= 1900),
    'moyen 75-105 kg, pilotes 80/86, fuel 320-1900': (mean_kg >= 75) & (mean_kg <= 105) & np.isin(pil, [80, 86]) & (fuel >= 320) & (fuel <= 1900),
}
lines.append('\n## Meilleurs ordres (marge minimale maximale) verifies au banc Python\n')
lines.append('| places | avion | domaine | ordre (bras in) | uniformes : echecs / marge min CG | avec masses individuelles : echecs / marge min |')
lines.append('|---|---|---|---|---|---|')
best_orders = {}
for r in res:
    sl, av, dom, crit = [t.strip() for t in r['name'].split('|')]
    if crit != 'enveloppe complete' or r['n_max'] < 20:
        continue
    order = r['best_order']
    arms = arms_for(sl)
    mg = margins_arms(order, arms)
    mask = DOM_MASKS[dom] & feas & (np.ones(len(scs), bool) if av == 'deux avions' else (immat == av))
    mu = mask & uniform
    e_u, mn_u = int((mg[mu] < 0).sum()), float(mg[mu].min()) if mu.any() else float('nan')
    e_a, mn_a = int((mg[mask] < 0).sum()), float(mg[mask].min())
    arms_txt = ' '.join(f'{arms["C208B-A"][i]:.0f}' for i in order)
    print(f'  {sl:6s} {av:11s} {dom:46s} uniformes {e_u:3d}/{int(mu.sum()):5d} (min {mn_u:+.2f})  individuelles {e_a:3d}/{int(mask.sum()):5d} (min {mn_a:+.2f})')
    lines.append(f'| {sl} | {av} | {dom} | {arms_txt} | {e_u} / {int(mu.sum())}, {mn_u:+.2f} in | {e_a} / {int(mask.sum())}, {mn_a:+.2f} in |')
    best_orders[r['name']] = dict(ordre=order, bras=[arms['C208B-A'][i] for i in order], echecs_uniformes=e_u,
                                  marge_min_uniformes=mn_u, echecs_individuelles=e_a, marge_min_individuelles=mn_a)

# --- l ordre d origine, pour comparaison, dans les memes termes
lines.append('\n## Ordre d origine (filling_order_bon) sur les memes domaines\n')
lines.append('| avion | domaine | uniformes : echecs / marge min CG |')
lines.append('|---|---|---|')
order_orig = [legacy_slots('C208B-A').index(x) if False else None for x in []]
x_list = legacy_slots('C208B-A')
order_orig = [FILLING_ORDER.index(rk) for rk in range(1, 21)]   # index de place (dans x_list) par rang
for av in ('C208B-A', 'C208B-B', 'deux avions'):
    for dom, dmask in DOM_MASKS.items():
        mg = margins_arms(order_orig, arms_for('legacy'))
        mask = dmask & feas & uniform & (np.ones(len(scs), bool) if av == 'deux avions' else (immat == av))
        lines.append(f'| {av} | {dom} | {int((mg[mask] < 0).sum())} / {int(mask.sum())}, {mg[mask].min():+.2f} in |')

(OUT / 'enumeration.md').write_text('\n'.join(lines) + '\n')
(OUT / 'enumeration_meilleurs_ordres.json').write_text(json.dumps(best_orders, indent=1))
print('\necrit output/enumeration.md et output/enumeration_meilleurs_ordres.json')
