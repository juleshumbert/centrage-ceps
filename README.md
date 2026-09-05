# Centrage CEPS · optimisation du centrage des avions de parachutage

Projet dedie a la masse et au centrage des avions largueurs : comment placer les paras
pour rester dans l'enveloppe quels que soient leur nombre, leurs masses et le carburant,
et avec quelles donnees constructeur (enveloppes, bras de levier, dimensions de cabine)
pour chaque type d'avion.

Il rassemble :

- l'etude **heuristique de remplissage a places fixes** du Caravan (ordres de remplissage,
  enumeration exhaustive, placement optimal d'un manifeste par MILP, binaires livrables),
  migree depuis `centrage_c208/heuristique_remplissage/` le 05/09/2026 ;
- les **donnees masse et centrage par type d'avion** (`avions/`), extraites des manuels de
  vol (POH / AFM) avec leurs sources, pour tracer centrogrammes et schemas de cabine.

## Avions

| Dossier | Type | Documents obtenus | Enveloppe | Stations | Cabine |
|---|---|---|---|---|---|
| `avions/c208b` | Cessna 208B Grand Caravan (C208B-A, C208B-B) | POH 208B G1000 complet (536 p.), TCDS FAA A37CE et EASA IM.A.226 | oui, 208B / 208B EX, decollage et atterrissage | oui (sieges, 6 zones cargo, pod) | oui (stations FS, largeurs, hauteurs, portes, rails) |
| `avions/c208` | Cessna 208 Caravan (675 SHP) | TCDS, extrait POH sections 1 a 4, Spec & Description | oui (TCDS) | partiel (section 6 non trouvee) | stations et porte cargo |
| `avions/pc6-b2h4` | Pilatus PC-6/B2-H4 (PC6-A, PC6-B) | AFM 1820 rev. 8 (PIM, 80 p.), TCDS OFAC F 56-10, brochures, DT FFP 33 | oui (identique aux planches club) | rangees de sieges, carburant, options | volume seulement, porte non cotee (valeurs tierces non verifiees) |
| `avions/pc6-b2h2` | Pilatus PC-6/B2-H2 | mêmes sources (aucun AFM B2-H2 public) | oui (TCDS) | idem B2-H4 | idem B2-H4 |
| `avions/pac750xl` | Pacific Aerospace 750XL | POH complet (278 p.), TCDS EASA IM.A.081 | oui, deux variantes de reservoirs | oui, 12 positions paras (fig. 6-10) | oui (158 x 54 x 56 in, porte a rouleau, trains) |
| `avions/dhc6` | de Havilland DHC-6-300 Twin Otter | TCDS FAA A9EA, manuel FlightSafety (local seulement, 213 Mo), brochures Viking | oui (decollage, atterrissage, flotteurs) | pilotes, soutes, carburant ; rangees de sieges non trouvees | oui (221 x 69 x 59 in, portes) |
| `avions/dhc6/dhc5` | DHC-5 Buffalo (demande initiale « DHC5 ») | brochure constructeur seulement | non (aucun manuel de vol public) | non | dimensions generales |

Le detail des valeurs, des sources (URL, fichier, page) et des points ouverts est dans le
`notes.md` de chaque avion ; `avions/README.md` decrit le format et les ecarts constates
avec les planches du club.

## Arborescence

