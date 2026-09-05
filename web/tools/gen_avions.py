"""Genere web/js/avions.js (base avions de l'IHM) depuis avions/*/planches_club.json,
avions/pac750xl/envelope.json et avions/dhc6/envelope.json : rien n'est recopie a la main.
Aucune immatriculation : les avions sont designes par type et lettre (A, B). Relancer apres
toute mise a jour de ces fichiers.

    python3 web/tools/gen_avions.py

Modele d'un avion :
  id, libelle, type, famille, unites, kg_par_unite_masse, masse_vide, bras_vide, pilote,
  carburant {capacite, defaut, table [[masse, bras]]}, porte {x, y}, places [{id, x, y, ...}],
  rangees [{id, y, xmin, xmax}]  (placement libre : y de la rangee, bras borne),
  cabine {x0, x1, zones, porte}, mac {lemac, longueur},
  variantes [{id, libelle, mtow, enveloppe {avant, arriere}, source}], variante_defaut, a_verifier.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AV = ROOT / 'avions'
KG_PAR_LB = 1 / 2.20462


def env_c208b_poh():
    """Enveloppe 208B du POH (categorie normale, decollage) lue dans avions/c208b/envelope.json."""
    d = json.loads((AV / 'c208b' / 'envelope.json').read_text())
    e = next(x for x in d['envelopes'] if x['name'].startswith('C208B normal category, takeoff'))
    aft = e.get('aft_limit_in') or max(v[1] for v in e['vertices'])
    fwd = sorted({(v[0], v[1]) for v in e['vertices'] if v[1] < aft})
    if len(fwd) > 1 and fwd[0][1] == fwd[1][1]:
        fwd = fwd[1:]          # le premier sommet est le bas du graphique, pas une limite
    mtow = d['weights']['C208B']['max_takeoff']
    return mtow, {'avant': [[float(w), float(a)] for w, a in fwd], 'arriere': [[0.0, float(aft)], [float(mtow), float(aft)]]}, e.get('source', 'POH 208B')


def caravan():
    d = json.loads((AV / 'c208b' / 'planches_club.json').read_text())
    rows = {'copilote': 'COPI', 'droite': 'D', 'centre': 'C', 'gauche': 'G'}
    counters = {'D': 0, 'C': 0, 'G': 0}
    places = []
    for s in d['fixed_seats_n20']:
        if s['row'] == 'copilote':
            pid, extra = 'COPI', {'copilote': True}
        else:
            k = rows[s['row']]; counters[k] += 1; pid = f'{k}{counters[k]}'
            extra = {'centre': True} if k == 'C' else {}
        places.append({'id': pid, 'x': round(s['arm_in'], 1), 'y': s['lateral_in'], **extra})
    zones = [z for z in d['stations'] if z['name'].startswith('ZONE')]
    env_club = d['envelopes'][0]
    mtow_club = d['limits']['mtow_lb']
    fuel = d['fuel']
    try:
        mtow_poh, env_poh, src_poh = env_c208b_poh()
    except Exception as exc:   # fichier POH absent ou de forme differente : variante omise
        mtow_poh, env_poh, src_poh = None, None, str(exc)
    variantes = []
    if env_poh:
        variantes.append({'id': 'poh', 'libelle': f'POH, MTOW {mtow_poh} lb', 'mtow': mtow_poh, 'enveloppe': env_poh, 'source': src_poh})
    ape = json.loads((AV / 'c208b' / 'stc_ape.json').read_text())
    for vid, a in (('ape2', ape['ape2']), ('ape3', ape['ape3'])):
        variantes.append({'id': vid, 'libelle': f"{a['designation'].split(' (')[1].rstrip(')')} : STC {a['faa_stc']}, MTOW {a['mtow_lb']} lb" + (f", MLW {a['mlw_lb']} lb" if vid == 'ape3' else ''),
                          'mtow': a['mtow_lb'],
                          'enveloppe': {'avant': [[float(q['weight_lb']), float(q['arm_in'])] for q in a['cg_forward_limit']],
                                        'arriere': [[0.0, a['cg_aft_limit_in']], [float(a['mtow_lb']), a['cg_aft_limit_in']]]},
                          'source': f"avions/c208b/stc_ape.json : {a['designation']}, STC FAA {a['faa_stc']} ; limites CG du rapport TSB A14W0181 (limite avant prolongee jusqu'a 200.23 in a 9062 lb, arriere 204.35 in)" + (" ; MLW 9000 lb (non modelisee ici)" if vid == 'ape3' else '')})
    variantes.append({'id': 'planches', 'libelle': f'Planches club (MTOW {mtow_club} lb, limite avant des planches)', 'mtow': mtow_club,
                      'enveloppe': {'avant': [[w, a] for w, a in zip(env_club['forward_limit']['weight_lb'], env_club['forward_limit']['arm_in'])],
                                    'arriere': [[0, env_club['aft_limit_in']], [mtow_club, env_club['aft_limit_in']]]},
                      'source': 'planches club (avions/c208b/planches_club.json) : limite avant interpolee de (8000, 193.37) a (9062, 199.15), moins restrictive que le STC APE II au-dessus de 8000 lb', 'a_verifier': True})
    out = []
    for lettre, (_, r) in zip('AB', d['registrations'].items()):
        out.append({
            'id': f'c208b-{lettre}', 'libelle': f'Caravan 208B · avion {lettre}', 'type': 'Cessna 208B Grand Caravan', 'famille': 'c208b',
            'unites': {'masse': 'lb', 'bras': 'in', 'carburant': 'lb'},
            'kg_par_unite_masse': KG_PAR_LB,
            'masse_vide': r['ew_lb'], 'bras_vide': r['ew_cg_in'],
            'mac': {'lemac': d['mac']['lemac_in'], 'longueur': d['mac']['length_in']},
            'pilote': {'bras': 135.5, 'masse_kg_defaut': 80},
            'carburant': {'capacite': fuel['capacity_usable_lb'], 'par_rotation': fuel['per_rotation_lb'], 'reserve': fuel['reserve_lb'],
                          'defaut': 900, 'table': [[t['lb'], t['arm_in']] for t in fuel['table']]},
            'porte': {'x': 307.0, 'y': -32.0, 'cote': 'gauche'},
            'places': places,
            'rangees': [{'id': 'D', 'libelle': 'droite', 'y': 16.0, 'xmin': 128.0, 'xmax': 352.0},
                        {'id': 'C', 'libelle': 'centre', 'y': 0.0, 'xmin': 140.0, 'xmax': 352.0},
                        {'id': 'G', 'libelle': 'gauche', 'y': -16.0, 'xmin': 154.0, 'xmax': 352.0}],
            'cabine': {'x0': 100.0, 'x1': 356.0,
                       'zones': [{'nom': z['name'], 'x0': z['x0_in'], 'x1': z['x1_in'], 'largeur': z['width_in']} for z in zones],
                       'porte': {'x0': 282.0, 'x1': 332.0, 'cote': 'gauche'}},
            'variantes': variantes, 'variante_defaut': 'ape2',
            'source': 'avions/c208b/planches_club.json (planches club) ; porte cargo FS 282 a 332 (POH 208B)',
        })
    return out


def pilatus():
    d = json.loads((AV / 'pc6-b2h4' / 'planches_club.json').read_text())
    env = d['envelopes'][0]
    # Rangee haute des planches = droite (y > 0), basse = gauche. Porte de largage a droite
    # (n'influence que le classement par proximite de la porte).
    places = [{'id': f'D{i+1}', 'x': x, 'y': 0.45} for i, x in enumerate(d['fixed_seats']['rangee_haute_m'])]
    places += [{'id': f'G{i+1}', 'x': x, 'y': -0.45} for i, x in enumerate(d['fixed_seats']['rangee_basse_m'])]
    fuel = d['fuel']
    table = [[t['kg'], t['arm_m']] for t in fuel['table'] if t['kg'] > 0]
    mtow = d['limits']['mtow_kg']
    variante = {'id': 'afm', 'libelle': f'AFM B2-H4, MTOW {mtow} kg', 'mtow': mtow,
                'enveloppe': {'avant': [[w, a] for w, a in zip(env['forward_limit']['weight_kg'], env['forward_limit']['arm_m'])],
                              'arriere': [[0, env['aft_limit_m']], [mtow, env['aft_limit_m']]]},
                'source': 'planches club, identique au TCDS OFAC F 56-10'}
    out = []
    for lettre, (_, r) in zip('AB', d['registrations'].items()):
        out.append({
            'id': f'pc6-{lettre}', 'libelle': f'Pilatus PC-6 B2-H4 · avion {lettre}', 'type': 'Pilatus PC-6/B2-H4', 'famille': 'pc6',
            'unites': {'masse': 'kg', 'bras': 'm', 'carburant': 'L'},
            'kg_par_unite_masse': 1.0,
            'masse_vide': r['ew_kg'], 'bras_vide': r['ew_cg_m'],
            'mac': {'lemac': d['mac']['lemac_m'], 'longueur': d['mac']['length_m']},
            'pilote': {'bras': 3.05, 'masse_kg_defaut': 80},
            'carburant': {'capacite': fuel['capacity_l'], 'par_rotation': fuel['per_rotation_l'], 'reserve': fuel['reserve_l'],
                          'defaut': 250, 'kg_par_litre': 129.6 / 160.9, 'table': table},
            'porte': {'x': 5.3, 'y': 0.9, 'cote': 'droite'},
            'places': places,
            'rangees': [{'id': 'D', 'libelle': 'droite', 'y': 0.45, 'xmin': 2.6, 'xmax': 5.65},
                        {'id': 'G', 'libelle': 'gauche', 'y': -0.45, 'xmin': 3.3, 'xmax': 5.65}],
            'cabine': {'x0': 2.5, 'x1': 5.7, 'zones': [{'nom': 'cabine', 'x0': 2.5, 'x1': 5.7, 'largeur': 1.16}],
                       'porte': {'x0': 4.2, 'x1': 5.5, 'cote': 'droite'}},
            'variantes': [variante], 'variante_defaut': 'afm',
            'source': 'avions/pc6-b2h4/planches_club.json (planches club) ; cabine et porte : ordre de grandeur, voir avions/pc6-b2h4/notes.md',
        })
    return out


def pac750():
    d = json.loads((AV / 'pac750xl' / 'envelope.json').read_text())
    paras = [s for s in d['stations'] if s['type'] == 'parachutist']
    places = [{'id': f'P{i+1}', 'x': s['arm_in'], 'y': 0.0} for i, s in enumerate(paras)]
    cab = d['cabin']
    mtow = d['weights']['mtow_lb']
    variantes = []
    for e in d['envelopes']:
        vid = 'std' if 'standard' in e['name'] else 'gros_reservoirs'
        variantes.append({'id': vid, 'libelle': e['name'].replace('Normal category, ', 'POH, ') + f', MTOW {mtow} lb', 'mtow': mtow,
                          'enveloppe': {'avant': [list(map(float, p)) for p in e['forward_limit']], 'arriere': [[0.0, e['aft_limit_in']], [float(mtow), e['aft_limit_in']]]},
                          'source': e['source']})
    return [{
        'id': 'pac750xl', 'libelle': 'PAC 750XL (generique)', 'type': 'Pacific Aerospace 750XL', 'famille': 'pac750xl',
        'unites': {'masse': 'lb', 'bras': 'in', 'carburant': 'lb'},
        'kg_par_unite_masse': KG_PAR_LB,
        'masse_vide': 3300, 'bras_vide': 110.58,
        'mac': {'lemac': d['mac']['lemac_in'], 'longueur': d['mac']['length_in']},
        'pilote': {'bras': 66.5, 'masse_kg_defaut': 80},
        'carburant': {'capacite': 1476, 'par_rotation': None, 'reserve': None, 'defaut': 500, 'table': [[0, 110.21], [1476, 110.21]]},
        'porte': {'x': 212.0, 'y': -27.0, 'cote': 'gauche'},
        'places': places,
        'rangees': [{'id': 'D', 'libelle': 'droite', 'y': 18.0, 'xmin': 85.0, 'xmax': 238.0},
                    {'id': 'C', 'libelle': 'centre', 'y': 0.0, 'xmin': 85.0, 'xmax': 238.0},
                    {'id': 'G', 'libelle': 'gauche', 'y': -18.0, 'xmin': 85.0, 'xmax': 238.0}],
        'cabine': {'x0': cab['floor_from_sta_in'], 'x1': cab['floor_to_sta_in'],
                   'zones': [{'nom': 'cabine', 'x0': cab['floor_from_sta_in'], 'x1': cab['floor_to_sta_in'], 'largeur': cab['max_width_in']}],
                   'porte': {'x0': cab['door']['from_sta_in'], 'x1': cab['door']['to_sta_in'], 'cote': 'gauche'}},
        'variantes': variantes, 'variante_defaut': 'std',
        'a_verifier': ['masse a vide 3300 lb et bras 110.58 in : ordre de grandeur (tiers / exemple POH), saisir la pesee reelle',
                       'bras carburant : reservoir avant 110.21 in, arriere 139.15 in ; sequence de remplissage non connue',
                       'positions paras 1 a 12 sur l axe (figure 6-10 du POH), pas de position laterale publiee'],
        'source': 'avions/pac750xl/envelope.json (POH PAC 750XL, TCDS EASA)',
    }]


def dhc6():
    d = json.loads((AV / 'dhc6' / 'envelope.json').read_text())
    st = {s['name']: s.get('arm') for s in d['stations']}
    cab = d['cabin']
    x0, x1 = cab['front_bulkhead_station_in'], cab['rear_bulkhead_station_in']
    mtow = d['weights'].get('mtow_lb') or 12500
    variantes = []
    for e in d['envelopes']:
        vs = e.get('vertices') or []
        if not vs or any(v[0] is None or v[1] is None for v in vs):
            continue
        fwd = [v for v in vs if v[1] < 210]; aft = max(v[1] for v in vs)
        top = max(v[0] for v in vs)
        variantes.append({'id': 'decollage' if 'take-off' in e['name'] else ('atterrissage' if 'landing' in e['name'] else 'flotteurs'),
                          'libelle': e['name'].replace('Series 300 landplane and wheel-skiplane, ', 'TCDS A9EA, ') + f', max {top} lb',
                          'mtow': top, 'enveloppe': {'avant': [list(map(float, v)) for v in sorted(fwd)], 'arriere': [[0.0, aft], [float(top), aft]]},
                          'source': e.get('source', 'TCDS FAA A9EA')})
    variantes = [v for v in variantes if v['id'] != 'flotteurs']
    st2 = json.loads((AV / 'dhc6' / 'stations.json').read_text())
    # Positions de paras au sol : hypothese de travail de stations.json (deux files le long des parois,
    # pas 20 in du seuil de porte FS 325 a la cloison avant FS 125), bras = station fuselage.
    xs = sorted(st2['floor_positions_hypothesis_in'])
    places = [{'id': f'D{i+1}', 'x': float(x), 'y': 20.0} for i, x in enumerate(xs)]
    places += [{'id': f'G{i+1}', 'x': float(x), 'y': -20.0} for i, x in enumerate(xs)]
    porte = st2['door']
    return [{
        'id': 'dhc6-300', 'libelle': 'DHC-6 Twin Otter 300 (generique)', 'type': 'de Havilland DHC-6-300 Twin Otter', 'famille': 'dhc6',
        'unites': {'masse': 'lb', 'bras': 'in', 'carburant': 'lb'},
        'kg_par_unite_masse': KG_PAR_LB,
        'masse_vide': 7400, 'bras_vide': 200.0,
        'mac': {'lemac': d['mac']['lemac_in'], 'longueur': d['mac']['length_in']},
        'pilote': {'bras': st.get('Pilot seats (2)', 95.0), 'masse_kg_defaut': 80, 'nombre': 2},
        'carburant': {'capacite': int(378 * 6.7), 'par_rotation': None, 'reserve': None, 'defaut': 1200,
                      # avant (+162.5, 181 USG) rempli en premier puis arriere (+240) : bras moyen en fonction de la masse
                      'table': [[0, 162.5], [round(181 * 6.7), 162.5], [round(378 * 6.7), round((181 * 162.5 + 197 * 240.0) / 378, 2)]]},
        'porte': {'x': (porte['clear_opening_from_sta_in'] + porte['clear_opening_to_sta_in']) / 2, 'y': -40.0, 'cote': 'gauche'},
        'places': places,
        'rangees': [{'id': 'D', 'libelle': 'droite', 'y': 20.0, 'xmin': x0 + 8, 'xmax': x1 - 6},
                    {'id': 'C', 'libelle': 'centre', 'y': 0.0, 'xmin': x0 + 8, 'xmax': x1 - 6},
                    {'id': 'G', 'libelle': 'gauche', 'y': -20.0, 'xmin': x0 + 8, 'xmax': x1 - 6}],
        'cabine': {'x0': x0, 'x1': x1, 'zones': [{'nom': 'cabine', 'x0': x0, 'x1': x1, 'largeur': cab['width_max_in']}],
                   'porte': {'x0': float(porte['clear_opening_from_sta_in']), 'x1': float(porte['clear_opening_to_sta_in']), 'cote': 'gauche'},
                   'train_principal': st2['main_gear_sta_in'], 'train_avant': st2['nose_gear_sta_in'],
                   'rangees_sieges_commuter': st2['seat_rows_arm_in']},
        'variantes': variantes, 'variante_defaut': 'decollage',
        'a_verifier': ['masse a vide 7400 lb et bras 200 in : ordre de grandeur, saisir la pesee reelle',
                       'positions des paras au sol : hypothese (deux files, pas 20 in, FS 125 a 325), le manuel de masse et centrage PSM 1-63-8 n a pas ete trouve ; rangees commuter mesurees sur plan FS 129 a 315 (+/- 5 in)',
                       'ordre de remplissage des reservoirs (avant puis arriere) suppose pour le bras carburant',
                       'porte gauche FS 270 a 326 et trains (FS 232 et 53) mesures sur les plans FlightSafety, +/- 5 in'],
        'source': 'avions/dhc6/envelope.json (TCDS FAA A9EA, Viking) et avions/dhc6/stations.json (mesures sur plans)',
    }]


if __name__ == '__main__':
    avions = caravan() + pilatus() + pac750() + dhc6()
    js = ('// Genere par web/tools/gen_avions.py depuis avions/*/planches_club.json et avions/*/envelope.json.\n'
          '// Ne pas editer a la main : corriger la source puis relancer le script. Aucune immatriculation ici.\n'
          'export const AVIONS = ' + json.dumps(avions, indent=1, ensure_ascii=False) + ';\n')
    (ROOT / 'web' / 'js' / 'avions.js').write_text(js)
    print('ecrit web/js/avions.js :', [(a['id'], [v['id'] for v in a['variantes']]) for a in avions])
