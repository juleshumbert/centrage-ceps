"""Recuit simule sur l'ordre de remplissage (permutation des 20 places).

Cout = nombre d'echecs heuristiques + 0.05 x depassement cumule (continu,
pour guider la descente). Depart : ordre par pivot 235 in.
"""
import numpy as np

from caravan_model import SLOTS, order_by_pivot
from fast import Bench


def cost(B, order, hf=True):
    return B.failures(order, hf) + 0.05 * B.margin_loss(order, hf)


def anneal(B, start=None, iters=30000, t0=3.0, t1=0.02, seed=1, hf=True, verbose=False):
    rng = np.random.default_rng(seed)
    cur = list(start or order_by_pivot(235.0))
    c_cur = cost(B, cur, hf)
    best, c_best = list(cur), c_cur
    for it in range(iters):
        T = t0 * (t1 / t0) ** (it / iters)
        i, j = rng.choice(20, 2, replace=False)
        cand = list(cur)
        cand[i], cand[j] = cand[j], cand[i]
        c = cost(B, cand, hf)
        if c <= c_cur or rng.random() < np.exp((c_cur - c) / T):
            cur, c_cur = cand, c
            if c < c_best:
                best, c_best = list(cand), c
                if verbose:
                    print(f'  it {it:6d}  cout {c:8.2f}  echecs {B.failures(best, hf)}')
    return best, c_best


def describe(B, order, label):
    st = B.status(order)
    nf = int(B.feasible.sum())
    bad = int(((st != 0) & B.feasible).sum())
    print(f'--- {label}: {bad} echecs / {nf} faisables ({100*bad/max(nf,1):.2f} %), '
          f'marge min {B.min_margin_mac(order):+.2f} in')
    print('    ordre (bras in) :', ' '.join(f'{SLOTS[i].x:.0f}' for i in order))
    print('    ordre (places)  :', ' '.join(str(i) for i in order))
    print('    N : echecs avant/arriere')
    for n in range(1, 21):
        sel = (B.n == n) & B.feasible
        a, r = int((sel & (st < 0)).sum()), int((sel & (st > 0)).sum())
        if a or r:
            print(f'      N={n:2d} : {a:4d} / {r:4d}   (sur {int(sel.sum())})')
    return bad


if __name__ == '__main__':
    import json
    from pathlib import Path
    from scenarios import all_scenarios
    scs, _ = all_scenarios()
    B = Bench(scs)
    ordres = {}

    print('=== 1. Recuit sur tous les scenarios')
    best, _ = anneal(B, iters=20000)
    describe(B, best, 'meilleur ordre fixe (tous scenarios)')
    ordres['fixe_tous_scenarios'] = [int(i) for i in best]

    print('\n=== 2. Recuit sur un sous-ensemble "realiste" (fuel >= 320 lbs, masses uniformes 70-110 seulement)')
    real = [s for s in scs if s.fuel_lbs >= 320 and not s.family in ('uniforme_60', 'uniforme_120')]
    Br = Bench(real)
    best_r, _ = anneal(Br, iters=20000)
    describe(Br, best_r, 'meilleur ordre fixe (realiste), evalue sur le realiste')
    describe(B, best_r, 'meme ordre, evalue sur TOUS les scenarios')
    ordres['fixe_realiste'] = [int(i) for i in best_r]

    print('\n=== 3. Deux ordres selon le carburant (seuil T)')
    for T in (800, 1000, 1200, 1400):
        lo = [s for s in scs if s.fuel_lbs < T]
        hi = [s for s in scs if s.fuel_lbs >= T]
        Blo, Bhi = Bench(lo), Bench(hi)
        o_lo, _ = anneal(Blo, iters=12000)
        o_hi, _ = anneal(Bhi, iters=12000)
        b1 = describe(Blo, o_lo, f'T={T}: fuel < {T}')
        b2 = describe(Bhi, o_hi, f'T={T}: fuel >= {T}')
        print(f'    ==> total {b1+b2} echecs pour T={T}')
        ordres[f'fuel_lt_{T}'] = [int(i) for i in o_lo]
        ordres[f'fuel_ge_{T}'] = [int(i) for i in o_hi]

    out = Path(__file__).resolve().parent / 'output' / 'ordres.json'
    out.write_text(json.dumps(dict(
        places=[dict(idx=s.idx, bras_in=s.x, y_in=s.y, rangee=s.row) for s in SLOTS],
        ordres=ordres), indent=1))
    print('ecrit', out)
