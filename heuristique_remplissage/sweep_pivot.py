"""Balayage du pivot : taux d'echec heuristique en fonction du pivot (in)."""
import numpy as np
from caravan_model import order_by_pivot, SLOTS
from scenarios import all_scenarios, N_GRID
from fast import Bench

scs, dropped = all_scenarios()
B = Bench(scs)
nf = int(B.feasible.sum())
print(f'{len(scs)} scenarios sous MTOW, {nf} faisables, {len(scs)-nf} infaisables quel que soit l ordre')
print('pivot   echecs(lourds 1er)   echecs(legers 1er)   marge min (in)')
best = None
for p in np.arange(190, 260.1, 2.5):
    o = order_by_pivot(p)
    f1, f2 = B.failures(o, True), B.failures(o, False)
    mm = B.min_margin_mac(o, True)
    print(f'{p:6.1f}   {f1:6d} ({100*f1/nf:5.1f} %)     {f2:6d} ({100*f2/nf:5.1f} %)     {mm:+6.2f}')
    if best is None or f1 < best[1]:
        best = (p, f1)
print('meilleur pivot (lourds d abord) :', best)
# detail par N pour le meilleur pivot
o = order_by_pivot(best[0])
st = B.status(o)
print('\n N  faisables  echecs  (avant/arriere)   ordre des bras utilises')
for n in N_GRID:
    sel = (B.n == n) & B.feasible
    bad = sel & (st != 0)
    print(f'{n:2d}  {sel.sum():6d}  {bad.sum():6d}  ({(sel & (st<0)).sum():4d}/{(sel & (st>0)).sum():4d})   '
          f'moy bras {np.mean([SLOTS[i].x for i in o[:n]]):6.1f}')
