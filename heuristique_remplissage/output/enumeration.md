# Enumeration exhaustive des configurations (Rust, enumeration/)

Places : 20, donc 1,048,575 configurations non vides (sous-ensembles), C(20,N) par N (max C(20,10) = 184 756), et 20! = 2.433e+18 ordres de remplissage possibles. Masses uniformes (forfait ou poids moyen de la rotation) : une configuration = un sous-ensemble de places, un ordre = une chaine de sous-ensembles emboites.

| places | avion | domaine | critere | configs valides N=10 (sur 184 756) | N max atteignable | ordres valides (sur 2,43e18) | marge min du meilleur ordre (in de bras moyen) |
|---|---|---|---|---|---|---|---|
| legacy | C208B-A | forfait 90 kg, pilote 80 | enveloppe complete | 87,171 | 20 | 1.39e+17 (5.7237 %) | +5.88 |
| legacy | C208B-A | forfait 90 kg, pilote 80 | arriere seule | 179,433 | 20 | 1.19e+18 (48.7337 %) | +5.88 |
| legacy | C208B-B | forfait 90 kg, pilote 80 | enveloppe complete | 68,690 | 20 | 7.09e+16 (2.9123 %) | +6.63 |
| legacy | C208B-B | forfait 90 kg, pilote 80 | arriere seule | 182,530 | 20 | 1.69e+18 (69.5264 %) | +12.74 |
| legacy | deux avions | forfait 90 kg, pilote 80 | enveloppe complete | 65,593 | 20 | 3.23e+16 (1.3264 %) | +5.88 |
| legacy | deux avions | forfait 90 kg, pilote 80 | arriere seule | 179,433 | 20 | 1.19e+18 (48.7337 %) | +5.88 |
| legacy | C208B-A | forfait 80 kg, pilote 86 | enveloppe complete | 76,555 | 20 | 3.56e+17 (14.6411 %) | +3.47 |
| legacy | C208B-A | forfait 80 kg, pilote 86 | arriere seule | 183,355 | 20 | 2.06e+18 (84.8136 %) | +3.47 |
| legacy | C208B-B | forfait 80 kg, pilote 86 | enveloppe complete | 50,784 | 20 | 1.07e+17 (4.3812 %) | +4.35 |
| legacy | C208B-B | forfait 80 kg, pilote 86 | arriere seule | 184,382 | 20 | 2.25e+18 (92.2793 %) | +4.35 |
| legacy | deux avions | forfait 80 kg, pilote 86 | enveloppe complete | 49,757 | 20 | 7.49e+16 (3.0794 %) | +3.47 |
| legacy | deux avions | forfait 80 kg, pilote 86 | arriere seule | 183,355 | 20 | 2.06e+18 (84.8136 %) | +3.47 |
| legacy | C208B-A | moyen 70-110 kg, pilotes 80/86 | enveloppe complete | 56,487 | 20 | 1.53e+15 (0.0630 %) | +1.75 |
| legacy | C208B-B | moyen 70-110 kg, pilotes 80/86 | enveloppe complete | 24,668 | 20 | 2.84e+13 (0.0012 %) | +1.58 |
| legacy | deux avions | moyen 70-110 kg, pilotes 80/86 | enveloppe complete | 18,145 | 20 | 1.10e+11 (0.0000 %) | +0.76 |
| legacy | C208B-A | moyen 60-120 kg, pilotes 80/86 | enveloppe complete | 45,457 | 20 | 5.14e+10 (0.0000 %) | +0.27 |
| legacy | C208B-B | moyen 60-120 kg, pilotes 80/86 | enveloppe complete | 14,263 | 11 | 0.00e+00 (0.0000 %) | +0.31 |
| legacy | deux avions | moyen 60-120 kg, pilotes 80/86 | enveloppe complete | 7,115 | 10 | 0.00e+00 (0.0000 %) | +0.63 |
| legacy | C208B-A | moyen 70-110 kg, pilotes 65-110 | enveloppe complete | 32,112 | 20 | 5.72e+12 (0.0002 %) | +1.15 |
| legacy | C208B-B | moyen 70-110 kg, pilotes 65-110 | enveloppe complete | 7,459 | 20 | 3.19e+08 (0.0000 %) | +0.41 |
| legacy | deux avions | moyen 70-110 kg, pilotes 65-110 | enveloppe complete | 0 | 9 | 0.00e+00 (0.0000 %) | +1.74 |
| legacy | C208B-A | moyen 70-110 kg, pilotes 80/86, fuel 320-1900 | enveloppe complete | 78,158 | 20 | 1.33e+16 (0.5484 %) | +3.18 |
| legacy | C208B-B | moyen 70-110 kg, pilotes 80/86, fuel 320-1900 | enveloppe complete | 55,501 | 20 | 1.34e+15 (0.0549 %) | +1.88 |
| legacy | deux avions | moyen 70-110 kg, pilotes 80/86, fuel 320-1900 | enveloppe complete | 48,978 | 20 | 3.57e+13 (0.0015 %) | +1.50 |
| legacy | C208B-A | moyen 75-105 kg, pilotes 80/86, fuel 320-1900 | enveloppe complete | 82,304 | 20 | 3.85e+16 (1.5840 %) | +3.29 |
| legacy | C208B-B | moyen 75-105 kg, pilotes 80/86, fuel 320-1900 | enveloppe complete | 60,462 | 20 | 1.11e+16 (0.4546 %) | +3.30 |
| legacy | deux avions | moyen 75-105 kg, pilotes 80/86, fuel 320-1900 | enveloppe complete | 53,124 | 20 | 1.40e+15 (0.0574 %) | +2.60 |
| n20 | C208B-A | forfait 90 kg, pilote 80 | enveloppe complete | 92,379 | 20 | 1.44e+17 (5.9290 %) | +5.39 |
| n20 | C208B-A | forfait 90 kg, pilote 80 | arriere seule | 178,995 | 20 | 1.15e+18 (47.4067 %) | +5.39 |
| n20 | C208B-B | forfait 90 kg, pilote 80 | enveloppe complete | 58,113 | 20 | 7.49e+16 (3.0799 %) | +6.67 |
| n20 | C208B-B | forfait 90 kg, pilote 80 | arriere seule | 183,599 | 20 | 2.07e+18 (85.0278 %) | +15.22 |
| n20 | deux avions | forfait 90 kg, pilote 80 | enveloppe complete | 53,509 | 20 | 1.31e+16 (0.5396 %) | +4.38 |
| n20 | deux avions | forfait 90 kg, pilote 80 | arriere seule | 178,995 | 20 | 1.15e+18 (47.4067 %) | +5.39 |
| n20 | C208B-A | forfait 80 kg, pilote 86 | enveloppe complete | 77,645 | 20 | 3.40e+17 (13.9945 %) | +3.01 |
| n20 | C208B-A | forfait 80 kg, pilote 86 | arriere seule | 183,120 | 20 | 1.96e+18 (80.5212 %) | +3.01 |
| n20 | C208B-B | forfait 80 kg, pilote 86 | enveloppe complete | 39,219 | 20 | 8.85e+16 (3.6359 %) | +6.88 |
| n20 | C208B-B | forfait 80 kg, pilote 86 | arriere seule | 184,621 | 20 | 2.38e+18 (97.8948 %) | +6.88 |
| n20 | deux avions | forfait 80 kg, pilote 86 | enveloppe complete | 37,718 | 20 | 3.49e+16 (1.4343 %) | +3.01 |
| n20 | deux avions | forfait 80 kg, pilote 86 | arriere seule | 183,120 | 20 | 1.96e+18 (80.5212 %) | +3.01 |
| n20 | C208B-A | moyen 70-110 kg, pilotes 80/86 | enveloppe complete | 56,054 | 20 | 1.53e+15 (0.0631 %) | +1.29 |
| n20 | C208B-B | moyen 70-110 kg, pilotes 80/86 | enveloppe complete | 18,116 | 20 | 3.41e+13 (0.0014 %) | +1.67 |
| n20 | deux avions | moyen 70-110 kg, pilotes 80/86 | enveloppe complete | 4,249 | 10 | 0.00e+00 (0.0000 %) | +0.55 |
| n20 | C208B-A | moyen 60-120 kg, pilotes 80/86 | enveloppe complete | 45,281 | 20 | 1.93e+11 (0.0000 %) | +0.39 |
| n20 | C208B-B | moyen 60-120 kg, pilotes 80/86 | enveloppe complete | 11,460 | 11 | 0.00e+00 (0.0000 %) | +0.24 |
| n20 | deux avions | moyen 60-120 kg, pilotes 80/86 | enveloppe complete | 0 | 9 | 0.00e+00 (0.0000 %) | +1.14 |
| n20 | C208B-A | moyen 70-110 kg, pilotes 65-110 | enveloppe complete | 37,372 | 20 | 7.48e+12 (0.0003 %) | +0.68 |
| n20 | C208B-B | moyen 70-110 kg, pilotes 65-110 | enveloppe complete | 7,103 | 20 | 6.01e+08 (0.0000 %) | +0.23 |
| n20 | deux avions | moyen 70-110 kg, pilotes 65-110 | enveloppe complete | 0 | 9 | 0.00e+00 (0.0000 %) | +0.39 |
| n20 | C208B-A | moyen 70-110 kg, pilotes 80/86, fuel 320-1900 | enveloppe complete | 80,526 | 20 | 1.53e+16 (0.6304 %) | +2.83 |
| n20 | C208B-B | moyen 70-110 kg, pilotes 80/86, fuel 320-1900 | enveloppe complete | 45,290 | 20 | 1.27e+15 (0.0521 %) | +2.07 |
| n20 | deux avions | moyen 70-110 kg, pilotes 80/86, fuel 320-1900 | enveloppe complete | 31,423 | 13 | 0.00e+00 (0.0000 %) | +0.59 |
| n20 | C208B-A | moyen 75-105 kg, pilotes 80/86, fuel 320-1900 | enveloppe complete | 86,098 | 20 | 4.24e+16 (1.7424 %) | +2.83 |
| n20 | C208B-B | moyen 75-105 kg, pilotes 80/86, fuel 320-1900 | enveloppe complete | 48,169 | 20 | 1.10e+16 (0.4505 %) | +3.28 |
| n20 | deux avions | moyen 75-105 kg, pilotes 80/86, fuel 320-1900 | enveloppe complete | 36,995 | 20 | 6.76e+12 (0.0003 %) | +1.03 |

