"""Banc d'essai du placement MILP sur des manifestes aleatoires.

Pour chaque manifeste : phase 1 (existe-t-il un placement valide, marge max) comparee a
l'oracle de caravan_model.feasible_exists ; phase 2 avec temps limite court ; temps.
"""
import sys
import time

import numpy as np

from caravan_model import feasible_exists, MTOW_LBS, LBS2KG, base_state
from placement_milp import Placement


def random_manifest(rng):
    immat = rng.choice(['C208B-A', 'C208B-B'])
    pilot = float(rng.integers(65, 111))
    n = int(rng.integers(3, 21))
    kg = np.clip(rng.normal(88, 13, n), 60, 125).round()
    # groupes : tailles aleatoires 1 a 6, ordre de sortie = ordre des groupes
    paras, g, exit_rank, i = [], 0, 1, 0
    while i < n:
        size = int(rng.integers(1, 7))
        members = list(range(i, min(n, i + size)))
        gname = chr(65 + g) if len(members) > 1 else None
        for j in members:
            paras.append(dict(nom=f'P{j+1}', kg=float(kg[j]), groupe=gname, sortie=exit_rank))
        i += len(members); g += 1; exit_rank += 1
    # carburant tire pour rester sous la MTOW dans ~80 % des cas
    _, w0 = base_state(immat, pilot, 0)
    room = MTOW_LBS - w0 - kg.sum() * LBS2KG
    fuel = float(np.clip(rng.uniform(320, max(400, room + 300)), 320, 2224))
    return dict(immat=immat, pilote_kg=pilot, fuel_lbs=fuel, paras=paras)


def main(n_cases=40, seed=0, t2=10.0):
    rng = np.random.default_rng(seed)
    stats = dict(total=0, mtow=0, faisables=0, accord=0, t1=[], t2=[], opt=0, gaps=[])
    for k in range(n_cases):
        man = random_manifest(rng)
        weights = tuple(p['kg'] for p in man['paras'])
        stats['total'] += 1
        pl = Placement(man, sequence=False)
        res = pl.solve(time_limit=t2)
        feas, _ = feasible_exists(man['immat'], man['pilote_kg'], man['fuel_lbs'], weights)
        if not res['ok'] and 'MTOW' in res['message']:
            stats['mtow'] += 1
            assert not feas
            continue
        stats['accord'] += (res['ok'] == feas)
        if res['ok']:
            stats['faisables'] += 1
            stats['t1'].append(res['temps_phase1']); stats['t2'].append(res['temps'] - res['temps_phase1'])
            stats['opt'] += res['optimal']
            if res['gap'] is not None:
                stats['gaps'].append(res['gap'])
            assert all(e['ok'] for e in res['etapes'][:1]), 'placement rendu hors enveloppe'
        print(f"  {k:2d} {man['immat']} N={len(weights):2d} fuel {man['fuel_lbs']:5.0f} pilote {man['pilote_kg']:3.0f} : "
              f"{'OK' if res['ok'] else 'IMPOSSIBLE'} (oracle {'OK' if feas else 'impossible'})"
              + (f", marge max {res['mu_max']:+.2f}, phase 1 {res['temps_phase1']:.1f} s, phase 2 {res['temps'] - res['temps_phase1']:.1f} s, "
                 f"{'optimum' if res['optimal'] else 'ecart %.0f %%' % (100 * res['gap'])}" if res['ok'] else ''))
    print(f"\n{stats['total']} manifestes : {stats['mtow']} au-dessus de la MTOW, {stats['faisables']} places, "
          f"accord solveur/oracle {stats['accord']}/{stats['total'] - stats['mtow']}")
    if stats['t1']:
        print(f"phase 1 : {np.mean(stats['t1']):.2f} s en moyenne, max {np.max(stats['t1']):.2f} s ; "
              f"phase 2 ({t2:.0f} s max) : {np.mean(stats['t2']):.1f} s, optimum prouve {stats['opt']}/{stats['faisables']}, "
              f"ecart median restant {100 * np.median(stats['gaps']) if stats['gaps'] else 0:.0f} %")


if __name__ == '__main__':
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 40, t2=float(sys.argv[2]) if len(sys.argv) > 2 else 10.0)
