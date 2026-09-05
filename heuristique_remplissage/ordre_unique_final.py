"""Ordre unique par domaine : recherche de la marge maximale, plans et JSON.

Domaines :
  - C208B-A seul, domaine realiste (fuel >= 320 lbs, masse moyenne 70 a 110 kg) ;
  - C208B-B seul, idem ;
  - les deux avions, realiste (impossible a 100 %, on montre ce qui reste) ;
  - les deux avions, fuel <= 1900 lbs et masse moyenne 75 a 105 kg.
"""
import json
from collections import Counter
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from scenarios import all_scenarios
from fast import Bench, XS
from caravan_model import order_by_pivot
from ordre_unique import stats
from fiche_heuristique import draw_plan

OUT = Path(__file__).resolve().parent / 'output'


def anneal_maxmargin(B, start, iters, seed, target):
    rng = np.random.default_rng(seed)

    def cost(o):
        m = B.moments(o, True)
        marg = np.minimum(m - B.r_lo, B.r_hi - m) * 1000 / B.mass
        marg = marg[B.feasible]
        short = np.maximum(target - marg, 0)
        return int((marg < 0).sum()) * 10 + float(short.sum()) - 0.05 * float(marg.min())

    cur = list(start); c_cur = cost(cur); best, c_best = list(cur), c_cur
    t0, t1 = 5.0, 0.01
    for it in range(iters):
        T = t0 * (t1 / t0) ** (it / iters)
        i, j = rng.choice(20, 2, replace=False)
        cand = list(cur)
        if rng.random() < 0.5:
            cand[i], cand[j] = cand[j], cand[i]
        else:
            v = cand.pop(i); cand.insert(j, v)
        c = cost(cand)
        if c <= c_cur or rng.random() < np.exp((c_cur - c) / T):
            cur, c_cur = cand, c
            if c < c_best:
                best, c_best = list(cand), c
    return best


def main():
    scs, _ = all_scenarios(seed=0, k_per_cell=6)
    B = Bench(scs)
    feas = B.feasible
    fuel = np.array([s.fuel_lbs for s in scs]); mean_kg = np.array([np.mean(s.weights_kg) for s in scs])
    immat = np.array([s.immat for s in scs])
    real = (fuel >= 320) & (mean_kg >= 70) & (mean_kg <= 110)
    doms = {
        'C208B-A, realiste': real & (immat == 'C208B-A'),
        'C208B-B, realiste': real & (immat == 'C208B-B'),
        'deux avions, realiste': real,
        'deux avions, fuel <= 1900 et moy 75-105': real & (fuel <= 1900) & (mean_kg >= 75) & (mean_kg <= 105),
    }
    starts = {
        'C208B-A, realiste': [int(i) for i in json.loads((OUT / 'ordre_suiveur.json').read_text())['C208B-A, realiste']['recuit']['ordre']],
        'C208B-B, realiste': [int(i) for i in json.loads((OUT / 'ordre_suiveur.json').read_text())['C208B-B, realiste']['recuit']['ordre']],
    }
    results = {}
    for name, mask in doms.items():
        Bm = Bench([s for s, ok in zip(scs, mask) if ok])
        best = None
        for seed, start in ((1, starts.get(name, order_by_pivot(232.5))), (2, order_by_pivot(235.0))):
            o = anneal_maxmargin(Bm, start, 15000, seed, target=1.5)
            e, n, mn, p1 = stats(B, o, mask)
            if best is None or (e, -mn) < (best[1], -best[2]):
                best = (o, e, mn, p1, n)
        o, e, mn, p1, n = best
        e_a, n_a, mn_a, _ = stats(B, o, np.ones(len(scs), bool))
        print(f'== {name} : {e} echecs / {n}, marge min {mn:+.2f} in, 1er centile {p1:.2f} ; sur le domaine complet {e_a}/{n_a} (marge min {mn_a:+.2f})')
        print('   ordre (bras) : ' + ' '.join(f'{XS[i]:.0f}' for i in o))
        print('   moyenne des k premieres : ' + ' '.join(f'{np.mean(XS[o[:k]]):.0f}' for k in range(1, 21)))
        m = B.moments(o, True); marg = np.minimum(m - B.r_lo, B.r_hi - m) * 1000 / B.mass
        idx = np.where((marg < 0) & feas & mask)[0]
        if len(idx):
            print('   echecs restants : N', sorted(Counter(scs[i].n for i in idx).items()),
                  '| avion', dict(Counter(scs[i].immat for i in idx)),
                  '| fuel', sorted(Counter(int(round(scs[i].fuel_lbs, -2)) for i in idx).items()),
                  '| moy kg', sorted(Counter(int(round(np.mean(scs[i].weights_kg), -1)) for i in idx).items()))
        idx_a = np.where((marg < 0) & feas & ~mask)[0]
        if len(idx_a):
            print('   hors domaine, ce qui casse : fuel', sorted(Counter(int(round(scs[i].fuel_lbs, -2)) for i in idx_a).items())[:6], '...',
                  '| moy kg', sorted(Counter(int(round(np.mean(scs[i].weights_kg), -1)) for i in idx_a).items()))
        results[name] = dict(ordre=[int(i) for i in o], bras=[float(XS[i]) for i in o], echecs=e, n=n,
                             marge_min=mn, centile1=p1, echecs_complet=e_a, marge_min_complet=mn_a)

    # plans des deux ordres par avion
    fig, axes = plt.subplots(2, 1, figsize=(10, 6.2))
    for ax, name in zip(axes, ('C208B-A, realiste', 'C208B-B, realiste')):
        r = results[name]
        draw_plan(ax, r['ordre'], f"Ordre unique {name.split(',')[0]} (carburant >= 320 lbs, masse moyenne 70 a 110 kg) : "
                                  f"{r['echecs']} echec / {r['n']}, marge min {r['marge_min']:+.2f} in")
    fig.suptitle('Un seul ordre par avion : le para le plus lourd sur la place 1', fontsize=11, fontweight='bold')
    fig.tight_layout(); fig.savefig(OUT / 'fig_ordre_unique_par_avion.png', dpi=160); plt.close(fig)
    (OUT / 'ordre_unique_final.json').write_text(json.dumps(results, indent=1))


if __name__ == '__main__':
    main()