## Meilleurs ordres (marge minimale maximale) verifies au banc Python

| places | avion | domaine | ordre (bras in) | uniformes : echecs / marge min CG | avec masses individuelles : echecs / marge min |
|---|---|---|---|---|---|
| legacy | C208B-A | forfait 90 kg, pilote 80 | 307 294 282 136 282 161 258 258 162 258 149 234 185 234 185 222 186 209 210 307 | 0 / 297, +1.92 in | 0 / 297, +1.92 in |
| legacy | C208B-B | forfait 90 kg, pilote 80 | 307 307 294 136 282 258 149 258 185 258 161 234 162 234 185 210 186 209 222 282 | 0 / 286, +1.83 in | 0 / 286, +1.83 in |
| legacy | deux avions | forfait 90 kg, pilote 80 | 307 294 282 136 282 258 149 258 234 161 258 162 234 186 185 222 185 210 209 307 | 0 / 583, +1.50 in | 0 / 583, +1.50 in |
| legacy | C208B-A | forfait 80 kg, pilote 86 | 307 307 294 136 282 149 258 258 161 258 234 162 234 185 209 210 185 222 186 282 | 0 / 329, +1.39 in | 0 / 329, +1.39 in |
| legacy | C208B-B | forfait 80 kg, pilote 86 | 307 307 294 282 136 282 149 258 258 162 234 161 234 185 222 185 209 210 186 258 | 0 / 318, +1.72 in | 0 / 318, +1.72 in |
| legacy | deux avions | forfait 80 kg, pilote 86 | 307 307 282 294 136 282 149 258 186 258 161 234 162 234 185 222 185 210 209 258 | 0 / 647, +1.39 in | 0 / 647, +1.39 in |
| legacy | C208B-A | moyen 70-110 kg, pilotes 80/86 | 307 307 136 294 149 282 162 282 234 161 258 186 210 209 185 234 185 258 222 258 | 0 / 2983, +0.54 in | 0 / 2983, +0.54 in |
| legacy | C208B-B | moyen 70-110 kg, pilotes 80/86 | 307 307 294 149 282 161 258 162 258 234 186 209 185 222 185 210 258 234 136 282 | 0 / 2883, +0.31 in | 0 / 2883, +0.31 in |
| legacy | deux avions | moyen 70-110 kg, pilotes 80/86 | 307 294 282 136 282 149 258 258 185 234 209 210 185 222 186 234 162 258 161 307 | 0 / 5866, +0.24 in | 0 / 5866, +0.24 in |
| legacy | C208B-A | moyen 60-120 kg, pilotes 80/86 | 307 307 136 294 149 282 185 258 185 258 186 222 210 209 234 162 282 161 258 234 | 0 / 4212, +0.06 in | 0 / 4212, +0.06 in |
| legacy | C208B-A | moyen 70-110 kg, pilotes 65-110 | 307 307 136 294 258 149 282 161 282 162 234 185 234 186 210 222 185 258 209 258 | 0 / 2983, +0.54 in | 8 / 8013, -0.84 in |
| legacy | C208B-B | moyen 70-110 kg, pilotes 65-110 | 307 307 282 149 282 161 258 258 162 234 210 186 222 185 209 185 258 234 136 294 | 0 / 2883, +0.28 in | 28 / 7723, -1.08 in |
| legacy | C208B-A | moyen 70-110 kg, pilotes 80/86, fuel 320-1900 | 307 307 136 294 149 282 161 258 258 162 234 186 234 210 209 222 185 258 185 282 | 0 / 2258, +0.76 in | 0 / 2258, +0.76 in |
| legacy | C208B-B | moyen 70-110 kg, pilotes 80/86, fuel 320-1900 | 307 294 282 136 282 149 258 258 185 234 185 222 209 210 186 258 162 307 234 161 | 0 / 2185, +0.55 in | 0 / 2185, +0.55 in |
| legacy | deux avions | moyen 70-110 kg, pilotes 80/86, fuel 320-1900 | 307 307 136 294 149 282 185 282 162 258 185 234 210 209 222 186 258 161 258 234 | 0 / 4443, +0.37 in | 0 / 4443, +0.37 in |
| legacy | C208B-A | moyen 75-105 kg, pilotes 80/86, fuel 320-1900 | 307 307 136 282 149 282 161 258 258 162 234 234 209 185 222 210 186 258 185 294 | 0 / 1341, +1.25 in | 0 / 1341, +1.25 in |
| legacy | C208B-B | moyen 75-105 kg, pilotes 80/86, fuel 320-1900 | 307 294 282 136 282 149 258 258 161 258 185 234 209 186 210 234 162 222 307 185 | 0 / 1295, +0.85 in | 0 / 1295, +0.85 in |
| legacy | deux avions | moyen 75-105 kg, pilotes 80/86, fuel 320-1900 | 307 294 282 136 282 161 258 162 258 234 185 234 209 186 210 222 185 258 149 307 | 0 / 2636, +0.64 in | 0 / 2636, +0.64 in |
| n20 | C208B-A | forfait 90 kg, pilote 80 | 307 294 282 136 282 155 263 256 155 256 168 231 181 231 181 206 206 200 231 307 | 0 / 297, +1.71 in | 0 / 297, +1.71 in |
| n20 | C208B-B | forfait 90 kg, pilote 80 | 307 294 282 282 136 263 231 256 155 256 168 231 181 231 181 206 206 200 307 155 | 0 / 286, +1.90 in | 0 / 286, +1.90 in |
| n20 | deux avions | forfait 90 kg, pilote 80 | 307 282 282 294 136 263 155 256 256 155 231 181 231 168 231 206 200 206 181 307 | 0 / 583, +1.31 in | 0 / 583, +1.31 in |
| n20 | C208B-A | forfait 80 kg, pilote 86 | 307 307 294 136 282 155 263 256 155 256 231 168 231 181 231 181 206 206 200 282 | 0 / 329, +1.20 in | 0 / 329, +1.20 in |
| n20 | C208B-B | forfait 80 kg, pilote 86 | 307 307 294 282 136 282 263 155 256 231 155 256 168 231 181 206 181 231 200 206 | 0 / 318, +1.90 in | 0 / 318, +1.90 in |
| n20 | deux avions | forfait 80 kg, pilote 86 | 307 307 294 282 136 282 168 263 181 256 155 256 155 231 206 200 181 231 206 231 | 0 / 647, +1.20 in | 0 / 647, +1.20 in |
| n20 | C208B-A | moyen 70-110 kg, pilotes 80/86 | 307 307 136 294 155 282 168 282 155 256 231 200 206 206 181 231 181 263 231 256 | 0 / 2983, +0.73 in | 0 / 2983, +0.73 in |
| n20 | C208B-B | moyen 70-110 kg, pilotes 80/86 | 307 307 282 136 282 263 168 256 181 231 231 200 206 206 181 256 155 294 231 155 | 0 / 2883, +0.43 in | 0 / 2883, +0.43 in |
| n20 | C208B-A | moyen 60-120 kg, pilotes 80/86 | 307 294 155 282 155 282 168 263 181 256 200 231 206 206 231 181 256 231 136 307 | 0 / 4212, +0.08 in | 0 / 4212, +0.08 in |
| n20 | C208B-A | moyen 70-110 kg, pilotes 65-110 | 307 307 136 294 263 155 282 168 231 200 231 206 206 181 231 181 256 155 282 256 | 0 / 2983, +0.56 in | 10 / 8013, -1.13 in |
| n20 | C208B-B | moyen 70-110 kg, pilotes 65-110 | 307 282 282 294 136 256 168 256 231 231 206 181 231 200 206 181 263 155 307 155 | 0 / 2883, +0.31 in | 24 / 7723, -0.77 in |
| n20 | C208B-A | moyen 70-110 kg, pilotes 80/86, fuel 320-1900 | 307 307 136 282 155 282 155 263 256 168 231 200 231 206 206 231 181 256 181 294 | 0 / 2258, +0.78 in | 0 / 2258, +0.78 in |
| n20 | C208B-B | moyen 70-110 kg, pilotes 80/86, fuel 320-1900 | 307 294 282 155 282 155 256 256 181 263 181 231 200 206 206 231 168 307 231 136 | 0 / 2185, +0.50 in | 0 / 2185, +0.50 in |
| n20 | C208B-A | moyen 75-105 kg, pilotes 80/86, fuel 320-1900 | 307 307 136 282 155 282 155 263 256 168 256 181 231 200 206 206 231 181 231 294 | 0 / 1341, +1.11 in | 0 / 1341, +1.11 in |
| n20 | C208B-B | moyen 75-105 kg, pilotes 80/86, fuel 320-1900 | 307 307 294 136 282 155 282 181 256 231 181 231 200 206 206 231 168 263 155 256 | 0 / 1295, +1.02 in | 0 / 1295, +1.02 in |
| n20 | deux avions | moyen 75-105 kg, pilotes 80/86, fuel 320-1900 | 307 307 136 282 282 155 294 155 263 168 256 206 206 181 231 200 231 181 256 231 | 0 / 2636, +0.41 in | 0 / 2636, +0.41 in |

