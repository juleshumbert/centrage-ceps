"""Prepare l'entree de l'enumerateur Rust : pour chaque cas (jeu de places x domaine),
la bande admissible de la somme des bras des N places occupees, N = 1..20.

Un domaine = ensemble de scenarios (avion, pilote, carburant, masse uniforme). Pour un
scenario et un N, la condition d'enveloppe se traduit par lo <= somme des bras <= hi ;
sur le domaine on garde l'intersection (max des lo, min des hi), en ignorant les
scenarios au-dessus de la MTOW (aucune configuration ne les sauve).
"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from caravan_model import (SLOTS, MTOW_LBS, LBS2KG, base_state, fwd_limit, AFT_CG)
from ordre_origine import legacy_slots

HERE = Path(__file__).resolve().parent
FUELS = list(range(200, 2224, 100)) + [2224]


def interval(immat, pilot, fuel, mass_kg, n, aft_only=False):
    """[lo, hi] de la somme des bras pour n paras de mass_kg, ou None si > MTOW."""
    m0, w0 = base_state(immat, pilot, fuel)
    w = mass_kg * LBS2KG
    mass = w0 + n * w
    if mass > MTOW_LBS:
        return None
    lo = -np.inf if aft_only else (fwd_limit(mass) * mass / 1000 - m0) * 1000 / w
    hi = (AFT_CG * mass / 1000 - m0) * 1000 / w
    return lo, hi


def bands(scenarios, aft_only=False, offsets=None):
    """scenarios : liste (immat, pilot, fuel, mass). offsets : decalage de bras par avion
    (pour exprimer les bandes de LA sur les bras de BK quand les places sont a +3 in)."""
    lo = np.full(21, -np.inf)
    hi = np.full(21, np.inf)
    for immat, pil, f, m in scenarios:
        off = (offsets or {}).get(immat, 0.0)
        for n in range(1, 21):
            iv = interval(immat, pil, f, m, n, aft_only)
            if iv is None:
                break
            lo[n] = max(lo[n], iv[0] - off * n)
            hi[n] = min(hi[n], iv[1] - off * n)
    return lo, hi


def scen(immats, pilots, masses, fuels=FUELS):
    return [(a, p, f, m) for a in immats for p in pilots for f in fuels for m in masses]


DOMAINS = {
    'forfait 90 kg, pilote 80': dict(pilots=[80], masses=[90]),
    'forfait 80 kg, pilote 86': dict(pilots=[86], masses=[80]),
    'moyen 70-110 kg, pilotes 80/86': dict(pilots=[80, 86], masses=list(range(70, 111, 5))),
    'moyen 60-120 kg, pilotes 80/86': dict(pilots=[80, 86], masses=list(range(60, 121, 5))),
    'moyen 70-110 kg, pilotes 65-110': dict(pilots=[65, 80, 95, 110], masses=list(range(70, 111, 5))),
    'moyen 70-110 kg, pilotes 80/86, fuel 320-1900': dict(pilots=[80, 86], masses=list(range(70, 111, 5)),
                                                          fuels=[f for f in FUELS if 320 <= f <= 1900]),
    'moyen 75-105 kg, pilotes 80/86, fuel 320-1900': dict(pilots=[80, 86], masses=list(range(75, 106, 5)),
                                                          fuels=[f for f in FUELS if 320 <= f <= 1900]),
}

SLOTSETS = {
    'legacy': dict(arms=legacy_slots('C208B-A'), offsets={'C208B-A': 0.0, 'C208B-B': 3.0}),
    'n20': dict(arms=[s.x for s in SLOTS], offsets={'C208B-A': 0.0, 'C208B-B': 0.0}),
}

lines = []
for sname, sdef in SLOTSETS.items():
    for dname, d in DOMAINS.items():
        for immats, ilabel in (['C208B-A'], 'C208B-A'), (['C208B-B'], 'C208B-B'), (['C208B-A', 'C208B-B'], 'deux avions'):
            for aft_only in (False, True):
                if aft_only and not dname.startswith('forfait'):
                    continue
                sc = scen(immats, d['pilots'], d['masses'], d.get('fuels', FUELS))
                lo, hi = bands(sc, aft_only, sdef['offsets'])
                crit = 'arriere seule' if aft_only else 'enveloppe complete'
                lines.append(f'CASE {sname} | {ilabel} | {dname} | {crit}')
                lines.append('SLOTS ' + ' '.join(f'{x:.3f}' for x in sdef['arms']))
                for n in range(1, 21):
                    lines.append(f'N {n} {lo[n]:.6f} {hi[n]:.6f}'.replace('-inf', '-1e300').replace('inf', '1e300'))
(HERE / 'input.txt').write_text('\n'.join(lines) + '\n')
print(len(lines), 'lignes,', sum(1 for l in lines if l.startswith('CASE')), 'cas')
