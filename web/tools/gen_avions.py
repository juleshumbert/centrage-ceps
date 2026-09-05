"""Genere web/js/avions.js (base avions de l'IHM) depuis avions/*/planches_club.json et
avions/pac750xl/envelope.json : rien n'est recopie a la main. Relancer apres toute mise a
jour de ces fichiers.

    python3 web/tools/gen_avions.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AV = ROOT / 'avions'


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
    env = d['envelopes'][0]
    fuel = d['fuel']
    out = []
    for immat, r in d['registrations'].items():
        out.append({
            'id': immat, 'immat': immat, 'type': 'Cessna 208B Grand Caravan', 'famille': 'c208b',
            'unites': {'masse': 'lb', 'bras': 'in', 'carburant': 'lb'},
            'kg_par_unite_masse': 1 / 2.20462,
            'masse_vide': r['ew_lb'], 'bras_vide': r['ew_cg_in'],
            'mtow': d['limits']['mtow_lb'],
            'enveloppe': {'avant': [[w, a] for w, a in zip(env['forward_limit']['weight_lb'], env['forward_limit']['arm_in'])],
                          'arriere': [[0, env['aft_limit_in']], [d['limits']['mtow_lb'], env['aft_limit_in']]]},
            'mac': {'lemac': d['mac']['lemac_in'], 'longueur': d['mac']['length_in']},
            'pilote': {'bras': 135.5, 'masse_kg_defaut': 80},
            'carburant': {'capacite': fuel['capacity_usable_lb'], 'par_rotation': fuel['per_rotation_lb'], 'reserve': fuel['reserve_lb'],
                          'defaut': 900,
                          'table': [[t['lb'], t['arm_in']] for t in fuel['table']]},
            'porte': {'x': 307.0, 'y': -32.0, 'cote': 'gauche'},
            'places': places,
            'cabine': {'x0': 100.0, 'x1': 356.0,
                       'zones': [{'nom': z['name'], 'x0': z['x0_in'], 'x1': z['x1_in'], 'largeur': z['width_in']} for z in zones],
                       'porte': {'x0': 282.0, 'x1': 332.0, 'cote': 'gauche'}},
            'source': 'avions/c208b/planches_club.json (planches club) ; porte cargo FS 282 a 332 (POH 208B)',
        })
    return out


def pilatus():
    d = json.loads((AV / 'pc6-b2h4' / 'planches_club.json').read_text())
    env = d['envelopes'][0]
    # Rangees des planches : "haute" et "basse" sur le dessin en vue de dessus. Convention ici :
    # haute = droite (y > 0), basse = gauche (y < 0). Porte de largage a droite (hypothese,
    # n'influence que le classement par proximite de la porte, pas le centrage).
    places = [{'id': f'D{i+1}', 'x': x, 'y': 0.45} for i, x in enumerate(d['fixed_seats']['rangee_haute_m'])]
    places += [{'id': f'G{i+1}', 'x': x, 'y': -0.45} for i, x in enumerate(d['fixed_seats']['rangee_basse_m'])]
    fuel = d['fuel']
    table = [[t['kg'], t['arm_m']] for t in fuel['table'] if t['kg'] > 0]
    out = []
    for immat, r in d['registrations'].items():
        out.append({
            'id': immat, 'immat': immat, 'type': 'Pilatus PC-6/B2-H4', 'famille': 'pc6',
            'unites': {'masse': 'kg', 'bras': 'm', 'carburant': 'L'},
            'kg_par_unite_masse': 1.0,
            'masse_vide': r['ew_kg'], 'bras_vide': r['ew_cg_m'],
            'mtow': d['limits']['mtow_kg'],
            'enveloppe': {'avant': [[w, a] for w, a in zip(env['forward_limit']['weight_kg'], env['forward_limit']['arm_m'])],
                          'arriere': [[0, env['aft_limit_m']], [d['limits']['mtow_kg'], env['aft_limit_m']]]},
            'mac': {'lemac': d['mac']['lemac_m'], 'longueur': d['mac']['length_m']},
            'pilote': {'bras': 3.05, 'masse_kg_defaut': 80},
            'carburant': {'capacite': fuel['capacity_l'], 'par_rotation': fuel['per_rotation_l'], 'reserve': fuel['reserve_l'],
                          'defaut': 250, 'kg_par_litre': 129.6 / 160.9,
                          'table': table},
            'porte': {'x': 5.3, 'y': 0.9, 'cote': 'droite'},
            'places': places,
            'cabine': {'x0': 2.5, 'x1': 5.7, 'zones': [{'nom': 'cabine', 'x0': 2.5, 'x1': 5.7, 'largeur': 1.16}],
                       'porte': {'x0': 4.2, 'x1': 5.5, 'cote': 'droite'}},
            'source': 'avions/pc6-b2h4/planches_club.json (planches club) ; cabine et porte : ordre de grandeur, voir avions/pc6-b2h4/notes.md',
        })
    return out


def pac750():
    d = json.loads((AV / 'pac750xl' / 'envelope.json').read_text())
    env = d['envelopes'][0]
    paras = [s for s in d['stations'] if s['type'] == 'parachutist']
    places = [{'id': f'P{i+1}', 'x': s['arm_in'], 'y': 0.0} for i, s in enumerate(paras)]
    cab = d['cabin']
    return [{
        'id': 'PAC750XL', 'immat': 'PAC 750XL (generique)', 'type': 'Pacific Aerospace 750XL', 'famille': 'pac750xl',
        'unites': {'masse': 'lb', 'bras': 'in', 'carburant': 'lb'},
        'kg_par_unite_masse': 1 / 2.20462,
        'masse_vide': 3300, 'bras_vide': 110.58,
        'mtow': d['weights']['mtow_lb'],
        'enveloppe': {'avant': [list(p) for p in env['forward_limit']],
                      'arriere': [[0, env['aft_limit_in']], [d['weights']['mtow_lb'], env['aft_limit_in']]]},
        'mac': {'lemac': d['mac']['lemac_in'], 'longueur': d['mac']['length_in']},
        'pilote': {'bras': 66.5, 'masse_kg_defaut': 80},
        'carburant': {'capacite': 1476, 'par_rotation': None, 'reserve': None, 'defaut': 500,
                      'table': [[0, 110.21], [1476, 110.21]]},
        'porte': {'x': 212.0, 'y': -27.0, 'cote': 'gauche'},
        'places': places,
        'cabine': {'x0': cab['floor_from_sta_in'], 'x1': cab['floor_to_sta_in'],
                   'zones': [{'nom': 'cabine', 'x0': cab['floor_from_sta_in'], 'x1': cab['floor_to_sta_in'], 'largeur': cab['max_width_in']}],
                   'porte': {'x0': cab['door']['from_sta_in'], 'x1': cab['door']['to_sta_in'], 'cote': 'gauche'}},
        'a_verifier': ['masse a vide 3300 lb et bras 110.58 in : ordre de grandeur (tiers / exemple POH), saisir la pesee reelle',
                       'bras carburant : reservoir avant 110.21 in, arriere 139.15 in ; sequence de remplissage non connue',
                       'positions paras 1 a 12 sur l axe (figure 6-10 du POH), pas de position laterale publiee'],
        'source': 'avions/pac750xl/envelope.json (POH PAC 750XL, TCDS EASA)',
    }]


if __name__ == '__main__':
    avions = caravan() + pilatus() + pac750()
    js = ('// Genere par web/tools/gen_avions.py depuis avions/*/planches_club.json et avions/pac750xl/envelope.json.\n'
          '// Ne pas editer a la main : corriger la source puis relancer le script.\n'
          'export const AVIONS = ' + json.dumps(avions, indent=1, ensure_ascii=False) + ';\n')
    (ROOT / 'web' / 'js' / 'avions.js').write_text(js)
    print('ecrit web/js/avions.js :', [a['id'] for a in avions])
