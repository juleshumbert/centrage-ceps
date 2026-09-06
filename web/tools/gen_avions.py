"""Genere web/js/avions.js (base avions de l'IHM) depuis avions/*/planches_club.json (pesees,
places, tables carburant), avions/*/envelope.json, avions/c208b/stc_ape.json et
avions/dhc6/stations.json : rien n'est recopie a la main. Aucune immatriculation : un seul
modele par type, les pesees connues sont listees par lettre.

    python3 web/tools/gen_avions.py

Modele d'un avion :
  id, libelle, type, famille, unites, kg_par_unite_masse,
  pesees [{id, libelle, masse_vide, bras_vide, source}]   (la premiere est celle par defaut),
  pilote {bras, masse_kg_defaut}, carburant {capacite, defaut, table [[masse, bras]]},
  porte {x, y, cote, moment_ouverture?}, places [{id, x, y, copilote?, centre?}],
  rangees [{id, libelle, y, xmin, xmax, exterieur?}]   (placement libre ; la rangee exterieure est
                                                       cote porte, hors fuselage : paras a la porte),
  cabine {x0, x1, zones [{nom, x0, x1, largeur}], porte {x0, x1, cote}},
  dessin {fuselage [[x, demi_largeur], ...] (profil en plan, de l'avant a la queue), aile {x0, x1},
          blocs [{x0, x1, y0, y1, nom}] (volumes dessines en bleu, coordonnees avion)},
  mac {lemac, longueur}, variantes [{id, libelle, mtow, enveloppe {avant, arriere}, source}], variante_defaut,
  a_verifier [...].
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AV = ROOT / 'avions'
KG_PAR_LB = 1 / 2.20462


def lit(*p):
    return json.loads((AV.joinpath(*p)).read_text())


def enveloppe_depuis_sommets(vertices, mtow):
    """Sommets d'un centrogramme -> {avant, arriere} ; le premier sommet (bas du graphique) est ignore."""
    aft = max(v[1] for v in vertices)
    fwd = sorted({(float(v[0]), float(v[1])) for v in vertices if v[1] < aft})
    if len(fwd) > 1 and fwd[0][1] == fwd[1][1]:
        fwd = fwd[1:]
    return {'avant': [list(p) for p in fwd], 'arriere': [[0.0, float(aft)], [float(mtow), float(aft)]]}



def schema_planches_caravan(zones, lemac, mac, porte, roues, nez):
    """Schema du Caravan des planches du club (plot_conf du notebook) et de l ancienne page
    centrage.html : trapezes entre zones, derniere zone effilee, porte en barre cote gauche, aile de
    LEMAC a LEMAC + MAC sur les deux bords, roues, reperes 204 (limite arriere) et 250, pilote."""
    z = sorted(zones, key=lambda q: q['x0'])
    prims = []
    for i, q in enumerate(z):
        if i < len(z) - 1:
            nxt = z[i + 1]
            pts = [[q['x0'], -q['largeur'] / 2], [q['x0'], q['largeur'] / 2], [q['x1'], nxt['largeur'] / 2], [q['x1'], -nxt['largeur'] / 2]]
        else:
            pts = [[q['x0'], -q['largeur'] / 2], [q['x0'], q['largeur'] / 2], [q['x1'], q['largeur'] / 2 - 5], [q['x1'], -q['largeur'] / 2 + 5]]
        prims.append({'type': 'polygone', 'points': pts, 'trait': 'fuselage', 'nom': q['nom'], 'etiquette': [(q['x0'] + q['x1']) / 2, 0]})
    prims.append({'type': 'polygone', 'points': [[nez[0], -nez[1] / 2], [nez[0], nez[1] / 2], [z[0]['x0'], z[0]['largeur'] / 2], [z[0]['x0'], -z[0]['largeur'] / 2]], 'trait': 'fuselage', 'nom': 'Z-1'})
    zi = next(q for q in z if q['x0'] <= porte['x0'] < q['x1']); zf = next(q for q in z if q['x0'] < porte['x1'] <= q['x1'])
    prims.append({'type': 'polygone', 'points': [[porte['x0'], -zi['largeur'] / 2 + 2], [porte['x0'], -zi['largeur'] / 2], [porte['x1'], -zf['largeur'] / 2], [porte['x1'], -zf['largeur'] / 2 + 2]], 'trait': 'porte', 'nom': 'porte'})
    za = next(q for q in z if q['x0'] <= lemac < q['x1']); zb = next(q for q in z if q['x0'] < lemac + mac <= q['x1'])
    for sg in (1, -1):
        prims.append({'type': 'polygone', 'points': [[lemac, sg * (za['largeur'] / 2 + 1)], [lemac, sg * (za['largeur'] / 2 + 30)], [lemac + mac, sg * (zb['largeur'] / 2 + 20)], [lemac + mac, sg * zb['largeur'] / 2]], 'trait': 'aile', 'nom': 'aile'})
        prims.append({'type': 'polygone', 'points': [[roues[1], sg * 75], [roues[0], sg * 75], [roues[0], sg * 65], [roues[1], sg * 65]], 'trait': 'roue', 'nom': 'roue'})
    prims.append({'type': 'cercle', 'centre': [(z[0]['x0'] + z[0]['x1']) / 2, -z[0]['largeur'] / 4], 'rayon': 10, 'trait': 'pilote', 'nom': 'P'})
    return prims

