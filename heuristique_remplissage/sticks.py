"""Fiches de stick (PDF du logiciel club) -> manifestes -> placement MILP.

Parseur : texte `pdftotext -layout`. Bloc des paras entre la premiere ligne
portant la hauteur (4000) et « Masse aéronef ». Chaque ligne membre : [niveau]
nom [voile | Tdm] [couleurs] discipline [libelle de groupe « X n°k »]. Les
libelles de groupe sont des cellules fusionnees, rendues au milieu du bloc
(ligne seule ou en fin d'une ligne membre) : chaque membre est rattache au
libelle le plus proche de meme famille. Le passager tandem est marque « Tdm »
(pas de voile), le porteur a la discipline « Tandem » avec sa voile.

Masses : la fiche ne donne que la masse totale des paras. Masses individuelles
tirees selon une loi normale (ecart type --sigma, 12 kg par defaut), bornees
55 a 130 kg, renormalisees pour respecter la masse totale declaree, graine =
numero de stick (reproductible).

Ordre de sortie (demande) : VR, puis freefly, puis eleves, puis PAC, puis
tandem, puis wingsuit. Hypotheses : « Libre » et « Largueur » avec les eleves ;
Track et Derive juste apres le freefly ; Suivi Vdo et Video avec le freefly ;
Prepa test avec le VR. Dans une classe, les groupes sortent par numero puis les
solos dans l'ordre de la fiche.

Usage : python3 sticks.py [--dossier D] [--sigma 12] [--temps 10] [--procs 8] [--max N]
"""
import argparse
import collections
import csv
import json
import re
import subprocess
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

from caravan_model import AIRCRAFT, MTOW_LBS, LBS2KG
from placement_milp import Placement

OUT = Path(__file__).resolve().parent / 'output' / 'sticks'
DEFAULT_DIR = Path('/home/jules/Documents/mtow-juillet/fiche_avionnage_juillet/fiche_avionnage')

LEVELS = {'A', 'B', 'B+', 'BP', 'BPA', 'C', 'D', 'MF', 'Init', 'Élève', 'Eleve', 'BE/DE', 'Tdm'}
# famille de discipline -> (famille de libelle exacte, famille de base, classe de sortie)
CLASSES = {'VR': 1, 'FF': 2, 'TRACK': 2.5, 'ELEVE': 3, 'PAC': 4, 'TANDEM': 5, 'WS': 6}


def family(label):
    """Famille exacte d'un libelle ou d'une discipline, famille de base, classe."""
    t = label.strip().lower()
    t = re.sub(r"\s*n°\s*\d+$", '', t)
    if t in ('libre', 'largueur', 'psv solo', 'psv'):
        return t, 'ELEVE', 3
    if t in ('dérive', 'derive'):
        return 'dérive', 'TRACK', 2.5
    if t == '1er solo pac':
        return '1er solo pac', 'PAC', 4
    if t == 'ff solo':
        return 'ff solo', 'FF', 2
    if 'tandem' in t or 'tdm' in t:
        return 'tandem', 'TANDEM', 5
    if t in ('wingsuit', 'ws', 'init ws') or 'ws' in t.split():
        return 'ws' if t != 'init ws' else 'init ws', 'WS', 6
    if 'pac' in t or t == 'psv':
        return ('init pac' if 'init' in t else 'pac'), 'PAC', 4
    if 'track' in t or 'dérive' in t or 'derive' in t:
        return 'track', 'TRACK', 2.5
    if 'ff' in t.split() or t == 'ff' or 'freefly' in t:
        if 'init' in t:
            return 'init ff', 'FF', 2
        if 'anim' in t:
            return 'anim ff', 'FF', 2
        return 'ff', 'FF', 2
    if 'vdo' in t or 'vidéo' in t or 'video' in t:
        return 'suivi vdo', 'FF', 2
    if 'vr' in t.split():
        if 'init' in t:
            return 'init vr', 'VR', 1
        if 'anim' in t:
            return 'anim vr', 'VR', 1
        return 'vr', 'VR', 1
    if 'prépa test' in t or 'prepa test' in t:
        return t, 'VR', 1
    return t, None, None          # equipe nommee ou inconnu : famille a deduire du libelle