## Ordre d origine (filling_order_bon) sur les memes domaines

| avion | domaine | uniformes : echecs / marge min CG |
|---|---|---|
| C208B-A | forfait 90 kg, pilote 80 | 0 / 297, +0.59 in |
| C208B-A | forfait 80 kg, pilote 86 | 1 / 329, -0.18 in |
| C208B-A | moyen 70-110 kg, pilotes 80/86 | 92 / 2983, -1.34 in |
| C208B-A | moyen 60-120 kg, pilotes 80/86 | 170 / 4212, -2.43 in |
| C208B-A | moyen 70-110 kg, pilotes 65-110 | 92 / 2983, -1.34 in |
| C208B-A | moyen 70-110 kg, pilotes 80/86, fuel 320-1900 | 76 / 2258, -1.27 in |
| C208B-A | moyen 75-105 kg, pilotes 80/86, fuel 320-1900 | 17 / 1341, -0.18 in |
| C208B-B | forfait 90 kg, pilote 80 | 8 / 286, -0.70 in |
| C208B-B | forfait 80 kg, pilote 86 | 14 / 318, -0.72 in |
| C208B-B | moyen 70-110 kg, pilotes 80/86 | 137 / 2883, -1.35 in |
| C208B-B | moyen 60-120 kg, pilotes 80/86 | 257 / 4079, -2.18 in |
| C208B-B | moyen 70-110 kg, pilotes 65-110 | 137 / 2883, -1.35 in |
| C208B-B | moyen 70-110 kg, pilotes 80/86, fuel 320-1900 | 49 / 2185, -1.35 in |
| C208B-B | moyen 75-105 kg, pilotes 80/86, fuel 320-1900 | 8 / 1295, -0.62 in |
| deux avions | forfait 90 kg, pilote 80 | 8 / 583, -0.70 in |
| deux avions | forfait 80 kg, pilote 86 | 15 / 647, -0.72 in |
| deux avions | moyen 70-110 kg, pilotes 80/86 | 229 / 5866, -1.35 in |
| deux avions | moyen 60-120 kg, pilotes 80/86 | 427 / 8291, -2.43 in |
| deux avions | moyen 70-110 kg, pilotes 65-110 | 229 / 5866, -1.35 in |
| deux avions | moyen 70-110 kg, pilotes 80/86, fuel 320-1900 | 125 / 4443, -1.35 in |
| deux avions | moyen 75-105 kg, pilotes 80/86, fuel 320-1900 | 25 / 2636, -0.62 in |
