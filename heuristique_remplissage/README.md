# Heuristique de remplissage a places fixes · Caravan

Sous-projet d'etude : peut-on remplir le Caravan avec une regle simple, sans
calcul, en gardant le centrage dans l'enveloppe quels que soient le nombre de
paras, leurs masses individuelles et le carburant ?

Les places sont **fixes** : les 20 places de la disposition N=20 des planches
(copilote a 135,5 in, 7 places a droite et 7 a gauche de 155 a 307 in, 5 places
au centre de 168 a 294 in). Une heuristique est un **ordre** de ces 20 places
plus une regle d'affectation des paras (les plus lourds d'abord ou non).

## Verdict sur la proposition « places les plus proches de 202 in, plus lourds d'abord »

**Elle ne fonctionne pas.** Sur 18 867 scenarios sous MTOW (BK et LA, 1 a 20
paras, carburant 200 a 2224 lbs, masses individuelles de 60 a 120 kg, pilote 65
a 110 kg), elle sort de l'enveloppe dans **52 %** des cas, toujours par
l'**avant**. Chacun de ces scenarios admet pourtant une affectation valide.

La raison est geometrique : 202 in est la cible du CG de l'avion complet, pas
celle des paras. L'avion vide plus pilote est a 187 in (14 %MAC) et le carburant
a 200 a 203 in, tous deux **en avant** de la bande admissible a masse elevee
(199 a 204 in a la MTOW). Les paras doivent donc compenser en se plaçant nettement
**en arriere** : entre 215 et 250 in de bras moyen selon la charge, jamais
autour de 202. Voir `output/fig_bandes.png` : la courbe « pivot 202 » reste 20 a 40 in
sous la bande admissible pour tous les N.

L'ordre lourds/legers d'abord change le resultat de moins d'un point : c'est le
pivot qui compte, pas le tri des masses.

## Ce qui marche le mieux, et ce qui ne peut pas marcher

| Heuristique | Echecs (sur scenarios faisables) |
|---|---|
| pivot 202 in, lourds d'abord (proposition) | 52,5 % |
| pivot 220 in | 12,5 % |
| **pivot 235 in** (meilleur pivot unique) | **5,4 %** |
| meilleur ordre fixe quelconque (recuit simule) | 0,67 % |
| deux pivots selon le carburant (229 in si < 1600 lbs, 244 in sinon) | 1,2 % |
| deux ordres fixes selon le carburant (recuit, seuil 1200 lbs) | 0,10 % |

Le pivot 235 in (frontiere zones 2/3 moins 12 in) remplit d'abord les trois places
a 231 in, puis 256, 263, 206, 200, 282, 181, 294, 168, 307, 155, et le copilote en
dernier. Ses echecs restants sont concentres sur deux coins :

- 215 cas trop **avant**, tous sur C208B-B avec 1900 lbs ou plus de carburant,
  N = 1 a 10 (l'avion vide LA est plus avant que BK : 186,5 in contre 189,0) ;
- 813 cas trop **arriere**, N = 11 a 20 avec 1000 lbs ou moins de carburant,
  paras de 80 a 90 kg pour la plupart, BK surtout : c'est le chargement
  complet standard (par exemple 17 paras a 90 kg et 500 lbs), et la pour N = 16
  a 18 le pivot 235 echoue plus d'une fois sur deux. A forte charge les paras
  doivent se rapprocher de 225 in, comme la disposition N=20 des planches
  (bras moyen 226 in).

**Aucun ordre fixe ne peut couvrir tous les scenarios.** Pour N = 10 a 17, la
bande de bras moyen admissible est vide quand on croise tous les scenarios : les
paras legers (60 a 70 kg) avec le plein sur LA exigent un bras moyen d'au moins
238 in, les paras lourds (110 a 120 kg) avec 200 lbs sur BK exigent au plus 230 in
(`output/resume.md`, section « bande admissible »). Le recuit simule confirme :
0,67 % d'echecs au mieux, sur ces memes coins.

Le carburant est la variable qui separe les deux coins. Avec deux ordres selon
le carburant (seuil 1200 lbs) on tombe a 19 echecs sur 18 867, tous avec des
paras uniformement a 60 ou 100 kg, c'est-a-dire des tirages extremes.

## Heuristique retenue : ordre equilibre autour d'un pivot, pivot lu dans une table

Fiche une page : `output/Fiche_heuristique_remplissage_Caravan.pdf` (et `.png`).
Ordres et table en JSON : `output/heuristique_retenue.json`.

**Regle.** Masse totale des paras equipes (manifeste) et carburant au decollage
donnent un plan (A a E). Chaque plan numerote les 20 places ; on remplit dans
l'ordre des numeros, **le para le plus lourd sur la place 1**, le suivant sur la
2, sans sauter de numero.

| masse totale des paras | carburant < 1600 lbs | carburant >= 1600 lbs |
|---|---|---|
| moins de 800 kg | plan D (pivot 240 in) | plan E (pivot 252,5 in) |
| 800 a 1200 kg | plan C (pivot 232,5 in) | plan D (pivot 240 in) |
| 1200 a 1400 kg | plan B (pivot 227,5 in) | au-dessus de la MTOW |
| 1400 kg et plus | plan A (pivot 225 in) | au-dessus de la MTOW |

Au forfait 90 kg les classes de masse correspondent a 1-8 / 9-13 / 14-15 / 16-20
paras ; au forfait 80 kg a 1-9 / 10-14 / 15-17 / 18-20.

**Resultat.** 0 sortie d'enveloppe sur les 18 867 scenarios (BK et LA, 1 a 20
paras, masses individuelles 60 a 120 kg, carburant 200 a 2224 lbs, pilote 65 a
110 kg). Marge CG : minimum 0,01 in, 1er centile 0,87 in, mediane 4,2 in
(1 in = 1,5 %MAC). Les marges les plus minces (moins de 0,5 in, 0,23 % des
scenarios) sont sur C208B-B avec 1600 lbs ou plus de carburant, ou sur des
chargements uniformement a 60 ou 120 kg (`output/fig_marge_retenue.png`).
Si les paras s'asseyent dans le desordre (masses non triees sur le plan), on
reste dans l'enveloppe dans 99,8 % des cas ; le tri « lourd sur la place 1 »
compte surtout a forte charge.