def parse_sheet(txt):
    r = dict(warn=[])
    m = re.search(r"(F-[A-Z]{4})\s+(.+?)\s*\(stick n°\s*(\d+)\)", txt)
    if not m:
        r['warn'].append('entete'); return r
    r['immat'], r['avion'], r['stick'] = m.group(1), m.group(2).strip(), int(m.group(3))
    m = re.search(r"Date de validation\s*:\s*(\d{2})/(\d{2})/(\d{4})\s+(\d{2}):(\d{2})", txt)
    r['date'] = f"{m.group(3)}-{m.group(2)}-{m.group(1)} {m.group(4)}:{m.group(5)}" if m else ''
    m = re.search(r"Total\s+(\d+)\s*pax\s*\((\d+)\s*groupes?\s*/\s*(\d+)\s*voiles?\)", txt)
    if m:
        r['nb_pax'], r['nb_groupes'], r['nb_voiles'] = int(m.group(1)), int(m.group(2)), int(m.group(3))
    else:
        r['warn'].append('total_pax')

    def grab(label):
        m = re.search(re.escape(label) + r"\s+([\d ]+(?:,\d+)?)\s*kg", txt)
        return float(m.group(1).replace(' ', '').replace(',', '.')) if m else None
    r['ew_kg'] = grab('Masse aéronef'); r['pilote_kg'] = grab('Masse pilote équipé')
    r['paras_kg'] = grab('Masse parachutistes équipés'); r['total_kg'] = grab('Masse totale au décollage')
    m = re.search(r"Masse carburant au décollage\s+([\d ]+(?:,\d+)?)\s*kg\s*\(([\d ]+)\s*L\)\s+([\d ]+(?:,\d+)?)\s*lb", txt)
    if m:
        r['fuel_kg'] = float(m.group(1).replace(' ', '').replace(',', '.'))
        r['fuel_l'] = float(m.group(2).replace(' ', ''))
        r['fuel_lbs'] = float(m.group(3).replace(' ', '').replace(',', '.'))
    else:
        r['fuel_lbs'] = None; r['warn'].append('carburant_absent')

    # bloc des paras
    lines = txt.splitlines()
    start = next((i for i, l in enumerate(lines) if re.match(r"^\s*\d{3,4}\s{2,}\S", l) and 'pax' not in l), None)
    end = next((i for i, l in enumerate(lines) if 'Masse aéronef' in l), None)
    if start is None or end is None:
        r['warn'].append('bloc_paras'); return r
    # colonnes : (offset, texte). La colonne discipline est la derniere colonne
    # la plus frequente ; tout ce qui commence nettement plus a droite est un
    # libelle de groupe (« FF n°1 » ou un nom d'equipe).
    parsed = []
    for i in range(start, end):
        cols = [(m.start(), m.group(0)) for m in re.finditer(r"\S+(?: \S+)*", lines[i])]
        if cols and re.fullmatch(r"\d{3,4}", cols[0][1]):
            cols = cols[1:]
        if cols:
            parsed.append((i, cols))
    from collections import Counter
    last_offsets = Counter(c[-1][0] for _, c in parsed if len(c) >= 2)
    disc_off = last_offsets.most_common(1)[0][0] if last_offsets else 0
    members, labels = [], []
    for i, cols in parsed:
        label = None
        if cols[-1][0] > disc_off + 6:
            label = cols[-1][1]; cols = cols[:-1]
        if label and not cols:
            labels.append(dict(line=i, text=label)); continue
        if not cols:
            continue
        cols = [c[1] for c in cols]
        level = cols[0] if cols[0] in LEVELS else None
        rest = cols[1:] if level else cols
        # niveau colle au nom ("BPA Prenom Nom")
        if level is None and rest and rest[0].split(' ', 1)[0] in LEVELS and len(rest[0].split(' ', 1)) == 2:
            level, rest = rest[0].split(' ', 1)[0], [rest[0].split(' ', 1)[1]] + rest[1:]
        if len(rest) < 2:
            continue
        name, disc = re.sub(r"^[^\w]+", '', rest[0]).strip(), rest[-1]
        middle = rest[1:-1]
        members.append(dict(line=i, nom=name, niveau=level, discipline=disc,
                            passager_tdm=any(c.strip() == 'Tdm' for c in middle) or level == 'Tdm', groupe=None))
        if label:
            labels.append(dict(line=i, text=label))
    # rattachement des membres aux libelles
    for k, lab in enumerate(labels, 1):
        lab['fam'], lab['base'], lab['classe'] = family(lab['text'])
        m = re.search(r"n°\s*(\d+)", lab['text'])
        lab['num'] = int(m.group(1)) if m else 20 + k
        lab['key'] = lab['text'].strip().lower()
        if any(l['key'] == lab['key'] for l in labels[:k - 1]):
            lab['key'] += f" (l{lab['line']})"
    SOLO = ('libre', 'largueur', 'ff solo', 'psv solo', 'psv', '1er solo pac', 'dérive')
    if not any(l['base'] == 'WS' for l in labels):
        SOLO = SOLO + ('ws', 'init ws')        # wingsuit sans libelle WS : solo
    for mb in members:
        mb['fam'], mb['base'], mb['classe'] = family(mb['discipline'])

    def assign_centered():
        # Le libelle est une cellule fusionnee centree sur son bloc : si le bloc commence
        # a la ligne s et le libelle est a la ligne L, il finit a la ligne 2L - s.
        for mb in members:
            mb['groupe'] = None
        blk = [mb for mb in members if mb['fam'] not in SOLO]
        pos = 0
        for lab in sorted(labels, key=lambda l: l['line']):
            if pos >= len(blk):
                break
            s_line = blk[pos]['line']
            e_line = 2 * lab['line'] - s_line
            chosen = [mb for mb in blk[pos:] if mb['line'] <= e_line + 0.5] or [blk[pos]]
            for mb in chosen:
                mb['groupe'] = lab['key']
            pos += len(chosen)

    def assign_nearest():
        for mb in members:
            mb['groupe'] = None
            fam, base = mb['fam'], mb['base']
            if fam in SOLO:
                continue
            video = 'vdo' in fam or 'vid' in fam
            cands = [l for l in labels if l['fam'] == fam]
            if not cands and base is not None and not video:
                cands = [l for l in labels if l['base'] == base]
            if not cands and (base is None or video):
                cands = labels
            if cands:
                mb['groupe'] = min(cands, key=lambda l: (abs(l['line'] - mb['line']), l['line']))['key']

    def n_groups():
        return len({m['groupe'] for m in members if m['groupe']}) + sum(1 for m in members if not m['groupe'])

    assign_centered()
    method = 'centre'
    if 'nb_groupes' in r and n_groups() != r['nb_groupes']:
        keep = [m['groupe'] for m in members]
        assign_nearest()
        method = 'proche'
        if n_groups() != r['nb_groupes']:
            for m, g in zip(members, keep):
                m['groupe'] = g
            method = 'centre?'
    r['methode_groupes'] = method
    for mb in members:
        if mb['groupe'] and mb['base'] is None:
            lab = next(l for l in labels if l['key'] == mb['groupe'])
            mb['base'], mb['classe'] = lab['base'], lab['classe']
        if mb['base'] is None:
            mb['base'], mb['classe'] = 'ELEVE', 3
        if mb['groupe'] and ('vdo' in mb['fam'] or 'vid' in mb['fam']):
            lab = next(l for l in labels if l['key'] == mb['groupe'])
            if lab['base'] is not None:
                mb['base'], mb['classe'] = lab['base'], lab['classe']   # le video sort avec son groupe
    r['membres'], r['libelles'] = members, labels
    if 'nb_pax' in r:
        if len(members) != r['nb_pax']:
            r['warn'].append(f"pax {len(members)}/{r['nb_pax']}")
        if n_groups() != r['nb_groupes']:
            r['warn'].append(f"groupes {n_groups()}/{r['nb_groupes']}")
    return r


