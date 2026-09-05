"""Effet des accelerations de la phase 2 du binaire C++ (recommandations de
RESUME_RECHERCHES.md) : amorcage par recuit, ecart accepte 5 %, mode rapide.

Variantes comparees sur les 2 exemples et les fiches de juillet a 20 paras :
  A  ancien : sans recuit, gap 1 %, 10 s par phase
  B  nouveau defaut : recuit 1 s, gap 5 %, 10 s
  C  recuit 1 s, gap 5 %, 3 s par phase
  D  --rapide (phase 1 exacte + recuit seul)
Colonnes : cout de realisme final, statut de la phase 2, temps total.
"""
import json
import subprocess
import time
from pathlib import Path

from export_json import export

HERE = Path(__file__).resolve().parent
BIN = HERE.parent / 'solveur' / 'build' / 'placement'
VARIANTS = {
    'A ancien (gap 1 %, sans recuit)': ['--gap', '0.01', '--recuit', '0', '--temps', '10'],
    'B defaut (recuit 1 s, gap 5 %)': ['--temps', '10'],
    'C recuit + gap 5 %, 3 s': ['--temps', '3'],
    'D rapide (recuit seul)': ['--rapide'],
}


def run(man, args):
    inp = export(man, dict(etapes='premier_groupe', marge_avant_min=0.5, tolerance_marge=0.25))
    t0 = time.time()
    r = subprocess.run([str(BIN), '-', '--silencieux'] + args, input=json.dumps(inp), capture_output=True, text=True)
    out = json.loads(r.stdout)
    out['_t'] = time.time() - t0
    return out


manifests = [('exemple_groupes', json.loads((HERE / 'manifestes/exemple_groupes.json').read_text())),
             ('exemple_tandems', json.loads((HERE / 'manifestes/exemple_tandems.json').read_text()))]
for p in sorted((HERE / 'output/sticks').glob('2026-*.json')):
    man = json.loads(p.read_text())['manifeste']
    if len(man['paras']) == 20:
        manifests.append((p.stem, man))
manifests = manifests[:8]
print(f'{"manifeste":16s} {"N":>2s} | ' + ' | '.join(f'{v[:22]:>22s}' for v in VARIANTS))
print(f'{"":16s} {"":>2s} | ' + ' | '.join(f'{"cout / statut / t":>22s}' for _ in VARIANTS))
tot = {v: [0.0, 0.0] for v in VARIANTS}
for name, man in manifests:
    cells = []
    for v, args in VARIANTS.items():
        out = run(man, args)
        if not out['ok']:
            cells.append(f'{"echec":>22s}')
            continue
        st = out['phase2'].replace('temps limite', 'limite').replace('recuit (mode rapide)', 'recuit')[:8]
        cells.append(f'{out["cout_realisme"]:6.1f} {st:>8s} {out["_t"]:5.1f}s')
        tot[v][0] += out['cout_realisme']; tot[v][1] += out['_t']
    print(f'{name:16s} {len(man["paras"]):2d} | ' + ' | '.join(cells), flush=True)
print(f'{"total":16s} {"":>2s} | ' + ' | '.join(f'{tot[v][0]:6.1f} {"":>8s} {tot[v][1]:5.1f}s' for v in VARIANTS))
