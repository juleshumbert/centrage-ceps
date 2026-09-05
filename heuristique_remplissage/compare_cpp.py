"""Valide le binaire C++ (placement_cpp/build/placement, HiGHS embarque) :
- sur les manifestes d'exemple et des fiches de juillet ;
- verification independante du placement rendu avec placement_milp.Placement.check
  (marges par etape), tandems (passager devant le porteur) et ordre des groupes ;
- comparaison avec le MILP Python en marge symetrique (reference de faisabilite).

Objectif du binaire : marge arriere maximale au decollage sous marge avant >= marge_avant_min
a toutes les etapes, puis realisme a marge arriere >= max - tolerance.
"""
import json
import subprocess
import sys
import time
from pathlib import Path

from caravan_model import fwd_limit, AFT_CG
from export_json import export
from placement_milp import Placement

HERE = Path(__file__).resolve().parent
BIN = HERE / 'placement_cpp' / 'build' / 'placement'


def run_cpp(man, **options):
    inp = export(man, dict(temps_max_s=10.0, marge_avant_min=0.5, tolerance_marge=0.25, **options))
    t0 = time.time()
    r = subprocess.run([str(BIN), '-'], input=json.dumps(inp), capture_output=True, text=True)
    if r.returncode != 0 or not r.stdout.strip():
        return dict(ok=False, message='binaire : ' + r.stderr[-300:], _temps=time.time() - t0)
    out = json.loads(r.stdout)
    out['_temps'] = time.time() - t0
    return out


def verify(man, out, ordonnes):
    """Recalcule les marges avec le modele Python et verifie tandems / ordre."""
    pl = Placement(man, sequence=True, groupes_ordonnes=ordonnes)
    names = [p['nom'] for p in man['paras']]
    seat = [int(next(q['place'] for q in out['placement'] if q['nom'] == n)) for n in names]
    et = pl.check(seat)
    fwd_min = min(e['cg_in'] - fwd_limit(e['masse_lbs']) for e in et[:-1])
    aft0 = AFT_CG - et[0]['cg_in']
    tandem_ok = all(seat[q] == seat[po] - 1 and pl.ys[seat[po]] != 0 and seat[po] != 0
                    for po, q in [(i, j) for i, p in enumerate(man['paras']) for j, r in enumerate(man['paras'])
                                  if p.get('tandem') and p.get('tandem') == r.get('tandem') and p.get('role') == 'porteur' and r.get('role') == 'passager'])
    order_ok = True
    if ordonnes:
        gs = {}
        for i, p in enumerate(man['paras']):
            if p.get('groupe'):
                gs.setdefault(p['groupe'], []).append(i)
        gs = {g: m for g, m in gs.items() if len(m) >= 2}
        for g, mg in gs.items():
            for h, mh in gs.items():
                rg = min(man['paras'][i]['sortie'] for i in mg); rh = min(man['paras'][i]['sortie'] for i in mh)
                if rg < rh and min(pl.xs[seat[i]] for i in mg) < max(pl.xs[seat[i]] for i in mh) - 1e-6:
                    order_ok = False
    return dict(aft0=aft0, fwd_min=fwd_min, tandem_ok=tandem_ok, order_ok=order_ok, len_seats=len(set(seat)) == len(seat))


if __name__ == '__main__':
    manifests = [('exemple_groupes', json.loads((HERE / 'manifestes/exemple_groupes.json').read_text())),
                 ('exemple_tandems', json.loads((HERE / 'manifestes/exemple_tandems.json').read_text()))]
    for p in sorted((HERE / 'output/sticks').glob('2026-07-1*.json'))[:6]:
        manifests.append((p.stem, json.loads(p.read_text())['manifeste']))
    print(f'{"manifeste":18s} {"N":>2s} {"ord":>3s} | {"marge ar. max":>13s} {"ar. rendue":>10s} {"av. min":>7s} {"verif av/ar":>12s} | {"ph1":>8s} {"ph2":>12s} {"boites":>6s} {"sortie":>6s} | {"t (s)":>5s} | {"py mu sym":>9s}')
    for name, man in manifests:
        for ordonnes in (False, True):
            out = run_cpp(man, groupes_ordonnes=ordonnes)
            if not out['ok']:
                print(f'{name:18s} {len(man["paras"]):2d} {str(ordonnes)[0]:>3s} | {out.get("message", "?")[:80]}  ({out["_temps"]:.1f} s)')
                continue
            v = verify(man, out, ordonnes)
            pl = Placement(man, sequence=True, groupes_ordonnes=ordonnes)
            res = pl.solve(time_limit=5)
            flags = ('' if v['tandem_ok'] else ' TANDEM!') + ('' if v['order_ok'] else ' ORDRE!') + ('' if v['len_seats'] else ' DOUBLON!')
            print(f'{name:18s} {len(man["paras"]):2d} {str(ordonnes)[0]:>3s} | {out["marge_arriere_max"]:13.2f} {out["marge_arriere"]:10.2f} {out["marge_avant_min_obtenue"]:7.2f} '
                  f'{v["fwd_min"]:5.2f}/{v["aft0"]:5.2f}{flags} | {out["phase1"]:>8s} {out["phase2"][:12]:>12s} {out["boites"]:6.2f} {out["ecart_sortie"]:6.1f} | {out["_temps"]:5.1f} | '
                  f'{res.get("mu_max", float("nan")):9.2f}')
            sys.stdout.flush()
