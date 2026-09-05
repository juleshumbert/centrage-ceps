"""L'ordre d'origine des planches (filling_order_bon sur les places legacy de
get_slots_bk / get_slots_la) tient-il quand les paras ne sont pas au forfait
mais au poids moyen de la rotation ?

config_ = filling_order_bon donne, pour chaque place de x_list = top + middle +
bottom, son rang de remplissage ; les N premiers paras occupent les places de
rang 1..N. Test sur masses uniformes 60 a 120 kg, carburant 200 a 2224 lbs,
pilotes 80 et 86 kg (puis 65 a 110), avec l'enveloppe complete (limite avant
incluse) et avec le seul critere des planches (limite arriere 40,33 %MAC + MTOW).
"""
import json
from collections import defaultdict
from pathlib import Path

import numpy as np

from caravan_model import (AIRCRAFT, MTOW_LBS, LBS2KG, base_state, fwd_limit, AFT_CG,
                           cg_to_mac, _NS)

ROOT = Path(__file__).resolve().parents[1]
FILLING_ORDER = [13, 18, 11, 3, 1, 5, 9, 19] + [17, 15, 7, 8, 16] + [14, 12, 4, 2, 6, 10, 20]


def legacy_slots(immat):
    nb = 'planche_c208b_A.ipynb' if immat == 'C208B-A' else 'planche_c208b_B.ipynb'
    src = ''.join(json.loads((ROOT / 'reference' / 'notebooks' / nb).read_text())['cells'][5]['source'])
    ns = {}
    exec(src, ns)
    top, mid, bot = ns['get_slots_bk' if immat == 'C208B-A' else 'get_slots_la']()[:3]
    return top + mid + bot


def original_order_arms(immat):
    x_list = legacy_slots(immat)
    return [x_list[FILLING_ORDER.index(r)] for r in range(1, 21)]


def evaluate(immat, arms, masses, fuels, pilots):
    """Retourne les listes d'echecs (N, masse, fuel, pilote, cg, statut) pour les deux criteres."""
    fails_full, fails_aft, feasible = [], [], 0
    cum = np.cumsum(arms)
    for pil in pilots:
        for f in fuels:
            m0, w0 = base_state(immat, pil, f)
            for m in masses:
                w_lbs = m * LBS2KG
                for n in range(1, 21):
                    mass = w0 + n * w_lbs
                    if mass > MTOW_LBS:
                        break
                    feasible += 1
                    cg = (m0 + w_lbs * cum[n - 1] / 1000) / mass * 1000
                    if cg > AFT_CG:
                        fails_aft.append((n, m, f, pil, cg, 'arriere'))
                        fails_full.append((n, m, f, pil, cg, 'arriere'))
                    elif cg < fwd_limit(mass):
                        fails_full.append((n, m, f, pil, cg, 'avant'))
    return fails_full, fails_aft, feasible


def summary(label, fails, feasible):
    byN = defaultdict(int); bym = defaultdict(int); byf = defaultdict(int); st = defaultdict(int)
    for n, m, f, pil, cg, s in fails:
        byN[n] += 1; bym[m] += 1; byf[f] += 1; st[s] += 1
    print(f'  {label}: {len(fails)} echecs / {feasible} ({100*len(fails)/feasible:.1f} %)  {dict(st)}')
    if fails:
        print('     par N     :', ' '.join(f'{n}:{byN[n]}' for n in sorted(byN)))
        print('     par masse :', ' '.join(f'{m}:{bym[m]}' for m in sorted(bym)))
        print('     par fuel  :', ' '.join(f'{f}:{byf[f]}' for f in sorted(byf)))
        worst = max(fails, key=lambda t: abs(t[4] - 202))
        print(f'     pire : N={worst[0]} masse {worst[1]} kg fuel {worst[2]} pilote {worst[3]} -> CG {worst[4]:.2f} in ({cg_to_mac(worst[4]):.2f} %MAC) {worst[5]}')


if __name__ == '__main__':
    fuels = list(range(200, 2224, 100)) + [2224]
    for immat in AIRCRAFT:
        arms = original_order_arms(immat)
        print(f'=== {immat} : ordre d origine (bras) : ' + ' '.join(f'{x}' for x in arms))
        print('    bras moyen des k premiers : ' + ' '.join(f'{np.mean(arms[:k]):.0f}' for k in range(1, 21)))
        for label, masses, pilots in [
            ('forfait 90 kg, pilote 80', [90], [80]),
            ('forfait 80 kg, pilote 86', [80], [86]),
            ('poids moyen 60 a 120 kg (pas 5), pilotes 80/86', list(range(60, 121, 5)), [80, 86]),
            ('poids moyen 70 a 110 kg, pilotes 80/86', list(range(70, 111, 5)), [80, 86]),
            ('poids moyen 70 a 110 kg, pilotes 65 a 110', list(range(70, 111, 5)), [65, 80, 95, 110]),
        ]:
            ff, fa, feas = evaluate(immat, arms, masses, fuels, pilots)
            print(f'  -- {label}')
            summary('enveloppe complete (avant + arriere + MTOW)', ff, feas)
            summary('critere des planches (arriere + MTOW)      ', fa, feas)
        print()
