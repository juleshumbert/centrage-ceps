"""Compromis entre realisme et CG avant : phase 3 avec tolerance croissante."""
import json
from pathlib import Path
from placement_milp import Placement
from caravan_model import fwd_limit

man = json.loads(Path('manifestes/exemple_groupes.json').read_text())
print(f'{"tolerance":>9s} {"cout real.":>10s} {"boites":>7s} {"sortie":>7s} {"CG (in)":>8s} {"lim. avant":>10s} {"marge":>6s} {"marge largage":>13s} {"temps":>6s}')
for tol in (0.0, 0.05, 0.2, 0.5, 1.0, 3.0):
    pl = Placement(man, sequence=True, cohesion='boite', groupes_ordonnes=True, cg_avant=tol > 0, tolerance=tol)
    res = pl.solve(time_limit=60)
    e0 = res['etapes'][0]
    worst = min(res['etapes'][1:-1], key=lambda e: e['marge_in'])
    mt = res['metriques']
    print(f'{tol:9.2f} {res["cout"]:10.2f} {mt["boites"]:7.2f} {mt["sortie"]:7.1f} {e0["cg_in"]:8.2f} {fwd_limit(e0["masse_lbs"]):10.2f} '
          f'{e0["marge_in"]:+6.2f} {worst["marge_in"]:+13.2f} {res["temps"]:6.0f}')