| Dossier | Contenu |
|---|---|
| `solveur/` | le solveur C++ `placement` (HiGHS embarque) : `src/placement.cpp`, `CMakeLists.txt`, `build.sh`, `MODELE.md`, `exemples/`, `tests/smoke.sh`. Binaires publies en release GitHub a chaque tag `v*` |
| `web/` | l'IHM (site statique Firebase Hosting `ceps09-centrage`) : choix de l'avion, stick, appel du solveur, plan cabine avec glisser-deposer, centrogramme. `js/avions.js` est genere par `web/tools/gen_avions.py` |
| `functions/` | Cloud Function `placement` (codebase `centrage`, europe-west1) : `/api/placement` execute le binaire du solveur sur le stick JSON, apres verification du jeton Firebase et de l'appartenance au club |
| `avions/` | un dossier par type : `envelope.json` (enveloppe, stations, carburant, cabine), `notes.md` (valeurs sourcees, URL de chaque manuel), `poh/` (manuels PDF, en local seulement, non versionnes) |
| `heuristique_remplissage/` | etude Caravan : scripts Python, `enumeration/` (Rust), `placement_rs/` (Rust), `output/` (figures, fiches PDF, JSON), voir son README |
| `reference/notebooks/` | snapshot des notebooks de planches de `centrage_c208`, lus par `caravan_model.py` (geometrie cabine, table carburant, enveloppe), ne pas editer ici |
| `.github/workflows/` | `solveur.yml` (build + test sur 4 plateformes, release sur tag), `deploy.yml` (tests, build du binaire statique, deploiement Firebase sur push main) |

## IHM web et solveur

```
navigateur (web/)  --POST /api/placement (stick JSON)-->  Cloud Function (functions/)  --stdin-->  placement (solveur/, binaire statique)
      ^                                                                                                      |
      +---------------------------- resultat JSON : places, etapes, marges  <--------------------------------+
```

- L'IHM construit le stick au format du solveur (`solveur/README.md`), l'envoie, puis affiche
  le placement sur le plan cabine. Deplacer un para (glisser-deposer, echange si la place est
  occupee) recalcule masse, CG, marges et centrogramme **cote client**, avec les memes formules.
  Un clic verrouille un para sur sa place : le solveur relance alors avec ces places imposees.
- Avions proposes : C208B-A, C208B-B (C208B), PC6-A, PC6-B (PC-6 B2-H4), donnees des planches
  du club ; PAC 750XL generique (POH, masse a vide a saisir). DHC-6 absent tant que les bras
  des rangees ne sont pas trouves.
- Acces reserve aux membres (portail `auth.js` partage avec les sites soeurs, projet Firebase
  `paraclub-planning-f966c`). URL : https://ceps09-centrage.web.app

### Developper en local

```bash
cd solveur && ./build.sh && ./tests/smoke.sh          # le binaire
npm test --prefix web && npm test --prefix functions   # moteur client, garde-fous de la fonction
python3 web/tools/gen_avions.py                        # apres modification de avions/*/planches_club.json
mkdir -p functions/bin && cp solveur/build/placement functions/bin/   # binaire statique (PLACEMENT_STATIC=1) pour la fonction
npx firebase-tools@15 deploy --only hosting:centrage,functions:centrage --project paraclub-planning-f966c
```

Le deploiement de production passe par `deploy.yml` (Workload Identity Federation, comme les
apps soeurs) a chaque push sur `main`. Publier une release du solveur : `git tag v1.1.0 && git push --tags`.

## Demarrage rapide (etude heuristique)

```bash
cd heuristique_remplissage
python3 caravan_model.py                                  # les 20 places et l'ordre par pivot
python3 placement_milp.py manifestes/exemple_groupes.json # placement optimal d'un manifeste (MILP Python)
python3 verif_heuristique.py 235                          # heuristique a pivot contre l'oracle
```

Dependances Python : `numpy`, `scipy` (>= 1.11 pour `milp`), `matplotlib`. Les binaires
Rust se reconstruisent comme decrit dans `heuristique_remplissage/README.md`.

## Conventions

- Bras en inches et masses en lbs pour les Cessna (datum et MAC du POH), metres et kg pour
  les Pilatus : chaque `envelope.json` porte ses unites et son datum, ne jamais melanger.
- Paras equipes : 90 kg (profil militaire) ou 80 kg (profil civil), pilote 80 ou 86 kg,
  memes forfaits que les planches de `centrage_c208`.
- Toute valeur constructeur est accompagnee de sa source (document, page).
