# placement · placement des paras à places fixes

Binaire autonome qui, pour un stick donné (masses, groupes, ordre de sortie,
tandems), calcule où s'assoit chaque para pour un centrage valide, **le plus
centré avant possible au décollage** tout en garantissant que, **quand le premier
groupe est sorti, l'avion n'est pas trop centré avant**. Parmi ces placements il
retient le plus réaliste : groupes compacts, premiers sortants près de la porte,
passager tandem juste devant son porteur sur un bord. Le solveur (HiGHS,
programmation linéaire en nombres entiers) est embarqué : aucune installation.

## Contenu

| chemin | rôle |
|---|---|
| `src/placement.cpp` | le programme (C++17), HiGHS et nlohmann/json embarqués |
| `CMakeLists.txt`, `build.sh`, `build_macos.sh` | construction (voir « Construire ») |
| `MODELE.md` | la modélisation en programme linéaire |
| `exemples/exemple_stick.json` | fichier d'entrée complet et commenté |
| `exemples/exemple_stick_resultat.json`, `exemple_stick.pdf` | ce que produit `placement exemple_stick.json --sortie ... --pdf ...` |
| `exemples/exemple_20_paras.json` | cabine pleine : 20 paras pour 20 places, à 54 lbs de la MTOW, `tolerance_marge` à 2 |
| `exemples/exemple_groupes.json`, `exemple_tandems.json` | manifestes de l'étude (groupes, tandems) |
| `tests/smoke.sh` | test de fumée : chaque exemple doit rendre `ok: true` |

Les binaires (`placement-linux-x86_64`, `placement-macos-arm64`, `placement-macos-x86_64`,
`placement-windows-x86_64.exe`) sont publiés dans les **releases GitHub** du dépôt, construits
par le workflow `.github/workflows/solveur.yml` à chaque tag `v*`. Le même binaire Linux
statique est embarqué dans la Cloud Function `functions/` qui sert l'IHM web.

## Utilisation

```bash
./build/placement --help
./build/placement exemples/exemple_stick.json --sortie resultat.json --pdf planche.pdf
./build/placement exemples/exemple_stick.json --rapide           # phase 2 par recuit seul, 1 à 2 s
./build/placement exemples/exemple_stick.json --temps 3          # solveur limité à 3 s par phase
./build/placement exemples/exemple_20_paras.json --pdf planche20.pdf  # cabine pleine, 20 paras
./build/placement exemples/exemple_stick.json --etapes toutes    # marge avant garantie après chaque sortie
cat stick.json | ./build/placement -                             # entrée standard, résultat JSON sur la sortie standard
```

Code de retour 0 si un placement est rendu, 1 si aucun placement ne respecte les
contraintes (le JSON dit pourquoi et donne le meilleur compromis), 2 sur erreur
d'entrée. Un résumé d'une ligne est écrit sur la sortie d'erreur (`--silencieux`
pour le taire).

## Fichier d'entrée

Masses et bras dans des unités cohérentes, au choix (lbs et in, ou kg et m) : le
programme ne convertit rien, il calcule des moments masse × bras.

```json
{
 "avion":     {"immat": "C208B-A", "masse_vide": 4890, "bras_vide": 188.99},
 "enveloppe": {"avant": [[5500, 179.6], [8000, 193.37], [9062, 199.15]],
               "arriere": [[0, 204.35], [9062, 204.35]], "mtow": 9062},
 "carburant": {"masse": 900, "bras": 203.3},
 "pilote":    {"masse": 176.4, "bras": 135.5},
 "porte":     {"x": 307, "y": -32},
 "places":    [{"id": "COPI", "x": 135.5, "y": 16, "copilote": true},
               {"id": "D1", "x": 155.4, "y": 16}, "...",
               {"id": "C1", "x": 168, "y": 0, "centre": true}, "..."],
 "paras":     [{"nom": "Alice", "masse": 205, "groupe": "VR4", "sortie": 1},
               {"nom": "Lea",  "masse": 143, "tandem": "TDM1", "role": "passager", "sortie": 6},
               {"nom": "Marc", "masse": 216, "tandem": "TDM1", "role": "porteur",  "sortie": 6},
               {"nom": "Julie", "masse": 172, "devant_de": "Karim", "sortie": 5},
               {"nom": "Hugo", "masse": 165, "sortie": 3, "interdit": ["COPI"]}],
 "options":   {"etapes": "premier_groupe", "marge_avant_min": 0.5, "tolerance_marge": 0.25,
               "groupes_ordonnes": false, "temps_max_s": 10}
}
```

