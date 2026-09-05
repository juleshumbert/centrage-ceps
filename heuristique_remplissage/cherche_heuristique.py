"""Recherche d'une heuristique qui marche bien.

Critere : pire affectation des masses sur les places utilisees (robuste a l'ordre
d'embarquement), marge cible 0.5 in de CG, sur l'espace realiste (fuel >= 320 lbs,
masse moyenne des paras 70 a 110 kg, pilote 65 a 110 kg). Evaluation ensuite sur
l'espace complet.

Variables de bascule comparees : aucune, carburant (2 ou 3 regimes), masse totale
des paras (2 ou 3 regimes), carburant x masse (4 regimes).
Deux familles d'ordres : libre (permutation des 20 places) ou par paires
(place droite et gauche d'un meme rang remplies a la suite, lisible en cabine).
"""
import json
import sys
from pathlib import Path

import numpy as np

from caravan_model import SLOTS, order_by_pivot, LBS2KG
from scenarios import all_scenarios
from fast import BenchRobust

OUT = Path(__file__).resolve().parent / 'output'
TARGET_MARGIN = 0.5   # in de CG (0.75 %MAC)

# unites "par paires" : (droite, gauche) au meme bras, centres seuls, copilote
PAIRS = [(1, 13), (2, 14), (3, 15), (4, 16), (5, 17), (6, 18), (7, 19)]
UNITS = [list(p) for p in PAIRS] + [[8], [9], [10], [11], [12], [0]]


def expand(unit_order):
    return [i for u in unit_order for i in UNITS[u]]


def anneal(B, start, iters, seed=1, paired=False):
    rng = np.random.default_rng(seed)
    cur = list(start)
    k = len(cur)
    f = (lambda o: B.cost_worst(expand(o), TARGET_MARGIN)) if paired else \
        (lambda o: B.cost_worst(o, TARGET_MARGIN))
    c_cur = f(cur)
    best, c_best = list(cur), c_cur
    t0, t1 = 2.0, 0.01
    for it in range(iters):
        T = t0 * (t1 / t0) ** (it / iters)
        i, j = rng.choice(k, 2, replace=False)
        cand = list(cur)
        if rng.random() < 0.5:
            cand[i], cand[j] = cand[j], cand[i]
        else:                       # insertion
            v = cand.pop(i)
            cand.insert(j, v)
        c = f(cand)
        if c <= c_cur or rng.random() < np.exp((c_cur - c) / T):
            cur, c_cur = cand, c
            if c < c_best:
                best, c_best = list(cand), c
    return best, c_best


def report(B, order, label):
    st = B.status_worst(order)
    marg = B.margin_worst(order)
    nf = int(B.feasible.sum())
    bad = int(((st != 0) & B.feasible).sum())
    under = int(((marg < TARGET_MARGIN) & B.feasible).sum())
    print(f'  {label:52s} echecs {bad:5d}/{nf} ({100*bad/nf:5.2f} %)  '
          f'sous marge {under:5d}  marge min {marg[B.feasible].min():+6.2f} in')
    return bad, under


def regime_masks(scs, kind, thresholds):
    if kind == 'fuel':
        v = np.array([s.fuel_lbs for s in scs])
    elif kind == 'wp':
        v = np.array([sum(s.weights_kg) for s in scs])
    else:
        raise ValueError(kind)
    edges = [-np.inf] + list(thresholds) + [np.inf]
    return [(v >= a) & (v < b) for a, b in zip(edges[:-1], edges[1:])]


def main(iters=6000):
    scs_all, _ = all_scenarios(seed=0, k_per_cell=6)
    real = [s for s in scs_all if s.fuel_lbs >= 320 and 70 <= np.mean(s.weights_kg) <= 110]
    print(f'{len(scs_all)} scenarios complets, {len(real)} realistes\n')
    B_all = BenchRobust(scs_all)
    B_real = BenchRobust(real)

    print('Reference : pivots fixes, critere pire affectation, espace realiste')
    for p in (202, 225, 230, 235):
        report(B_real, order_by_pivot(p), f'pivot {p}')
    print()

    configs = [
        ('aucune', None, ()),
        ('fuel 2 regimes', 'fuel', (1200,)),
        ('fuel 2 regimes', 'fuel', (1500,)),
        ('fuel 3 regimes', 'fuel', (1000, 1700)),
        ('masse paras 2 regimes', 'wp', (1100,)),
        ('masse paras 2 regimes', 'wp', (1300,)),
        ('masse paras 3 regimes', 'wp', (900, 1300)),
        ('masse paras 3 regimes', 'wp', (1000, 1400)),
    ]
    results = {}
    for name, kind, thr in configs:
        for paired in (False, True):
            label = f'{name} {thr} {"paires" if paired else "libre"}'
            masks = [np.ones(len(real), bool)] if kind is None else regime_masks(real, kind, thr)
            masks_all = [np.ones(len(scs_all), bool)] if kind is None else regime_masks(scs_all, kind, thr)
            orders = []
            tot_bad = tot_under = 0
            tot_bad_all = 0
            print(f'== {label}')
            for r, (m, m_all) in enumerate(zip(masks, masks_all)):
                Br = BenchRobust([s for s, ok in zip(real, m) if ok])
                Ba = BenchRobust([s for s, ok in zip(scs_all, m_all) if ok])
                if paired:
                    start = list(range(13))
                    # depart : unites triees par distance a 235
                    start.sort(key=lambda u: abs(SLOTS[UNITS[u][0]].x - 235))
                    o, _ = anneal(Br, start, iters, paired=True)
                    order = expand(o)
                else:
                    o, _ = anneal(Br, order_by_pivot(235.0), iters)
                    order = o
                b, u = report(Br, order, f'  regime {r} realiste ({int(Br.feasible.sum())} sc.)')
                b_all, _ = report(Ba, order, f'  regime {r} complet  ({int(Ba.feasible.sum())} sc.)')
                tot_bad += b; tot_under += u; tot_bad_all += b_all
                orders.append([int(i) for i in order])
            print(f'   ==> realiste : {tot_bad} echecs, {tot_under} sous marge ; complet : {tot_bad_all} echecs')
            results[label] = dict(kind=kind, thresholds=list(thr), paired=paired, orders=orders,
                                  echecs_realiste=tot_bad, sous_marge_realiste=tot_under,
                                  echecs_complet=tot_bad_all)
    (OUT / 'cherche_heuristique.json').write_text(json.dumps(results, indent=1))


if __name__ == '__main__':
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 6000)
