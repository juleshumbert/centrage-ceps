"""Raffinement de l'heuristique "ordre equilibre autour d'un pivot, lourds d'abord,
pivot choisi par une table selon la masse totale des paras (et le carburant)".

Recherche des seuils et des pivots (pas 2.5 in) qui minimisent les echecs sur
l'espace realiste ; evaluation sur l'espace complet ; robustesse a un
embarquement non trie ; caracterisation des echecs restants.
"""
import itertools
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

from caravan_model import SLOTS
from scenarios import all_scenarios
from fast import Bench, XS
from pivot_regimes import order_balanced, margins

OUT = Path(__file__).resolve().parent / 'output'
PIVOTS = [210 + 2.5 * i for i in range(19)]      # 210 .. 255


def load():
    scs, _ = all_scenarios(seed=0, k_per_cell=6)
    real = np.array([s.fuel_lbs >= 320 and 70 <= np.mean(s.weights_kg) <= 110 for s in scs])
    B = Bench(scs)
    M = np.stack([margins(B, order_balanced(p)) for p in PIVOTS], axis=1)   # S x P
    return scs, real, B, M


def table_for(keys, M, mask, nb):
    """Pivot par case : lexicographique (couverture marge 0, couverture marge 0.5,
    somme des marges ecretees a 2 in), sur les scenarios de mask."""
    table = {}
    for k in range(nb):
        sel = (keys == k) & mask
        if sel.any():
            Mk = M[sel]
            score = [(int((Mk[:, j] >= 0).sum()), int((Mk[:, j] >= 0.5).sum()),
                      float(np.minimum(Mk[:, j], 2.0).sum()), -abs(PIVOTS[j] - 232.5))
                     for j in range(len(PIVOTS))]
            table[k] = int(max(range(len(PIVOTS)), key=lambda j: score[j]))
    return table


def evaluate(keys, table, M, mask):
    """Nb d'echecs (marge < 0) et nb sous marge 0.5 sur mask."""
    j = np.array([table.get(int(k), 0) for k in keys])
    mg = M[np.arange(len(keys)), j]
    return int(((mg < 0) & mask).sum()), int(((mg < 0.5) & mask).sum()), mg


def search(scs, real, B, M):
    feas = B.feasible
    wp = np.array([sum(s.weights_kg) for s in scs])
    fuel = np.array([s.fuel_lbs for s in scs])
    nf_r, nf_a = int((feas & real).sum()), int(feas.sum())
    results = {}

    def run(name, mass_edges, fuel_edges):
        km = np.digitize(wp, mass_edges)
        kf = np.digitize(fuel, fuel_edges) if fuel_edges else np.zeros(len(scs), int)
        keys = kf * (len(mass_edges) + 1) + km
        nb = (len(fuel_edges) + 1) * (len(mass_edges) + 1)
        table = table_for(keys, M, feas & real, nb)
        e_r, u_r, _ = evaluate(keys, table, M, feas & real)
        e_a, u_a, _ = evaluate(keys, table, M, feas)
        return dict(name=name, mass_edges=list(mass_edges), fuel_edges=list(fuel_edges),
                    table={int(k): PIVOTS[j] for k, j in table.items()},
                    echecs_realiste=e_r, sous_marge_realiste=u_r,
                    echecs_complet=e_a, sous_marge_complet=u_a)

    mass_grid = list(range(400, 1701, 100))
    print('--- masse seule, 3 classes')
    best = min((run('masse3', e, []) for e in itertools.combinations(mass_grid, 2)),
               key=lambda r: (r['echecs_realiste'], r['sous_marge_realiste']))
    results['masse3'] = best; show(best, nf_r, nf_a)
    print('--- masse seule, 4 classes')
    best = min((run('masse4', e, []) for e in itertools.combinations(mass_grid, 3)),
               key=lambda r: (r['echecs_realiste'], r['sous_marge_realiste']))
    results['masse4'] = best; show(best, nf_r, nf_a)
    print('--- carburant 2 classes x masse 3 classes')
    best = min((run('fuel2_masse3', e, [f]) for e in itertools.combinations(mass_grid, 2)
                for f in range(800, 1801, 200)),
               key=lambda r: (r['echecs_realiste'], r['sous_marge_realiste']))
    results['fuel2_masse3'] = best; show(best, nf_r, nf_a)
    print('--- carburant 2 classes x masse 4 classes')
    best = min((run('fuel2_masse4', e, [f]) for e in itertools.combinations(mass_grid, 3)
                for f in range(1000, 1801, 200)),
               key=lambda r: (r['echecs_realiste'], r['sous_marge_realiste']))
    results['fuel2_masse4'] = best; show(best, nf_r, nf_a)
    print('--- carburant 3 classes x masse 3 classes')
    best = min((run('fuel3_masse3', e, list(f)) for e in itertools.combinations(mass_grid, 2)
                for f in itertools.combinations(range(800, 1801, 200), 2)),
               key=lambda r: (r['echecs_realiste'], r['sous_marge_realiste']))
    results['fuel3_masse3'] = best; show(best, nf_r, nf_a)
    return results