- **avion** : masse à vide et bras à vide (ou `moment_vide` = masse × bras).
- **enveloppe** : limite avant et limite arrière du CG en fonction de la masse,
  chacune une ligne brisée `[masse, cg]` interpolée linéairement ; `mtow`.
- **carburant**, **pilote** : masse et bras (le placement du pilote est son bras).
- **porte** : position, sert à classer les places par proximité de la porte.
- **places** : `id`, `x` (bras), `y` (latéral : positif à droite, négatif à
  gauche, 0 rangée centrale). `copilote` et `centre` excluent la place des
  tandems et des paires. La place « devant » (pour le passager) est déduite :
  même côté, bras immédiatement inférieur ; `"devant": "id"` pour la fixer,
  `"interdit_tandem": true` pour l'exclure.
- **paras** : `nom`, `masse`, `groupe` (les membres d'un groupe sont gardés
  proches), `sortie` (rang ; les ex aequo sortent ensemble, le plus petit rang
  sort en premier ; sans rang : sort en dernier), `tandem` + `role`
  (`porteur` / `passager` : le passager est juste devant le porteur, sur un
  bord), `devant_de` (ce para est juste devant le para nommé, même côté),
  `interdit` (liste d'ids de places refusées).
- **options** : `etapes` (`premier_groupe` par défaut, `toutes`, `decollage`),
  `marge_avant_min` (0,5 dans l'unité des bras), `tolerance_marge` (0,25),
  `groupes_ordonnes` (un groupe qui sort avant est entièrement en arrière),
  `poids_groupe` (2), `poids_sortie` (1), `poids_lateral` (0,5), `pas` (25,
  distance entre deux places pour normaliser), `temps_max_s` (10 s par phase),
  `gap` (0,05, écart accepté à l'optimum en phase 2), `recuit_s` (1 s de recuit
  simulé pour amorcer la phase 2, 0 pour s'en passer), `rapide` (phase 2 par
  recuit seul). La ligne de commande prime sur ce bloc.

## Ce que calcule le programme

1. **Phase 1, exacte** : la marge arrière maximale au décollage (donc le CG le
   plus avant possible) sous les contraintes : une place par para, marge avant
   ≥ `marge_avant_min` au décollage **et après la sortie du premier groupe**
   (tous les paras de plus petit rang de sortie ; les autres restent à leur
   place), enveloppe respectée côté arrière à cette étape, tandems et paires,
   places interdites. Si c'est impossible, il cherche la marge avant maximale
   atteignable et la rend avec son placement.
2. **Phase 2** : parmi les placements dont la marge arrière est à
   `tolerance_marge` près du maximum, le plus réaliste. Un recuit simulé
   (1 s) fournit d'abord une bonne solution, que le solveur améliore et
   prouve à 5 % près ; il s'arrête à `temps_max_s` avec la meilleure solution
   trouvée. `--rapide` garde le recuit seul : réponse en 1 à 2 s, coût de
   réalisme à quelques pour cent de l'optimum sur les cas testés.

Les paras qui s'avancent vers la porte pendant le largage ne sont pas modélisés :
seule la première sortie est prise en compte, comme demandé. `--etapes toutes`
impose la marge avant après chaque sortie, avec les paras restants à leur place.

**Réglage important** : maximiser la marge arrière pousse la charge vers l'avant,
donc les premiers sortants loin de la porte. `tolerance_marge` règle ce
compromis : 0,25 privilégie le centrage, 2 à 4 redonne de la place au réalisme.

L'exemple `exemple_20_paras.json` le montre sur une cabine pleine (20 paras, masse
au décollage à 54 lbs de la MTOW, bande de CG admissible de 5,5 in) : toutes les
places étant occupées, seule la permutation des masses joue, et la marge arrière
maximale n'est que de 2,6 in. À 0,25 près il ne reste aucune liberté et les 4 VR
qui sortent en premier sont dispersés loin de la porte ; le fichier fixe donc
`tolerance_marge` à 2, et la ligne de commande permet de comparer
(`--tolerance 0.25`) :

| tolérance | marge arrière au décollage | marge avant après le 1er groupe | écart de sortie | boîtes | phase 2 |
|---|---|---|---|---|---|
| 0,25 in | 2,34 | 7,56 | 120 | 17,3 | optimum, 1 s |
| 1 in | 1,60 | 2,92 | 61 | 15,0 | optimum, 1 s |
| 2 in | 0,65 | 1,58 | 35 | 7,8 | temps limite, 10 s |
| 4 in | 0,26 | 0,80 | 26 | 8,8 | temps limite, 10 s |

À 2 in les VR sont au fond près de la porte (C5, G5, G6, G7), les deux PAC et le
tandem à l'avant sur les bords, et la marge avant après la sortie des VR reste de
1,6 in, au-dessus des 0,5 in demandés.

## Sortie

JSON : `ok`, `marge_arriere_max` (et `phase1` : « optimum » = prouvé),
`marge_arriere` et `marge_avant_min_obtenue` du placement rendu, `premier_groupe`,
`placement` (nom, id de place, bras, latéral, rang de proximité de la porte),
`etapes` (masse, CG, marge avant, marge arrière au décollage puis après le premier
groupe), `boites`, `ecart_sortie`, `phase2`, temps.

PDF (`--pdf`) : plan de la cabine avec les paras (numéro = rang de sortie,
couleur = groupe, trait = paire porteur / passager), le CG au décollage et après
le premier groupe avec les limites avant et arrière tracés sur l'avion, un
centrogramme masse / CG avec l'enveloppe, et les tableaux.

## Temps de calcul

Phase 1 en moins d'une seconde jusqu'à 20 paras. Phase 2 sur huit cas de
validation (deux exemples à 16 paras, six fiches réelles à 20 paras) :

| réglage | temps total des 8 cas | coût de réalisme cumulé |
|---|---|---|
| sans recuit, écart 1 % (ancien) | 55 s | 869 |
| défaut : recuit 1 s, écart 5 % | 34 s (1 s par stick à 20 paras, optimum prouvé) | 867 |
| défaut avec `--temps 3` | 19 s | 868 |
| `--rapide` | 9 s (1 s par stick) | 873 |

Sur `exemple_20_paras.json` (cabine pleine, `tolerance_marge` à 2), la phase 2
s'arrête à `temps_max_s` (11 s au total) ; avec la tolérance par défaut elle est à
l'optimum en 1 s.

Validé contre un modèle Python indépendant : marges recalculées à chaque étape,
tandems, ordre des groupes.

## Construire

Linux ou macOS avec un compilateur C++17, `cmake` et de préférence `ninja` :

```bash
./build.sh                    # clone HiGHS v1.9.0 et nlohmann/json, compile ./build/placement
PLACEMENT_STATIC=1 ./build.sh # Linux : binaire entierement statique (releases, Cloud Functions)
./tests/smoke.sh              # verifie les exemples
```

Sur macOS : `brew install cmake ninja` puis `./build.sh` (compilation native,
recommandée plutôt que les binaires croisés fournis). `build_macos.sh` produit
les binaires macOS depuis Linux avec `zig cc`, sans Mac (les releases GitHub, elles,
sont compilées nativement sur des runners macOS et Windows).

Licences des composants embarqués : HiGHS (MIT), nlohmann/json (MIT).
