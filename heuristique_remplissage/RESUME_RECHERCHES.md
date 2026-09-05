# Résumé des recherches · placement des paras par MILP, accélération, littérature

Session du 4 septembre 2026. Trois documents détaillés existent dans `output/` :
`Placement_MILP_modele_et_acceleration.pdf` (le modèle et les techniques),
`Revue_litterature_placement_equilibre.pdf` (les problèmes voisins) et
`bench_fenetres.log` (un banc). Ce fichier en est le condensé.

## 1. Question de départ : un solveur libre embarquable en Rust ou C++

| Solveur | Licence | LP | MILP | Rust | Remarque |
|---|---|---|---|---|---|
| HiGHS | MIT | oui | oui | crates `highs`, `good_lp` | référence libre actuelle, celui de scipy |
| SCIP + SoPlex | Apache 2.0 | oui | oui, MINLP | `russcip` | branch-and-bound le plus puissant, build lourd |
| CBC / CLP | EPL 2.0 | oui | oui | `coin_cbc` | mature, dépassé par HiGHS |
| OR-Tools CP-SAT | Apache 2.0 | non | entiers | FFI communautaire | souvent meilleur sur affectation et ordonnancement à contraintes logiques |
| microlp | MIT | oui | basique | Rust pur | seul choix sans compilateur C |
| Clarabel | Apache 2.0 | oui, QP, SOCP | non | Rust pur | pas d'entiers |
| GLPK | GPL | oui | oui | `glpk-sys` | lent, licence contaminante |

Réponse courte : HiGHS, lié en statique, via le crate `highs` ou `good_lp`. Il faut un
compilateur C++ sur la machine de build (absent sur le poste actuel) ; sinon microlp en
Rust pur, nettement plus faible.

## 2. Le modèle en bref

- Variables : $x_{p,s} \in \{0,1\}$ (para $p$ sur la place $s$), marge $\mu$ continue,
  bornes de boîte par groupe ($M^{\min}, M^{\max}, Y^{\min}, Y^{\max}$).
- Le centrage est linéaire parce que la masse totale ne dépend pas du placement : la
  condition d'enveloppe devient une bande $[\ell, h]$ sur le moment des paras,
  $\sum m_p a_s x_{p,s}/1000$. La limite avant, fonction de la masse, est évaluée à une
  masse connue. Pendant le largage, après $k$ sorties, la masse restante est encore
  connue : une bande par étape, sans marge.
- Tandems : le passager est sur la place juste devant le porteur (une égalité par place
  admissible, variables interdites mises à zéro).
- Groupes : boîte englobante par contraintes agrégées et désagrégées, borne inférieure
  exacte sur la taille de la boîte, option « groupes ordonnés » (un groupe qui sort avant
  est entièrement en arrière).
- Coût de réalisme : $w_s \sum |r_s - t_p|\, x_{p,s}$ (rang de porte contre rang de
  sortie, constant par couple donc linéaire) plus $w_g/25$ fois la taille des boîtes.
- Trois phases : marge maximale (instantané), réalisme minimal sous marge (lent),
  option CG avant sous coût de réalisme borné.
- Taille sur l'exemple à 16 paras et 3 groupes : 333 variables dont 320 binaires,
  1046 contraintes, relaxation LP résolue en 20 ms.

## 3. Ce que les mesures ont montré (exemple à 16 paras, phase 2, 60 s)

| Formulation | Borne LP racine | Meilleure solution | Nœuds | Résultat |
|---|---|---|---|---|
| boîte | 26,55 | 39,33 | 1417 | écart 19 % à 60 s |
| boîte + groupes ordonnés | 26,55 | 41,80 | 460 | prouvé en 20,7 s |
| fenêtres candidates | 30,93 | 39,79 | 67 | écart 15 % à 60 s |
| fenêtres + ordonnés | 30,94 | 41,80 | 89 | prouvé en 27,4 s |

- HiGHS trouve la solution finale à 7 s et passe les 53 s restantes à remonter la borne
  duale : c'est la preuve qui coûte, pas la recherche.
- La relaxation triche en répartissant chaque para « à moitié » sur deux places, ce qui
  satisfait la bande de moment à moindre coût et ramène les boîtes à leur taille minimale.
