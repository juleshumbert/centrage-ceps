"""Chronometre le binaire Rust sur les manifestes des fiches de juillet (output/sticks/*.json)
et compare aux resultats Python de resultats.csv quand ils existent."""
import csv
import json
import subprocess
import time
from pathlib import Path

from export_json import export

HERE = Path(__file__).resolve().parent
BIN = HERE / 'placement_rs' / 'placement'
rows = []
for p in sorted((HERE / 'output/sticks').glob('2026-*.json')):
    man = json.loads(p.read_text())['manifeste']
    inp = export(man, dict(temps_max_s=1.5, groupes_ordonnes=False))
    t0 = time.time()
    r = json.loads(subprocess.run([str(BIN), '-'], input=json.dumps(inp), capture_output=True, text=True).stdout)
    rows.append(dict(fichier=p.stem, n=len(man['paras']), ok=r['ok'], marge_max=r.get('marge_max'), prouvee=r.get('marge_max_prouvee'),
                     marge=r.get('marge'), cout=r.get('cout_realisme'), boites=r.get('boites'), sortie=r.get('ecart_sortie'),
                     temps=time.time() - t0, temps_phase1=r.get('temps_phase1_s')))
with open(HERE / 'output/sticks/resultats_rs.csv', 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
import numpy as np
ok = [r for r in rows if r['ok']]
t = np.array([r['temps'] for r in ok]); mg = np.array([r['marge_max'] for r in ok])
print(f"{len(rows)} manifestes, {len(ok)} places par le binaire ; temps mediane {np.median(t):.1f} s, max {t.max():.1f} s ; "
      f"marge max prouvee {sum(r['prouvee'] for r in ok)}/{len(ok)} ; marge max mediane {np.median(mg):.2f} in")
for r in rows:
    if not r['ok']:
        print('  echec', r['fichier'])
