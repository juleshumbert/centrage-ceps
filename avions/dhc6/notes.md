# DHC-6 Twin Otter Series 300 : notes masse et centrage (recherche documentaire du 2026-09-05)

Dossier : `scratchpad/poh/dhc6/`. Toutes les valeurs ci-dessous sont en livres (lb) et pouces (in) sauf mention contraire.
Convention de fiabilité : **[OFF]** = lu dans un document officiel (TCDS FAA, fiche constructeur Viking), **[FSI]** = manuel de formation FlightSafety (reprend l'AFM mais n'est pas l'AFM), **[TIERS]** = site ou manuel tiers (simulateur, forum), **[DERIVE]** = calculé par moi à partir de valeurs officielles.

Remarque sur la demande initiale « DHC5 » : l'avion de largage courant est le DHC-6 Twin Otter ; le DHC-5 Buffalo est traité brièvement en fin de document.

## 1. Sources

| Fichier local | Origine (URL) | Nature | Pages utiles |
|---|---|---|---|
| `FAA_TCDS_A9EA_paraclete_1.pdf` (20 p) | https://paracleteaviation.com/wp-content/uploads/2017/10/Twin-Otter-Type-Data-Sheet.pdf | TCDS FAA A9EA Rev. 15 (miroir sur le site d'un centre de parachutisme, contenu officiel FAA) [OFF] | p. 12 (enveloppe CG, masses, sièges, bagages), p. 13 (carburant, huile), p. 18 (datum, MAC, mise à niveau), p. 20 (notes carburant inutilisable, huile) |
| `FAA_TCDS_A9EA_paraclete_2.pdf` (20 p) | https://paracleteaviation.com/wp-content/uploads/2017/10/Twin-Otter-DHC-6.pdf | même TCDS Rev. 15, autre export | idem |
| `FAA_TCDS_A9EA.txt` | extraction pdftotext du précédent | texte | |
| `FlightSafety_DHC6_PTM_full.pdf` (654 p, 223 Mo) | https://archive.org/download/dhc-6-ptm/DHC-6%20Pilot%20Training%20Materials/DHC-6%20PTM.pdf | FlightSafety Twin Otter Pilot Training Manual Series 100/200/300, Rev. 5.0 nov. 2010 [FSI] | p. 30 (structure, STA 60), p. 37 (Fig. 1-10 seating), p. 39 (Fig. 1-12 parachute seats), p. 40 (Fig. 1-15 doors), p. 45 (parachute door, Supplement 23 AFM), p. 53 (Fig. 1-38 dimensions), p. 405 (STA 281/301,5/321,6/332), p. 463 (15 000 lb bombardier d'eau), p. 600 (14 000 lb EO 69077) |
| `FlightSafety_DHC6_Client_Guide.pdf` (86 p) | https://ia803205.us.archive.org/28/items/dhc-6-ptm/DHC-6%20Pilot%20Training%20Materials/DHC-6%20Pilot%20Initial%20and%20Recurrent%20Client%20Guide.pdf | FlightSafety Client Guide Rev. 2.0 [FSI] | p. 1-1 (limites CG, MAC 78,0 in, formulaire à trous), p. 2-2 (feuille de chargement, formule d'index) |
| `Viking_Series400_TechSpecs_2018.pdf` (15 p) | https://www.vikingair.com/sites/default/files/Viking-Twin-Otter-Series-400-Technical-Specifications-R-01-2018.pdf | Fiche technique constructeur Series 400 [OFF, mais Series 400] | p. 1 (dimensions, cabine, portes, masses) |
| `Viking_Series400_Brochure.pdf` (16 p) | https://www.aerocontact.com/public/img/aviaexpo/produits/catalogues/17/Twin-Otter-Series-400-Multi-Page-Brochure-low-res.pdf | Brochure Viking Series 400 [OFF, Series 400] | p. 3 (specs, 3 vues cotées), p. 11 (interiors) |
| `Viking_400S_Brochure.pdf` (16 p) | https://altitudesystemsco.com/images/downloads/400S-Twin-Otter-Brochure.pdf | Brochure Viking 400S [OFF, Series 400] | p. 2 (specs) |
| `Viking_SpecialMissions_Parachute.pdf` (1 p) | https://altitudesystemsco.com/images/downloads/Parachute.pdf | Fiche Viking « Special Missions : Parachute & Aerial Drop » [OFF, Series 400] | p. 1 (porte roll-up ou bi-fold, porte arrière cabine à STN 332, banquettes) |
| `MSFS2024_DHC6_AOM.pdf` (57 p) | https://flightsimulator.azureedge.net/wp-content/uploads/2024/11/MSFS2024_DHC-6_TWIN_OTTER_AOM.pdf | Aircraft Operating Manual du simulateur Microsoft (Asobo) [TIERS] | p. 44 (enveloppe Series 300 redessinée, limitations porte air-operable) |
| `Aerosoft_TwinOtter_MSFS_manual.pdf` (161 p) | https://manuals.aerosoft.com/files/Manual_Aerosoft-Aircraft-Twin-Otter_MSFS_eng.pdf | Manuel Aerosoft [TIERS] | description conversion parachutisme (porte roll-up sur rails plastiques) |
| `tcds_p12-12.png`, `msfs_p44-44.png`, `ptm_p37/39/40/45/53-*.png` | rasterisations pdftoppm | figures lues | |

Non obtenus (introuvables en téléchargement libre) : AFM PSM 1-63-1A complet (vendu en réimpression : Essco, PilotMall, flightmanuals.com ; un exemplaire sur Scribd, non téléchargeable : https://www.scribd.com/document/817757783/), Weight and Balance Handbook PSM 1-63-8, Maintenance Manual PSM 1-63-2 chap. 6/8 (pdfcoffee renvoie une page HTML, Avialogs payant), TCDS Transport Canada A-82 (pas de PDF direct trouvé ; le TCDS FAA A9EA reprend les mêmes valeurs et cite Viking Air comme détenteur du TC).

## 2. Datum et MAC

| Donnée | Valeur | Source |
|---|---|---|
| Datum (Station 0) | 109,32 in **en avant** d'un repère de gabarit (jig point) matérialisé par une plaque sur la cloison entre poste de pilotage et cabine (donc cloison cockpit/cabine à FS ≈ 109,3) | TCDS A9EA p. 18 [OFF] |
| Datum, formulation Maintenance Manual | « Station 0 is 60.00 inches forward of the flight compartment front bulkhead » ; le PTM confirme que la structure semi-monocoque commence à Station 60 (en avant : nez bagages balsa/fibre) | résumé pdfcoffee du PSM 1-63-2 chap. 6 [TIERS], PTM p. 30 [FSI] |
| Longueur MAC | 78 in (1,921 m) | TCDS p. 18 [OFF], Client Guide p. 1-1 [FSI] |
| LEMAC | Station 188,24 in | TCDS p. 18 [OFF] |
| TEMAC | 266,24 in | [DERIVE] 188,24 + 78 |
| Formule %MAC | %MAC = (bras − 188,24) / 78 × 100 | [DERIVE], vérifiée : 20 % = 203,84 ; 25 % = 207,74 ; 32 % = 213,20 ; 36 % = 216,32 (valeurs exactement celles du TCDS) |
| Mise à niveau | rails de plancher cabine (latéral et longitudinal) ; plancher cabine à 15 in sous la ligne d'eau 0 | TCDS p. 18 [OFF] |
| Bras de référence de l'index de la feuille de chargement | 210 in : INDEX = 10 + Poids × (bras − 210) / 10 000 | Client Guide p. 2-2 [FSI] |

## 3. Masses limites

| Donnée | Valeur | Source |
|---|---|---|
| MTOW (landplane, floatplane, skiplane) | 12 500 lb | TCDS p. 12 [OFF] |
| Max landing weight landplane et wheel-ski | 12 300 lb | TCDS p. 12 [OFF] |
| Max landing weight floatplane | 12 500 lb | TCDS p. 12 [OFF] |
| Max zero fuel weight | aucune valeur dans le TCDS (pas de MZFW publiée) ; à vérifier dans l'AFM | TCDS [OFF] |
| Plage de CG à vide | « None » (aucune restriction spécifique) | TCDS p. 12 [OFF] |
| Masse à vide typique | Series 400 équipé : 7 445 lb (3 377 kg). Series 300 : aucune valeur officielle trouvée ; ordre de grandeur usuel 7 000 à 7 500 lb selon équipement [TIERS, non sourcé, à confirmer par la pesée de l'avion] | Viking TechSpecs p. 1 [OFF] |
| Carburant inutilisable inclus dans la masse à vide | 3,5 US gal (3,0 Imp gal) pour tous modèles sauf Model 1 | TCDS p. 20 note 1(b) [OFF] |
| Huile incluse dans la masse à vide | 54 lb à +177,0 in (total circuit + réservoirs) | TCDS p. 20 note 1(c) [OFF] |
| Masse max au-delà de 12 500 lb | 14 000 lb landplane (Engineering Order 69077, supplément AFM, vols non commerciaux avec accord autorité) ; 15 000 lb bombardier d'eau sur flotteurs (Supplement 28) | PTM p. 600 et p. 463 [FSI] |
| Sièges | 22 max Series 300 (dont 2 à Stn +95,0 in), limité par l'arrangement approuvé (W&B Handbook PSM 1-63-8) | TCDS p. 12 [OFF] |
| Équipage minimal | 1 pilote à +95,0 in | TCDS p. 12 [OFF] |

## 4. Stations et bras

| Poste | Bras (in) | Limite | Source |
|---|---|---|---|
| Sièges pilotes (2) | +95,0 | | TCDS p. 12 [OFF] |
| Soute avant nez court | +41,0 | 200 lb | TCDS p. 12 [OFF] |
| Soute avant nez long (Mod 6/1077, standard sur Series 300 sauf flotteurs) | +25,0 | 300 lb (radar inclus) | TCDS p. 12 [OFF], PTM p. 30 [FSI] |
| Soute arrière | +354,0 | 500 lb | TCDS p. 12 [OFF] |
| Étagère d'extension arrière | +391,0 | 150 lb (arrière + extension ≤ 500 lb) | TCDS p. 12 [OFF] |
| Réservoir carburant avant | +162,5 | 181 US gal utilisables | TCDS p. 13 [OFF] |
| Réservoir carburant arrière | +240,0 | 197 US gal utilisables | TCDS p. 13 [OFF] |
| Huile (2 × 1,5 US gal) | +177,0 | 22 lb utilisable, 54 lb total inclus dans masse à vide | TCDS p. 13 et p. 20 [OFF] |
| Cloison poste/cabine (jig point) | ≈ 109,3 | | TCDS p. 18 [OFF] (dérivé de la définition du datum) |
| Début structure semi-monocoque / cloison avant du poste | 60,0 | | PTM p. 30 [FSI] |
| LEMAC (aile rectangulaire à corde constante, donc bord d'attaque aile ≈ LEMAC sur toute l'envergure) | 188,24 | | TCDS p. 18 [OFF] ; corde constante : Viking TechSpecs p. 3 [OFF] |
| Porte arrière de cabine (accès soute arrière) | STN 332 | | Viking Parachute sheet p. 1 [OFF, Series 400] ; PTM p. 405 cite aussi STA 281,0 / 301,5 / 321,6 / 332,0 pour des équipements de climatisation en zone arrière [FSI] |
| Rangées de sièges passagers (rows 1 à 7) | **non trouvé** : les bras par rangée sont dans le W&B Handbook PSM 1-63-8, introuvable en ligne | Client Guide p. 2-2 (feuille de charge à 7 rangées + nose, crew, baggage, shelf, sans bras chiffrés) [FSI] |
| Train principal, train avant (FS) | non trouvé (seulement l'empattement 14 ft 10,5 in = 178,5 in, voir § 7) | PTM p. 53 [FSI] |

## 5. Carburant

| Donnée | Valeur | Source |
|---|---|---|
| Capacité utilisable Series 300 | avant 181 US gal (151 Imp) à +162,5 in ; arrière 197 US gal (164 Imp) à +240,0 in ; total 378 US gal (315 Imp) | TCDS p. 13 [OFF] |
| Capacité Series 400 | 374,5 US gal (1 419 l) + option long range 89 US gal (337 l) ; brochure : 378 US gal + 89 | Viking TechSpecs p. 1, Brochure p. 3 [OFF, Series 400] |
| Emplacement | réservoirs souples sous le plancher cabine, groupe avant et groupe arrière (« Nine Tanks » sur la brochure Viking) | Brochure p. 5 [OFF], PTM [FSI] |
| Densité | aucune densité dans les documents obtenus ; hypothèse usuelle Jet A-1 6,7 lb/US gal (0,80 kg/l) [TIERS, standard] ; plein 378 US gal ≈ 2 533 lb à 6,7 lb/gal [DERIVE] | |
| Table de chargement carburant (poids vs bras) | non trouvée (AFM section W&B / PSM 1-63-8). Les deux groupes ont chacun un bras fixe déclaré au TCDS, ce qui permet un calcul linéaire par groupe | |

## 6. Enveloppe CG (centrogramme)

Source principale : TCDS A9EA Rev. 15 p. 12, figure « C.G. range (Landing gear fixed) », Series 300 landplane et wheel-skiplane [OFF]. Lecture faite sur le texte extrait et la rasterisation `tcds_p12-12.png` (200 dpi) : les valeurs des sommets sont imprimées en clair sur la figure (poids 9 000 / 11 000 / 11 600 / 12 300 / 12 500 ; bras 203,84 / 207,74 / 216,32), il n'y a pas d'incertitude de lecture graphique. Le bas du graphe est à 9 000 lb : c'est le cadre du dessin, pas une limite déclarée ; le texte du TCDS et le Client Guide disent « 36 % MAC at all weights » pour la limite arrière ; l'AOM MSFS [TIERS] redessine les mêmes segments verticaux jusqu'à 6 000 lb. Pour l'outil d'optimisation : prolonger les limites 20 % et 36 % verticalement sous 9 000 lb, avec ce caveat.

### 6.1 Décollage, landplane et wheel-skiplane (Series 300)

| Sommet | Poids (lb) | Bras (in) | %MAC |
|---|---|---|---|
| A (bas avant) | 9 000 | 203,84 | 20 |
| B (coude avant) | 11 600 | 203,84 | 20 |
| C (avant à MTOW) | 12 500 | 207,74 | 25 |
| D (arrière à MTOW) | 12 500 | 216,32 | 36 |
| E (bas arrière) | 9 000 | 216,32 | 36 |

Entre B et C la limite avant est linéaire (bras = 203,84 + 3,90 × (W − 11 600) / 900).

### 6.2 Atterrissage, landplane et wheel-skiplane (Series 300)

| Sommet | Poids (lb) | Bras (in) | %MAC |
|---|---|---|---|
| A | 9 000 | 203,84 | 20 |
| B' | 11 000 | 203,84 | 20 |
| C' | 12 300 | 207,74 | 25 |
| D' | 12 300 | 216,32 | 36 |
| E | 9 000 | 216,32 | 36 |

### 6.3 Floatplane (Series 300)

Limite avant 25 % MAC (STA 207,74) et limite arrière 32 % MAC (STA 213,20) à tous les poids jusqu'à 12 500 lb (rectangle). Bombardier d'eau Series 300 (flotteurs CAP 12000A/B) : 12 500 lb, 25 à 32 % MAC. TCDS p. 12 et p. 19 [OFF].

### 6.4 Configuration parachutage

- Aucune enveloppe spécifique « parachutage » ni restriction « aft CG with cargo door removed » trouvée dans les documents obtenus. Le PTM p. 45 [FSI] indique que la porte parachutiste (bi-fold, ouverture vers l'intérieur, remplaçant les deux portes gauche) est couverte par le **Supplement 23 de l'AFM** (« air operable door ») ; c'est là que se trouveraient d'éventuelles limitations de masse et centrage propres au largage. Non obtenu.
- L'AOM MSFS p. 44 [TIERS] reproduit des limitations « air operable door » : 140 KIAS max porte ouverte, porte fermée au décollage, à l'atterrissage et en monomoteur, largage à volets 20° et 70 KIAS, occupants limités à l'équipage et aux paras largués. À recouper avec le Supplement 23 réel.
- Viking (Series 400) propose porte roll-up ou bi-fold « air operable », banquettes latérales murales, porte arrière cabine à STN 332 [OFF].
- Description tierce (Aerosoft p. 27 et 28) : portes cargo démontées, sièges déposés, porte roll-up transparente sur rails plastiques, barre de maintien dans le cadre, paras assis au sol dos à la route [TIERS].

## 7. Dimensions cabine, portes, extérieur

| Donnée | Valeur | Source |
|---|---|---|
| Longueur cabine | 18 ft 5 in = 221 in (5,61 m) | Viking TechSpecs p. 1, Brochure p. 3 [OFF, Series 400 ; fuselage identique au 300] |
| Hauteur cabine | 4 ft 11 in = 59 in (1,50 m) | idem |
| Largeur cabine (max) | 5 ft 9 in = 69 in (1,75 m) ; largeur au plancher : non trouvée | idem |
| Volume utile cabine | 384 cu ft (10,87 m³) | idem |
| Portes cabine gauche (double : airstair avant + cargo arrière) | ouverture combinée 50 × 56 in (1,27 × 1,42 m), largeur × hauteur | Viking TechSpecs p. 1, Brochure p. 3 [OFF] |
| Porte cabine droite | 30 × 45,5 in (0,76 × 1,16 m) | idem |
| Porte de largage roll-up (conversion parachutisme) | dimensions non trouvées dans une source officielle ; elle occupe le cadre des deux portes gauche (nominal 50 × 56 in). Un fil Dropzone.com sur le sujet existe mais redirige vers un domaine non fiable, non consulté | Aerosoft [TIERS], PTM p. 45 [FSI] |
| Position longitudinale de la cabine | cloison avant à FS ≈ 109,3 (jig point), cloison arrière / porte arrière à STN 332 ; 332 − 109,3 = 222,7 in, cohérent avec la longueur cabine de 221 in | [DERIVE] à partir de TCDS p. 18 et Viking Parachute sheet |
| Position des portes gauche (FS) | non trouvée ; sur la Fig. 1-15 du PTM (p. 40) la double porte gauche est immédiatement en arrière de l'aile, derrière le bord de fuite (FS ≈ 266) ; à mesurer sur plan | PTM p. 40 [FSI] |
| Envergure | 65 ft 0 in (19,81 m) | Viking, PTM Fig. 1-38 [OFF/FSI] |
| Longueur hors tout | 51 ft 9 in (15,77 m) | idem |
| Hauteur hors tout | 19 ft 6 in (5,94 m) au poids normal | idem |
| Empattement | 14 ft 10,5 in (4,53 m) = 178,5 in | PTM Fig. 1-38 p. 53 [FSI] |
| Voie | 12 ft 2 in (3,70 m) | idem |
| Envergure empennage horizontal | 20 ft 8 in (6,29 m) | idem |
| Hauteur fuselage / dessus d'aile | 9 ft 8 in (2,94 m) | idem |
| Diamètre hélice / garde au sol / garde fuselage | 8 ft 6 in (2,59 m) / 60 in (1,52 m) / 25,6 in (0,65 m) | idem |
| Cote « 33,8 in (0,85 m) » sur la Fig. 1-38 | placée au bas du fuselage près du train avant, vraisemblablement hauteur du seuil ou du plancher au-dessus du sol ; interprétation incertaine | PTM p. 53 [FSI], lecture d'image |
| Cote « 9 ft 3 in » (vue de face, à droite) | probablement hauteur du bout d'aile ; interprétation incertaine | idem |
| Aile | plan rectangulaire à corde constante (78 in = MAC), bord d'attaque à FS 188,24 | Viking TechSpecs p. 3 [OFF], TCDS p. 18 [OFF] |
| Arrangement sièges commuter | 19/20 : 6 sièges doubles à gauche + 1 simple arrière, 5 simples à droite + 3 optionnels devant la soute arrière, 7 rangées ; alternative utility 13/14 | PTM Fig. 1-10 p. 37 [FSI] ; Fig. 1-12 p. 39 « parachute seats » (non lue en détail) |
| Charges de plancher | non trouvées (rubrique à trous dans le Client Guide p. 1-1) | |

## 8. Points ouverts et incertitudes

1. **Bras des rangées de sièges / du plancher cabine par station** : absents de tous les documents libres ; il faut le W&B Handbook PSM 1-63-8 ou le devis de masse de l'avion réel (chaque avion a sa fiche de pesée avec bras par rangée). Pour un schéma à l'échelle, l'ensemble « cloison FS 109,3 ; LEMAC 188,24 ; TE aile 266,24 ; STN 332 » suffit à positionner la cabine ; les bras des paras assis au sol se déduisent des FS.
2. **Supplement 23 de l'AFM (air operable door)** : non obtenu ; c'est le document de référence pour d'éventuelles restrictions CG en largage.
3. **MZFW** : non publiée au TCDS ; l'AFM Series 300 n'en déclare pas à ma connaissance (à vérifier).
4. **Masse à vide Series 300** : aucune valeur officielle ; prendre la pesée de l'avion.
5. **Densité carburant** utilisée par les tables AFM : non lue.
6. **Position FS du train principal et du train avant** : non trouvées (empattement 178,5 in connu).
7. **Dimensions exactes de la porte roll-up** : non sourcées officiellement.
8. **TCDS Transport Canada A-82** : non téléchargé (aucun PDF public trouvé) ; le TCDS FAA A9EA est le miroir de contenu et cite Viking Air comme détenteur du TC.
9. Les dimensions de cabine et de portes proviennent de la documentation Series 400 ; Viking indique que dimensions et structure primaire n'ont pas changé par rapport au 300 (TechSpecs p. 1), mais le nez long / court et l'aménagement peuvent différer.
10. Le TCDS Rev. 15 date de 2013 environ ; une révision plus récente peut exister sur drs.faa.gov (mêmes valeurs attendues pour le Series 300).

## 9. DHC-5 Buffalo (recherche brève)

- **Aucun flight manual DHC-5 en téléchargement libre.** Les manuels existent en vente : « De Havilland Canada DHC-5 Buffalo (CV-7, C-8) » sur flight-manuals-online.com, et « Aircraft Operating Instructions EO 05-200A-1 (1967, rev. 1971, 283 p) » sur aircraft-reports.com ; aussi « Buffalo Model DHC-5 Flight Manual » et « Preliminary Airplane Flight Manual » référencés sur Google Books sans aperçu.
- Seule source gratuite obtenue : brochure constructeur « DHC-5 Buffalo & General Electric T64 » (archive.org, item TNM_De_Havilland_Canada_DHC-5_Buffalo_and_General_E_20171025_0093), enregistrée dans `dhc5/DHC5_Buffalo_brochure_archiveorg.pdf` (52 pages, vérifiée avec pdfinfo, texte extrait dans `dhc5/DHC5_Buffalo_brochure.txt`). Valeurs lues [OFF, brochure] (p. 4 pour les masses et la cabine, p. 16 pour la plage de CG, p. 14 pour la mention d'une plage « wide » adaptée au largage) : masse de décollage de conception 41 000 lb, masse d'atterrissage 39 100 lb, masse à vide opérationnelle 24 220 lb, charge utile max 12 780 lb, carburant interne max 13 556 lb, « C of G range 18.5 in » (sans %MAC ni longueur de MAC), cabine 31 ft 5 in de long (jusqu'au bord avant de la rampe), 7 ft 9 in au plancher, 8 ft 9 in max, hauteur 6 ft 6 in (avant du longeron arrière) et 6 ft 10 in (arrière), porte de chargement arrière 92 in de large, hauteur hors tout 28 ft 8 in, voie 30 ft 6 in.
- **Aucune enveloppe de centrage (sommets poids/bras) trouvée pour le DHC-5.**