def show(r, nf_r, nf_a):
    print(f"  seuils masse {r['mass_edges']} kg, carburant {r['fuel_edges']} lbs")
    print(f"  pivots par case : {r['table']}")
    print(f"  realiste : {r['echecs_realiste']} echecs ({100*r['echecs_realiste']/nf_r:.2f} %), "
          f"{r['sous_marge_realiste']} sous 0.5 in ({100*r['sous_marge_realiste']/nf_r:.2f} %)")
    print(f"  complet  : {r['echecs_complet']} echecs ({100*r['echecs_complet']/nf_a:.2f} %), "
          f"{r['sous_marge_complet']} sous 0.5 in ({100*r['sous_marge_complet']/nf_a:.2f} %)")


def pivot_of(r, scs):
    wp = np.array([sum(s.weights_kg) for s in scs])
    fuel = np.array([s.fuel_lbs for s in scs])
    km = np.digitize(wp, r['mass_edges'])
    kf = np.digitize(fuel, r['fuel_edges']) if r['fuel_edges'] else np.zeros(len(scs), int)
    keys = kf * (len(r['mass_edges']) + 1) + km
    return np.array([r['table'][int(k)] for k in keys])


def detail(r, scs, real, B, M):
    feas = B.feasible
    piv = pivot_of(r, scs)
    j = np.array([PIVOTS.index(p) for p in piv])
    mg = M[np.arange(len(scs)), j]
    idx = np.where((mg < 0) & feas)[0]
    print(f"\n=== detail {r['name']} : {len(idx)} echecs sur l espace complet")
    print('  N        :', sorted(Counter(scs[i].n for i in idx).items()))
    print('  avion    :', dict(Counter(scs[i].immat for i in idx)))
    print('  famille  :', dict(Counter(scs[i].family for i in idx)))
    print('  fuel     :', sorted(Counter(int(round(scs[i].fuel_lbs, -2)) for i in idx).items()))
    print('  moy kg   :', sorted(Counter(int(round(np.mean(scs[i].weights_kg), -1)) for i in idx).items()))
    print('  pilote   :', sorted(Counter(int(round(scs[i].pilot_kg, -1)) for i in idx).items()))
    if len(idx):
        print('  depassement max : %.2f in (%.2f %%MAC)' % (-mg[idx].min(), -mg[idx].min() / 66.4 * 100))
    for i in sorted(idx, key=lambda i: mg[i])[:6]:
        s = scs[i]
        print(f'    {s.immat} pil {s.pilot_kg:5.1f} fuel {s.fuel_lbs:6.0f} N={s.n:2d} {s.family:12s} '
              f'moy {np.mean(s.weights_kg):5.1f} kg  pivot {piv[i]}  marge {mg[i]:+.2f} in')
    # distribution des marges
    m = mg[feas]
    print('  marges (espace complet) : min %.2f, 1%% %.2f, 5%% %.2f, mediane %.2f in' %
          (m.min(), np.percentile(m, 1), np.percentile(m, 5), np.median(m)))

    # robustesse : embarquement non trie (permutation aleatoire des masses)
    rng = np.random.default_rng(3)
    orders = {p: order_balanced(p) for p in set(piv)}
    n_fail = n_tot = 0
    n_fail_h = 0
    for i in np.where(feas)[0]:
        s = scs[i]
        o = orders[piv[i]]
        xs = XS[np.asarray(o[:s.n])]
        w = np.array(s.weights_kg) * 2.20462
        for _ in range(3):
            perm = rng.permutation(len(w))
            mom = float((w[perm] * xs).sum() / 1000)
            n_tot += 1
            n_fail += not (B.r_lo[i] - 1e-6 <= mom <= B.r_hi[i] + 1e-6)
    print(f'  embarquement aleatoire (3 tirages/scenario) : {n_fail}/{n_tot} echecs ({100*n_fail/n_tot:.2f} %)')
    # regle inverse (legers d abord)
    st_l = 0
    for i in np.where(feas)[0]:
        s = scs[i]
        xs = XS[np.asarray(orders[piv[i]][:s.n])]
        w = np.sort(np.array(s.weights_kg) * 2.20462)          # legers au pivot
        mom = float((w * xs).sum() / 1000)
        st_l += not (B.r_lo[i] - 1e-6 <= mom <= B.r_hi[i] + 1e-6)
    print(f'  legers d abord : {st_l} echecs')


def self_test(scs, B, M):
    """Compare la marge vectorisee a un calcul direct (caravan_model.evaluate)."""
    from caravan_model import evaluate as ev, fwd_limit, AFT_CG
    rng = np.random.default_rng(0)
    for i in rng.choice(len(scs), 200, replace=False):
        s = scs[i]
        for j in (0, 9, 18):
            st, mass, cg, _ = ev(order_balanced(PIVOTS[j]), s.immat, s.pilot_kg, s.fuel_lbs, s.weights_kg)
            marg = min(cg - fwd_limit(mass), AFT_CG - cg)
            assert abs(marg - M[i, j]) < 1e-6, (s, j, marg, M[i, j])
    print('auto-test ok (200 scenarios x 3 pivots)')


if __name__ == '__main__':
    scs, real, B, M = load()
    self_test(scs, B, M)
    results = search(scs, real, B, M)
    for key in ('masse4', 'fuel2_masse4', 'fuel3_masse3'):
        detail(results[key], scs, real, B, M)
    print('\nOrdres equilibres (bras dans l ordre de remplissage) :')
    for p in PIVOTS:
        print(f'  {p:5.1f} : ' + ' '.join(f'{XS[i]:.0f}' for i in order_balanced(p)))
    (OUT / 'heuristique_finale.json').write_text(json.dumps(results, indent=1))
