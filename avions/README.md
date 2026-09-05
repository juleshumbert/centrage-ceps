# Donnees masse et centrage par type d'avion

Un dossier par type. Chaque dossier contient :

| Fichier | Contenu |
|---|---|
| `envelope.json` | donnees lisibles par programme : datum, MAC, masses limites, enveloppe(s) de centrage en sommets `[masse, bras]`, stations et bras, carburant, dimensions cabine et portes, points ouverts ; `null` = non trouve, jamais une estimation silencieuse |
| `notes.md` | chaque valeur avec son unite et sa source (URL, fichier, page), marquage officiel / tiers / deduit, incertitudes de lecture des figures |
| `poh/` | manuels recuperes (POH, AFM, TCDS) au format PDF, verifies avec `pdfinfo` |
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

## Regenerer les valeurs club

```bash
python3 avions/extract_planches_club.py
```