**Pourquoi ca marche.** Un plan est l'ordre « equilibre » autour d'un pivot : a
chaque numero on ajoute la place qui garde la moyenne des bras utilises la
plus proche du pivot (la moyenne ne zigzague plus, contrairement au tri par
distance de la proposition initiale). Avec le plus lourd au pivot, le bras
moyen pondere reste pres du pivot quelle que soit la repartition des masses.
Il ne reste qu'a choisir le pivot : la bande admissible de bras moyen depend
surtout de la masse totale des paras (limite arriere) et, a faible charge, du
carburant (limite avant), d'ou la table. Sur cette famille d'ordres, chaque
scenario est couvert par au moins un pivot ; la table a 6 cases en trouve un a
chaque fois.

**Variante plus simple, masse seule** (4 plans, sans regarder le carburant) :
pivots 245 / 232,5 / 227,5 / 225 in pour moins de 900 / 900 a 1200 / 1200 a
1400 / 1400 kg et plus. Elle sort de l'enveloppe dans 5 scenarios sur 18 867,
tous sur C208B-B avec 1700 a 1900 lbs, de 0,4 in au plus.

Les autres variables de bascule ont ete comparees (`output/pivot_regimes.log`) :
le carburant seul (3 classes) laisse 74 echecs, le nombre de paras seul ne
suffit pas (voir la bande vide pour N = 10 a 17). Le critere « pire affectation
des masses » (`cherche_heuristique.py`) montre qu'a forte charge aucun ordre ne
tient si l'on ne trie pas les lourds : la regle « lourd sur la place 1 » fait
partie de l'heuristique.

## Un seul ordre qui marche a chaque fois ?

**Sur le domaine complet, non, et c'est demontre.** Avec des paras de masses
egales, le moment paras d'un ordre vaut N x masse x (bras moyen des N premieres
places) : chaque scenario impose une bande de bras moyen, et si les bandes de
deux scenarios ne se recoupent pas pour un N, aucun ordre ne convient. C'est le
cas pour N = 10 a 17 (`analyse_bandes.py`, `output/fig_bandes.png`).

**Sur le domaine realiste** (carburant >= 320 lbs, masse moyenne 70 a 110 kg),
toujours non pour un ordre commun aux deux avions, mais de peu : a N = 11,
C208B-B avec 2200 lbs et des paras de 70 kg exige un bras moyen d'au moins
237,5 in, C208B-A avec 400 lbs et des paras de 110 kg exige au plus 237,3 in. Le
meilleur ordre commun (recuit) rate 29 a 37 scenarios sur 13 942, jusqu'a 1,4 in
dehors, sur C208B-B plein avec paras legers et sur C208B-A peu charge en
carburant avec paras lourds (`output/ordre_unique.log`, `ordre_unique_final.log`).

**Oui sous conditions** (`ordre_unique_plans.py`, `output/ordre_unique_retenu.json`,
`output/fig_ordre_unique_par_avion.png`) :

| domaine | echecs | marge min | ordre (bras in, place 1 en premier) |
|---|---|---|---|
| C208B-A, realiste | 0 / 7092 | +0,51 in | 282 256 307 136 155 307 282 155 206 231 263 200 168 256 181 206 181 231 231 294 |
| C208B-B, realiste | 0 / 6850 | +0,27 in | 307 307 294 136 282 155 263 231 200 256 206 206 181 231 181 231 168 256 155 282 |
| deux avions, carburant <= 1900 lbs et masse moyenne 75 a 105 kg | 0 / 9799 | +0,17 in | 307 155 307 282 136 282 168 263 206 256 256 155 231 181 231 181 231 206 200 294 |

Ces ordres sont trouves par recuit simule et n'ont pas de structure lisible :
ils font deriver le bras moyen des k premieres places de 240 in vers 226 in en
piochant tot dans les extremes (siege copilote a la 4e place, 307 in a la 1re).
La bande admissible descend en effet de 238 in (N <= 10) a 226 in (N = 20),
ce qu'un pivot fixe ne peut pas suivre : le meilleur ordre equilibre a pivot
unique rate encore 63 cas sur C208B-A et 259 sur C208B-B. La version structuree
« suiveur de bande » (`ordre_suiveur.py`, la moyenne des k premieres places
suit le milieu de la bande a N = k) s'en approche : 2 echecs sur C208B-A, 6 sur
C208B-B, de 0,5 in au plus.