- « Groupes ordonnés » ne change pas la borne LP mais fait éliminer 59 binaires au
  présolve et divise les nœuds par trois.
- La formulation « fenêtres » (une binaire par groupe et fenêtre candidate, coût exact)
  relève la borne mais rend le modèle six fois plus dense : temps équivalent.

## 4. Techniques d'accélération : verdicts

| Technique | Principe | Verdict ici |
|---|---|---|
| Coupes métier, dominance, symétries | interdire les solutions équivalentes ou peu réalistes avant de brancher | le levier le plus rentable, déjà ×3 |
| Formulation plus serrée (fenêtres, blocs) | convexifier la cohésion | borne meilleure, à alléger pour gagner du temps |
| CP-SAT | SAT + propagation + LNS + LP, portefeuille parallèle | à tester une journée, en mesurant le temps de preuve |
| Réglages, warm start, bet-and-run | `mip_rel_gap`, effort heuristique, graines multiples | marginal mais gratuit via highspy |
| Prétraitement | éliminer les $x_{p,s}$ impossibles et les étapes redondantes | modeste |
| Benders logique, branch and check | maître fenêtres et réalisme, sous-problème places sous centrage | 2e option ; sous-problème trivial donc gain incertain |
| Génération de colonnes, branch-and-price | colonne = placement complet d'un groupe | seulement à plus grande échelle |
| Relaxation lagrangienne | dualiser les bandes | borne égale à la LP (Geoffrion) ; utile sans solveur seulement |
| Benders classique | sous-problème continu dualisé | sans objet, le sous-problème est trivial |

Question préalable : si un placement bon à 10 % près sur un coût de réalisme
conventionnel suffit, un écart accepté de 10 % et une limite de 10 s donnent la même
solution dès aujourd'hui.

## 5. Littérature : problèmes voisins et techniques utilisées

Cinq familles, une soixantaine de références (détail et sources dans le PDF de revue).

**Fret aérien et « aircraft weight and balance ».** La famille la plus proche : objets
de masses connues sur positions à bras connus, CG en bande linéaire sur le moment.
Mongeau et Bès 2003, Limbourg 2012 (B747 en moins de 2 s avec CPLEX, objectif
« moment d'inertie » qui pilote la recherche), Vancroonenburg 2014 (enveloppe vérifiée
à des états discrets ZFW, TOW, LW), Lurkin 2015 et Brandt 2017 (une bande par étape de
vol, ensembles bloquants FILO), Zhao 2021 (enveloppe réelle linéarisée), Zhao 2023
(Benders battu 150 fois par Gurobi direct), Zhao 2026 (Benders logique sur deux
étapes). Les outils industriels (Lufthansa, Sabre, IBM) sont à base de règles.

**Passagers et pratique.** Trois articles seulement, tous agrégés : Zhao et Xiao 2024 et
2025 comptent des passagers par rangée (B737 en 1 s, Monte Carlo ou stochastique sur la
masse moyenne), Pardo González 2024 équilibre des comptes gauche-droite. La FAA
AC 120-27F impose les masses réelles sur monomoteur à turbine et donne une recette de
rognage d'enveloppe par zone. Les documents parachutisme (AC 105-2E, USPA, NTSB, EASA,
Traficom) exigent le CG à chaque phase, y compris pendant la mise en place à la porte,
mais ne proposent aucune méthode ; l'ordre d'embarquement des centres est dicté par la
vitesse de chute, pas par le CG.

**Groupes assis ensemble.** La leçon la plus nette. Les formulations par blocs énumérés
(Tajima et Misono 1999 : set packing, avions de 300 à 460 passagers en secondes ; Blom
2020 : 1250 sièges en secondes) ont des relaxations presque entières ; les boîtes
englobantes (Haque et Hamid 2023), big-M (Clausen 2010, Deplano 2019) et flots de
connexité (Vangerven 2022) plafonnent vite. Les inégalités qui relèvent la borne : coupes
de distance $x_{p,s} + x_{p',s'} \le 1$, bris de symétrie, voisinage relatif. Au-delà de
quelques dizaines de groupes, tout le monde passe aux métaheuristiques (tabou, GRASP,
ALNS), souvent pour amorcer le MIP.

