# Pilatus PC-6/B2-H2 et PC-6/B2-H4 Turbo Porter · notes masse et centrage

Dossier : `scratchpad/poh/pc6/`. Recherche du 2026-09-05. Toutes les valeurs ci-dessous sont
recopiées telles quelles des documents cités ; les valeurs *dérivées* (calculées par moi) sont
marquées **[dérivé]**, les valeurs de sites tiers non officiels sont marquées **[tiers]**.

## 1. Sources

### Officielles (téléchargées, PDF valides, vérifiés avec pdfinfo)

| Réf. | Fichier local | Document | URL d'origine | Pages |
|---|---|---|---|---|
| S1 | `TCDS_FOCA_F56-10_PC-6_Issue7.pdf` (+ `.txt`) | Fiche de navigabilité (TCDS) OFAC/BAZL **F 56-10, Issue 7, 20 sept. 2006**, tous modèles PC-6 (piston et turbine, H2 et H4). C'est le TCDS de l'autorité d'origine ; le PIM (S2) y renvoie explicitement. Il n'existe pas de TCDS « EASA.A.078 » pour le PC-6 : la page EASA du constructeur ne liste que PC-12 (A.089) et PC-24 (A.594). | https://www.bazl.admin.ch/dam/en/sd-web/MhHgrj9FZ6uJ/pc-6_tcds_f56-107.pdf | 27 |
| S2 | `PC-6_PIM_01820_R08_Pilatus.pdf` (+ `.txt`) | **Pilot's Information Manual = copie « for general and familiarization purposes only » de l'Airplane Flight Manual PC-6/B2-H4, Report No. 1820, Revision 8, avril 2017 (EASA approved)**. Sections 1 à 4 complètes. L'appendice « Actual Weight and Balance » (procédure de chargement, masse à vide, abaques) n'est PAS inclus (il est propre à chaque avion). | Original https://www.pilatus-aircraft.com/data/tech_pub/PC-6%20PIM%2001820%20R08.pdf (403 aujourd'hui) ; copie Wayback utilisée : https://web.archive.org/web/20240508214458/https://www.pilatus-aircraft.com/data/tech_pub/PC-6%20PIM%2001820%20R08.pdf | 80 |
| S3 | `Pilatus_PC-6_Brochure_2019.pdf` (+ `.txt`, rasterisations `png/brochure_p10..16.png`) | Brochure constructeur « PC-6 Turbo Porter », pages doubles. | https://web.archive.org/web/20190224223425/https://www.pilatus-aircraft.com/data/document/Pilatus-Aircraft-Ltd-PC-6-Brochure.pdf | 18 (36 pages imprimées) |
| S4 | `Pilatus_PC-6_Factsheet_2019.pdf` (+ `png/factsheet2019-1/2.png`) | Fiche technique constructeur STA0515E (B2-H4), avec trois-vues cotée. | https://web.archive.org/web/20190224210125/https://www.pilatus-aircraft.com/data/document/Pilatus-Aircraft-Ltd-PC-6-Factsheet.pdf | 2 |
| S5 | `Pilatus_PC-6_FactSheet_French_2015.pdf` | Fiche technique constructeur en français. | https://web.archive.org/web/20150513092510/http://www.pilatus-aircraft.com/00-def/main/scripts/ckfinder/userfiles/files/Downloads/Sales%20PC-6/PC-6%20Fact%20Sheet%20French.pdf | 2 |
| S6 | `FFP_Directive_Technique_33_PC-6.pdf` (+ `FFP_DT033.txt`) | Fédération Française de Parachutisme, Directive technique n° 33 du 5 juillet 2012 « Largage à bord de Pilatus PC 6 tous types (B2H2 et B2H4) ». | https://www.ffp.asso.fr/wp-content/uploads/2012/07/Directive_Technique_33.pdf | 2 |
| S7 | `BEA_BEA-PC6_PC-6_B2-H4_rapport.pdf` (+ `.txt`) | Rapport BEA, accident PC-6/B2-H4 BEA-PC6 (vol cargo, Maripasoula) ; cite des limitations du manuel de vol. | https://bea.aero/fileadmin/user_upload/BEA-PC6.pdf | 9 |
| S8 | `PC-6_MMOP_Pilatus.pdf` (+ `.txt`) | Pilatus « PC-6 Series Master Maintenance and Operating Procedures Manual », Doc. No. 02399. Aucune donnée de centrage. | Wayback de https://www.pilatus-aircraft.com/data/tech_pub/5979ea7077e2d_Pilatus-Aircraft-Ltd-PC-6-MMOP.pdf | 30 |
| S9 | `Pilatus_PC-6_SN935_Para_for_sale_2006.pdf`, `Pilatus_PC-6_SN700_Para_for_sale_2006.pdf` | Fiches de vente Pilatus (2004) de deux B2-H4 « Paraequipment ». Aucune masse à vide indiquée. | Wayback de pilatus-aircraft.com/media/ | 2 + 1 |