# ------------------------------------------------------------------ Cessna 208B
def caravan_208b():
    pc = lit('c208b', 'planches_club.json')
    env = lit('c208b', 'envelope.json')
    ape = lit('c208b', 'stc_ape.json')
    rows = {'copilote': 'COPI', 'droite': 'D', 'centre': 'C', 'gauche': 'G'}
    counters = {'D': 0, 'C': 0, 'G': 0}
    places = []
    for s in pc['fixed_seats_n20']:
        if s['row'] == 'copilote':
            pid, extra = 'COPI', {'copilote': True}
        else:
            k = rows[s['row']]; counters[k] += 1; pid = f'{k}{counters[k]}'
            extra = {'centre': True} if k == 'C' else {}
        places.append({'id': pid, 'x': round(s['arm_in'], 1), 'y': s['lateral_in'], **extra})
    zones = [{'nom': z['name'].replace('ZONE ', 'Z'), 'x0': z['x0_in'], 'x1': z['x1_in'], 'largeur': z['width_in']}
             for z in pc['stations'] if z['name'].startswith('ZONE')]
    zones.sort(key=lambda z: z['x0'])
    fuel = pc['fuel']
    e_poh = next(x for x in env['envelopes'] if x['name'].startswith('C208B normal category, takeoff'))
    mtow_poh = env['weights']['C208B']['max_takeoff']
    variantes = [{'id': 'poh', 'libelle': f'POH, MTOW {mtow_poh} lb', 'mtow': mtow_poh,
                  'enveloppe': enveloppe_depuis_sommets(e_poh['vertices'], mtow_poh), 'source': e_poh['source']}]
    for vid, a in (('ape2', ape['ape2']), ('ape3', ape['ape3'])):
        variantes.append({'id': vid, 'libelle': f"{a['designation'].split(' (')[1].rstrip(')')} : STC {a['faa_stc']}, MTOW {a['mtow_lb']} lb" + (f", MLW {a['mlw_lb']} lb" if vid == 'ape3' else ''),
                          'mtow': a['mtow_lb'],
                          'enveloppe': {'avant': [[float(q['weight_lb']), float(q['arm_in'])] for q in a['cg_forward_limit']],
                                        'arriere': [[0.0, a['cg_aft_limit_in']], [float(a['mtow_lb']), a['cg_aft_limit_in']]]},
                          'source': f"avions/c208b/stc_ape.json : {a['designation']}, STC FAA {a['faa_stc']}, limites CG du rapport TSB A14W0181 (limite avant 200.23 in a 9062 lb, arriere 204.35 in)" + (' ; MLW 9000 lb (non modelisee ici)' if vid == 'ape3' else '')})
    pesees = [{'id': l, 'libelle': f'pesee {l}', 'masse_vide': r['ew_lb'], 'bras_vide': r['ew_cg_in'], 'source': 'planches du club'}
              for l, (_, r) in zip('AB', pc['registrations'].items())]
    demi = max(z['largeur'] for z in zones) / 2
    return {
        'id': 'c208b', 'libelle': 'Cessna 208B Grand Caravan', 'type': 'Cessna 208B Grand Caravan', 'famille': 'c208',
        'unites': {'masse': 'lb', 'bras': 'in', 'carburant': 'lb'}, 'kg_par_unite_masse': KG_PAR_LB,
        'pesees': pesees,
        'mac': {'lemac': pc['mac']['lemac_in'], 'longueur': pc['mac']['length_in']},
        'pilote': {'bras': 135.5, 'masse_kg_defaut': 80},
        'carburant': {'capacite': fuel['capacity_usable_lb'], 'par_rotation': fuel['per_rotation_lb'], 'reserve': fuel['reserve_lb'],
                      'defaut': 900, 'table': [[t['lb'], t['arm_in']] for t in fuel['table']]},
        'porte': {'x': 307.0, 'y': -32.0, 'cote': 'gauche'},
        'places': places,
        'rangees': [{'id': 'D', 'libelle': 'droite', 'y': 16.0, 'xmin': 128.0, 'xmax': 352.0},
                    {'id': 'C', 'libelle': 'centre', 'y': 0.0, 'xmin': 140.0, 'xmax': 352.0},
                    {'id': 'G', 'libelle': 'gauche', 'y': -16.0, 'xmin': 154.0, 'xmax': 352.0},
                    {'id': 'EXT', 'libelle': 'exterieur (porte)', 'y': -(demi + 14.0), 'xmin': 270.0, 'xmax': 356.0, 'exterieur': True}],
        'cabine': {'x0': 100.0, 'x1': 356.0, 'zones': zones, 'porte': {'x0': 282.0, 'x1': 332.0, 'cote': 'gauche'}},
        'dessin': {'vue': {'x0': 70.0, 'x1': 400.0, 'demi_largeur': 80.0},
                   'primitives': schema_planches_caravan(zones, pc['mac']['lemac_in'], pc['mac']['length_in'], {'x0': 282.0, 'x1': 332.0}, (200.0, 228.0), (100.0, 53.0))
                                 + [{'type': 'ligne', 'x': 204.35, 'demi': 32.0, 'trait': 'repere', 'nom': 'limite arriere 204.35'}, {'type': 'ligne', 'x': 250.0, 'demi': 32.0, 'trait': 'repere_rouge', 'nom': '250'}],
                   'graduations': [100, 125, 150, 175, 200, 225, 250, 275, 300, 325, 350, 375, 400],
                   'source': 'schema des planches du club (plot_conf) et de l ancienne page centrage.html'},
        'variantes': variantes, 'variante_defaut': 'ape2',
        'source': 'places et pesees : planches du club ; zones cabine et porte cargo FS 282 a 332 : POH 208B ; schema repris de l ancienne IHM centrage_c208',
    }


