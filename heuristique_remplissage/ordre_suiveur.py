"""Ordre unique "suiveur de bande" : construction gloutonne et explicable.

Pour un domaine donne, la bande de bras moyen admissible [lo_N, hi_N] (masses
uniformes) descend quand N augmente. A chaque numero k on ajoute la place
inutilisee qui amene la moyenne des k premieres places au plus pres du milieu
de la bande a N=k. Contrairement au pivot fixe, la moyenne derive avec k.
"""
import json
from pathlib import Path

import numpy as np

from scenarios import all_scenarios
from fast import Bench, XS
from pivot_regimes import margins
from ordre_unique import bands, anneal_margin, stats
from caravan_model import order_by_pivot

OUT = Path(__file__).resolve().parent / 'output'


def order_following(targets):
    """targets[n] : bras moyen vise pour n paras (n = 1..20)."""
    used, rest = [], list(range(20))
    while rest:
        k = len(used) + 1
        t = targets[k]
        s = sum(XS[i] for i in used)
        nxt = min(rest, key=lambda i: (abs((s + XS[i]) / k - t), abs(XS[i] - t), i))
        used.append(nxt); rest.remove(nxt)
    return used


def targets_from_bands(bd, shift=0.0):
    t = {}
    for n, (lo, hi, k) in bd.items():
        t[n] = (lo + hi) / 2 + shift if k else t[n - 1]
    return t


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
        'deux avions, realiste + fuel <= 1900 + moy 75-105': real & (fuel <= 1900) & (mean_kg >= 75) & (mean_kg <= 105),
        'C208B-A, complet': immat == 'C208B-A',
        'C208B-B, complet': immat == 'C208B-B',
    }
    results = {}
    for name, mask in doms.items():
        bd = bands(scs, B, mask)
        print(f'== {name}')
        print('   bande par N (lo/hi) : ' + ' '.join(f'{n}:{bd[n][0]:.0f}-{bd[n][1]:.0f}' for n in range(1, 21) if bd[n][2]))
        best = None
        for shift in (-2, -1, 0, 1, 2):
            o = order_following(targets_from_bands(bd, shift))
            e, n, mn, p1 = stats(B, o, mask)
            if best is None or (e, -mn) < (best[1], -best[2]):
                best = (o, e, mn, p1, shift)
        o, e, n_, mn, p1, sh = best[0], best[1], 0, best[2], best[3], best[4]
        e_a, n_a, mn_a, _ = stats(B, o, np.ones(len(scs), bool))
        print(f'   suiveur (decalage {sh:+d} in) : {e} echecs / {int((mask & feas).sum())}, marge min {mn:+.2f}, 1er centile {p1:.2f} ; complet {e_a}/{n_a}')
        print('   ordre (bras) : ' + ' '.join(f'{XS[i]:.0f}' for i in o))
        print('   moyenne des k premieres : ' + ' '.join(f'{np.mean(XS[o[:k]]):.0f}' for k in range(1, 21)))
        # raffinement par recuit a partir du suiveur
        Bm = Bench([s for s, ok in zip(scs, mask) if ok])
        o2 = anneal_margin(Bm, o, iters=12000)
        e2, _, mn2, p12 = stats(B, o2, mask)
        e2a, _, mn2a, _ = stats(B, o2, np.ones(len(scs), bool))
        print(f'   recuit depuis le suiveur : {e2} echecs, marge min {mn2:+.2f}, 1er centile {p12:.2f} ; complet {e2a}')
        print('   ordre (bras) : ' + ' '.join(f'{XS[i]:.0f}' for i in o2))
        results[name] = dict(suiveur=dict(ordre=[int(i) for i in o], echecs=e, marge_min=mn, decalage=sh),
                             recuit=dict(ordre=[int(i) for i in o2], echecs=e2, marge_min=mn2),
                             bandes={n: bd[n][:2] for n in bd})
    (OUT / 'ordre_suiveur.json').write_text(json.dumps(results, indent=1, default=float))


if __name__ == '__main__':
    main()