**Équilibre en théorie et autres modes.** Placer des masses vers un CG cible est
fortement NP-difficile dès la dimension 1 (Amiouny 1992) ; l'ordre de retrait sous bande
de CG l'est aussi, même à masses égales (Fekete 2018, 2,7-approximation). Le stowage
maritime découpe en maître (zones, stabilité linéarisée) et slots (CP en moins de 1 s) ;
la génération de colonnes n'y apparaît que chez Roberti et Pacino 2018. Les charges par
essieu à chaque arc d'une tournée (Pollaris 2017) et la stabilité à chaque tâche de grue
(Sun 2021, Benders logique) sont les analogues de notre contrainte de largage.

**Méthodes exactes et hybrides.** Sur « affectation + sac à dos », l'exact passe par des
bornes lagrangiennes ou de Dantzig-Wolfe (Mazzola et Neebe 1986, Savelsbergh 1997,
Posta 2012) ; par Geoffrion, dualiser les bandes en gardant une affectation pure ne gagne
rien. Le Benders logique gagne 100 à 1000 fois quand le sous-problème est dur (Hooker
2007, Ciré 2016) et perd quand il est trivial. CP-SAT est compétitif sur le purement
entier (MiniZinc 2024) mais un ordre de grandeur derrière Gurobi pour la preuve sur
l'affectation à contraintes de côté (Johannesson 2026, Grus 2026). Symétries : 15 % sur
MIPLIB, bien plus avec des objets identiques (Pfetsch et Rehn 2019). Bet-and-run : temps
de preuve réduit de 17 à 28 % (Fischetti et Monaci 2014).

## 6. Recommandations, par ordre de priorité

1. Fixer le critère d'arrêt (écart 5 à 10 %, limite de temps) avant tout autre travail.
2. Cohésion par blocs énumérés plutôt que par boîte, encodage allégé, plus coupes de
   distance à la Vangerven.
3. Règles de terrain en coupes de dominance (plus lourds devant, masses décroissantes
   dans un groupe, passager de tandem le plus léger, ensembles bloquants FILO) et
   symétries exactes au forfait.
4. Séquence de largage : bornes constantes par état, étapes actives seulement, états
   transitoires « m paras debout à la porte ».
5. Essai CP-SAT calibré (hint complet, 8 workers, stratégie de décision sur les blocs),
   temps de preuve mesuré.
6. Agrégation par zone au forfait pour la phase 1 et la fiche mémo ; programmation
   dynamique exacte sur (places occupées, moment) en Rust pour la faisabilité et la marge.
7. Warm start, bet-and-run, fix-and-optimize via highspy ou le crate Rust.
8. Benders logique maître fenêtres / sous-problème places, seulement si 2 à 5 laissent des
   instances non prouvées.
9. Incertitude des masses : marge statistique (AC 120-27F appendice D) et Monte Carlo sur
   la solution retenue, plutôt que programmation stochastique.

## 7. Fichiers produits

| Fichier | Contenu |
|---|---|
| `doc_placement_milp.html`, `output/Placement_MILP_modele_et_acceleration.pdf` | le modèle contrainte par contrainte, ce que fait HiGHS, revue des accélérations, recommandation |
| `bench_fenetres.py`, `output/bench_fenetres.log` | formulation « fenêtres candidates » contre la formulation boîte |
| `doc_revue_litterature.html`, `output/Revue_litterature_placement_equilibre.pdf` | revue de littérature en cinq familles, synthèse transversale, neuf transferts, sources |
| `RESUME_RECHERCHES.md` | ce résumé |

Les PDF se regénèrent avec Chrome headless (commande dans le README) ; MathJax et les
polices sont chargés depuis le réseau.

## 8. Réserves

Plusieurs éditeurs refusent l'accès automatisé : une partie des références n'a été lue
qu'en résumé (marquées « nv » dans le PDF de revue, listées en section 9). La carte EASA
A6 sur le parachutage n'a pas pu être lue. Le corridor de moments, la programmation
dynamique sur les places et les tailles d'états sont des raisonnements propres, pas des
résultats publiés. Les deux articles Zhao 2026 et Bergman 2019 ne sont connus que par
leur résumé.