# ------------------------------------------------------------------ Cessna 208A (fuselage court)
def caravan_208a():
    env = lit('c208b', 'envelope.json')
    e = next(x for x in env['envelopes'] if x['name'].startswith('C208 (675 SHP) landplane normal category, takeoff'))
    w = env['weights']['C208']; cab = env['cabin']['C208']; fuel = env['fuel']['C208']
    mtow = w['max_takeoff']
    st = cab['reference_stations_in']
    zones = [{'nom': 'Z0', 'x0': 118.0, 'x1': 155.4, 'largeur': 53.0},
             {'nom': 'Z1', 'x0': 155.4, 'x1': float(st['s180']), 'largeur': 62.0},
             {'nom': 'Z2', 'x0': float(st['s180']), 'x1': float(st['cargo_door_fwd']), 'largeur': 64.0},
             {'nom': 'Z3', 'x0': float(st['cargo_door_fwd']), 'x1': float(st['cargo_door_aft_raised_floor']), 'largeur': 53.0},
             {'nom': 'Z4', 'x0': float(st['cargo_door_aft_raised_floor']), 'x1': float(st['aft_wall']), 'largeur': 46.0}]
    xs_bord = [155.4, 180.7, 205.9, 231.2, 256.5]
    xs_centre = [168.0, 199.6, 231.2, 262.8]
    places = [{'id': 'COPI', 'x': 135.5, 'y': 16.0, 'copilote': True}]
    places += [{'id': f'D{i+1}', 'x': x, 'y': 16.0} for i, x in enumerate(xs_bord)]
    places += [{'id': f'C{i+1}', 'x': x, 'y': 0.0, 'centre': True} for i, x in enumerate(xs_centre)]
    places += [{'id': f'G{i+1}', 'x': x, 'y': -16.0} for i, x in enumerate(xs_bord)]
    d0, d1 = float(st['cargo_door_fwd']), float(st['cargo_door_aft_raised_floor'])
    return {
        'id': 'c208a', 'libelle': 'Cessna 208A Caravan (fuselage court)', 'type': 'Cessna 208 Caravan (675 SHP)', 'famille': 'c208',
        'unites': {'masse': 'lb', 'bras': 'in', 'carburant': 'lb'}, 'kg_par_unite_masse': KG_PAR_LB,
        'pesees': [{'id': 'estim', 'libelle': 'estimation (a remplacer par la pesee)', 'masse_vide': w['standard_empty_weight_estimate'], 'bras_vide': 166.0,
                    'source': 'masse a vide standard estimee (TCDS / Spec & Description), bras a vide suppose (13 % MAC) : saisir la pesee reelle'}],
        'mac': {'lemac': env['mac']['C208']['lemac_in'] if isinstance(env['mac'].get('C208'), dict) else 157.57, 'longueur': 66.40},
        'pilote': {'bras': 135.5, 'masse_kg_defaut': 80},
        'carburant': {'capacite': fuel['usable_lb_jet_a_6_7'], 'par_rotation': None, 'reserve': None, 'defaut': 900,
                      'table': [[0, fuel['tcds_tank_arm_in']], [fuel['usable_lb_jet_a_6_7'], fuel['tcds_tank_arm_in']]]},
        'porte': {'x': d1 - 5.0, 'y': -30.0, 'cote': 'gauche'},
        'places': places,
        'rangees': [{'id': 'D', 'libelle': 'droite', 'y': 16.0, 'xmin': 128.0, 'xmax': 302.0},
                    {'id': 'C', 'libelle': 'centre', 'y': 0.0, 'xmin': 140.0, 'xmax': 302.0},
                    {'id': 'G', 'libelle': 'gauche', 'y': -16.0, 'xmin': 154.0, 'xmax': 302.0},
                    {'id': 'EXT', 'libelle': 'exterieur (porte)', 'y': -(32.0 + 14.0), 'xmin': d0 - 12.0, 'xmax': float(st['aft_wall']), 'exterieur': True}],
        'cabine': {'x0': 100.0, 'x1': float(st['aft_wall']), 'zones': zones, 'porte': {'x0': d0, 'x1': d1, 'cote': 'gauche'}},
        'dessin': {'vue': {'x0': 70.0, 'x1': 350.0, 'demi_largeur': 80.0},
                   'primitives': schema_planches_caravan(zones, 157.57, 66.40, {'x0': d0, 'x1': d1}, (180.0, 208.0), (100.0, 53.0))
                                 + [{'type': 'ligne', 'x': 184.35, 'demi': 32.0, 'trait': 'repere', 'nom': 'limite arriere 184.35'}],
                   'graduations': [100, 125, 150, 175, 200, 225, 250, 275, 300, 325, 350],
                   'source': 'meme schema que le 208B, transpose sur la cabine courte (zones du Spec & Description)'},
        'variantes': [{'id': 'poh', 'libelle': f'POH / TCDS, MTOW {mtow} lb', 'mtow': mtow, 'enveloppe': enveloppe_depuis_sommets(e['vertices'], mtow), 'source': e['source']}],
        'variante_defaut': 'poh',
        'a_verifier': ['masse a vide 4230 lb et bras 166 in : estimation, saisir la pesee reelle',
                       'places : disposition construite par analogie avec le 208B sur la cabine courte (cloison arriere FS 308), aucune source club',
                       'bras carburant unique +183.8 in (TCDS), pas de table detaillee',
                       'porte cargo FS 234 a 284 (Spec & Description)'],
        'source': 'avions/c208b/envelope.json (TCDS A37CE, extrait POH 208, Spec & Description 2016)',
    }