def build_manifest(r, sigma=12.0, seed=None):
    members = r['membres']
    n = len(members)
    rng = np.random.default_rng(r['stick'] if seed is None else seed)
    mean = r['paras_kg'] / n
    kg = np.clip(rng.normal(mean, sigma, n), 55, 130)
    for _ in range(3):
        kg = np.clip(kg * r['paras_kg'] / kg.sum(), 55, 130)
    kg = kg * r['paras_kg'] / kg.sum()
    # ordre de sortie : classe, puis numero de groupe, puis solos dans l'ordre
    solo_rank = 0
    paras = []
    for i, mb in enumerate(members):
        if mb['groupe']:
            lab = next(l for l in r['libelles'] if l['key'] == mb['groupe'])
            sortie = mb['classe'] * 100 + lab['num']
        else:
            solo_rank += 1
            sortie = mb['classe'] * 100 + 50 + solo_rank
        p = dict(nom=mb['nom'], kg=round(float(kg[i]), 1), sortie=sortie,
                 discipline=mb['discipline'], niveau=mb['niveau'])
        if mb['groupe']:
            p['groupe'] = mb['groupe']
        paras.append(p)
    # etiquette lisible : rang de sortie 1, 2, 3... (ex aequo dans un groupe)
    ranks = {v: k + 1 for k, v in enumerate(sorted({p['sortie'] for p in paras}))}
    for p in paras:
        p['etiquette'] = ranks[p['sortie']]
    # tandems : dans un groupe tandem, porteur = discipline Tandem avec voile, passager = Tdm
    for g in {p.get('groupe') for p in paras if p.get('groupe')}:
        idx = [i for i, p in enumerate(paras) if p.get('groupe') == g]
        pas = [i for i in idx if members[i]['passager_tdm']]
        por = [i for i in idx if not members[i]['passager_tdm'] and members[i]['fam'] == 'tandem'
               and 'vdo' not in members[i]['discipline'].lower()]
        for k, (ip, ipo) in enumerate(zip(pas, por)):
            tid = f"{g} t{k + 1}"
            paras[ip].update(tandem=tid, role='passager'); paras[ipo].update(tandem=tid, role='porteur')
    return dict(immat=r['immat'], pilote_kg=r['pilote_kg'], fuel_lbs=r['fuel_lbs'], paras=paras,
                stick=r['stick'], date=r['date'], paras_kg=r['paras_kg'], sigma=sigma)