Les marges sont minces (0,2 a 0,5 in, soit 0,3 a 0,75 %MAC, contre 0,87 in au
1er centile pour l'heuristique a 5 plans) et l'ordre s'effondre hors domaine
(257 echecs pour l'ordre C208B-A et 703 pour l'ordre C208B-B sur le domaine complet). Un ordre unique par avion est donc
possible, mais l'heuristique a 5 plans reste plus sure.

## L'ordre d'origine des planches, et l'enumeration exhaustive (Rust)

**L'ordre d'origine.** Les anciennes planches (`notebooks/archive/`, dossier
`centrage_c208 (Copy)`) utilisaient 20 places « legacy » (`get_slots_bk`, 8 a
droite, 5 au centre, 7 a gauche, C208B-B decale de +3 in) et l'ordre
`filling_order_bon` = 234 234 209 210 258 258 222 258 282 282 185 186 136 162 185
294 149 161 307 307 (bras, rang 1 en premier). `ordre_origine.py` le teste :

| domaine | C208B-A | C208B-B |
|---|---|---|
| forfait 90 kg, critere des planches (arriere + MTOW) | 0 echec | 0 echec |
| forfait 90 kg, enveloppe complete (limite avant incluse) | 0 echec | 8 echecs avant, plein carburant, N = 3 a 7 |
| poids moyen 70 a 110 kg, pilotes 80/86, enveloppe complete | 144 / 5354 (2,7 %) | 217 / 5176 (4,2 %) |
| poids moyen 60 a 120 kg, pilotes 80/86, enveloppe complete | 299 / 7801 (3,8 %) | 446 / 7555 (5,9 %) |

Au forfait il tient (c'est ce pour quoi il a ete regle). Au poids moyen de la
rotation il casse par l'arriere pour N = 10 a 12 avec des paras de 100 kg et
plus (les rangs 9 et 10 sont a 282 in, bras moyen 245 in) et par l'avant pour
les paras legers sur C208B-B.

**Enumeration exhaustive** (`enumeration/`, Rust, `main.rs`, compile avec la cible
musl et `rust-lld` faute de `cc` sur la machine). Avec des masses uniformes
(forfait ou poids moyen), une configuration est un sous-ensemble de places et
seule compte la somme des bras : la condition d'enveloppe est une bande sur
cette somme, calculee par `prepare.py` comme intersection sur tout le domaine.
Le programme parcourt les 2^20 sous-ensembles et fait une programmation
dynamique sur les chaines emboitees (un ordre = une chaine S1 c S2 c ... c S20) :
nombre exact d'ordres valides, et ordre de marge minimale maximale. 54 cas
(2 jeux de places x 7 domaines x 3 avions, plus le critere arriere seule) en
3,4 s. `rapport_enum.py` verifie ensuite les meilleurs ordres au banc Python,
masses individuelles comprises ; `output/enumeration.md` a tout le detail.

- Configurations possibles : 2^20 - 1 = 1 048 575 sous-ensembles (184 756 pour
  N = 10) ; ordres possibles : 20! = 2,43e18.
- Au forfait 90 kg (places legacy, enveloppe complete), 87 171 configurations
  a 10 paras sont valides sur C208B-A, et 1,4e17 ordres complets (5,7 % de
  tous les ordres) ; 3,2e16 ordres valent pour les deux avions a la fois. Avec le
  seul critere des planches (arriere + MTOW), un ordre sur deux est valide.
- Au poids moyen 70 a 110 kg, pilotes 80 et 86, tout carburant : 1,5e15 ordres
  sur C208B-A, 2,8e13 sur C208B-B, et encore 1,1e11 communs aux deux avions sur
  les places legacy (aucun sur les places N=20 : N max 10). Le meilleur commun
  a 0,24 in de marge CG.
- Au poids moyen 60 a 120 kg : 5e10 ordres sur C208B-A, aucun sur C208B-B
  (N max 11), aucun commun (N max 10).
- Avec les pilotes de 65 a 110 kg : C208B-A 5,7e12, C208B-B 3,2e8, aucun commun
  (N max 9). Les meilleurs ordres tiennent sur les masses uniformes mais
  laissent 8 a 28 echecs avec des masses individuelles et des pilotes hors grille.
- Carburant 320 a 1900 lbs et poids moyen 75 a 105 kg : 1,4e15 ordres communs
  aux deux avions, le meilleur a 0,64 in de marge CG (2,6 in de bras moyen).

Les meilleurs ordres sont dessines dans `output/fig_enumeration_ordres.png` et
listes dans `output/enumeration_meilleurs_ordres.json`. Conclusion : pour un
avion donne et un domaine de poids moyen raisonnable, des ordres uniques
existent par milliards, mais leur marge fond des que le domaine s'elargit
(pilotes, paras tres legers ou tres lourds), et aucun ne survit au domaine
complet. L'enumeration donne la reponse exacte la ou le recuit ne faisait
qu'approcher.

## Placement par programmation lineaire en nombres entiers (`placement_milp.py`)

Oui, le placement « ou s'assoit qui » se modelise directement en MILP, et le
solveur HiGHS livre avec `scipy.optimize.milp` suffit. Entree : un manifeste JSON
(avion, pilote, carburant, liste des paras avec masse, groupe facultatif, rang de
sortie facultatif, ex aequo permis). Sortie : la place de chacun, le CG et la
marge, un plan (`output/placement_<manifeste>.png`).

```bash
python3 placement_milp.py manifestes/exemple_groupes.json --sequence --groupes-ordonnes
python3 placement_milp.py manifestes/exemple_tandems.json --sequence --cg-avant --tolerance 0.2
python3 sticks.py --temps 10 --procs 8            # les 234 fiches de juillet, 4 min
python3 sticks.py --tirages 3 --sans-plans        # sensibilite au tirage des masses
```

**Modele.** Variables binaires x[p, s] (para p sur la place s). Contraintes :
une place par para, un para au plus par place ; enveloppe au decollage (la masse
totale est fixee, le moment est lineaire en x) avec une marge mu en in de CG ;
avec `--sequence`, enveloppe encore respectee apres la sortie des k premiers
paras pour tout k (les autres restent assis) ; par groupe, une boite englobante
(bras mini et maxi, lateral mini et maxi) avec une borne inferieure exacte sur sa
taille (plus petite boite pouvant contenir n places, par fenetre glissante).

**Resolution en deux phases.** 1) maximiser la marge mu : c'est la reponse
exacte a « existe-t-il un placement valide » (accord 19/19 avec l'oracle sur
des manifestes aleatoires, 0,3 s en moyenne, 0,6 s au pire). 2) sous
mu >= min(mu*, marge cible, 0,5 in par defaut), minimiser le cout de realisme :
`poids_groupe` x somme des boites (en pas de place, 25 in, lateral pondere 0,5)
+ `poids_sortie` x somme sur les paras classes de |rang de la place par
distance a la porte - rang de sortie|. Le para qui sort premier vise donc la
place la plus proche de la porte, le suivant la deuxieme, et ainsi de suite ;
un groupe vise des places contigues.

**Ce que ca donne.** Sur l'exemple a 16 paras et 3 groupes (C208B-A, 800 lbs) :
groupe A (sortie 1) sur les places 282 a 307 pres de la porte, B au milieu, C en
zone 2, les solos et le dernier a sortir (120 kg) a l'avant, CG 203,8 in avec
0,8 in de marge, et 0,1 in de marge au pire pendant le largage. La phase 1 est
instantanee ; la phase 2 trouve de bonnes solutions en quelques secondes mais
ne prouve l'optimum que pour les petits manifestes (N <= 9) : au-dela, on
arrete au temps limite (`--temps`, 60 s par defaut) avec un ecart residuel de 10
a 20 % qui vient surtout de la faiblesse de la borne, pas de la solution. Banc
d'essai : `python3 test_placement.py 30 10` (30 manifestes, 10 s par phase).

### Coupes et contraintes supplementaires : ce qui accelere la preuve

Le modele accepte en plus (`bench_placement.py`, `output/bench_placement.log`) :

- **tandems** (`"tandem": "T1", "role": "porteur"|"passager"`) : porteur sur une
  place laterale, passager sur la place juste devant du meme cote, jamais au
  centre ni en siege copilote ; fixer le porteur fixe le passager (une egalite
  par place, et les autres variables des deux paras sont mises a zero) ;
- **groupes ordonnes** (`--groupes-ordonnes`) : un groupe qui sort avant est
  entierement en arriere d'un groupe qui sort apres (Mn_g >= Mx_h), coupe dure ;
