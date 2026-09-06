# API REST · centrage et placement des paras

Base : `https://ceps09-centrage.web.app/api/v1` · specification OpenAPI 3 : [`openapi.json`](openapi.json)
(aussi servie sur `/api/v1/openapi.json`). Sans authentification, CORS ouvert. JSON en entree et en
sortie, UTF-8. Toute reponse porte `ok` (booleen) et, en cas d'erreur, `message`.

Unites : chaque avion a ses unites natives (`unites` dans le modele : lb et in pour Cessna, PAC et
DHC-6 ; kg et m pour le PC-6). Les masses des paras et du pilote sont toujours en **kg** ; le
carburant est en unite carburant de l'avion (lb, ou litres pour le PC-6) ; masses limites, bras,
CG et marges sont en unites natives.

## Routes

| Methode | Route | Role |
|---|---|---|
| GET | `/version` | version de l'API et du solveur, limites |
| GET | `/openapi.json` | la specification |
| GET | `/avions` | liste des modeles (id, libelle, unites, variantes, pesees, nombre de places) |
| GET | `/avions/{id}` | un modele complet : places (id, bras `x`, lateral `y`), rangees (dont la ligne exterieure cote porte), cabine, dessin, MAC, carburant, porte, variantes (MTOW et enveloppe), pesees, points a verifier |
| POST | `/avions/{id}/centrage` | etapes de centrage d'un placement donne, calcul pur (aucun appel au solveur, pas de limite) |
| POST | `/avions/{id}/placement` | placement optimal par le solveur a partir du modele ; reponse enrichie (placement, etapes) |
| POST | `/placement` | stick brut au format du binaire `placement` (voir `../solveur/README.md`) |

Identifiants d'avion : `c208b`, `c208a`, `pc6`, `pac750xl`, `dhc6`.

## Corps des POST par avion

```json
{
  "variante": "ape2",            "pesee": "A",
  "masse_vide": 4890,            "bras_vide": 188.99,          (facultatif : corrige la pesee)
  "pilote_kg": 80,               "carburant": 900,             (unite carburant de l'avion)
  "porte_ouverte": false,                                      (PC-6 : +21 kg.m apres le decollage)
  "enveloppe": {"mtow": 9062, "avant": [[5500, 179.6], [9062, 200.23]], "arriere": [[0, 204.35], [9062, 204.35]]},   (facultatif)
  "paras": [
    {"nom": "Alice", "masse_kg": 93, "groupe": "VR4", "sortie": 1},
    {"nom": "Bruno", "masse_kg": 105, "groupe": "VR4", "sortie": 1, "verrou": "G4"},
    {"nom": "Chloe", "masse_kg": 80, "sortie": 2, "pos": {"x": 250, "y": -16}, "verrou": "libre"},
    {"nom": "Lea", "masse_kg": 65, "tandem": "T1", "role": "passager", "sortie": 3},
    {"nom": "Marc", "masse_kg": 98, "tandem": "T1", "role": "porteur", "sortie": 3, "interdit": ["COPI"]}
  ],
  "options": {"marge_avant_min": 0.5, "tolerance_marge": 0.25, "etapes": "premier_groupe", "temps_max_s": 8, "groupes_ordonnes": false, "rapide": false}
}
```

- `place` : id d'une place du modele (pour `/centrage`, la place occupee ; pour `/placement`, la
  place imposee si `verrou` est vrai). `pos` : position libre `{x: bras, y: lateral}` (rangee ou
  ligne exterieure, voir `rangees` du modele). `verrou` : `true`, un id de place ou `"libre"`.
- `sortie` : rang de sortie ; les ex aequo sortent ensemble, le plus petit rang en premier. Les
  etapes sont : decollage, (porte ouverte), apres la sortie du premier groupe, ou apres chaque
  rang avec `options.etapes = "toutes"`.
- `options.marge_avant_min` et `tolerance_marge` sont dans l'unite de bras de l'avion : par defaut
  0.5 et 0.25 in (Cessna, PAC, DHC-6), 0.013 et 0.006 m (PC-6).
- Solveur : marge arriere maximale au decollage sous marge avant garantie (`marge_avant_min`) au
  decollage et apres le premier groupe ; puis, a `tolerance_marge` pres, le placement le plus
  realiste (groupes proches, premiers sortants pres de la porte, passager tandem devant son
  porteur). `temps_max_s` est plafonne a 10 s par phase.

