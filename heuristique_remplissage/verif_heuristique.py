"""Verification de l'heuristique de remplissage a places fixes (Caravan).

Heuristique testee (proposition) : remplir les places par distance croissante
a un pivot (202 in), les paras les plus lourds d'abord.

Pour chaque scenario (avion, pilote, carburant, masses individuelles) on
compare le statut de l'heuristique avec l'oracle (existe-t-il une affectation
quelconque dans l'enveloppe ?). Un "echec heuristique" est un scenario ou
l'heuristique sort de l'enveloppe alors qu'une affectation valide existe.

Usage : python3 verif_heuristique.py [pivot_in]
"""
import sys
from collections import Counter, defaultdict

import numpy as np

from caravan_model import (SLOTS, order_by_pivot, evaluate, feasible_exists,
                           cg_to_mac)
from scenarios import all_scenarios, FUEL_GRID, N_GRID


def run(order, scenarios, heaviest_first=True, oracle_cache=None):
    """Retourne la liste des resultats par scenario."""
    res = []
    for sc in scenarios:
        st, mass, cg, mac = evaluate(order, sc.immat, sc.pilot_kg, sc.fuel_lbs,
                                     sc.weights_kg, heaviest_first)
        key = (sc.immat, sc.pilot_kg, sc.fuel_lbs, sc.weights_kg)
        if oracle_cache is not None and key in oracle_cache:
            feas = oracle_cache[key]
        else:
            feas, _ = feasible_exists(sc.immat, sc.pilot_kg, sc.fuel_lbs, sc.weights_kg)
            if oracle_cache is not None:
                oracle_cache[key] = feas
        res.append(dict(sc=sc, status=st, mass=mass, cg=cg, mac=mac, feasible=feas))
    return res


def summarize(res, label=''):
    n = len(res)
    feas = [r for r in res if r['feasible']]
    infeas = n - len(feas)
    fail = [r for r in feas if r['status'] != 'ok']
    by_status = Counter(r['status'] for r in fail)
    print(f'--- {label}')
    print(f'  scenarios sous MTOW        : {n}')
    print(f'  dont aucune affectation OK : {infeas}  (infaisables quel que soit le remplissage)')
    print(f'  dont affectation possible  : {len(feas)}')
    print(f'  echecs de l heuristique    : {len(fail)}  ({100*len(fail)/max(1,len(feas)):.2f} %)  '
          f'{dict(by_status)}')
    return fail, feas


def table_by_n(res):
    """Taux d'echec heuristique par N (sur les scenarios faisables)."""
    tot, bad, worst = defaultdict(int), defaultdict(int), {}
    for r in res:
        if not r['feasible']:
            continue
        n = r['sc'].n
        tot[n] += 1
        if r['status'] != 'ok':
            bad[n] += 1
            d = r['mac']
            if n not in worst or abs(d - worst[n][0]) < 0:
                worst[n] = (d, r)
    print('   N   faisables  echecs   taux    statuts')
    for n in N_GRID:
        if tot[n] == 0:
            continue
        sts = Counter(r['status'] for r in res if r['feasible'] and r['sc'].n == n
                      and r['status'] != 'ok')
        print(f'  {n:2d}   {tot[n]:6d}   {bad[n]:6d}   {100*bad[n]/tot[n]:5.1f} %  {dict(sts) if sts else ""}')


def table_by_fuel(res):
    tot, bad = defaultdict(int), defaultdict(int)
    for r in res:
        if not r['feasible']:
            continue
        f = min(FUEL_GRID, key=lambda g: abs(g - r['sc'].fuel_lbs))
        tot[f] += 1
        bad[f] += r['status'] != 'ok'
    print('  fuel(lbs)  faisables  echecs   taux')
    for f in FUEL_GRID:
        if tot[f]:
            print(f'  {f:6d}     {tot[f]:6d}   {bad[f]:6d}   {100*bad[f]/tot[f]:5.1f} %')


def show_examples(fail, k=8):
    print(f'  exemples d echecs (max {k}) :')
    for r in sorted(fail, key=lambda r: -abs(r['mac'] - 36.5))[:k]:
        sc = r['sc']
        ws = sc.weights_kg
        print(f'    {sc.immat} pilote {sc.pilot_kg:5.1f} kg  fuel {sc.fuel_lbs:6.0f} lbs  '
              f'N={sc.n:2d} ({sc.family}, moy {np.mean(ws):5.1f} kg)  '
              f'-> masse {r["mass"]:5.0f} lbs, CG {r["cg"]:6.2f} in = {r["mac"]:5.2f} %MAC  [{r["status"]}]')


if __name__ == '__main__':
    pivot = float(sys.argv[1]) if len(sys.argv) > 1 else 202.0
    scs, dropped = all_scenarios()
    print(f'{len(scs)} scenarios sous MTOW ({dropped} ecartes car > MTOW)\n')
    order = order_by_pivot(pivot)
    print('Ordre de remplissage :', ' '.join(f'{SLOTS[i].x:.0f}' for i in order))
    cache = {}
    res = run(order, scs, heaviest_first=True, oracle_cache=cache)
    fail, feas = summarize(res, f'pivot {pivot} in, plus lourds d abord')
    table_by_n(res)
    table_by_fuel(res)
    show_examples(fail)
    res2 = run(order, scs, heaviest_first=False, oracle_cache=cache)
    fail2, _ = summarize(res2, f'pivot {pivot} in, plus legers d abord')