# ------------------------------------------------------------------ Pilatus PC-6
def pilatus():
    pc = lit('pc6-b2h4', 'planches_club.json')
    h2 = lit('pc6-b2h2', 'envelope.json')
    env = pc['envelopes'][0]
    places = [{'id': f'D{i+1}', 'x': x, 'y': 0.25} for i, x in enumerate(pc['fixed_seats']['rangee_haute_m'])]
    places += [{'id': f'G{i+1}', 'x': x, 'y': -0.25} for i, x in enumerate(pc['fixed_seats']['rangee_basse_m'])]
    fuel = pc['fuel']
    table = [[t['kg'], t['arm_m']] for t in fuel['table'] if t['kg'] > 0]
    mtow = pc['limits']['mtow_kg']
    v_h4 = {'id': 'b2h4', 'libelle': f'B2-H4 (AFM 1820), MTOW {mtow} kg', 'mtow': mtow,
            'enveloppe': {'avant': [[w, a] for w, a in zip(env['forward_limit']['weight_kg'], env['forward_limit']['arm_m'])],
                          'arriere': [[0, env['aft_limit_m']], [mtow, env['aft_limit_m']]]},
            'source': 'TCDS OFAC F 56-10 et AFM 1820, identique aux planches du club'}
    e2 = next(x for x in h2['envelopes'] if x.get('vertices'))
    m2 = h2['weights_kg']['max_takeoff']
    v_h2 = {'id': 'b2h2', 'libelle': f'B2-H2 (TCDS), MTOW {m2} kg', 'mtow': m2,
            'enveloppe': enveloppe_depuis_sommets(e2['vertices'], m2),
            'source': 'TCDS OFAC F 56-10 (aucun AFM B2-H2 public) ; pesee a saisir, les pesees listees sont celles des B2-H4'}
    pesees = [{'id': l, 'libelle': f'pesee {l} (B2-H4)', 'masse_vide': r['ew_kg'], 'bras_vide': r['ew_cg_m'], 'source': 'planches du club'}
              for l, (_, r) in zip('AB', pc['registrations'].items())]
    return {
        'id': 'pc6', 'libelle': 'Pilatus PC-6 Turbo Porter', 'type': 'Pilatus PC-6/B2-H4 (variante B2-H2)', 'famille': 'pc6',
        'unites': {'masse': 'kg', 'bras': 'm', 'carburant': 'L'}, 'kg_par_unite_masse': 1.0,
        'pesees': pesees,
        'mac': {'lemac': pc['mac']['lemac_m'], 'longueur': pc['mac']['length_m']},
        'pilote': {'bras': 3.05, 'masse_kg_defaut': 80},
        'carburant': {'capacite': fuel['capacity_l'], 'par_rotation': fuel['per_rotation_l'], 'reserve': fuel['reserve_l'],
                      'defaut': 250, 'kg_par_litre': 129.6 / 160.9, 'table': table},
        # Porte coulissante droite ; a l'ouverture elle recule et ajoute +21 kg.m (supplement AFM 1824 p. 7,
        # repris de l etude Cahors), masse totale inchangee.
        'porte': {'x': 5.3, 'y': 0.6, 'cote': 'droite', 'moment_ouverture': {'kgm': 21.0, 'libelle': 'porte coulissante ouverte (+21 kg.m, supplement AFM 1824)'}},
        'places': places,
        'rangees': [{'id': 'D', 'libelle': 'droite', 'y': 0.25, 'xmin': 2.6, 'xmax': 5.65},
                    {'id': 'G', 'libelle': 'gauche', 'y': -0.25, 'xmin': 3.2, 'xmax': 5.65},
                    {'id': 'EXT', 'libelle': 'exterieur (porte, marche)', 'y': 0.5 + 0.35, 'xmin': 3.9, 'xmax': 5.9, 'exterieur': True}],
        'cabine': {'x0': 2.55, 'x1': 5.7, 'zones': [{'nom': 'cabine', 'x0': 2.55, 'x1': 5.7, 'largeur': 1.0}], 'porte': {'x0': 4.02, 'x1': 5.6, 'cote': 'droite'}},
        # Schema des planches (repris de l ancienne IHM et de l etude Cahors) : fuselage 2.55 a 5.70 m,
        # aile 3.50 a 5.10 m, volume cabine cote porte 3.30 a 5.60 m, compartiment arriere 5.30 a 5.60 m.
        'dessin': {'fuselage': [[1.9, 0.30], [2.55, 0.50], [5.7, 0.50], [7.4, 0.22], [8.4, 0.12]],
                   'aile': {'x0': 3.5, 'x1': 5.1}, 'empennage': {'x0': 7.6, 'x1': 8.4, 'demi_envergure': 1.4},
                   'blocs': [{'nom': 'porte coulissante', 'x0': 4.02, 'x1': 5.6, 'cote': 'droite'},
                             {'nom': 'volume cabine', 'x0': 3.3, 'x1': 5.6, 'y0': 0.05, 'y1': 0.45},
                             {'nom': 'compartiment arriere', 'x0': 5.3, 'x1': 5.6, 'y0': -0.45, 'y1': -0.05}],
                   'graduations': [3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0]},
        'variantes': [v_h4, v_h2], 'variante_defaut': 'b2h4',
        'source': 'avions/pc6-b2h4/planches_club.json, avions/pc6-b2h2/envelope.json ; schema : planches et etude Cahors',
    }