- **cohesion par ancre** (`--cohesion ancre`) : une place d'ancrage par groupe et
  chaque membre paie sa distance a l'ancre (formulation de type localisation,
  relaxation continue plus serree mais 400 variables de plus par membre).

| variante (16 paras, 60 s max, sequence) | phase 2 | etat | boites | ecart sortie |
|---|---|---|---|---|
| boite | 60 s | ecart 18 % | 7,66 | 24 |
| **boite + groupes ordonnes** | **18 s** | **optimum prouve** | 6,40 | 29 |
| ancre | 60 s | ecart 13 % | 5,90 | 27 |
| ancre + groupes ordonnes | 60 s | ecart 24 % | 5,14 | 35 |
| avec 3 tandems, boite | 20 s | optimum prouve | 5,00 | 26 |
| avec 3 tandems, boite + ordonnes | 16 s | optimum prouve | 3,99 | 33 |

Oui, les regles metier font des coupes efficaces : l'ordre des groupes et les
tandems suppriment les symetries que le solveur explorait en vain, et le meme
manifeste passe de « 60 s sans preuve » a « optimum prouve en 18 s ». La
formulation par ancre n'aide pas avec HiGHS (modele plus gros). Les tandems
rendent tout prouvable en 20 s parce que six paras sur seize n'ont plus que
douze positions possibles.

### CG le plus avant a MTOW : un compromis, pas un bonus

`--cg-avant` ajoute une phase 3 : sous cout de realisme <= (1 + tolerance) x le
cout de la phase 2, minimiser le moment (CG vers la limite avant, marge cible
conservee). Sur l'exemple a 16 paras (`bench_cg_avant.py`, `output/bench_cg_avant.log`) :

| tolerance | ecart sortie | CG decollage (in) | marge decollage | marge pendant le largage |
|---|---|---|---|---|
| 0 (phase 2 seule) | 29 | 203,63 | +0,72 | +0,00 |
| 5 % | 30 | 203,59 | +0,76 | +0,00 |
| 20 % | 37 | 202,53 | +1,82 | +0,00 |
| 50 % | 48 | 201,56 | +2,75 | +0,02 |
| 100 % | 74 | 200,57 | +1,76 | +0,05 |
| 300 % | 118 | 199,33 | +0,52 | +0,21 |

Deux enseignements. D'abord, « premiers sortants pres de la porte » met la
masse a l'arriere : avancer le CG au decollage se paie directement en ordre de
sortie (l'ecart passe de 29 a 118 rangs pour gagner 4 in). Ensuite, ce n'est pas
le decollage qui bloque mais le **largage** : des que les groupes arriere sont
sortis, les paras restants sont a l'avant et le CG vient buter sur la limite
avant, marge nulle, quelle que soit la tolerance. Avec `--sequence`, la
contrainte en vol est la vraie limite ; sans elle, le solveur avancerait le CG
au decollage et sortirait de l'enveloppe en vol. Si l'objectif est un CG avant
a MTOW, il faut le formuler comme une marge minimale en vol plutot que comme
une cible au decollage.

Autres pistes : places interdites (materiel), paires imposees hors tandem,
poids de realisme a regler avec les utilisateurs (`--poids-groupe`,
`--poids-sortie`), ou CBC/Gurobi via `pulp` pour les manifestes sans groupes
ordonnes ni tandems.

### Le modele explique, et comment accelerer la preuve : document de synthese

`output/Placement_MILP_modele_et_acceleration.pdf` (12 pages A4, source
`doc_placement_milp.html`, HTML + MathJax) explique le modele contrainte par
contrainte (pourquoi le centrage est lineaire, affectation, marge, sequence de
largage, tandems, boites, groupes ordonnes, ancre, cout de realisme, trois
phases, taille du modele), decrit ce que fait HiGHS et ou le temps passe, puis
passe en revue les techniques d'acceleration de la litterature (formulation
plus serree, symetries, reglages du branch and bound, pretraitement, Benders
classique et logique, generation de colonnes, relaxation lagrangienne, CP-SAT)
avec leur applicabilite ici, une recommandation ordonnee et les sources.

Ce que les mesures ont montre (exemple a 16 paras, phase 2, `--sequence`) :

- HiGHS trouve la solution finale a 7 s et passe les 53 s restantes a remonter
  la borne duale : c'est la preuve qui coute, pas la recherche ;
