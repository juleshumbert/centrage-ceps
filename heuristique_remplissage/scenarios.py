"""Jeu de scenarios de test : nombre de paras, carburant, masses individuelles.

Deux familles :
  - grille : masses uniformes (tous les paras a la meme masse), pilote 80/86 kg,
    balayage exhaustif N x carburant x masse ;
  - tirages : masses individuelles aleatoires (plusieurs lois), pilote aleatoire,
    K tirages par (N, carburant).
Les scenarios qui depassent la MTOW sont ecartes en amont (aucune heuristique ne
peut les rendre faisables), ils sont comptes a part.
"""
from dataclasses import dataclass

import numpy as np

from caravan_model import AIRCRAFT, LBS2KG, MTOW_LBS, base_state, FUEL_MAX_LBS

FUEL_GRID = list(range(200, FUEL_MAX_LBS, 100)) + [FUEL_MAX_LBS]
N_GRID = list(range(1, 21))
UNIFORM_KG = [60, 70, 80, 90, 100, 110, 120]
PILOT_GRID = [80, 86]


@dataclass
class Scenario:
    immat: str
    pilot_kg: float
    fuel_lbs: float
    weights_kg: tuple
    family: str      # 'uniforme_XX', 'U60-120', 'N85-12', 'bimodal'

    @property
    def n(self):
        return len(self.weights_kg)


def within_mtow(sc):
    _, w0 = base_state(sc.immat, sc.pilot_kg, sc.fuel_lbs)
    return w0 + sum(sc.weights_kg) * LBS2KG <= MTOW_LBS + 1e-6


def grid_scenarios():
    out = []
    for immat in AIRCRAFT:
        for pilot in PILOT_GRID:
            for kg in UNIFORM_KG:
                for n in N_GRID:
                    for fuel in FUEL_GRID:
                        out.append(Scenario(immat, pilot, fuel, (float(kg),) * n,
                                            f'uniforme_{kg}'))
    return out


def _draw(rng, law, n):
    if law == 'U60-120':
        return rng.uniform(60, 120, n)
    if law == 'N85-12':
        return np.clip(rng.normal(85, 12, n), 55, 130)
    if law == 'bimodal':
        return np.where(rng.random(n) < 0.5, 65.0, 115.0)
    raise ValueError(law)


def random_scenarios(k_per_cell=6, seed=0, laws=('U60-120', 'N85-12', 'bimodal')):
    rng = np.random.default_rng(seed)
    out = []
    for immat in AIRCRAFT:
        for law in laws:
            for n in N_GRID:
                for fuel in FUEL_GRID:
                    for _ in range(k_per_cell):
                        pilot = float(rng.uniform(65, 110))
                        f = float(np.clip(fuel + rng.uniform(-50, 50), 100, FUEL_MAX_LBS))
                        ws = tuple(round(float(w), 1) for w in _draw(rng, law, n))
                        out.append(Scenario(immat, pilot, f, ws, law))
    return out


def all_scenarios(seed=0, k_per_cell=6):
    scs = grid_scenarios() + random_scenarios(k_per_cell, seed)
    kept = [s for s in scs if within_mtow(s)]
    return kept, len(scs) - len(kept)
