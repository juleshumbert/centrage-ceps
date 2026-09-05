"""Heuristique pivot + lourds d'abord, avec pivot choisi par une petite table.

1. Deux familles d'ordres pour un pivot donne :
   - distance : places par distance croissante au pivot (proposition initiale) ;
   - equilibre : a chaque etape, la place inutilisee qui garde la moyenne des
     bras utilises la plus proche du pivot (la moyenne des k premieres places
     ne zigzague plus).
2. Pour chaque scenario et chaque pivot candidat : OK ou pas (lourds d'abord),
   avec marge.
3. Tables de decision : pivot choisi par classe de carburant x classe de masse
   totale des paras (ou x classe de N). On retient par case le pivot qui couvre
   le plus de scenarios, et on mesure la couverture globale.
"""
import json
import sys
from pathlib import Path

import numpy as np

from caravan_model import SLOTS, order_by_pivot
from scenarios import all_scenarios
from fast import Bench, XS

OUT = Path(__file__).resolve().parent / 'output'
PIVOTS = list(range(210, 256, 5))


def order_balanced(pivot):
    used, rest = [], list(range(20))
    while rest:
        s = sum(XS[i] for i in used)
        k = len(used) + 1
        nxt = min(rest, key=lambda i: (abs((s + XS[i]) / k - pivot), abs(XS[i] - pivot), i))
        used.append(nxt)
        rest.remove(nxt)
    return used


def margins(B, order):
    """Marge CG (in, + dedans) par scenario, lourds d'abord."""
    m = B.moments(order, True)
    return np.minimum(m - B.r_lo, B.r_hi - m) * 1000 / B.mass


def bins_of(v, edges):
    return np.digitize(v, edges)


def best_table(ok, keys, nbins):
    """Pour chaque case (cle), le pivot couvrant le plus de scenarios ; couverture totale."""
    table, covered = {}, 0
    for key in range(nbins):
        sel = keys == key
        if not sel.any():
            continue
        cov = ok[sel].sum(axis=0)
        j = int(np.argmax(cov))
        table[key] = (PIVOTS[j], int(cov[j]), int(sel.sum()))
        covered += int(cov[j])
    return table, covered


def main():
    scs_all, _ = all_scenarios(seed=0, k_per_cell=6)
    real_mask = np.array([s.fuel_lbs >= 320 and 70 <= np.mean(s.weights_kg) <= 110 for s in scs_all])
    B = Bench(scs_all)
    feas = B.feasible
    nf_all, nf_real = int(feas.sum()), int((feas & real_mask).sum())
    print(f'{nf_all} scenarios (dont {nf_real} realistes)\n')

    fams = {'distance': order_by_pivot, 'equilibre': order_balanced}
    print('Pivot unique, lourds d abord : echecs (realiste / complet), marge min realiste')
    print('pivot   ' + '   '.join(f'{f:>28s}' for f in fams))
    for p in range(215, 251, 5):
        row = []
        for f, fn in fams.items():
            mg = margins(B, fn(p))
            e_r = int(((mg < 0) & feas & real_mask).sum())
            e_a = int(((mg < 0) & feas).sum())
            row.append(f'{100*e_r/nf_real:5.1f} % / {100*e_a/nf_all:5.1f} %   min {mg[feas & real_mask].min():+5.1f}')
        print(f'{p:4d}    ' + '   '.join(row))

    print('\nOrdre equilibre pour quelques pivots (bras des places dans l ordre) :')
    for p in (225, 230, 235, 240):
        o = order_balanced(p)
        print(f'  {p} : ' + ' '.join(f'{XS[i]:.0f}' for i in o))

    # matrice OK (scenario x pivot) pour la famille equilibre, avec marge cible
    for fam, fn in fams.items():
        for target in (0.0, 0.5):
            M = np.stack([margins(B, fn(p)) for p in PIVOTS], axis=1)   # S x P
            ok = (M >= target) & feas[:, None]
            print(f'\n=== famille {fam}, marge cible {target} in')
            any_ok = ok.any(axis=1)
            print(f'  scenarios couverts par au moins un pivot : {int((any_ok & feas).sum())}/{nf_all} '
                  f'(realiste {int((any_ok & feas & real_mask).sum())}/{nf_real})')
            fuel = np.array([s.fuel_lbs for s in scs_all])
            wp = np.array([sum(s.weights_kg) for s in scs_all])
            nn = np.array([s.n for s in scs_all])
            candidates = {
                'fuel 2 (1200)': bins_of(fuel, [1200]),
                'fuel 3 (900,1600)': bins_of(fuel, [900, 1600]),
                'masse 2 (1100)': bins_of(wp, [1100]),
                'masse 3 (800,1300)': bins_of(wp, [800, 1300]),
                'masse 4 (600,1000,1400)': bins_of(wp, [600, 1000, 1400]),
                'fuel 2 x masse 2': bins_of(fuel, [1200]) * 2 + bins_of(wp, [1100]),
                'fuel 2 x masse 3': bins_of(fuel, [1200]) * 3 + bins_of(wp, [800, 1300]),
                'fuel 3 x masse 3': bins_of(fuel, [900, 1600]) * 3 + bins_of(wp, [800, 1300]),
                'fuel 2 x N 3 (8,14)': bins_of(fuel, [1200]) * 3 + bins_of(nn, [8, 14]),
                'fuel 3 x N 3 (8,14)': bins_of(fuel, [900, 1600]) * 3 + bins_of(nn, [8, 14]),
                'fuel 2 x N 4 (6,11,16)': bins_of(fuel, [1200]) * 4 + bins_of(nn, [6, 11, 16]),
            }
            for name, keys in candidates.items():
                nb = int(keys.max()) + 1
                # table choisie sur l espace realiste, couverture mesuree sur les deux
                okr = ok & real_mask[:, None]
                table, cov_r = best_table(okr, keys, nb)
                cov_a = sum(int(ok[(keys == k) & feas, PIVOTS.index(p)].sum()) for k, (p, _, _) in table.items())
                miss_r = nf_real - cov_r
                miss_a = nf_all - cov_a
                cells = ' '.join(f'{k}:{p}' for k, (p, _, _) in sorted(table.items()))
                print(f'  {name:26s} rate realiste {miss_r:5d} ({100*miss_r/nf_real:5.2f} %)  '
                      f'complet {miss_a:5d} ({100*miss_a/nf_all:5.2f} %)   pivots {cells}')


if __name__ == '__main__':
    main()
