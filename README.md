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
| `avions/` | un dossier par type : `envelope.json` (enveloppe, stations, carburant, cabine), `notes.md` (valeurs sourcees), `poh/` (manuels PDF recuperes) |
| `heuristique_remplissage/` | etude Caravan : scripts Python, `enumeration/` (Rust), `placement_rs/` (Rust), `placement_cpp/` (C++ + HiGHS), `output/` (figures, fiches PDF, JSON), voir son README |
| `reference/notebooks/` | snapshot des notebooks de planches de `centrage_c208`, lus par `caravan_model.py` (geometrie cabine, table carburant, enveloppe), ne pas editer ici |

## Demarrage rapide

```bash
cd heuristique_remplissage
python3 caravan_model.py                                  # les 20 places et l'ordre par pivot
python3 placement_milp.py manifestes/exemple_groupes.json # placement optimal d'un manifeste
python3 verif_heuristique.py 235                          # heuristique a pivot contre l'oracle
```

Dependances Python : `numpy`, `scipy` (>= 1.11 pour `milp`), `matplotlib`. Les binaires
Rust et C++ se reconstruisent comme decrit dans `heuristique_remplissage/README.md` et
`heuristique_remplissage/placement_cpp/README_livrable.md` ; ils ne sont pas versionnes.

## Conventions

- Bras en inches et masses en lbs pour les Cessna (datum et MAC du POH), metres et kg pour
  les Pilatus : chaque `envelope.json` porte ses unites et son datum, ne jamais melanger.
- Paras equipes : 90 kg (profil militaire) ou 80 kg (profil civil), pilote 80 ou 86 kg,
  memes forfaits que les planches de `centrage_c208`.
- Toute valeur constructeur est accompagnee de sa source (document, page).
