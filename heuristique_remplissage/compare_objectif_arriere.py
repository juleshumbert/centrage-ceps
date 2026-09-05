"""Objectif « marge arriere » : compare le binaire Rust (recuit + recherche exacte) au
binaire C++ (HiGHS) sur les memes manifestes.

Rust : options objectif="marge_arriere", etapes="premier_groupe" (contrainte avant au
decollage et apres la sortie du premier groupe) puis etapes="toutes" (apres chaque sortie).
C++ : il n'a pas (encore) d'option `etapes` : il impose la marge avant apres chaque sortie,
ce qui correspond au mode "toutes" du Rust. La colonne Rust "toutes" est donc la
comparaison a modele egal ; "premier_groupe" est le modele demande par Jules.
Les marges Rust sont recalculees avec placement_milp.Placement.check.
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
RS = HERE / 'placement_rs' / 'placement'
CPP = HERE.parent / 'solveur' / 'build' / 'placement'
_cpp_src = (HERE.parent / 'solveur' / 'src' / 'placement.cpp').read_text()
CPP_HAS_ETAPES = any(k in _cpp_src for k in ('value("etapes"', 'o["etapes"]', 'opt(o, "etapes"', 'contains("etapes")'))


def run(binary, man, **options):
    inp = export(man, {**dict(objectif='marge_arriere', etapes='premier_groupe', marge_avant_min=0.5,
                              tolerance_marge=0.25, temps_max_s=1.5), **options})
    t0 = time.time()
    r = subprocess.run([str(binary), '-'], input=json.dumps(inp), capture_output=True, text=True)
    try:
        out = json.loads(r.stdout)
    except json.JSONDecodeError:
        out = dict(ok=False, message='sortie illisible : ' + r.stderr[-200:])
    out['_temps'] = time.time() - t0
    return out


def verify_rs(man, out):
    """Marges recalculees en Python : decollage, apres le premier groupe, minimum sur toutes les sorties."""
    pl = Placement(man, sequence=True)
    names = [p['nom'] for p in man['paras']]
    seat = [int(next(q['place'] for q in out['placement'] if q['nom'] == n)) for n in names]
    et = pl.check(seat)
    first = min(p['sortie'] for p in man['paras'] if p.get('sortie') is not None)
    n_first = sum(1 for p in man['paras'] if p.get('sortie') == first)
    fwd = lambda e: e['cg_in'] - fwd_limit(e['masse_lbs'])
    return dict(aft0=AFT_CG - et[0]['cg_in'], fwd0=fwd(et[0]), fwd_first=fwd(et[n_first]),
                fwd_all=min(fwd(e) for e in et[:-1]))


if __name__ == '__main__':
    manifests = [('exemple_groupes', json.loads((HERE / 'manifestes/exemple_groupes.json').read_text())),
                 ('exemple_tandems', json.loads((HERE / 'manifestes/exemple_tandems.json').read_text()))]
    sticks = sorted((HERE / 'output/sticks').glob('2026-*.json'))
    six = [p for p in sticks if p.stem.startswith('2026-07-1')][:6]
    n20 = [p for p in sticks if len(json.loads(p.read_text())['manifeste']['paras']) == 20]
    for p in six + n20:
        manifests.append((p.stem, json.loads(p.read_text())['manifeste']))
    print(('C++ : option etapes presente' if CPP_HAS_ETAPES else
           'C++ : pas d option etapes, il impose la marge avant apres chaque sortie (= mode "toutes")'))
    hdr = (f'{"manifeste":16s} {"N":>2s} | {"Rust 1er grp":>12s} {"prv":>3s} {"av0/av1g/avT":>16s} {"boit":>5s} {"sort":>4s} {"t":>4s} | '
           f'{"Rust toutes":>11s} {"prv":>3s} {"boit":>5s} {"sort":>4s} {"t":>4s} | {"C++ (toutes)":>12s} {"av.min":>6s} {"ph2":>6s} {"boit":>5s} {"sort":>4s} {"t":>5s}')
    print(hdr)
    for name, man in manifests:
        n = len(man['paras'])
        a = run(RS, man, etapes='premier_groupe')
        b = run(RS, man, etapes='toutes')
        c = run(CPP, man, temps_max_s=10.0)
        def col_rs(o):
            if not o.get('ok'):
                return f'{o.get("message", "?")[:30]:>30s}'
            return f'{o["marge_max"]:12.2f} {str(o["marge_max_prouvee"])[0]:>3s}'
        va = verify_rs(man, a) if a.get('ok') else None
        line = f'{name:16s} {n:2d} | '
        if a.get('ok'):
            line += (f'{a["marge_max"]:12.2f} {str(a["marge_max_prouvee"])[0]:>3s} '
                     f'{va["fwd0"]:5.2f}/{va["fwd_first"]:4.2f}/{va["fwd_all"]:4.2f} {a["boites"]:5.2f} {a["ecart_sortie"]:4.0f} {a["_temps"]:4.1f} | ')
        else:
            line += f'{a.get("message", "?")[:50]:50s} | '
        if b.get('ok'):
            line += f'{b["marge_max"]:11.2f} {str(b["marge_max_prouvee"])[0]:>3s} {b["boites"]:5.2f} {b["ecart_sortie"]:4.0f} {b["_temps"]:4.1f} | '
        else:
            line += f'{b.get("message", "?")[:32]:32s} | '
        if c.get('ok'):
            line += (f'{c["marge_arriere_max"]:12.2f} {c["marge_avant_min_obtenue"]:6.2f} {c["phase2"][:6]:>6s} '
                     f'{c["boites"]:5.2f} {c["ecart_sortie"]:4.0f} {c["_temps"]:5.1f}')
        else:
            line += f'{c.get("message", "?")[:45]}'
        print(line)
        sys.stdout.flush()
