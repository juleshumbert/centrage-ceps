"""Compare le binaire Rust (placement_rs/placement) au solveur Python (placement_milp)
sur les memes manifestes : marge maximale (phase 1) et cout de realisme (phase 2)."""
import json
import subprocess
import sys
import time
from pathlib import Path

from export_json import export
from placement_milp import Placement

HERE = Path(__file__).resolve().parent
BIN = HERE / 'placement_rs' / 'placement'


def run_rs(man, ordonnes, temps=1.5):
    inp = export(man, dict(groupes_ordonnes=ordonnes, temps_max_s=temps))
    t0 = time.time()
    r = subprocess.run([str(BIN), '-'], input=json.dumps(inp), capture_output=True, text=True)
    out = json.loads(r.stdout)
    out['_temps'] = time.time() - t0
    return out


def run_py(man, ordonnes, temps=10.0):
    pl = Placement(man, sequence=True, groupes_ordonnes=ordonnes, marge_cible=0.5)
    res = pl.solve(time_limit=temps)
    return pl, res


manifests = [('exemple_groupes', json.loads((HERE / 'manifestes/exemple_groupes.json').read_text())),
             ('exemple_tandems', json.loads((HERE / 'manifestes/exemple_tandems.json').read_text()))]
sticks = sorted((HERE / 'output/sticks').glob('2026-07-1*.json'))[:6]
for p in sticks:
    manifests.append((p.stem, json.loads(p.read_text())['manifeste']))

print(f'{"manifeste":18s} {"N":>2s} {"ord":>3s} | {"marge max py":>12s} {"rs":>7s} {"prouve":>6s} | {"cout py":>8s} {"rs":>7s} | {"boites py/rs":>13s} {"sortie py/rs":>13s} | {"t py":>5s} {"t rs":>5s}')
for name, man in manifests:
    for ordonnes in (False, True):
        pl, res = run_py(man, ordonnes)
        rs = run_rs(man, ordonnes)
        if not res['ok'] or not rs['ok']:
            print(f'{name:18s} {len(man["paras"]):2d} {str(ordonnes)[0]:>3s} | py: {res.get("message", "ok")[:40]} | rs: {rs.get("message", "ok")[:40]}')
            continue
        mt = res['metriques']
        print(f'{name:18s} {len(man["paras"]):2d} {str(ordonnes)[0]:>3s} | {res["mu_max"]:12.2f} {rs["marge_max"]:7.2f} {str(rs["marge_max_prouvee"])[0]:>6s} | '
              f'{res["cout"]:8.2f} {rs["cout_realisme"]:7.2f} | {mt["boites"]:5.2f} / {rs["boites"]:5.2f} {mt["sortie"]:5.1f} / {rs["ecart_sortie"]:5.1f} | '
              f'{res["temps"]:5.1f} {rs["_temps"]:5.1f}')
        sys.stdout.flush()
