"""Pour chaque N : intersection des bandes de bras moyen paras admissibles.

Sur les scenarios a masses uniformes (grille), le moment paras vaut
n * w * xbar ; la bande admissible [r_lo, r_hi] se traduit en bande de bras
moyen. Si l'intersection sur tous les scenarios d'un N est vide, aucun ordre
fixe (quel que soit le pivot) ne peut satisfaire tous les scenarios de ce N.
"""
import numpy as np
from scenarios import all_scenarios
from fast import Bench

scs, _ = all_scenarios()
B = Bench(scs)
print(' N   xbar_lo max (scenario)                          xbar_hi min (scenario)                    largeur')
for n in range(1, 21):
    idx = [i for i, sc in enumerate(scs) if sc.n == n and sc.family.startswith('uniforme')]
    lo = [(B.r_lo[i] * 1000 / B.W_desc[i, :n].sum(), i) for i in idx]
    hi = [(B.r_hi[i] * 1000 / B.W_desc[i, :n].sum(), i) for i in idx]
    (xlo, ilo), (xhi, ihi) = max(lo), min(hi)
    a, b = scs[ilo], scs[ihi]
    print(f'{n:2d}   {xlo:6.1f}  {a.immat} pil {a.pilot_kg:3.0f} fuel {a.fuel_lbs:4.0f} {a.family:12s}   '
          f'{xhi:6.1f}  {b.immat} pil {b.pilot_kg:3.0f} fuel {b.fuel_lbs:4.0f} {b.family:12s}   {xhi-xlo:+6.1f}')