# ------------------------------------------------------------------ PAC 750XL
def pac750():
    d = lit('pac750xl', 'envelope.json')
    cab = d['cabin']
    x0, x1 = cab['floor_from_sta_in'], cab['floor_to_sta_in']
    mtow = d['weights']['mtow_lb']
    # Configuration du club : 10 places cote copilote (droite), 7 places derriere le pilote (gauche),
    # reparties sur le plancher (STA 82 a 240). Les 12 positions de la figure 6-10 du POH sont
    # gardees dans avions/pac750xl/envelope.json pour memoire.
    xd = [round(x0 + 10 + i * (x1 - x0 - 16) / 9, 1) for i in range(10)]
    xg = [round(120 + i * (x1 - 4 - 120) / 6, 1) for i in range(7)]
    places = [{'id': f'D{i+1}', 'x': x, 'y': 18.0} for i, x in enumerate(xd)]
    places += [{'id': f'G{i+1}', 'x': x, 'y': -18.0} for i, x in enumerate(xg)]
    variantes = []
    for e in d['envelopes']:
        vid = 'std' if 'standard' in e['name'] else 'gros_reservoirs'
        variantes.append({'id': vid, 'libelle': e['name'].replace('Normal category, ', 'POH, ') + f', MTOW {mtow} lb', 'mtow': mtow,
                          'enveloppe': {'avant': [list(map(float, p)) for p in e['forward_limit']], 'arriere': [[0.0, e['aft_limit_in']], [float(mtow), e['aft_limit_in']]]},
                          'source': e['source']})
    door = cab['door']
    return {
        'id': 'pac750xl', 'libelle': 'PAC 750XL', 'type': 'Pacific Aerospace 750XL', 'famille': 'pac750xl',
        'unites': {'masse': 'lb', 'bras': 'in', 'carburant': 'lb'}, 'kg_par_unite_masse': KG_PAR_LB,
        'pesees': [{'id': 'estim', 'libelle': 'estimation (a remplacer par la pesee)', 'masse_vide': 3300, 'bras_vide': 110.58,
                    'source': 'ordre de grandeur (tiers, exemple POH) : saisir la pesee reelle'}],
        'mac': {'lemac': d['mac']['lemac_in'], 'longueur': d['mac']['length_in']},
        'pilote': {'bras': 66.5, 'masse_kg_defaut': 80},
        'carburant': {'capacite': 1476, 'par_rotation': None, 'reserve': None, 'defaut': 500, 'table': [[0, 110.21], [1476, 110.21]]},
        'porte': {'x': (door['from_sta_in'] + door['to_sta_in']) / 2, 'y': -27.0, 'cote': 'gauche'},
        'places': places,
        'rangees': [{'id': 'D', 'libelle': 'droite (cote copilote)', 'y': 18.0, 'xmin': x0 + 4, 'xmax': x1 - 2},
                    {'id': 'C', 'libelle': 'centre', 'y': 0.0, 'xmin': x0 + 4, 'xmax': x1 - 2},
                    {'id': 'G', 'libelle': 'gauche (derriere le pilote)', 'y': -18.0, 'xmin': 112.0, 'xmax': x1 - 2},
                    {'id': 'EXT', 'libelle': 'exterieur (porte)', 'y': -(27.0 + 14.0), 'xmin': door['from_sta_in'] - 10, 'xmax': door['to_sta_in'] + 20, 'exterieur': True}],
        'cabine': {'x0': x0, 'x1': x1, 'zones': [{'nom': 'cabine', 'x0': x0, 'x1': x1, 'largeur': cab['max_width_in']}],
                   'porte': {'x0': door['from_sta_in'], 'x1': door['to_sta_in'], 'cote': 'gauche'}},
        'dessin': {'fuselage': [[-10.0, 14.0], [30.0, 22.0], [x0, 27.0], [x1, 27.0], [330.0, 12.0], [380.0, 8.0]],
                   'aile': {'x0': d['mac']['lemac_in'], 'x1': d['mac']['lemac_in'] + d['mac']['length_in']}, 'empennage': {'x0': 345.0, 'x1': 380.0, 'demi_envergure': 55.0},
                   'blocs': [{'nom': 'porte a rouleau', 'x0': door['from_sta_in'], 'x1': door['to_sta_in'], 'cote': 'gauche'}],
                   'train': [{'nom': 'train principal (STA 141.42)', 'x0': 128.0, 'x1': 155.0, 'y': 72.0}, {'nom': 'roue avant (STA 16.4)', 'x0': 4.0, 'x1': 29.0, 'y': 0.0}],
                   'graduations': [100, 125, 150, 175, 200, 225, 250, 300, 350]},
        'variantes': variantes, 'variante_defaut': 'std',
        'a_verifier': ['masse a vide 3300 lb et bras 110.58 in : ordre de grandeur, saisir la pesee reelle',
                       'places : 10 cote copilote et 7 derriere le pilote (configuration du club), bras repartis sur le plancher STA 82 a 240 sans source',
                       'bras carburant : reservoir avant 110.21 in, arriere 139.15 in ; sequence de remplissage non connue'],
        'source': 'avions/pac750xl/envelope.json (POH PAC 750XL, TCDS EASA)',
    }


