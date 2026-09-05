# Notebooks de reference (snapshot)

Copies des quatre notebooks militaires du depot `centrage_c208` (commit `e7a80d1`,
04/09/2026) :

| Fichier | Avion | Immat | Unites |
|---|---|---|---|
| `planche_c208b_A.ipynb` | Cessna 208B Grand Caravan | C208B-A | lbs / in |
| `planche_c208b_B.ipynb` | Cessna 208B Grand Caravan | C208B-B | lbs / in |
| `planche_pc6_A.ipynb` | Pilatus PC-6/B2-H4 | PC6-A | kg / m |
| `planche_pc6_B.ipynb` | Pilatus PC-6/B2-H4 | PC6-B | kg / m |

Pourquoi ils sont la : `heuristique_remplissage/caravan_model.py` execute les cellules
0 a 5 du notebook BK (geometrie cabine, table carburant, positions N=20, enveloppe) et
`ordre_origine.py` relit la cellule 5 de BK et LA. Rien n'est recopie a la main, le code
reste fidele aux planches.

Regles :

- ne pas les editer ici, la source de verite reste `centrage_c208/notebooks/` ;
- pour rafraichir apres une modification des planches (pesee, geometrie) : recopier les
  quatre fichiers et noter le nouveau commit ci-dessus ;
- les cellules 6 et suivantes (orchestration, ecriture des PDF) ne sont jamais executees ici.