`PC-6_PIM_truncated_2021capture.pdf` : capture Wayback d'avril 2021 tronquée à 1 MiB, conservée
uniquement pour mémoire (ne pas utiliser).

### Non obtenues

- **TCDS FAA 7A15** : rgl.faa.gov ne résout plus, drs.faa.gov n'est pas indexé ; aucun miroir PDF
  trouvé. Le TCDS FOCA F 56-10 est de toute façon le document source (le PC-6 est certifié CAR 3
  par l'OFAC ; la FAA a validé).
- **AFM PC-6/B2-H2** : aucun PDF public trouvé. Le document Scribd « Pilatus PC-6 Porter Flight
  Manual » (176 p., https://www.scribd.com/document/694285492/) n'est pas accessible sans compte et
  semble concerner un B1-H2 d'après l'extrait de recherche.
- **Supplément AFM 1824** « Operation with Cabin Doors Removed and Sliding Door/Hatch Open »
  (configuration parachutage) : contenu non public.
- **Appendice Weight & Balance de l'AFM 1820** (masse à vide, bras détaillés, abaque de
  chargement) : non inclus dans le PIM.

### Tiers (non officiels, à ne pas utiliser sans vérification)

- Wikipedia (PC-6/B2-H4, d'après Jane's 1993-94) : longueur 11 m, envergure 15.87 m, hauteur
  3.2 m, surface 30.15 m², masse à vide 1270 kg, MTOW 2800 kg, charge 1130 kg / 10 places.
- Extrait de recherche (choosemyplane.com / tsunamiair.com, pages en 403 au fetch) : cabine
  longueur env. 2.29 m (7.5 ft), largeur 1.16 m, hauteur 1.28 m. **[tiers, non vérifié]**
- jecobra.com : cabine « 5'2" x 4'3" x 3'4", 124 cu ft », BOW 3280 lb, MZFW 5291 lb : valeurs
  incohérentes entre elles, à ignorer.

## 2. Datum et MAC

| Donnée | Valeur | Source |
|---|---|---|
| Datum (référence des bras) | **3 m en avant de la tangente verticale au bord d'attaque de l'aile** (« 3 m in front of vertical tangent to the wing leading edge »). Identique pour tous les modèles PC-6, H2 et H4. | S1, § 2.45, p. 18 |
| Moyens de mise à niveau | Rails en T du plancher cabine horizontaux ; repères de niveau de chaque côté du fuselage. | S1, § 2.46, p. 18 |
| Position du bord d'attaque | 3000 mm derrière le datum (par définition du datum). Aile rectangulaire, profil NACA 64-514 constant sur l'envergure. | S1, § 2.22 et 2.45 |
| Corde | 1.9 m (« Chord length »), constante. | S1, § 2.22, p. 17 |
| MAC | **1900 mm**, LEMAC = **3000 mm** derrière le datum. **[dérivé]** Vérification : 11 % MAC = 3000 + 0.11 x 1900 = 3209 mm ; 25 % = 3475 ; 32 % = 3608 ; 34 % = 3646 ; 38 % = 3722 mm, valeurs identiques à celles publiées dans S1 et S2. Formule : %MAC = (bras_mm - 3000) / 19. | S1 § 2.22 + 2.44 |

## 3. Masses limites

| Limite | PC-6/B2-H2 (index H2) | PC-6/B2-H4 | Source |
|---|---|---|---|
| Masse max au roulage (MRW) | non trouvée | 2810 kg | S2 p. 1-6 (PDF 20) ; S3 p. 18 |
| Masse max au décollage (MTOW) | **2200 kg** (4850 lb) | **2800 kg** (6173 lb) | S1 § 2.41 p. 18 ; S2 p. 1-6 |
| Masse max à l'atterrissage (MLW) | égale à la MTOW : 2200 kg | **2660 kg** (5864 lb) | S1 § 2.42 ; S2 p. 1-6 |
| Masse max sans carburant (MZFW) | non trouvée | 2400 kg | S2 p. 1-6 ; S3 p. 18 |
| Masse max en cabine (derrière les sièges avant) | non trouvée | 1000 kg | S2 p. 1-6 ; S7 p. 5 |
| Charge max au plancher | 488 kp/m² (tous modèles) | 488 kg/m² | S1 § 2.52 ; S2 p. 1-6 |
| Charge max sur les trappes de plancher | 300 kp (total) | 150 kg par trappe | S1 § 2.52 ; S2 p. 1-6 |
| Masse à vide de base « standard IFR » (brochure) | non trouvée | 1395 kg | S3 p. 18 |
| Basic operating weight (fiche 2019) | non trouvée | 1250 kg (« depending on configuration ») | S4 |
| Masse à vide (fiche FR 2015) | non trouvée | env. 1250 à 1400 kg | S5 |
| Charge utile max / avec plein | non trouvée | env. 1200 kg / env. 1080 kg | S4, S5 |
| Facteurs de charge | non trouvés | +3.58 / -1.43 g volets rentrés ; +2.00 / 0 g volets sortis | S2 p. 1-6 |
| Catégorie | CAR 3 « Normal » uniquement (placard « must be operated as a normal category airplane »). Pas de catégorie utility ni restricted dans l'AFM 1820. | S2 p. 1-3 |

Autres masses S1 § 2.41 : sans index H : 1960 kg ; H1 : 2016 kg.

## 4. Stations et bras (mm derrière le datum)

Source principale : S1 § 2.51 (p. 19) et liste des équipements optionnels S1 p. 22 et 23.
Le PIM ne donne aucun bras (ils sont dans l'appendice W&B propre à chaque avion).

| Station | Bras (mm) | Remarque | Source |
|---|---|---|---|
| Sièges avant (pilote et copilote), rangée 1 | **+3050** | « 2 at + 3050 mm » (le PIM précise que le siège pilote est réglable) | S1 § 2.51 |
| Rangée 2 : 2 sièges individuels ou 1 banquette triple | **+3850** | | S1 § 2.51 |
| Rangée 3 : 2 sièges individuels ou 1 banquette triple | **+4570** | | S1 § 2.51 |
| Rangée 4 : 2 sièges individuels ou 1 banquette triple | **+5280** | | S1 § 2.51 |
| Configuration « normale » | 8 places (2 + 2 + 2 + 2) | | S1 § 2.51 |
| Configuration « maximum » | 11 places (2 avant + 3 banquettes triples) | | S1 § 2.51 |
| Rangement des 6 sièges passagers derrière la cabine (cadre 6, porte côté droit) | **+6630** | 27 kp pour les 6 sièges (4.5 kp par siège) | S1 § 2.51 et équipement 02 |
| Trappes de plancher (« trap doors ») | +3000 | bras de l'équipement trappe, 1.5 kg | S1 équipement 06 |
| Civières (2) avec supports | +4500 | 30 kg | S1 équipement 08 |
| Réservoir de convoyage cabine 3 x 200 L | +4500 | 98 kg à vide | S1 équipement 18 |
| Réservoir de convoyage cabine 200 L | +5500 | 21 kg | S1 équipement 19 |
| Ventilation cabine « de luxe » | +5653 | | S1 équipement 12 |
| Filtre d'entrée d'air moteur Mk 3B | +50 | indique que le datum est proche du nez | S1 équipement 23 |
| Système hydraulique skis (fixe) | +2580 | | S1 équipement 07 |
| Gratte-boue roues principales | +2900 | indicatif de la position du train principal (bras de l'accessoire, pas de l'essieu) | S1 équipement 16 |
| Protège-débris roulette de queue | +9850 | indicatif de la position de la roulette (bras de l'accessoire) | S1 équipement 15 |
| Nez du stabilisateur / de la dérive (revêtement fibre) | +9300 / +8700 | | S1 équipement 17 |

Arrimage cargo (S2 p. 1-8, PDF 22) : rails de sièges au plancher, ferrures d'arrimage
à 100 mm min. de l'extrémité de rail, espacées de 300 mm min. (600 mm si > 70 kg par paire de
rails), 140 kg max par barre de retenue, 280 kg pour un colis pleine largeur sur deux paires de
rails, colis suivant à 600 mm. 9 points d'arrimage (S3 p. 29, liste d'options).

## 5. Carburant

| Donnée | Valeur | Source |
|---|---|---|
| Réservoirs d'aile (modèles turbine) | 2 réservoirs de 63.5 ou **85 US gal** ; + 1 réservoir de pompe de gavage de 3 US gal | S1 § 2.23 p. 17 |
| Bras des réservoirs d'aile | **+3790 mm** | S1 § 2.23 |
| Bras du réservoir de pompe de gavage | **+5820 mm** | S1 § 2.23 |
| Capacité totale (grands réservoirs) | 173 US gal (655 L) | S1 § 2.23 |
| Capacité utilisable (grands réservoirs) | 170 US gal = **644 L** (2 x 83.5 + 3 US gal) | S1 § 2.23 ; S2 p. 1-4 (placard) |
| Masse du plein utilisable | **520 kg** (placard AFM : 644 LTR / 170 US GAL / 520 KG / 1145 LBS), soit 0.807 kg/L **[dérivé]** ; la brochure indique 515 kg (0.80 kg/L) | S2 p. 1-4 ; S3 p. 18 |
| Petits réservoirs (option) | 2 x 63.5 US gal, utilisable 128 US gal | S1 § 2.23 |
| Réservoirs sous voilure (option, suppl. 1826-1) | 372 / 477 / 487 L ; brochure : 128 US gal = 487 L = 390 kg ; bras **+3420 mm** ; masse installation 55 à 60 kg | S2 p. 4-1 ; S3 p. 18 ; S1 équipement 20 |
| Consommation indicative | 148 L/h (118.8 kg/h) | S3 p. 18 |
| Carburant | Jet A / A-1 / B (P&WC SB 1244) | S2 p. 1-3 |

Note : le placard « usable capacity 644 L » s'applique au B2-H4 (AFM 1820). Pour le B2-H2, S1 donne
les mêmes capacités possibles (130 ou 173 US gal total) ; la modification 1242 « Wing fuel tanks
644 ltrs » figure dans la liste des modifications (S1 p. 26).

## 6. Enveloppe de centrage (centrogramme)

Source : S1 § 2.44 p. 18 (tous modèles) et S2 p. 1-6 (B2-H4). « Straight line variation between
points given. » Catégorie normale uniquement. Aucune enveloppe distincte « parachutage » n'est
publiée dans les documents obtenus (le supplément 1824 n'a pas été trouvé ; S6 ne donne aucune
limite de centrage, seulement des effectifs).

### PC-6/B2-H2 (et tous modèles sauf B2-H4)

| Sommet | Masse (kg) | Bras (mm) | Bras (m) | %MAC |
|---|---|---|---|---|
| Avant, bas | 1450 | 3209 | 3.209 | 11 |
| Avant, haut (MTOW) | 2200 | 3475 | 3.475 | 25 |
| Arrière, haut (MTOW) | 2200 | 3646 | 3.646 | 34 |
| Arrière, bas | 1450 | 3646 | 3.646 | 34 |

En dessous de 1450 kg les limites restent 3209 / 3646 mm (« up to 1450 kg »). Pente de la limite
avant : 266 mm / 750 kg = 0.3547 mm/kg **[dérivé]**.

### PC-6/B2-H4

| Sommet | Masse (kg) | Bras (mm) | Bras (m) | %MAC |
|---|---|---|---|---|
| Avant, bas | 1450 | 3209 | 3.209 | 11 |
| Avant, haut (MTOW) | 2800 | 3608 | 3.608 | 32 |
| Arrière, haut (MTOW) | 2800 | 3722 | 3.722 | 38 |
| Arrière, bas | 1450 | 3722 | 3.722 | 38 |

Pente de la limite avant : 399 mm / 1350 kg = 0.2956 mm/kg **[dérivé]**. Limite avant interpolée à
la MLW 2660 kg : 3567 mm (29.8 % MAC) **[dérivé]** ; à la MZFW 2400 kg : 3490 mm (25.8 %)
**[dérivé]**.

## 7. Dimensions extérieures, cabine et portes

| Donnée | B2-H2 (tous sauf H4) | B2-H4 | Source |
|---|---|---|---|
| Envergure | **15.2 m** | **15.87 m** | S1 § 2.22 p. 17 ; S3 p. 14 ; S4 |
| Longueur hors tout | 10.9 m | 10.9 m (10.90 m) | S1 ; S3 ; S4 |
| Hauteur (statique) | 3.2 m | 3.20 m | S1 ; S3 ; S4 |
| Corde | 1.9 m | 1.9 m | S1 |
| Surface alaire | 28.5 m² | 30.15 m² | S1 ; S3 |
| Voie du train principal | non précisée | 3.00 m | S3 p. 14 ; S4 trois-vues |
| Envergure du stabilisateur | non précisée | 5.70 m | S3 p. 14 ; S4 |
| Diamètre hélice | non précisé | 2.67 m | S4 trois-vues |
| Empattement (train principal / roulette) | non trouvé | non trouvé | (indices S1 : accessoires à +2900 et +9850 mm) |
| Volume cabine | non précisé | « over 3 m³ » (« 10.5 ft3 » sic sur la fiche, brochure : « more than three cubic meters ») | S4 ; S3 p. 22 |
| Longueur / largeur / hauteur cabine | non trouvées dans les documents officiels | idem ; **[tiers]** env. 2.29 x 1.16 x 1.28 m | extrait de recherche non vérifié |
| Portes cabine | « Large sliding doors left and right side » ; porte de rangement des sièges côté droit derrière la cabine ; trappe de plancher (standard sur B2-H4 récent, option sinon) ; portes de cockpit largables. Dimensions des portes coulissantes : **non trouvées**. | | S4 ; S3 p. 22, 24, 25 ; S2 p. 1-4 et 2-17 |
| Portes battantes (hinged doors) | placard « ensure hinged doors are closed before operating flaps » (si installées) | | S2 p. 1-4 |
| Figures utiles | Trois-vues cotée : S4 page 2 (`png/factsheet2019-2.png`) et S3 p. 14 (`png/brochure_p10.png`). Écorché cabine avec porte coulissante, rangement des sièges et trappe : S3 p. 22 (`png/brochure_p14.png`). Aménagements cabine (7 pax, 10 pax, paradropping, ambulance, photo, convoyage) : S3 p. 26 (`png/brochure_p16.png`). | | |

## 8. Configuration parachutage (France)

- S6 (FFP DT 33, 2012) : dès qu'un élève en ouverture automatique est à bord, **B2-H2 : 8 paras max
  embarqués (moniteur compris) ; B2-H4 : 9 paras max** ; 1 para max assis au plancher en plus du
  moniteur. Le schéma (p. 1) montre : place copilote, moniteur au plancher, 1er OC au plancher,
  OA au plancher, para au « siège vidéo » près de la porte, et 4 paras sur banquette côté opposé.
  « Dans le respect des masses et du centrage, des manuels de vol des appareils et Manuels
  d'Activités Particulières des exploitants. » Aucun bras ni masse dans ce document.
- S1 modification **1824** (B2-H4) : « Cabin doors removed, sliding door/hatch open » ; catégorie
  Normal. Modification 1186 : « Installation for parachutist's operation as detailed in AFM
  Supplement ». Modification 1104 (B1-H2, B2-H2, B2-H4) : réservoirs cabine, restricted CAM 8
  en surcharge (« parachuting » apparaît dans la même ligne pour le B2-H4, à confirmer sur S1 p. 26).
- S2 p. 4-1 : supplément 1824 « Operation with Cabin Doors Removed and Sliding Door/Hatch Open ».
- S3 p. 27 (options) : « Para kit », « Belts for 9 skydivers », « Triple bench seat » ; texte
  p. 21 : « the Porter with 10 parachutists has proven to be an ideal solution ».
- S3 p. 26 « Cabin Layouts » (`png/brochure_p16.png`, vues en plan non cotées, nez à gauche,
  côté pilote en bas) : **Paradropping** = 2 sièges avant (pilote, copilote) + une banquette
  longitudinale unique le long du côté pilote (gauche) sur toute la longueur de la cabine, l'autre
  côté (droit, porte coulissante) entièrement libre au plancher. Comparaison : « 7 passengers » =
  2 avant + 3 rangées de 2 sièges individuels (la 4e rangée n'est pas dessinée) ; « 10 passengers »
  = 2 avant + 3 banquettes triples ; « Ambulance » = 2 avant + civière longitudinale côté gauche +
  2 sièges côté droit ; « Ferry » = 3 réservoirs cabine, env. 568 L au total (150 US gal), CAR 8.
  Ces schémas servent de base qualitative pour un plan de cabine ; ils ne donnent aucune cote.

## 9. Points ouverts et incertitudes

1. **Bras exacts pour le parachutage** (paras assis au plancher, banquette longitudinale, position
   « porte ») : non publiés. À reconstruire à partir des rangées de sièges (+3050 / +3850 / +4570 /
   +5280 mm) et de la longueur de cabine ; à valider avec l'appendice W&B de l'avion réel.
2. **Longueur et largeur de cabine, dimensions de la porte coulissante** : aucune valeur officielle
   trouvée. Seule valeur : « plus de 3 m³ ». Les 2.29 x 1.16 x 1.28 m sont de source tierce.
3. **Position du train** par rapport au datum : non trouvée (empattement inconnu ; voie 3.00 m).
4. **B2-H2** : MZFW, MRW, masse max en cabine et masse à vide non trouvées (l'AFM B2-H2 n'a pas
   été obtenu). Les limites CG et MTOW du B2-H2 viennent uniquement du TCDS F 56-10.
5. **Masse à vide typique** : 1250 kg (BOW fiche 2019), 1250 à 1400 kg (fiche FR), 1395 kg (BEW
   standard IFR brochure), 1270 kg (Wikipedia). Ordre de grandeur seulement ; un B2-H4 para
   avec hélice 4 pales est à peser.
6. **Densité carburant** : 0.807 kg/L d'après le placard AFM (520 kg / 644 L), 0.80 d'après la
   brochure. Retenir la valeur du manuel d'exploitation du centre.
7. Le TCDS S1 date de 2006 (Issue 7). Une édition plus récente sous en-tête EASA n'a pas été
   trouvée ; le PIM Rev. 8 (2017) confirme les mêmes limites.
8. Numéro de page : pour S1, la numérotation utilisée est celle imprimée « x of 27 » ; pour S2,
   « p. 1-6 » désigne la page AFM et « PDF 20 » la page du fichier.