def run_one(args):
    path, sigma, temps, draw, seed = args
    txt = subprocess.run(['pdftotext', '-layout', str(path), '-'], capture_output=True, text=True).stdout
    r = parse_sheet(txt)
    row = dict(fichier=path.name, immat=r.get('immat'), stick=r.get('stick'), date=r.get('date'),
               warn=';'.join(r['warn']))
    if r.get('immat') not in AIRCRAFT or r.get('fuel_lbs') is None or 'membres' not in r:
        row['statut'] = 'ignore (' + (row['warn'] or 'avion non Caravan') + ')'
        return row
    man = build_manifest(r, sigma, seed=None if seed is None else r['stick'] * 100 + seed)
    row['tirage'] = seed
    row.update(n=len(man['paras']), groupes=len({p.get('groupe') for p in man['paras'] if p.get('groupe')}),
               tandems=sum(1 for p in man['paras'] if p.get('role') == 'porteur'),
               fuel_lbs=man['fuel_lbs'], pilote_kg=man['pilote_kg'], paras_kg=r['paras_kg'])
    _, w0 = __import__('caravan_model').base_state(man['immat'], man['pilote_kg'], man['fuel_lbs'])
    row['masse_lbs'] = w0 + r['paras_kg'] * LBS2KG
    t0 = time.time()
    first_mu = None
    for ordonnes, sequence in ((True, True), (False, True), (True, False), (False, False)):
        pl = Placement(man, sequence=sequence, groupes_ordonnes=ordonnes, marge_cible=0.5)
        res = pl.solve(time_limit=temps)
        if first_mu is None and 'mu_max' in res:
            first_mu = res['mu_max']
        if res['ok'] or 'MTOW' in res.get('message', ''):
            break
    row['temps'] = time.time() - t0
    row['mu_max_largage'] = first_mu          # marge max avec la contrainte de largage
    if not res['ok']:
        row['statut'] = ('ECHEC MTOW : ' if 'MTOW' in res['message'] else 'ECHEC CG : ') + res['message']
        if 'mu_max' in res:
            row['mu_max'] = res['mu_max']
        return row
    e0 = res['etapes'][0]
    worst = min(res['etapes'][1:-1], key=lambda e: e['marge_in']) if len(res['etapes']) > 2 else e0
    statut = 'ok'
    if not sequence:
        statut += ' sans contrainte de largage'
    if not ordonnes:
        statut += ' (groupes non ordonnes)'
    row.update(statut=statut, sequence=sequence, mu_max=res['mu_max'],
               cg_in=e0['cg_in'], mac=e0['mac'], marge_dec=e0['marge_in'], marge_largage=worst['marge_in'],
               optimal=res['optimal'], gap=res['gap'], boites=res['metriques']['boites'],
               ecart_sortie=res['metriques']['sortie'])
    if draw:
        OUT.mkdir(parents=True, exist_ok=True)
        pl.draw(res, OUT / f"{path.stem}.png",
                title=f"{man['immat']} stick {man['stick']} du {man['date']}, {man['fuel_lbs']:.0f} lbs, {len(man['paras'])} paras "
                      f"(masses tirees, sigma {sigma:.0f} kg) : CG {e0['cg_in']:.1f} in, marge {e0['marge_in']:+.2f} in, "
                      f"largage {worst['marge_in']:+.2f} in")
        (OUT / f"{path.stem}.json").write_text(json.dumps(dict(manifeste=man, places=res['seat_of']), indent=1, ensure_ascii=False))
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--dossier', default=str(DEFAULT_DIR))
    ap.add_argument('--sigma', type=float, default=12.0)
    ap.add_argument('--temps', type=float, default=10.0)
    ap.add_argument('--procs', type=int, default=8)
    ap.add_argument('--max', type=int, default=None)
    ap.add_argument('--sans-plans', action='store_true')
    ap.add_argument('--fichier', default=None, help='une seule fiche (test)')
    ap.add_argument('--tirages', type=int, default=1, help='nombre de tirages de masses par fiche')
    a = ap.parse_args()
    files = sorted(p for p in Path(a.dossier).iterdir() if p.is_file())
    if a.fichier:
        files = [Path(a.fichier)]
    if a.max:
        files = files[:a.max]
    OUT.mkdir(parents=True, exist_ok=True)
    seeds = [None] if a.tirages == 1 else list(range(a.tirages))
    jobs = [(p, a.sigma, a.temps, not a.sans_plans and sd in (None, 0), sd) for p in files for sd in seeds]
    t0 = time.time()
    rows = []
    with Pool(a.procs) as pool:
        for k, row in enumerate(pool.imap_unordered(run_one, jobs), 1):
            rows.append(row)
            print(f"[{k}/{len(jobs)}] {row['fichier']:22s} {row.get('immat', '')} N={row.get('n', '')} {row['statut']}"
                  + (f" marge {row['marge_dec']:+.2f} / largage {row['marge_largage']:+.2f} in, {row['temps']:.0f} s"
                     f"{'' if row['optimal'] else ' (non prouve)'}" if row['statut'].startswith('ok') else '')
                  + (f"  [{row['warn']}]" if row['warn'] else ''), flush=True)
    rows.sort(key=lambda r: (r['fichier'], r.get('tirage') or 0))
    keys = ['fichier', 'immat', 'stick', 'date', 'tirage', 'n', 'groupes', 'tandems', 'fuel_lbs', 'pilote_kg', 'paras_kg', 'masse_lbs',
            'statut', 'sequence', 'mu_max', 'mu_max_largage', 'cg_in', 'mac', 'marge_dec', 'marge_largage', 'optimal', 'gap',
            'boites', 'ecart_sortie', 'temps', 'warn']
    csv_name = 'resultats.csv' if a.tirages == 1 else f'resultats_{a.tirages}tirages.csv'
    with open(OUT / csv_name, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=keys, extrasaction='ignore'); w.writeheader(); w.writerows(rows)
    ok = [r for r in rows if r['statut'].startswith('ok')]
    cat = collections.Counter(r['statut'].split(':')[0].strip() for r in rows)
    print(f"\n{len(rows)} fiches x tirages, {len(ok)} placees, {time.time() - t0:.0f} s")
    for k_, v in sorted(cat.items(), key=lambda kv: -kv[1]):
        print(f"  {v:4d}  {k_}")
    if ok:
        md = np.array([r['marge_dec'] for r in ok]); ml = np.array([r['marge_largage'] for r in ok])
        print(f"marge decollage : min {md.min():+.2f}, mediane {np.median(md):+.2f} in ; "
              f"marge largage : min {ml.min():+.2f}, mediane {np.median(ml):+.2f} in ; "
              f"optimum prouve {sum(r['optimal'] for r in ok)}/{len(ok)} ; "
              f"groupes non ordonnes {sum('non ordonnes' in r['statut'] for r in ok)}")
    for r in rows:
        if r['statut'].startswith('ECHEC') or r['warn']:
            print('  ', r['fichier'], r['statut'], r['warn'])


if __name__ == '__main__':
    main()