- la borne de la relaxation LP a la racine vaut 26,5 pour un optimum a 41,8
  (ecart d'integrite 36 %) : la relaxation repartit chaque para « a moitie »
  sur deux places et ramene les boites a leur taille minimale ;
- « groupes ordonnes » ne change pas la relaxation (meme 26,55) mais fait
  eliminer 59 binaires au presolve et divise les noeuds par trois ;
- la formulation « fenetres » (`bench_fenetres.py`, `output/bench_fenetres.log`,
  une binaire par groupe et fenetre candidate, cout de cohesion exact par
  fenetre) releve la borne racine a 30,9 et divise les noeuds par 5 a 20, mais
  le modele est six fois plus dense (849 variables, 2338 lignes, 38 000
  coefficients) et le temps de preuve reste equivalent (27 s contre 21 s).

### Revue de litterature : problemes voisins et techniques utilisees

`output/Revue_litterature_placement_equilibre.pdf` (15 pages, source
`doc_revue_litterature.html`) recense une soixantaine de references en cinq
familles : fret aerien et « aircraft weight and balance » (Mongeau et Bes 2003,
Limbourg 2012, Vancroonenburg 2014, Lurkin 2015, Brandt 2017 et 2019, Zhao 2021 a
2026), passagers sous contrainte de centrage et pratique reglementaire (Zhao et
Xiao 2024 et 2025, FAA AC 120-27F, AC 105-2E, USPA, NTSB, EASA), groupes assis
ensemble (Tajima et Misono 1999, Clausen 2010, Blom 2020, Haque et Hamid 2023,
Vangerven 2022, Lewis 2016), equilibre en theorie et dans les autres modes
(Amiouny 1992, Fekete 2018, stowage, essieux, trains), et methodes exactes et
hybrides (GAP et branch-and-price, Benders logique, CP-SAT contre MIP, symetries,
matheuristiques). Conclusions a retenir :

- aucun article ne reunit affectation individuelle, CG a chaque sortie et
  groupes compacts ; le parachutisme n'a que des regles, pas de methode ;
- le fret aerien resout « affectation + bande de moment » en secondes par un
  MILP compact et un solveur commercial ; les decompositions (Benders, Benders
  logique) n'apparaissent que sur des extensions, et Gurobi direct bat le
  Benders de Zhao 2023 d'un facteur 150 ;
- pour la cohesion des groupes, les formulations par motifs enumeres (blocs de
  sieges, set packing : Tajima 1999, Blom 2020) ont des relaxations presque
  entieres, alors que boites englobantes, big-M et flots de connexite plafonnent
  vite ; les coupes de distance de Vangerven et le bris de symetrie sont les
  inegalites qui relevent la borne ;
- placer des masses vers un CG cible est fortement NP-difficile des la dimension
  1 (Amiouny), et l'ordre de retrait sous bande de CG l'est aussi (Fekete) : c'est
  la petite taille (20 places) qui rend l'exact accessible ;
- CP-SAT est competitif sur les problemes purement entiers mais reste un ordre
  de grandeur derriere Gurobi pour la preuve sur l'affectation a contraintes de
  cote (Johannesson 2026, Grus 2026) ; a tester quand meme, HiGHS n'est pas
  Gurobi.

Le rapport se termine par neuf transferts ordonnes (critere d'arret, cohesion par
blocs enumeres plus coupes de distance, regles de terrain en coupes de dominance,
corridor de moments par etape, essai CP-SAT, agregation par zone au forfait et
programmation dynamique exacte, warm start et bet-and-run via highspy, Benders
logique en secours, marge statistique sur les masses) et par la liste des
affirmations non verifiees.

Le PDF se regenere avec Chrome headless (pas de pdflatex ni pandoc sur la
machine ; MathJax et les polices sont charges depuis le reseau) :

```bash
cd heuristique_remplissage
google-chrome --headless=new --no-sandbox --disable-gpu --no-pdf-header-footer \
  --virtual-time-budget=20000 --print-to-pdf=output/Placement_MILP_modele_et_acceleration.pdf \
  doc_placement_milp.html
```

## Binaire autonome (`placement_rs/`)

`placement_rs/placement` est un executable Rust statique (4,9 Mo, aucune
dependance, compile avec la cible musl et `rust-lld` faute de compilateur C
sur la machine) qui fait le meme travail que `placement_milp.py` a partir d'un
JSON et rend le meilleur placement en JSON :

```bash
placement_rs/placement entree.json            # resultat sur la sortie standard
placement_rs/placement entree.json sortie.json
placement_rs/placement - < entree.json
```

Compilation : `cd placement_rs && rustc -O --edition 2021 --target
x86_64-unknown-linux-musl -C linker=rust-lld -C linker-flavor=ld.lld -C
link-self-contained=yes main.rs -o placement` (sur une machine avec `cc`,
`rustc -O --edition 2021 main.rs` suffit).

**Entree.** Masses et bras dans des unites coherentes (le programme ne convertit
rien : moment = masse x bras). Exemples complets : `placement_rs/exemple_groupes.json`,
`placement_rs/exemple_tandems.json`, produits par `export_json.py` a partir des
manifestes Python avec les donnees Caravan (places N=20, enveloppe, bras carburant
de la table du notebook pour la quantite donnee, pilote a 135,5 in).

```json
{"avion": {"masse_vide": 4890, "moment_vide": 924161},
 "enveloppe": {"avant": [[5500, 179.6], [8000, 193.37], [9062, 199.15]],
               "arriere": [[0, 204.35], [9062, 204.35]], "mtow": 9062},
 "carburant": {"masse": 800, "bras": 203.2},
 "pilote": {"masse": 176.4, "bras": 135.5},
 "porte": {"x": 307, "y": -32},
 "places": [{"id": "0", "x": 135.5, "y": 16, "copilote": true},
            {"id": "1", "x": 155.4, "y": 16}, "..."],
 "paras": [{"nom": "A1", "masse": 216, "groupe": "A", "sortie": 1},
           {"nom": "T1p", "masse": 209, "tandem": "T1", "role": "porteur", "sortie": 3},
           {"nom": "T1x", "masse": 150, "tandem": "T1", "role": "passager", "sortie": 3}, "..."],
 "options": {"marge_cible": 0.5, "sequence": true, "groupes_ordonnes": false,
             "poids_groupe": 2, "poids_sortie": 1, "poids_lateral": 0.5, "pas": 25,
             "temps_max_s": 1.5}}
```

`avion.bras_vide` peut remplacer `moment_vide`. L'enveloppe est une ligne
brisee (masse, CG) par limite, interpolee lineairement. `sortie` accepte les
ex aequo (un groupe), les paras sans `sortie` sortent en dernier. Le passager
tandem va sur la place `devant` du porteur (donnee par place, ou deduite : meme
`y`, `x` immediatement inferieur), jamais sur le siege copilote. `sequence`
verifie l'enveloppe apres chaque sortie. `groupes_ordonnes` impose qu'un
groupe qui sort avant soit entierement en arriere.

**Sortie.** `ok`, `marge_max` (marge maximale possible, minimum sur toutes les
etapes), `marge_max_prouvee`, `marge` (celle du placement rendu), `placement`
(nom, id de place, x, y, rang de distance a la porte), `etapes` (masse, CG,
marge apres chaque sortie), `cout_realisme`, `boites`, `ecart_sortie`, temps.
Si la masse depasse la MTOW ou si aucun placement ne tient dans l'enveloppe,
`ok` est faux avec un message (et « au mieux X dehors »).

**Methode.** Phase 0 : recuit simule maximisant la marge minimale (borne
inferieure). Phase 1 : recherche arborescente exacte avec bornes de moment (les
plus lourds restants sur les places libres les plus avant / arriere), une place
par valeur de bras distincte, elagage par l'ordre des groupes ; elle tente
marge + 0,05 et prouve la marge maximale quand elle epuise l'arbre (300 000
noeuds, environ 1 s). Phase 2 : recuit a redemarrages sur le cout de realisme
sous marge >= min(marge max, marge cible), chaque solution retenue etant
verifiee exactement (enveloppe a chaque etape, tandems, ordre).

**Validation contre le MILP Python** (`compare_rs.py`, `output/compare_rs.log`,
Python limite a 10 s par phase, binaire 1,5 s de recuit) : marge maximale
identique a 0,03 in pres sur les 16 cas ; cout de realisme egal sur 10 cas et
meilleur pour le binaire sur les 6 autres (40,3 contre 42,7 sur l'exemple a 16
paras et 3 groupes) ; 2 a 3 s au total contre 10 a 13 s. La preuve de la marge
maximale aboutit pour 6 a 10 paras avec groupes ordonnes, pas au-dela (bornes
trop laches), mais la valeur trouvee coincide avec celle du MILP.

