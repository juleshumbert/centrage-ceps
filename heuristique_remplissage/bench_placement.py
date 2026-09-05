"""Compare les formulations et les coupes sur les manifestes d'exemple :
boite / ancre, avec ou sans groupes ordonnes, puis l'effet de la phase 3 (CG avant)."""
import json
import sys
from pathlib import Path

from placement_milp import Placement

T = float(sys.argv[1]) if len(sys.argv) > 1 else 60.0
for name in ('exemple_groupes', 'exemple_tandems'):
    man = json.loads(Path(f'manifestes/{name}.json').read_text())
    print(f'=== {name} ({len(man["paras"])} paras), temps limite {T:.0f} s par phase')
    print(f'  {"variante":34s} {"ph.2 (s)":>9s} {"etat":>16s} {"boites":>7s} {"sortie":>7s} {"CG (in)":>8s} {"marge":>6s}')
    for cohesion in ('boite', 'ancre'):
        for ordonnes in (False, True):
            for cg_avant in (False, True):
                if cg_avant and not (cohesion == 'boite' and ordonnes):
                    continue
                pl = Placement(man, sequence=True, cohesion=cohesion, groupes_ordonnes=ordonnes, cg_avant=cg_avant)
                res = pl.solve(time_limit=T)
                label = f'{cohesion}{" + ordonnes" if ordonnes else ""}{" + CG avant" if cg_avant else ""}'
                if not res['ok']:
                    print(f'  {label:34s} ECHEC : {res["message"]}')
                    continue
                etat = 'optimum' if res['optimal'] else f'ecart {res["gap"]:.0%}'
                e0 = res['etapes'][0]
                extra = f' (ph.3 {res["temps_phase3"]:.0f} s{", optimum" if res.get("optimal3") else ""})' if cg_avant else ''
                print(f'  {label:34s} {res["temps_phase2"]:9.1f} {etat:>16s} {res["metriques"]["boites"]:7.2f} '
                      f'{res["metriques"]["sortie"]:7.1f} {e0["cg_in"]:8.2f} {e0["marge_in"]:+6.2f}{extra}')
                sys.stdout.flush()
