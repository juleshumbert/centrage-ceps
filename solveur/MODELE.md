# Modélisation en programme linéaire en nombres entiers du placement des paras

Objectif de cette version : **le plus de marge vers la limite arrière au décollage**,
tout en **garantissant une marge avant minimale à chaque étape du largage** (en
particulier dès que le premier groupe est sorti), puis, à marge arrière quasi égale,
le placement le plus réaliste (groupes compacts, premiers sortants près de la porte,
tandems côte à côte).

## Ensembles

| symbole | signification |
|---|---|
| P = {1..N} | paras (N ≤ nombre de places) |
| S | places fixes, chacune avec un bras x_s et une position latérale y_s |
| G | groupes (ensembles de paras d'au moins deux membres) |
| T | tandems, couples (porteur p, passager q) |
| K = {0..N−1} | étapes : k = 0 au décollage, k ≥ 1 après la sortie des k premiers paras de la séquence de sortie |
| R_k ⊆ P | paras encore à bord à l'étape k (R_0 = P) |

La séquence de sortie ordonne les paras par leur rang `sortie` (ex aequo dans un
groupe, gardés dans l'ordre du manifeste ; les paras sans rang sortent en dernier).

## Données

| symbole | signification |
|---|---|
| m_i | masse du para i |
| W_0, M_0 | masse et moment de l'avion sans paras (vide + pilote + carburant) |
| W_k = W_0 + Σ_{i∈R_k} m_i | masse à l'étape k, **constante** (ne dépend pas du placement) |
| L(W), U(W) | limite avant et limite arrière du CG à la masse W, lignes brisées interpolées ; on note L_k = L(W_k), U_k = U(W_k) |
| MTOW | masse maximale au décollage |
| μ_av | marge avant minimale exigée à toutes les étapes (paramètre, ex. 0,5 in) |
| d_s | rang de la place s par distance à la porte (1 = la plus proche) |
| r_i | rang de sortie cible du para i (rang moyen en cas d'ex aequo), défini seulement si i a un rang `sortie` |
| devant(s) | place juste devant s, même côté ; non définie pour le siège copilote et les places de tête de rangée |
| pas | pas entre deux places (normalisation des boîtes, 25 in) |
| w_g, w_s, λ | poids du réalisme : boîtes des groupes, écart de sortie, composante latérale |

Le CG à l'étape k vaut (M_0 + Σ_{i∈R_k} m_i X_i) / W_k, où X_i est le bras du para i.
Comme W_k est constant, **toute condition sur le CG est linéaire dans le moment**.

## Variables

| variable | type | signification |
|---|---|---|
| z_{is} | binaire | 1 si le para i occupe la place s |
| X_i = Σ_s x_s z_{is} | linéaire en z | bras du para i |
| μ_ar ≥ 0 | continue | marge arrière au décollage (à maximiser) |
| Xmin_g, Xmax_g, Ymin_g, Ymax_g | continues | boîte englobante du groupe g |

Nombre de binaires : N × |S| ≤ 400.

## Contraintes

**Affectation**

    (1)  Σ_s z_{is} = 1            pour tout i
    (2)  Σ_i z_{is} ≤ 1            pour tout s

**Masse**

    (3)  W_0 + Σ_i m_i ≤ MTOW      (vérifiée avant de lancer le solveur)

**Centrage au décollage** (k = 0, masse W_0' = W_0 + Σ_i m_i)

    (4)  Σ_i m_i X_i ≤ (U_0 − μ_ar) · W_0' − M_0        marge arrière μ_ar
    (5)  Σ_i m_i X_i ≥ (L_0 + μ_av) · W_0' − M_0        marge avant au moins μ_av

**Centrage pendant le largage** (k = 1..N−1)

    (6)  Σ_{i∈R_k} m_i X_i ≥ (L_k + μ_av) · W_k − M_0    pas trop centré avant une fois les premiers sortis
    (7)  Σ_{i∈R_k} m_i X_i ≤ U_k · W_k − M_0             toujours dans l'enveloppe côté arrière

La contrainte (6) à k = taille du premier groupe est exactement « quand le premier
groupe part, on n'est pas trop centré avant » ; on l'impose à toutes les étapes.
Hypothèse : les paras encore à bord restent à leur place.

**Tandems** (porteur p, passager q)

    (8)  z_{q, devant(s)} = z_{p,s}      pour toute place s ayant une place devant
    (9)  z_{p,s} = 0                     si s n'a pas de place devant, ou s est le siège copilote
    (10) z_{q,s} = 0                     si s n'est la place « devant » d'aucune place

Fixer le porteur fixe le passager ; les deux sont sur un côté, jamais au centre ni
en siège copilote.

**Boîtes des groupes** (pour tout g, tout i ∈ g, toute place s)

    (11) Xmin_g ≤ X_i ≤ Xmax_g,   Ymin_g ≤ Y_i ≤ Ymax_g
    (12) Xmax_g ≥ x_min + (x_s − x_min) z_{is}     forme désagrégée, plus forte en relaxation continue
         Xmin_g ≤ x_max − (x_max − x_s) z_{is}     (idem en y)
    (13) Xmax_g − Xmin_g ≥ ΔX(|g|),  Ymax_g − Ymin_g ≥ ΔY(|g|)

ΔX(n) est la plus petite étendue en x pouvant contenir n places (fenêtre glissante
sur les places triées) : borne inférieure valide qui relève la relaxation continue.

**Groupes ordonnés** (option) : pour g sortant avant h,

    (14) Xmin_g ≥ Xmax_h        g est entièrement en arrière de h

## Objectifs, en deux phases

**Phase 1 : marge arrière maximale.**

    max μ_ar   sous (1)–(14)

Si le problème est infaisable, aucun placement ne respecte μ_av à toutes les étapes ;
on relance avec μ_av relâché (dichotomie) pour dire de combien.

**Phase 2 : réalisme, à marge arrière quasi égale.** Avec μ_ar* la valeur de la
phase 1 et une tolérance τ (ex. 0,25 in) :

    min  w_g Σ_g [ (Xmax_g − Xmin_g) + λ (Ymax_g − Ymin_g) ] / pas
       + w_s Σ_i Σ_s |d_s − r_i| z_{is}
    sous (1)–(14) et  μ_ar ≥ μ_ar* − τ

Le premier terme rend chaque groupe compact (boîte englobante), le second met le
i-ème à sortir sur la i-ème place la plus proche de la porte. Le tout est linéaire.

## Ce qui change par rapport au modèle précédent

L'ancien modèle maximisait une marge symétrique (min des marges avant et arrière,
au décollage et à chaque étape). Ici la marge arrière est **maximisée** au décollage
et la marge avant est une **contrainte** (μ_av) valable à chaque étape, ce qui
correspond à la demande : CG le plus avant possible au décollage, sans risque de
passer devant la limite avant après la sortie des premiers groupes. Le compromis
avec le réalisme est réglé par la tolérance τ.

## Taille et résolution

N × |S| binaires (≤ 400), 2N contraintes de centrage, 4 |S| contraintes par membre de
groupe, quelques égalités par tandem. Résolu par HiGHS (branch-and-cut) embarqué dans
le binaire C++ `solveur/build/placement`. Les phases prennent de quelques dixièmes de
seconde à quelques secondes ; au-delà d'une dizaine de paras sans groupes ordonnés ni
tandems, la phase 2 peut atteindre la limite de temps avec une solution réalisable
et un écart borné.
