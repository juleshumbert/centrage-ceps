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

Un modele par type, sans immatriculation ; les pesees connues sont listees par lettre et se
corrigent dans l'application.

| Dossier | Type | Documents obtenus | Enveloppe(s) dans l'IHM | Places |
|---|---|---|---|---|
| `avions/c208b` | Cessna 208B Grand Caravan | POH 208B G1000 complet, TCDS FAA et EASA, STC APE (rapports TSB) | POH 8750 lb ; STC APE II 9062 lb ; STC APE III (MLW 9000) | 20 (planches club) |
| `avions/c208b` (section 208) | Cessna 208A Caravan (fuselage court) | TCDS, extrait POH sections 1 a 4, Spec & Description | POH / TCDS 8000 lb | 15 (par analogie, a verifier) |
| `avions/pc6-b2h4`, `avions/pc6-b2h2` | Pilatus PC-6 Turbo Porter | AFM 1820 rev. 8, TCDS OFAC F 56-10, brochures, DT FFP 33 | B2-H4 2800 kg ; B2-H2 2200 kg | 10 (planches club) ; porte coulissante ouverte +21 kg.m |
| `avions/pac750xl` | Pacific Aerospace 750XL | POH complet (278 p.), TCDS EASA IM.A.081 | POH, deux variantes de reservoirs | 17 : 10 cote copilote, 7 derriere le pilote (configuration club) |
| `avions/dhc6` | de Havilland DHC-6-300 Twin Otter | TCDS FAA A9EA, manuel FlightSafety (local), brochures Viking, rapports NTSB / TSB | TCDS decollage et atterrissage | 22 (hypothese : deux files, pas 20 in) |

Chaque maquette comporte une **ligne exterieure cote porte** (paras a la porte, sur la marche ou
le montant) et le dessin complet du fuselage jusqu'a la queue ; le bouton « Mise en place du 1er
groupe » envoie les premiers sortants a la porte pour verifier le centrage a cet instant. Les
schemas du Caravan et du Pilatus reprennent ceux des anciennes IHM (centrage_c208, etude Cahors).

Le detail des valeurs, des sources (URL, fichier, page) et des points ouverts est dans le
`notes.md` de chaque avion ; `avions/README.md` decrit le format et les ecarts constates.

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
- Acces public, sans authentification. La fonction est protegee contre l'abus : origine du
  site, limiteur par adresse IP (par minute et par jour), au plus deux calculs simultanes par
  instance et trois instances, cache des demandes identiques, temps de solveur plafonne
  (`functions/protection.js`). URL : https://ceps09-centrage.web.app
- **Aucune immatriculation dans le depot** (ni dans l'historique) : un modele par type, pesees
  par lettre. L'IHM permet un nom local, qui reste dans le navigateur. Les manifestes reels (noms
  des paras) sont eux aussi hors depot.
- Variantes par avion (masse max et enveloppe) : Caravan POH 8750 lb, STC APE II 9062 lb, STC
  APE III ; PC-6 B2-H4 / B2-H2 ; l'enveloppe et la MTOW se modifient dans l'application (tableau
  ou sommets deplacables), memorisees dans le navigateur.
- Placement : sur une place fixe ou en **position libre** le long d'une rangee (bras = position
  exacte), verrou sur une place ou une position libre ; le solveur ne deplace que les paras non
  verrouilles.

## API REST

`https://ceps09-centrage.web.app/api/v1` : modeles d'avions (`GET /avions`, `GET /avions/{id}`),
etapes de centrage d'un placement donne (`POST /avions/{id}/centrage`), placement optimal par le
solveur a partir du modele (`POST /avions/{id}/placement`), stick brut (`POST /placement`).
Documentation : [`docs/API.md`](docs/API.md), specification [`docs/openapi.json`](docs/openapi.json)
(servie aussi sur `/api/v1/openapi.json`). Sans authentification, CORS ouvert, memes limites que
l'IHM (12 calculs par minute et par IP, cache des demandes identiques).

## Tout lancer

Prerequis : Python 3 (avec `numpy`, `scipy`, `matplotlib` pour l'etude), Node 20 ou plus, un
compilateur C++17, `cmake` et de preference `ninja` ; `git` pour recuperer HiGHS.

```bash
git clone https://github.com/juleshumbert/centrage-ceps.git && cd centrage-ceps

# 1. le solveur (clone HiGHS v1.9.0 et nlohmann/json, compile solveur/build/placement, ~5 min)
(cd solveur && ./build.sh && ./tests/smoke.sh)
./solveur/build/placement solveur/exemples/exemple_stick.json --pdf /tmp/planche.pdf   # un stick, une planche PDF

# 2. l'IHM en local (sert web/ et branche /api/placement sur le binaire ci-dessus)
python3 web/tools/devserver.py            # puis http://127.0.0.1:8765/

# 3. les tests
npm test --prefix web                     # moteur de centrage cote client
npm ci --prefix functions && npm test --prefix functions   # garde-fous de la fonction

# 4. regenerer les donnees avions apres une modification dans avions/
python3 avions/extract_planches_club.py   # pesees, places, tables carburant depuis les notebooks
python3 web/tools/gen_avions.py           # -> web/js/avions.js

# 5. l'etude heuristique (Caravan)
(cd heuristique_remplissage && python3 placement_milp.py manifestes/exemple_groupes.json)
```

Sans compiler : les binaires du solveur sont dans les releases GitHub (Linux statique, macOS,
Windows) ; `placement --help` decrit les options et `solveur/README.md` le format JSON.

### Deployer (Firebase, projet partage du club)

Le deploiement de production est fait par `.github/workflows/deploy.yml` a chaque push sur
`main` : compilation du binaire statique, tests, `firebase deploy --only hosting:centrage,functions:centrage`
par Workload Identity Federation (variables de depot `GCP_WIF_PROVIDER`, `GCP_SERVICE_ACCOUNT`,
`FIREBASE_PROJECT_ID`, environnement `production`). Pour deployer sur un autre projet Firebase :
creer un site Hosting, adapter `.firebaserc`, puis

```bash
mkdir -p functions/bin && cp solveur/build/placement functions/bin/   # binaire Linux x86_64 STATIQUE (PLACEMENT_STATIC=1 ./build.sh)
npx firebase-tools@15 deploy --only hosting:centrage,functions:centrage --project <projet>
```

Publier une release du solveur : `git tag v1.1.0 && git push --tags` (workflow `solveur.yml`).

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