## Binaire C++ avec HiGHS embarque (`placement_cpp/`)

Modelisation complete dans `placement_cpp/MODELE.md`. Par rapport aux versions
precedentes, l'objectif change : **marge arriere maximale au decollage**, sous
**marge avant >= `marge_avant_min` a toutes les etapes du largage** (donc des la
sortie du premier groupe), puis realisme a marge arriere >= max − `tolerance_marge`.

- `placement.cpp` : lecture JSON (nlohmann/json), construction du MILP, resolution
  par HiGHS v1.9.0 (branch-and-cut) embarque en statique, phase 2 demarree de la
  solution de phase 1 (`setSolution`). Meme format d'entree que le binaire Rust,
  plus les options `marge_avant_min` (0,5), `tolerance_marge` (0,25), `gap`,
  `temps_max_s` (10 s par phase) ; place `centre: true` pour interdire les
  tandems sur la rangee centrale.
- `build.sh` : clone HiGHS et l'en-tete JSON, configure et compile avec le
  compilateur du systeme. Sur cette machine sans compilateur C, il a ete
  construit avec `zig cc` (paquet pip `ziglang` deballe a la main, plus `cmake`
  et `ninja` des wheels pip, wrappers `zigcc`/`zigcxx`/`zigar`/`zigranlib`
  passes a CMake). Binaire strippe de 3,8 Mo, `build/placement`.

```bash
placement_cpp/build/placement placement_cpp/exemple_groupes.json
```

**Sortie** : `marge_arriere_max` (phase 1, prouvee si `phase1` vaut « optimum »),
`marge_arriere` et `marge_avant_min_obtenue` du placement rendu, `phase2`
(« optimum » ou « temps limite » avec `ecart_phase2`), `placement`, `etapes`
(masse, CG, marges avant et arriere apres chaque sortie), couts, temps. Si la
marge avant n'est pas tenable, `ok` est faux avec la marge avant maximale
possible et le placement correspondant.

**Validation** (`compare_cpp.py`, `output/compare_cpp.log`) : sur les 2 exemples
et 6 fiches de juillet, chaque placement rendu est recalcule avec le modele
Python (marges avant a chaque etape >= 0,5 in, marge arriere identique a
l'annonce), tandems et ordre des groupes verifies. Phase 1 a l'optimum en moins
d'une seconde dans tous les cas ; phase 2 a l'optimum jusqu'a 11 paras ou avec
groupes ordonnes, sinon temps limite (10 s) avec une solution realisable.

**Compromis marge arriere / realisme** (exemple a 16 paras, 3 groupes,
`output/compromis_cpp.log`) :

| tolerance | marge arriere rendue | ecart de sortie (rangs) | boites |
|---|---|---|---|
| 0,25 in | 4,91 | 46 | 9,5 |
| 2 in | 3,09 | 33 | 8,9 |
| 4 in | 1,20 | 30 | 8,6 |
| sans limite | 0,17 | 22 | 7,7 |

Maximiser la marge arriere pousse toute la charge vers l'avant, donc les
premiers sortants loin de la porte ; la tolerance est le bouton de reglage
entre les deux, la marge avant pendant le largage restant garantie dans tous
les cas.

**A 20 paras** (6 fiches de juillet, `output/cpp_20paras.log`) : sans groupes
ordonnes, phase 1 a l'optimum en moins d'une seconde, phase 2 a l'optimum en 3 a
7 s sur trois fiches et arretee a 10 s sur les autres avec une solution
realisable ; avec `temps_max_s` a 3 s, 3 s au total. Avec groupes ordonnes, la
phase 1 prend 7 a 10 s et, sur trois fiches sur six, aucun placement ne tient la
marge avant de 0,5 in a toutes les etapes : le binaire le dit et rend la marge
avant maximale possible (dichotomie limitee a 5 pas de 3 s).

### Livrable (`placement_cpp/livrable/`)

Binaire Linux statique `placement-linux-x86_64` avec `--help`, `--pdf`, `--etapes`
(`premier_groupe` par defaut : marge avant garantie apres la sortie du premier
groupe seulement, les paras qui s'avancent ensuite n'etant pas modelises),
paires `devant_de`, places `interdit`, sortie PDF (plan cabine avec CG et
limites sur l'avion, centrogramme, tableaux). Fichier d'entree commente
`exemple_stick.json` (bras a vide, bras carburant, enveloppe, stick avec masses,
groupes, tandem sur un bord avec passager devant le porteur, paire eleve /
moniteur, places interdites), resultat JSON et PDF de l'exemple, second exemple
`exemple_20_paras.json` a cabine pleine (20 paras, 54 lbs sous la MTOW, `tolerance_marge`
a 2 : a 0,25 la marge arriere max de 2,6 in ne laisse aucune liberte et disperse les VR,
tableau tolerance / realisme dans le README du livrable), `MODELE.md`,
sources et scripts de construction. `README.md` du livrable = mode d'emploi.
Binaires macOS : compilation croisee avec `zig cc` tentee depuis Linux
(`build_macos.sh`), a defaut `./build.sh` sur le Mac (compilateur natif).

Compilateur installe sur cette machine sans droits administrateur : `zig cc`
(clang 21) deballe des wheels pip dans `~/.local/opt/ziglang`, avec `cc`,
`c++`, `clang`, `clang++`, `ar`, `ranlib`, `cmake`, `ninja` dans `~/.local/bin`.

**Accelerations retenues d'apres `RESUME_RECHERCHES.md`** (`bench_perf_cpp.py`,
`output/bench_perf_cpp.log`) : critere d'arret a 5 % d'ecart, recuit simule
d'une seconde comme point de depart de la phase 2 (le solveur ne fait plus que
prouver ou ameliorer), mode `--rapide` sans solveur en phase 2. Sur huit cas
(deux exemples a 16 paras, six fiches a 20 paras) : 55 s en tout avant, 34 s
avec les reglages par defaut a cout egal, 19 s avec `--temps 3`, 9 s en
`--rapide` (cout cumule +0,4 %). Les sticks a 20 paras sont prouves optimaux en
1 s. Les autres pistes du resume (cohesion par blocs enumeres, coupes de
dominance metier, CP-SAT) restent ouvertes : la formulation « fenetres »
avait deja ete mesuree equivalente en temps.