# ------------------------------------------------------------------ DHC-6
def dhc6():
    d = lit('dhc6', 'envelope.json')
    st = {s['name']: s.get('arm') for s in d['stations']}
    st2 = lit('dhc6', 'stations.json')
    cab = d['cabin']
    x0, x1 = cab['front_bulkhead_station_in'], cab['rear_bulkhead_station_in']
    variantes = []
    for e in d['envelopes']:
        vs = e.get('vertices') or []
        if not vs or any(v[0] is None or v[1] is None for v in vs):
            continue
        fwd = [v for v in vs if v[1] < 210]; aft = max(v[1] for v in vs); top = max(v[0] for v in vs)
        vid = 'decollage' if 'take-off' in e['name'] else ('atterrissage' if 'landing' in e['name'] else 'flotteurs')
        if vid == 'flotteurs':
            continue
        variantes.append({'id': vid, 'libelle': e['name'].replace('Series 300 landplane and wheel-skiplane, ', 'TCDS A9EA, ') + f', max {top} lb',
                          'mtow': top, 'enveloppe': {'avant': [list(map(float, v)) for v in sorted(fwd)], 'arriere': [[0.0, aft], [float(top), aft]]},
                          'source': e.get('source', 'TCDS FAA A9EA')})
    xs = sorted(st2['floor_positions_hypothesis_in'])
    places = [{'id': f'D{i+1}', 'x': float(x), 'y': 20.0} for i, x in enumerate(xs)]
    places += [{'id': f'G{i+1}', 'x': float(x), 'y': -20.0} for i, x in enumerate(xs)]
    porte = st2['door']
    p0, p1 = float(porte['clear_opening_from_sta_in']), float(porte['clear_opening_to_sta_in'])
    demi = cab['width_max_in'] / 2
    return {
        'id': 'dhc6', 'libelle': 'DHC-6 Twin Otter 300', 'type': 'de Havilland DHC-6-300 Twin Otter', 'famille': 'dhc6',
        'unites': {'masse': 'lb', 'bras': 'in', 'carburant': 'lb'}, 'kg_par_unite_masse': KG_PAR_LB,
        'pesees': [{'id': 'estim', 'libelle': 'estimation (a remplacer par la pesee)', 'masse_vide': 7400, 'bras_vide': 200.0, 'source': 'ordre de grandeur : saisir la pesee reelle'}],
        'mac': {'lemac': d['mac']['lemac_in'], 'longueur': d['mac']['length_in']},
        'pilote': {'bras': st.get('Pilot seats (2)', 95.0), 'masse_kg_defaut': 80, 'nombre': 2},
        'carburant': {'capacite': int(378 * 6.7), 'par_rotation': None, 'reserve': None, 'defaut': 1200,
                      'table': [[0, 162.5], [round(181 * 6.7), 162.5], [round(378 * 6.7), round((181 * 162.5 + 197 * 240.0) / 378, 2)]]},
        'porte': {'x': (p0 + p1) / 2, 'y': -40.0, 'cote': 'gauche'},
        'places': places,
        'rangees': [{'id': 'D', 'libelle': 'droite', 'y': 20.0, 'xmin': x0 + 8, 'xmax': x1 - 6},
                    {'id': 'C', 'libelle': 'centre', 'y': 0.0, 'xmin': x0 + 8, 'xmax': x1 - 6},
                    {'id': 'G', 'libelle': 'gauche', 'y': -20.0, 'xmin': x0 + 8, 'xmax': x1 - 6},
                    {'id': 'EXT', 'libelle': 'exterieur (porte)', 'y': -(demi + 14.0), 'xmin': p0 - 10, 'xmax': p1 + 20, 'exterieur': True}],
        'cabine': {'x0': x0, 'x1': x1, 'zones': [{'nom': 'cabine', 'x0': x0, 'x1': x1, 'largeur': cab['width_max_in']}],
                   'porte': {'x0': p0, 'x1': p1, 'cote': 'gauche'}, 'train_principal': st2['main_gear_sta_in'], 'train_avant': st2['nose_gear_sta_in'],
                   'rangees_sieges_commuter': st2['seat_rows_arm_in']},
        'dessin': {'fuselage': [[-40.0, 16.0], [40.0, 30.0], [x0, 34.5], [x1, 34.5], [420.0, 18.0], [560.0, 9.0]],
                   'aile': {'x0': d['mac']['lemac_in'], 'x1': d['mac']['lemac_in'] + d['mac']['length_in']}, 'empennage': {'x0': 500.0, 'x1': 560.0, 'demi_envergure': 90.0},
                   'blocs': [{'nom': 'double porte gauche', 'x0': p0, 'x1': p1, 'cote': 'gauche'}],
                   'train': [{'nom': 'train principal (FS 232)', 'x0': st2['main_gear_sta_in'] - 16, 'x1': st2['main_gear_sta_in'] + 16, 'y': 73.0}, {'nom': 'roue avant (FS 53)', 'x0': st2['nose_gear_sta_in'] - 12, 'x1': st2['nose_gear_sta_in'] + 12, 'y': 0.0}],
                   'graduations': [125, 150, 175, 200, 225, 250, 275, 300, 325, 400, 500]},
        'variantes': variantes, 'variante_defaut': 'decollage',
        'a_verifier': ['masse a vide 7400 lb et bras 200 in : ordre de grandeur, saisir la pesee reelle',
                       'positions des paras au sol : hypothese (deux files, pas 20 in, FS 125 a 325), manuel de masse et centrage PSM 1-63-8 non trouve',
                       'ordre de remplissage des reservoirs (avant puis arriere) suppose pour le bras carburant',
                       'porte gauche FS 270 a 326 et trains (FS 232 et 53) mesures sur plans FlightSafety, +/- 5 in'],
        'source': 'avions/dhc6/envelope.json (TCDS FAA A9EA, Viking) et avions/dhc6/stations.json (mesures sur plans)',
    }


