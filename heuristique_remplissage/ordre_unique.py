"""Existe-t-il UN ordre de remplissage qui marche a chaque fois ?

Argument exact : avec des masses uniformes (tous les paras a w kg), le moment
paras d'un ordre vaut n.w.xbar_n ou xbar_n est le bras moyen des n premieres
places. Chaque scenario impose xbar_n dans une bande ; si, pour un N, les bandes
de tous les scenarios ne se recoupent pas, aucun ordre ne peut convenir sur ce
domaine. On mesure ce recoupement sur plusieurs restrictions du domaine, puis
on cherche un ordre par recuit la ou le recoupement existe.
"""
import json
import sys
from pathlib import Path

import numpy as np

from caravan_model import SLOTS, order_by_pivot
from scenarios import all_scenarios, N_GRID
from fast import Bench, XS
from optimise_ordre import anneal as anneal_fail

OUT = Path(__file__).resolve().parent / 'output'


def bands(scs, B, mask):
    """Par N : (max des bornes basses, min des bornes hautes) du bras moyen, masses uniformes."""
    out = {}
    for n in N_GRID:
        idx = [i for i, sc in enumerate(scs) if sc.n == n and mask[i] and sc.family.startswith('uniforme')]
        if not idx:
            out[n] = (np.nan, np.nan, 0)
            continue
        lo = max(B.r_lo[i] * 1000 / B.W_desc[i, :n].sum() for i in idx)
        hi = min(B.r_hi[i] * 1000 / B.W_desc[i, :n].sum() for i in idx)
        out[n] = (lo, hi, len(idx))
    return out


def anneal_margin(B, start, iters=15000, seed=1, target=0.5):
    """Recuit : minimise (echecs, puis deficit de marge sous `target` in)."""
    rng = np.random.default_rng(seed)

    def cost(o):
        m = B.moments(o, True)
        marg = np.minimum(m - B.r_lo, B.r_hi - m) * 1000 / B.mass
        short = np.maximum(target - marg, 0)[B.feasible]
        return int((marg[B.feasible] < 0).sum()) + 0.3 * float(short.sum())

    cur = list(start)
    c_cur = cost(cur)
    best, c_best = list(cur), c_cur
    t0, t1 = 3.0, 0.01
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


def stats(B, order, mask):
    m = B.moments(order, True)
    marg = np.minimum(m - B.r_lo, B.r_hi - m) * 1000 / B.mass
    sel = B.feasible & mask
    return int((marg[sel] < 0).sum()), int(sel.sum()), float(marg[sel].min()), float(np.percentile(marg[sel], 1))


def main():
    scs, _ = all_scenarios(seed=0, k_per_cell=6)
    B = Bench(scs)
    fuel = np.array([s.fuel_lbs for s in scs])
    mean_kg = np.array([np.mean(s.weights_kg) for s in scs])
    pilot = np.array([s.pilot_kg for s in scs])
    immat = np.array([s.immat for s in scs])
    full = np.ones(len(scs), bool)
    real = (fuel >= 320) & (mean_kg >= 70) & (mean_kg <= 110)
    restrictions = {
        'complet': full,
        'realiste (fuel >= 320, moy 70-110 kg)': real,
        'realiste + pilote 70-100': real & (pilot >= 70) & (pilot <= 100),
        'realiste + fuel <= 1900': real & (fuel <= 1900),
        'realiste + fuel <= 1600': real & (fuel <= 1600),
        'realiste + moy 75-105 kg': real & (mean_kg >= 75) & (mean_kg <= 105),
        'realiste + moy 80-100 kg': real & (mean_kg >= 80) & (mean_kg <= 100),
        'realiste, C208B-A seul': real & (immat == 'C208B-A'),
        'realiste, C208B-B seul': real & (immat == 'C208B-B'),
        'realiste + fuel <= 1600 + moy 75-105': real & (fuel <= 1600) & (mean_kg >= 75) & (mean_kg <= 105),
        'realiste + fuel <= 1900 + moy 75-105': real & (fuel <= 1900) & (mean_kg >= 75) & (mean_kg <= 105),
        'realiste + fuel <= 1900 + moy 80-100': real & (fuel <= 1900) & (mean_kg >= 80) & (mean_kg <= 100),
        'C208B-A, realiste + fuel <= 1900': real & (immat == 'C208B-A') & (fuel <= 1900),
        'C208B-B, realiste + fuel <= 1900': real & (immat == 'C208B-B') & (fuel <= 1900),
    }
    results = {}
    print('Recoupement des bandes (masses uniformes) : largeur minimale sur N, et N concernes\n')
    for name, mask in restrictions.items():
        bd = bands(scs, B, mask)
        widths = {n: hi - lo for n, (lo, hi, k) in bd.items() if k}
        wmin = min(widths.values())
        neg = [n for n, w in widths.items() if w < 0]
        print(f'  {name:42s} largeur min {wmin:+6.1f} in   N sans solution : {neg if neg else "aucun"}')
        results[name] = dict(largeur_min=wmin, N_sans_solution=neg, bandes={n: bd[n][:2] for n in bd})

    print('\nRecuit d un ordre unique sur les domaines ou le recoupement existe (ou presque) :\n')
    for name, mask in restrictions.items():
        if results[name]['largeur_min'] < -2.0:
            continue
        Bm = Bench([s for s, ok in zip(scs, mask) if ok])
        order = anneal_margin(Bm, order_by_pivot(232.5), iters=15000)
        e_m, n_m, mn_m, p1_m = stats(B, order, mask)
        e_a, n_a, mn_a, _ = stats(B, order, full)
        e_r, n_r, mn_r, _ = stats(B, order, real)
        print(f'  {name}')
        print(f'     ordre (bras) : ' + ' '.join(f'{XS[i]:.0f}' for i in order))
        print(f'     sur ce domaine : {e_m} echecs / {n_m}, marge min {mn_m:+.2f} in, 1er centile {p1_m:.2f} in')
        print(f'     sur le realiste : {e_r} echecs / {n_r} (marge min {mn_r:+.2f}) ; sur le complet : {e_a} / {n_a} (marge min {mn_a:+.2f})')
        results[name].update(ordre=[int(i) for i in order], echecs_domaine=e_m, n_domaine=n_m,
                             marge_min_domaine=mn_m, echecs_realiste=e_r, echecs_complet=e_a)
    (OUT / 'ordre_unique.json').write_text(json.dumps(results, indent=1, default=float))


if __name__ == '__main__':
    main()