Recompile avec le gcc installe par Jules (build-essential, cmake 3.28, ninja) :
`build.sh` sans wrapper, `-static-libstdc++` pour la portabilite Linux.

**Autre approche testee en parallele** : le binaire Rust (`placement_rs`, recuit
+ recherche exacte, sans solveur) accepte le meme objectif (`objectif:
"marge_arriere"`, `etapes: "premier_groupe"`). Sur 14 manifestes (exemples,
fiches de juillet dont six a 20 paras), sa marge arriere maximale coincide avec
HiGHS a 0,02 in pres, en 2 s contre 3 a 11 s, sans preuve d'optimalite entre 7
et 16 paras (`compare_objectif_arriere.py`, `output/compare_objectif_arriere.log`).

## Test sur les fiches de stick de juillet 2026 (`sticks.py`)

234 fiches PDF du logiciel club (`mtow-juillet/fiche_avionnage_juillet/`), dont
218 Caravan avec carburant renseigne (8 Pilatus et 8 sans carburant ignorees).

**Lecture des fiches.** Texte `pdftotext -layout`. La fiche ne donne pas les
masses individuelles, seulement la masse totale des paras : les masses sont
tirees selon une loi normale (ecart type 12 kg, bornes 55 a 130 kg)
renormalisees a la masse totale declaree, graine = numero de stick. Les
groupes sont des cellules fusionnees dont le libelle (« FF n°1 », « Tandem n°2 »
ou un nom d'equipe comme « DEADLEAF ») est rendu au milieu du bloc : si le
bloc commence a la ligne s et le libelle est a la ligne L, il finit a 2L - s.
Cette regle retrouve le nombre de groupes declare sur 219 fiches sur 226, le
rattachement au libelle le plus proche complete les autres. Le passager
tandem est marque « Tdm » dans la colonne voile, le porteur a la discipline
« Tandem » avec sa voile, le videaste « Vdo Tdm ». Solos : Libre, FF Solo,
1er solo PAC, PSV, Derive, wingsuit sans libelle WS.

**Ordre de sortie** (demande) : VR, freefly, eleves, PAC, tandem, wingsuit.
Hypotheses prises : Libre et Largueur avec les eleves ; Track juste apres le
freefly ; Suivi Vdo et Video sortent avec leur groupe ; Prepa test avec le VR ;
Anim et Init dans la famille de leur discipline. Dans une classe, les groupes
par numero puis les solos dans l'ordre de la fiche.

**Resolution.** Pour chaque fiche, `placement_milp` avec sequence de largage et
groupes ordonnes, marge cible 0,5 in, 10 s par phase ; replis dans l'ordre :
groupes non ordonnes, puis sans contrainte de largage. 8 processus, 4 minutes
pour le lot. Resultats dans `output/sticks/` (`resultats.csv`, un plan PNG et
un JSON par fiche, `run.log`).

| resultat | fiches |
|---|---|
| placee, groupes ordonnes, largage verifie | 142 |
| placee, groupes non ordonnes (l'ordre strict est impossible) | 12 |
| **au-dessus de la MTOW selon les chiffres de la fiche** | **64** (2 a 281 kg, mediane 65 kg ; 18 a 20 paras avec 460 a 530 L) |

Sur les 154 fiches placees (marge = minimum sur le decollage et chaque etape du
largage, cible 0,5 in) : marge au decollage mediane 0,61 in (minimum 0,15),
marge minimale pendant le largage mediane 1,06 in (minimum 0,16). La marge
maximale possible descend avec la charge et, a pleine charge, c'est la limite
avant apres la sortie des premiers groupes qui dimensionne le placement, pas
le decollage. La marge
maximale possible (phase 1, avec largage) va de 8 in a 6 paras a 2,6 in a 20
paras ; 11 fiches a 17 paras et plus n'admettent aucun placement avec les
groupes strictement ordonnes de l'arriere vers l'avant, et 6 d'entre elles ont
alors un CG trop arriere au decollage (jusqu'a 1,3 in) : il faut y melanger
l'ordre des groupes. Optimum de realisme prouve sur 38 fiches en 10 s, les
autres s'arretent au temps limite avec une solution coherente (mediane 11 s
par fiche, 20 s au pire). Le binaire Rust place les 154 memes fiches en 2,5 s
en mediane et 6,2 s au pire (`bench_rs_sticks.py`, `output/sticks/resultats_rs.csv`),
sans preuve de marge maximale au-dela de 10 paras.

Les 64 depassements de MTOW sont ceux des fiches elles-memes (masse totale
declaree superieure a 4110 kg), concentres les 21 et 22 juillet ; le
placement n'y a pas de sens.

**Sensibilite au tirage des masses** (`--tirages 3`, `resultats_3tirages.csv`,
11 minutes) : pour une meme fiche, la marge maximale possible varie de 0,02 in
en mediane entre tirages (0,8 in au 90e centile), la marge au decollage de
0,23 in en mediane (1,8 in au pire). Aucune fiche ne bascule entre « placee »
et « impossible » selon le tirage, mais sur 15 fiches a 16 paras et plus la
faisabilite de l'ordre strict des groupes depend du tirage (statut different
selon le tirage pour 6 d'entre elles) : a pleine charge, la repartition reelle
des masses entre groupes decide si le groupe qui sort en premier peut etre
tout a l'arriere. C'est l'argument pour peser reellement les paras (ou au moins
les groupes) plutot que de se fier a la masse moyenne.

## Remarque hors sujet mais a noter

C208B-B avec un pilote de 100 kg ou plus et le plein (2224 lbs), **sans para**,
est en avant de la limite avant de 0,2 a 0,5 in. Avec un pilote de 80 a 86 kg
il reste dedans de 0,15 a 0,3 in. Les planches ne verifient que la limite
arriere (40,33 %MAC) et la MTOW, pas la limite avant.

## Fichiers

| Fichier | Role |
|---|---|
| `caravan_model.py` | relit cellules 0 a 5 du notebook BK (geometrie, table carburant, positions N=20) ; enveloppe avec limite avant ; heuristiques par pivot ; oracle (existe-t-il une affectation valide ?) |
| `scenarios.py` | jeu de scenarios : grille masses uniformes x N x carburant x avion x pilote, plus tirages aleatoires (uniforme 60-120, normale 85/12, bimodale 65/115) |
| `fast.py` | evaluation vectorisee d'un ordre sur tous les scenarios (bande de moment paras admissible precalculee) |
| `verif_heuristique.py` | verification detaillee d'un pivot : `python3 verif_heuristique.py 202` |
| `sweep_pivot.py` | balayage du pivot 190 a 260 in |
| `analyse_bandes.py` | intersection par N des bandes de bras moyen admissibles |
| `optimise_ordre.py` | recuit simule sur l'ordre (tous scenarios, sous-ensemble realiste, deux regimes carburant), ecrit `output/ordres.json` |
| `rapport.py` | figures et `output/resume.md` |
| `cherche_heuristique.py` | critere « pire affectation » et recuit par regimes (carburant, masse) |
| `pivot_regimes.py` | ordre equilibre autour d'un pivot ; tables de decision (carburant x masse, N) |
| `heuristique_finale.py` | raffinement des seuils et pivots (pas 2,5 in), detail des echecs, robustesse |
| `fiche_heuristique.py` | heuristique retenue : fiche PDF/PNG, JSON, carte des marges |
| `ordre_unique.py` | un seul ordre ? recoupement des bandes par domaine restreint, recuit la ou c'est possible |
| `ordre_suiveur.py` | ordre unique structure « suiveur de bande » et raffinement |
| `ordre_unique_final.py`, `ordre_unique_plans.py` | ordres uniques par avion : marge maximale, consolidation, plans |
| `ordre_origine.py` | test de l'ordre d'origine des planches (places legacy) au forfait et au poids moyen |
| `enumeration/main.rs` | enumerateur Rust : 2^20 configurations, comptage exact des ordres valides, ordre de marge max |
| `enumeration/prepare.py`, `rapport_enum.py`, `plans_enum.py` | bandes d'entree, rapport et verification au banc, plans |
| `placement_milp.py`, `manifestes/*.json` | placement d'un manifeste reel par MILP (HiGHS) : validite, marge, groupes, ordre de sortie |
| `test_placement.py` | banc d'essai du MILP sur manifestes aleatoires, compare a l'oracle |
| `bench_placement.py`, `bench_cg_avant.py` | comparaison des formulations et coupes ; compromis realisme / CG avant |
| `sticks.py` | fiches de stick PDF -> manifestes (masses tirees, groupes, ordre de sortie) -> placement en lot |
| `placement_rs/main.rs`, `json.rs` | binaire autonome : JSON -> meilleur placement (recuit + recherche exacte), sans dependance |
| `export_json.py`, `compare_rs.py`, `bench_rs_sticks.py` | export des manifestes vers le JSON des binaires, validation contre le MILP, chrono sur juillet |
| `placement_cpp/MODELE.md`, `placement.cpp`, `CMakeLists.txt`, `build.sh` | binaire C++ avec HiGHS embarque : marge arriere max sous marge avant garantie pendant le largage |
| `compare_cpp.py` | validation du binaire C++ (marges recalculees en Python, tandems, ordre) |
| `bench_fenetres.py` | formulation « fenetres candidates » par groupe : borne LP et MILP 60 s contre la formulation boite |
| `doc_placement_milp.html` | source du document de synthese (modele MILP + revue des accelerations), rendu en PDF par Chrome headless |
| `doc_revue_litterature.html` | source de la revue de litterature (problemes voisins, techniques, transferts), meme chaine de rendu |
| `RESUME_RECHERCHES.md` | condense des deux documents : solveurs, modele, mesures, verdicts, litterature, recommandations |

Sorties dans `output/` :

- `fig_pivot.png` : taux d'echec en fonction du pivot ;
- `fig_carte_202.png`, `fig_carte_235.png` : taux d'echec par N x carburant ;
- `fig_bandes.png` : bande de bras moyen admissible par N et bras moyen des k
  premieres places pour les pivots 202 et 235 ;
- `fig_plan_*.png` : plan cabine avec l'ordre numerote ;
- `Fiche_heuristique_remplissage_Caravan.pdf`, `fiche_heuristique.png`,
  `heuristique_retenue.json`, `fig_marge_retenue.png` : heuristique retenue ;
- `Placement_MILP_modele_et_acceleration.pdf`, `bench_fenetres.log` : document de
  synthese sur le MILP et banc de la formulation fenetres ;
- `Revue_litterature_placement_equilibre.pdf` : revue de litterature, cinq familles
  de problemes voisins et techniques utilisees ;
- `resume.md`, `ordres.json`, `optimise_ordre.log`, `pivot_regimes.log`,
  `heuristique_finale.log`, `cherche_heuristique.log`.

## Methode

Pour un scenario (avion, pilote, carburant, liste de masses), la masse totale ne
depend pas du placement ; seul le moment des paras varie. L'enveloppe se traduit
donc en une bande de moment paras admissible, calculee une fois par scenario.
Un ordre de places donne le moment par un simple produit matriciel, ce qui
permet le balayage et le recuit. Un « echec heuristique » est un scenario ou
l'heuristique sort de l'enveloppe alors qu'une affectation valide existe
(bornes min/max du moment par tri, confirmees par recherche locale). Les
scenarios au-dessus de la MTOW sont ecartes avant comptage.

Tout est relu depuis le notebook BK : une modification de la geometrie cabine ou
de la table carburant se repercute au prochain lancement. Ordre d'execution :

```bash
cd heuristique_remplissage
python3 verif_heuristique.py 202   # 15 s
python3 sweep_pivot.py             # 20 s
python3 analyse_bandes.py
python3 rapport.py                 # 20 s, figures + resume.md
python3 optimise_ordre.py          # 2 min 30, recuit + ordres.json
python3 pivot_regimes.py           # 10 s, tables de decision
python3 heuristique_finale.py      # 2 min, seuils et pivots raffines
python3 fiche_heuristique.py       # 15 s, fiche + JSON de l heuristique retenue
python3 ordre_unique.py            # 2 min, un seul ordre ? par domaine
python3 ordre_suiveur.py           # 1 min
python3 ordre_unique_final.py      # 1 min 30
python3 ordre_unique_plans.py      # 10 s, consolidation + plans par avion
python3 ordre_origine.py           # ordre d origine au forfait et au poids moyen
cd enumeration && python3 prepare.py \
  && rustc -O --target x86_64-unknown-linux-musl -C linker=rust-lld -C linker-flavor=ld.lld \
     -C link-self-contained=yes main.rs -o enumere \
  && ./enumere input.txt output.json && python3 rapport_enum.py && python3 plans_enum.py
```
