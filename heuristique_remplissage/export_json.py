"""Convertit un manifeste Python (placement_milp) en entree JSON du binaire placement_rs,
avec les donnees Caravan du modele (places N=20, enveloppe, bras carburant exact de la
table du notebook pour la quantite donnee, pilote a 135,5 in). Masses en lbs, bras en in.

Usage : python3 export_json.py manifestes/exemple_groupes.json > /tmp/x.json
"""
import json
import sys
from pathlib import Path

from caravan_model import SLOTS, AIRCRAFT, LBS2KG, MTOW_LBS, FWD_MASS, FWD_CG, AFT_CG, fuel_state


def export(man, options=None):
    ac = AIRCRAFT[man['immat']]
    fm, fw = fuel_state(man['fuel_lbs'])
    places = [dict(id=str(s.idx), x=s.x, y=s.y, copilote=(s.idx == 0), centre=(s.row == 'centre')) for s in SLOTS]
    paras = []
    for p in man['paras']:
        q = dict(nom=p['nom'], masse=round(p['kg'] * LBS2KG, 3))
        for k in ('groupe', 'sortie', 'tandem', 'role'):
            if p.get(k) is not None:
                q[k] = p[k]
        paras.append(q)
    return dict(
        unites=dict(masse='lbs', bras='in'),
        avion=dict(immat=man['immat'], masse_vide=ac['ew'], moment_vide=ac['ew_moment'] * 1000),
        enveloppe=dict(avant=[[float(w), float(c)] for w, c in zip(FWD_MASS, FWD_CG)],
                       arriere=[[0.0, AFT_CG], [MTOW_LBS, AFT_CG]], mtow=MTOW_LBS),
        carburant=dict(masse=fw, bras=(fm * 1000 / fw) if fw > 0 else 200.0),
        pilote=dict(masse=man['pilote_kg'] * LBS2KG, bras=135.5),
        porte=dict(x=307.0, y=-32.0),
        places=places, paras=paras,
        options={**dict(marge_cible=0.5, sequence=True, groupes_ordonnes=False, poids_groupe=2.0,
                        poids_sortie=1.0, poids_lateral=0.5, pas=25.0, temps_max_s=1.5), **(options or {})})


if __name__ == '__main__':
    man = json.loads(Path(sys.argv[1]).read_text())
    print(json.dumps(export(man), indent=1, ensure_ascii=False))
