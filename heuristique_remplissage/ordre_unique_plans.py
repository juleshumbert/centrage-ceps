"""Consolide les meilleurs ordres uniques trouves (ordre_unique.py, ordre_suiveur.py,
ordre_unique_final.py) : par domaine, garde celui de marge minimale la plus grande,
dessine les plans par avion et ecrit output/ordre_unique_retenu.json."""
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from scenarios import all_scenarios
from fast import Bench, XS
from ordre_unique import stats
from fiche_heuristique import draw_plan

OUT = Path(__file__).resolve().parent / 'output'

scs, _ = all_scenarios(seed=0, k_per_cell=6)
B = Bench(scs)
fuel = np.array([s.fuel_lbs for s in scs]); mean_kg = np.array([np.mean(s.weights_kg) for s in scs])
immat = np.array([s.immat for s in scs])
real = (fuel >= 320) & (mean_kg >= 70) & (mean_kg <= 110)
doms = {
    'C208B-A, realiste': real & (immat == 'C208B-A'),
    'C208B-B, realiste': real & (immat == 'C208B-B'),
    'deux avions, realiste': real,
    'deux avions, fuel <= 1900 et moy 75-105': real & (fuel <= 1900) & (mean_kg >= 75) & (mean_kg <= 105),
}
cands = {k: [] for k in doms}
ju = json.loads((OUT / 'ordre_unique.json').read_text())
for src, dst in [('realiste, C208B-A seul', 'C208B-A, realiste'), ('realiste, C208B-B seul', 'C208B-B, realiste'),
                 ('realiste (fuel >= 320, moy 70-110 kg)', 'deux avions, realiste'),
                 ('realiste + fuel <= 1900 + moy 75-105', 'deux avions, fuel <= 1900 et moy 75-105')]:
    cands[dst].append(ju[src]['ordre'])
js = json.loads((OUT / 'ordre_suiveur.json').read_text())
for src, dst in [('C208B-A, realiste', 'C208B-A, realiste'), ('C208B-B, realiste', 'C208B-B, realiste'),
                 ('deux avions, realiste', 'deux avions, realiste'),
                 ('deux avions, realiste + fuel <= 1900 + moy 75-105', 'deux avions, fuel <= 1900 et moy 75-105')]:
    cands[dst] += [js[src]['suiveur']['ordre'], js[src]['recuit']['ordre']]
jf = json.loads((OUT / 'ordre_unique_final.json').read_text())
for k in doms:
    cands[k].append(jf[k]['ordre'])

retenu = {}
for name, mask in doms.items():
    best = None
    for o in cands[name]:
        e, n, mn, p1 = stats(B, o, mask)
        if best is None or (e, -mn) < (best[1], -best[2]):
            best = (o, e, mn, p1, n)
    o, e, mn, p1, n = best
    e_a, n_a, mn_a, _ = stats(B, o, np.ones(len(scs), bool))
    print(f'{name:42s} {e} echecs / {n}, marge min {mn:+.2f} in, 1er centile {p1:.2f} ; complet {e_a}/{n_a}')
    print('   ' + ' '.join(f'{XS[i]:.0f}' for i in o))
    retenu[name] = dict(ordre=[int(i) for i in o], bras=[float(XS[i]) for i in o], echecs=e, n=n,
                        marge_min=mn, centile1=p1, echecs_complet=e_a)

fig, axes = plt.subplots(2, 1, figsize=(10, 6.2))
for ax, name in zip(axes, ('C208B-A, realiste', 'C208B-B, realiste')):
    r = retenu[name]
    draw_plan(ax, r['ordre'], f"{name.split(',')[0]} : ordre unique valable pour carburant >= 320 lbs et masse moyenne 70 a 110 kg "
                              f"({r['echecs']} echec / {r['n']}, marge min {r['marge_min']:+.2f} in)")
fig.suptitle('Un seul ordre par avion (para le plus lourd sur la place 1) : possible, mais marges minces', fontsize=11, fontweight='bold')
fig.tight_layout(); fig.savefig(OUT / 'fig_ordre_unique_par_avion.png', dpi=160); plt.close(fig)
(OUT / 'ordre_unique_retenu.json').write_text(json.dumps(retenu, indent=1))