if __name__ == '__main__':
    avions = [caravan_208b(), caravan_208a(), pilatus(), pac750(), dhc6()]
    js = ('// Genere par web/tools/gen_avions.py depuis avions/**. Ne pas editer a la main : corriger la source\n'
          '// puis relancer le script. Aucune immatriculation ici : un modele par type, pesees par lettre.\n'
          'export const AVIONS = ' + json.dumps(avions, indent=1, ensure_ascii=False) + ';\n')
    (ROOT / 'web' / 'js' / 'avions.js').write_text(js)
    # copies pour la Cloud Function (le paquet deploye ne contient que functions/) : memes modules,
    # extension .mjs ; functions/lib.test.js verifie qu'elles sont a jour.
    lib = ROOT / 'functions' / 'lib'; lib.mkdir(exist_ok=True)
    (lib / 'avions.mjs').write_text(js)
    (lib / 'centrage.mjs').write_text((ROOT / 'web' / 'js' / 'centrage.js').read_text())
    spec = ROOT / 'docs' / 'openapi.json'
    if spec.exists():
        (lib / 'openapi.json').write_text(spec.read_text())
    print('ecrit web/js/avions.js et functions/lib/ :', [(a['id'], len(a['places']), [v['id'] for v in a['variantes']], [p['id'] for p in a['pesees']]) for a in avions])