## Reponses

`/centrage` et `/placement` renvoient :

```json
{
  "ok": true,
  "avion": {"id": "c208b", "variante": "ape2", "pesee": "A", "unites": {...}, "mtow": 9062, "masse_vide": 4890, "bras_vide": 188.99, "enveloppe": {...}},
  "parametres": {"piloteKg": 80, "carburant": 900, "porteOuverte": false},
  "etapes": [
    {"etape": "decollage", "rang": null, "paras_a_bord": 15, "masse": 8894.1, "cg": 198.96, "pct_mac": 32.2,
     "limite_avant": 199.65, "limite_arriere": 204.35, "marge_avant": -0.69, "marge_arriere": 5.39, "statut": "avant"},
    {"etape": "apres la sortie du rang 1 (4 sorti(s))", "rang": 1, ...}
  ],
  "bilan": {"statut": "avant", "margeAvant": -0.69, "margeArriere": 5.39},
  "paras_sans_place": 0
}
```

`statut` vaut `ok`, `avant` (trop centre avant), `arriere` ou `mtow`. `/placement` ajoute
`solveur` (sortie brute : `marge_arriere_max`, `phase1`, `phase2`, `cout_realisme`,
`premier_groupe`, `temps_s`, et `placement_au_mieux` avec `message` quand aucun placement ne
respecte les contraintes, `ok` vaut alors `false`) et `placement` (`nom`, `masse_kg`, `place`,
`x`, `y`, `verrou`).

## Exemples

```bash
B=https://ceps09-centrage.web.app/api/v1
curl -s $B/avions | jq '.avions[] | {id, nb_places, variantes: [.variantes[].id]}'
curl -s $B/avions/pc6 | jq '.avion.places'

# centrage d'un placement donne (instantane)
curl -s -X POST $B/avions/c208b/centrage -H 'Content-Type: application/json' -d '{
  "variante": "ape2", "pesee": "A", "pilote_kg": 80, "carburant": 900,
  "paras": [{"nom": "A", "masse_kg": 90, "sortie": 1, "place": "G6"}, {"nom": "B", "masse_kg": 95, "sortie": 1, "place": "D6"},
            {"nom": "C", "masse_kg": 85, "sortie": 2, "pos": {"x": 231.2, "y": 0}}]}' | jq '.etapes[] | {etape, cg, marge_avant, marge_arriere, statut}'

# placement optimal par le solveur (2 a 10 s)
curl -s -X POST $B/avions/pc6/placement -H 'Content-Type: application/json' -d '{
  "pilote_kg": 80, "carburant": 250, "porte_ouverte": true,
  "paras": [{"nom": "P1", "masse_kg": 95, "sortie": 1}, {"nom": "P2", "masse_kg": 88, "sortie": 1}, {"nom": "P3", "masse_kg": 75, "sortie": 2},
            {"nom": "P4", "masse_kg": 102, "sortie": 2}, {"nom": "P5", "masse_kg": 80, "sortie": 3}]}' | jq '{ok, placement, bilan}'
```

Python :

```python
import requests
B = 'https://ceps09-centrage.web.app/api/v1'
r = requests.post(f'{B}/avions/c208b/placement', json={'pilote_kg': 80, 'carburant': 900,
    'paras': [{'nom': f'P{i}', 'masse_kg': 90, 'sortie': 1 + i // 4} for i in range(12)]}, timeout=60)
res = r.json()
print(res['ok'], [(p['nom'], p['place']) for p in res['placement']], res['bilan'])
```

## Limites et erreurs

- 12 calculs par minute et 300 par jour par adresse IP, 2 calculs simultanes par instance (3
  instances) : au-dela, `429` avec `Retry-After`. Une demande identique deja calculee est servie
  du cache (`X-Cache: hit`) et ne compte pas.
- Corps limite a 256 ko, 30 paras, 40 places ; `temps_max_s` entre 0.5 et 10.
- `400` entree invalide (le `message` dit quoi), `404` avion ou route inconnue, `413` corps trop
  gros, `504` solveur interrompu, `500` erreur du solveur.
- Les valeurs des modeles viennent des manuels et des planches du club, avec des points a
  verifier (`a_verifier` dans le modele) : outil d'aide, pas un document approuve.
