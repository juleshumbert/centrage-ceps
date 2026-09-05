# Donnees masse et centrage par type d'avion

Un dossier par type. Chaque dossier contient :

| Fichier | Contenu |
|---|---|
| `envelope.json` | donnees lisibles par programme : datum, MAC, masses limites, enveloppe(s) de centrage en sommets `[masse, bras]`, stations et bras, carburant, dimensions cabine et portes, points ouverts ; `null` = non trouve, jamais une estimation silencieuse |
| `notes.md` | chaque valeur avec son unite et sa source (URL, fichier, page), marquage officiel / tiers / deduit, incertitudes de lecture des figures |
| `poh/` | manuels recuperes (POH, AFM, TCDS) au format PDF, **en local seulement** (gitignore) : chaque `notes.md` donne l'URL et le nom de fichier pour les retelecharger |
| `figures/` | pages rasterisees utiles (centrogramme, stations, trois vues) pour relire ou decalquer |
| `planches_club.json` | (C208B, PC-6 B2-H4 seulement) valeurs effectivement utilisees par les planches du club, extraites des notebooks par `extract_planches_club.py` |

## Conventions

- **Unites natives du manuel**, jamais converties dans les fichiers : lb et in pour Cessna,
  PAC et DHC-6 ; kg et m (ou mm) pour Pilatus. Le bloc `units` de chaque JSON fait foi.
- **Datum** : toujours cite en clair (`datum`), car les bras n'ont de sens que par rapport
  a lui. Le %MAC se calcule avec `mac.lemac` et `mac.length` du meme fichier.
- **Enveloppe** : liste de sommets `[masse, bras]` parcourue depuis la limite avant a masse
  minimale, dans le sens horaire ; le bord bas (masse minimale) est souvent le bas du
  graphique du manuel, pas une limite certifiee (dit dans `note`). `forward_limit` et
  `aft_limit` redonnent la meme information sous forme de polyligne.
- **Stations** : bras du manuel ; les positions de paras assis au sol viennent soit du
  manuel (PAC : figure 6-10), soit des planches du club (C208B : 20 places fixes N=20,
  PC-6 : deux rangees).
- **Cabine** : longueur, largeurs (plancher et maximale), hauteur, position des stations
  de debut et de fin de plancher, portes (cote, type, dimensions, seuil, stations de
  debut et de fin), bord d'attaque de l'aile et trains : c'est ce qu'il faut pour un
  schema a l'echelle en vue de dessus et en coupe.

## Etat par avion

Voir le tableau du README racine et la section « Points ouverts » de chaque `notes.md`.

Les `envelope.json` ont ete rediges avion par avion a partir de manuels de structure
differente : le squelette est commun (`units`, `datum`, `mac`, `envelopes[].vertices`,
`stations`, `fuel`, `cabin`) mais les cles de detail varient (`arm_in` pour le PAC, `arm`
pour le DHC-6, `arm_m` pour le PC-6 ; masses par variante sous `weights` pour le Cessna).
Lire le fichier avant d'ecrire un chargeur generique.

## Ecarts entre planches club et manuels (a trancher)

| Avion | Planches club | Manuel | Commentaire |
|---|---|---|---|
| C208B | MTOW 9062 lb, limite avant interpolee de (8000 lb, 193.37 in) a (9062 lb, 199.15 in) | STC APE II (SA00392SE, `c208b/stc_ape.json`) : 199.15 in a 8750 lb puis 200.23 in a 9062 lb, arriere 204.35 in | **les planches sont moins restrictives que le STC** : 1.65 in a 8750 lb, 1.08 in a 9062 lb ; l'IHM propose les deux variantes, STC par defaut |
| C208B | enveloppe 179.60 / 193.37 / 199.15 / 204.35 in | identique (POH 2008, FAA rev. 22) | l'EASA TCDS 2025 donne 185.00 in a 6500 lb pour la limite avant, divergence notee dans `c208b/notes.md` |
| C208B | bras carburant 200.0 a 203.1 in (table club) | 203.0 a 203.4 in (POH) | coherent, ecart maximal 3 in a faible quantite |
| PC-6 B2-H4 | enveloppe 3.209 / 3.608 / 3.722 m | identique (TCDS F 56-10) | |
| PC-6 B2-H4 | bras carburant 4.03 m (table club : 129.6 kg pour 522.3 kg.m) | +3.79 m (TCDS § 2.23) | ecart de 24 cm, soit environ 5 cm de CG au plein a 2800 kg : verifier la table club contre le rapport de pesee de PC6-A |
| PC-6 B2-H4 | pilote 3.05 m, capacite 640 L | 3.05 m, 644 L utilisables | coherent |

## Regenerer les valeurs club

```bash
python3 avions/extract_planches_club.py
```
