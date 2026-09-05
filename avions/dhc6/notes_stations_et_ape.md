# DHC-6 Twin Otter (stations cabine, porte, trains) et Cessna 208B « STC APE II / APE III » : notes de recherche du 2026-09-05

Dossier : `scratchpad/poh/dhc6_bis/`. Unités : livres (lb) et pouces (in) sauf mention contraire. Cette recherche complète `scratchpad/poh/dhc6/notes.md` (datum, MAC, enveloppe, carburant, sièges pilotes, dimensions cabine : non repris ici).

Marquage de fiabilité : **[OFF]** document officiel (TCDS, rapport d'enquête TSB/NTSB/BEA, fiche constructeur) ; **[FSI]** manuel de formation FlightSafety (reprend l'AFM, n'est pas l'AFM) ; **[TIERS]** site du détenteur de STC, presse, simulateur ; **[DERIVE]** valeur calculée ou mesurée par moi sur un plan, avec sa précision estimée.

## 1. Sources téléchargées (toutes validées par pdfinfo)

| Fichier local | Origine (URL) | Nature | Pages utiles |
|---|---|---|---|
| `ntsb_aar0803_sullivan_dhc6.pdf` (32 p) | https://www.ntsb.gov/investigations/AccidentReports/Reports/AAR0803.pdf | NTSB AAR-08/03/SUM, DHC-6-100 immatriculation retiree, Skydive Quantum Leap, Sullivan MO, 29 juillet 2006 [OFF] | p. 23 (fig. 3, bancs mousse), p. 24 (fig. 5, plan d'assise des paras), p. 10 et 13 à 15 du rapport |
| `paraclete_twin_otter_type_data_sheet.pdf` (20 p) | https://paracleteaviation.com/wp-content/uploads/2017/10/Twin-Otter-Type-Data-Sheet.pdf | TCDS FAA A9EA Rev. 15 (miroir chez un exploitant de largage) [OFF] | p. 6 et 12 (sièges à +95,0 ; bagages +41,0 / +354,0 ; huile +177,0) |
| `viking_400_techspec_2018.pdf` (15 p) | https://www.vikingair.com/sites/default/files/Viking-Twin-Otter-Series-400-Technical-Specifications-R-01-2018.pdf | Fiche technique Viking Series 400 [OFF, Series 400] | p. 2 (dimensions cabine et portes), p. 9 (« cabin rear bulkhead at station 332 », description des portes) |
| `../dhc6/FlightSafety_DHC6_PTM_full.pdf` (déjà téléchargé) | https://archive.org/download/dhc-6-ptm/DHC-6%20Pilot%20Training%20Materials/DHC-6%20PTM.pdf | FlightSafety Twin Otter PTM Rev. 5.0, 2010 [FSI] | p. 37 (fig. 1-10 plan d'assise), p. 39 (fig. 1-12 photo « parachute seats »), p. 40 (fig. 1-15 portes), p. 53 (fig. 1-38 vue de côté cotée), p. 405 (train avant fixé à la cloison FS 60) |
| `ptm53_300-053.png`, `ptm53_sideview.png`, `door_zoom.png` | rasterisation 300 dpi de la p. 53 du PTM | mesures pixel (§ 3 et 4) | |
| `ptm37_300-037.png`, `ptm37_layout_crop.png` | rasterisation 300 dpi de la p. 37 du PTM | mesures pixel (§ 2) | |
| `aar0803_p-23.png`, `aar0803_p-24.png` | rasterisation du rapport NTSB | plan d'assise des paras | |
| `tsb_a12c0154.html` | https://www.bst.gc.ca/eng/rapports-reports/aviation/2012/a12c0154/a12c0154.html | Rapport TSB A12C0154, Cessna 208B, 2012 [OFF] | § 1.6 (APE II, STC, 8750 vers 9062 lb) |
| `tsb_a14w0181.html` | https://www.tsb.gc.ca/eng/rapports-reports/aviation/2014/a14w0181/a14w0181.html | Rapport TSB A14W0181, Cessna 208B immatriculation retiree Air Tindi, 20 nov. 2014 [OFF] | § 1.6.4 (APE III : masses, limites CG) |

Consultés sans téléchargement utile (ou fichiers HTML supprimés) : pages produit AeroAcoustics APE II / APE III (https://aeroacoustics.com/files/208bapeii.htm et https://aeroacoustics.com/files/208bapeiii.htm) [TIERS] ; article AOPA juin 2014 « Blackhawk boost » (https://www.aopa.org/news-and-media/all-news/2014/june/pilot/t_fblackhawk) [TIERS] ; page Wipaire APE III (https://www.wipaire.com/modification/ape-iii/) [TIERS] ; docket NTSB DCA06MA064 (c'est le Comair 5191 de Lexington, pas le Twin Otter de Sullivan ; documents téléchargés puis supprimés) ; documents de dockets NTSB trouvés par la recherche « Otter Weight & Balance » (DHC-3T immatriculation retiree), « Weight and Balance Worksheet » (ULM Challenger II), « Weight, Balance and Equipment List » (ICON A5), « Weight and Balance Evaluation » (Cessna 337) : hors sujet, supprimés ; BEA f-vc140913 (Cessna U206F immatriculation retiree, para éjecté, Tarbes 2014) et BEA PJ-WII (DHC-6-400 au sol, Mayotte) : pas de données de centrage DHC-6, supprimés ; Wipaire 13000 floats service manual : pas de stations fuselage ; NTSB ERA25LA222 (DHC-6 immatriculation retiree, largage, Tullahoma TN, 8 juin 2025) : rapport préliminaire de 2 pages sans chargement.

Non obtenus : Weight and Balance Handbook PSM 1-63-8 (seule source des bras officiels par rangée), AFM PSM 1-63-1A section 6 et Supplement 23 (porte de largage), Maintenance Manual PSM 1-6-2 chap. 8 (pesée : bras des points de pesée ; pdfcoffee ne donne que la méthode de mise à niveau sur les rails de sièges), TCDS Transport Canada A-82, document Wipaire « Executive Interior Installation in Viking Model DHC-6-200/300/400 » (403 Cloudflare ; il cite des stations fuselage de sièges d'après le résumé de recherche), docket NTSB de l'accident de Sullivan (numéro NTSB non identifié : DCA06MA063/065 et CHI06MA212 sont vides ; le rapport AAR-08/03 lui-même ne contient aucun tableau de centrage), load sheets d'exploitants (Grand Canyon, Kenn Borek, Trans Maldivian, Zimex, Winair, Air Seychelles : rien de public avec des bras), rapports d'accident avec tableau de centrage par rangée (TSB A99A0036 Davis Inlet : texte sans bras).

## 2. Rangées de sièges commuter (7 rangées) : bras déduits

Aucune source officielle en ligne ne donne les bras par rangée. Le TCDS ne fixe que les sièges pilotes (+95,0 in) et renvoie au PSM 1-63-8 pour « approved seating arrangement ». Les valeurs ci-dessous sont **mesurées sur le plan schématique fig. 1-10 du PTM FlightSafety** (p. 37, layout « STANDARD 19/20 (UTILITY / COMMUTER) »), rasterisé à 300 dpi.

Méthode [DERIVE] : ligne pointillée avant (cloison poste/cabine, FS 109,3) à x = 456 px ; cloison arrière cabine (trait vertical au bout des sièges optionnels, FS 332 selon Viking) à x = 2256 px ; échelle = 1800 px pour 221 in de cabine (Viking) soit 8,15 px/in. Les rectangles de sièges doubles ont un pas régulier de 244 à 246 px, soit **30,0 in de pas** (valeur usuelle du Twin Otter commuter, ce qui valide l'échelle). Le bras retenu est le centre du rectangle siège (coussin + dossier) ; le CG d'un occupant assis est plutôt à 60 % de la profondeur, soit 2 à 3 in plus en arrière.

| Rangée | Centre siège (px) | Bras déduit (in) | Composition sur le plan |
|---|---|---|---|
| 1 | 620 | **129** | 1 double (côté opposé à la double porte) + 1 simple |
| 2 | 864 | **159** | 1 double + 1 simple |
| 3 | 1108 | **189** | 1 double + 1 simple |
| 4 | 1352 | **219** | 1 double + 1 simple |
| 5 | 1596 | **249** | 1 double + 1 simple |
| 6 | 1844 | **280** | 1 double seule (côté porte : dégagement de la double porte) |
| 7 | 2128 | **315** | jusqu'à 3 sièges simples « optional seat » sur toute la largeur, devant la cloison arrière ; le PTM p. 616 confirme « a removable seat installed in the centre of row 7 to allow access to the door » (toilettes) |

Précision estimée : **± 5 in** (dessin schématique, « dimensions approximate » ; épaisseur de trait 4 px = 0,5 in ; incertitude principale = position réelle des rails et du calage des sièges sur les rails Douglas, réglable par l'exploitant). Contrôle de cohérence : moyenne des 7 rangées = 220 in, soit 41 % MAC, ce qui explique que les Twin Otter pleins de passagers travaillent près de la limite arrière (36 % MAC) et que le chargement de soute arrière (+354) soit contraint. Côtés : le plan place les 6 doubles du côté sans porte double (donc à droite, tribord) et les 5 simples + la double porte à gauche (bâbord), ce qui correspond à l'aménagement 2 + 1 habituel.

## 3. Configuration parachutage : positions au sol, bancs

- **Aucune source officielle trouvée** donnant les stations des 22 paras (banquettes latérales ou assis au sol). Le Supplement 23 de l'AFM (porte de largage) et l'approbation de l'aménagement (FAA Form 337 ou STC bancs, ex. AvFab « Twin Otter 3-place divan / skydive bench », https://avfab.com/products/view/dehavilland-viking-twin-otter-dhc6-skydive-firefighter/) en sont les dépositaires. Non obtenus.
- NTSB AAR-08/03 (Sullivan 2006, DHC-6-100, 8 occupants) [OFF] : sièges d'origine déposés, 20 jeux de sangles de retenue mono-point fixées aux parois, deux blocs de mousse pleine de 5 à 6 ft de long et 15 à 18 in de haut et de large servant de bancs le long de chaque paroi à partir de l'avant cabine (allée centrale libre), paras assis face à l'arrière, tandems à califourchon sur les blocs, solos au sol (fig. 3 et 5, `aar0803_p-24.png`). Le rapport ne contient **aucun tableau de masse et centrage** ni de station. La fig. 5 place le pilote, puis les 4 paras tandem sur les blocs dans le premier tiers de la cabine et les solos derrière, entre la cloison et la double porte gauche.
- PTM fig. 1-12 « Parachute Seats » (p. 39) [FSI] : photo d'une cabine équipée de deux banquettes basses longitudinales rouges le long des parois, sans cote.
- Viking « Special Missions : Parachute » (déjà en `../dhc6/`) [OFF, Series 400] : banquettes murales, porte roll-up ou bi-fold, cloison arrière STN 332.
- Hypothèse de travail proposée pour l'outil [DERIVE, hypothèse à faire valider par l'exploitant] : 22 paras répartis en deux files (une par paroi, ou deux files à califourchon au sol), 11 par file, de la cloison arrière vers l'avant, le premier à sortir au niveau de la porte. Avec un encombrement longitudinal de 18 à 20 in par para assis à califourchon, la file occupe de FS ≈ 325 (para 1, à la porte) à FS ≈ 125 (para 11, contre la cloison avant), pas 20 in : bras 325, 305, 285, 265, 245, 225, 205, 185, 165, 145, 125 ; moyenne 225 in (47 % MAC). Cette répartition est cohérente avec la longueur de cabine (221 in) mais n'est pas une donnée documentaire.

## 4. Double porte gauche (porte de largage) et train : stations déduites d'un plan coté

Base : vue de côté fig. 1-38 du PTM (p. 53), cotée « 51 FT 9 IN » (621 in) et empattement « 14 FT 10.5 IN » (178,5 in), rasterisée à 300 dpi (`ptm53_sideview.png`, `door_zoom.png`). Échelle mesurée sur les centres de roues : 335,4 px pour 178,5 in soit 1,879 px/in ; contrôle sur la longueur hors tout : 1177 px soit 626 in pour 621 in annoncés (écart 0,8 %). Ancrage en station : bord arrière de la double porte = cloison arrière cabine FS 332 (Viking p. 9 [OFF] ; PTM fig. 1-15 : « cabin rear bulkhead and baggage compartment door » pointe l'arrière de la « rear left cabin door »). Second ancrage indépendant : sur le plan d'assise fig. 1-10 (échelle du § 2), le vide du rail bâbord correspondant à la double porte va de x = 1738 à 2213 px, soit **FS 267 à FS 325**.

| Élément | Mesure | Station déduite | Précision | Statut |
|---|---|---|---|---|
| Double porte gauche, bord avant du contour | x = 683 px (vue de côté) ; x = 1738 px (plan) | FS ≈ 271 (côté) / 267 (plan) : retenir **FS ≈ 268** | ± 5 in | [DERIVE] |
| Double porte gauche, bord arrière du contour | x = 798 px (côté) ; x = 2213 px (plan) | FS ≈ 330 (côté, ancrage) / 325 (plan) : retenir **FS ≈ 328** | ± 5 in | [DERIVE] |
| Ouverture libre (Viking : 56 in de large × 50 in de haut) | contours mesurés 58 à 61 in (cadres compris) | ouverture ≈ **FS 270 à 326**, centre ≈ FS 298 ; elle commence au bord de fuite de l'aile (TEMAC 266,24) | ± 5 in | [DERIVE] + [OFF] pour 56 × 50 |
| Séparation porte airstair (avant) / porte cargo (arrière) | x = 742 px | FS ≈ 302 | ± 5 in | [DERIVE] |
| Axe train principal | x = 610 px, 100,2 in devant le bord arrière de porte | **FS ≈ 232** | ± 6 in | [DERIVE] |
| Axe train avant | 178,5 in devant le principal | **FS ≈ 53** | ± 6 in | [DERIVE] ; cohérent avec « nose gear attached to the forward face of the bulkhead at fuselage station 60 » (PTM p. 405 [FSI]), la jambe étant devant la cloison |
| Voie du train principal | cote fig. 1-38 | 12 ft 2 in = 146 in | | [FSI] |
| Pointe du nez long (Series 300) | x = 76 px | FS ≈ -52 | ± 8 in | [DERIVE], indicatif |
| Répartition statique de charge | avec CG à 210 in : nez = (232 − 210) / 178,5 | ≈ 12 % sur le train avant (20 % à 203,8, 9 % à 216,3) | | [DERIVE], ordre de grandeur plausible |

Note : « − » ci-dessus est le signe moins mathématique, pas un tiret typographique.

## 5. Largeur du plancher et section de cabine

- Largeur max cabine 69 in (5 ft 9 in) et hauteur 59 in : Viking p. 2 [OFF]. **Largeur au plancher : non trouvée** (aucune figure « cabin cross section » cotée dans les documents accessibles ; elle figure dans le Maintenance Manual et les brochures d'aménagement). Les seules indications qualitatives : deux rails Douglas au plancher (Viking p. 9, « standard two-track rail system », 20 sièges), plancher à 15 in sous la ligne d'eau 0 (TCDS, déjà noté), allée centrale entre deux blocs de 15 à 18 in de large avec espace résiduel contre chaque paroi (NTSB Sullivan, DHC-6-100), ce qui implique une largeur au plancher supérieure à 2 × 18 + allée, soit vraisemblablement 55 à 60 in [DERIVE, ordre de grandeur].

## 6. Cessna 208B Grand Caravan : « STC APE II » et « STC APE III »

### 6.1 Identification

- **APE = Aircraft Payload Extender**, gamme de kits de **AeroAcoustics Aircraft Systems, Inc.** (États-Unis, région de Seattle, d'où le suffixe FAA « SE » des STC), commercialisés aussi par Wipaire et intégrés dans les conversions Blackhawk. Le « 9062 lb ≈ 4110 kg (STC APE II) » du document du club correspond exactement à ce kit : 9062 lb = 4110,5 kg.
- **APE II pour 208B : FAA STC SA00392SE** (page produit AeroAcoustics [TIERS]). Le rapport TSB A12C0154 [OFF] écrit « STC SA00392SA » (coquille probable pour SA00392SE) et confirme : « The kit increases the authorized gross take-off weight of the aircraft from 8750 to 9062 pounds ». Contenu : « small aerodynamic device consisting of two 16" long stall fences/strakes attached to the wing leading edge », masse installée < 3 lb, pose < 2 h, PMA FAA, « increases payload up to 15 % », « maximum takeoff gross weight increased by up to 312 lb ».
- **APE III pour 208B : FAA STC SA01213SE** (page produit AeroAcoustics [TIERS] ; TSB A14W0181 [OFF]). Contenu : remplacement de l'essieu de train principal à vie limitée par un essieu « high cycle », fonctionne avec l'APE II et les pneus 29 in approuvés Cessna (fournis avec le kit s'ils ne sont pas déjà montés), + < 2 lb, pose « several hours ».
- Autres produits de la même famille (non détaillés) : « APE STOL » 208 et 208B (https://www.aeroacoustics.com/files/208bapestol.htm), et versions 208 (Caravan court : 8000 vers 8362 lb au décollage, atterrissage 7800 vers 8362 lb selon la page Wipaire APE III [TIERS]).
- **EASA** : aucune STC EASA AeroAcoustics trouvée (moteur de recherche EASA inaccessible, aucune référence dans les résultats). À vérifier auprès du détenteur ou dans la liste EASA « Foreign STC validated » avant usage en Europe ; le document du club suppose une validation.
- Détenteur / contact : AeroAcoustics Aircraft Systems, sales@aeroacoustics.com, 855-273-5487 (page produit).

### 6.2 Valeurs chiffrées

| Grandeur | Standard 208B (POH 208BPHBUS, `../c208/`) [OFF] | Avec APE II (SA00392SE) | Avec APE III (SA01213SE, inclut APE II + pneus 29 in) | Source APE |
|---|---|---|---|---|
| Masse max décollage | 8750 lb | **9062 lb** (4110 kg) | **9062 lb** | AeroAcoustics [TIERS] ; TSB A12C0154 et A14W0181 [OFF] |
| Masse max roulage | 8785 lb | non trouvée (vraisemblablement 9062 + 35 = 9097 lb, non confirmé) | idem | |
| Masse max atterrissage | 8500 lb | non modifiée par l'APE II seul (aucune mention) [DERIVE] | **9000 lb** (« increased from 8500 lb ») | AeroAcoustics APE III [TIERS] ; TSB A14W0181 [OFF] |
| Masse max sans carburant | pas de MZFW publiée pour le 208B | idem | idem | POH |
| Limite CG avant | 179,60 in à ≤ 5500 lb ; 193,37 in à 8000 lb ; 199,15 in à 8750 lb (droites) | inchangée jusqu'à 8750 lb puis **prolongée en droite de 199,15 in à 8750 lb jusqu'à 200,23 in à 9062 lb** | idem | TSB A14W0181 § 1.6.4 [OFF] (« Forward CG limits were unchanged except for an extension from 199.15 inches at 8750 pounds to 200.23 inches at 9062 pounds ») |
| Limite CG arrière | 204,35 in à toutes masses | **204,35 in inchangée jusqu'à 9062 lb** | idem | TSB A14W0181 [OFF] (« The aft CG limit was unchanged ») |
| Givrage connu | 8550 lb max avec cargo pod (supplément S1) | **inchangé : 8550 lb avec cargo pod**, l'augmentation ne s'applique pas en givrage connu | idem | TSB A14W0181 [OFF] |
| Vitesse de décrochage, lisse, 0° d'inclinaison, 9062 lb | | 63 KIAS | | TSB A12C0154 [OFF] |
| Distance de décollage 9062 lb, 0 °C, 800 ft, piste sèche, technique courte | | ≈ 1500 ft (roulement) | | TSB A12C0154 [OFF] |
| Index TSB « allowable index position at 9062 lb » | | valeur tronquée dans le HTML (« between −0. ... ») | | TSB A12C0154 |

Enveloppe décollage 208B avec APE II/III, en (masse lb ; bras in) [DERIVE à partir des lignes ci-dessus] : avant (5500 ; 179,60) → (8000 ; 193,37) → (8750 ; 199,15) → (9062 ; 200,23) ; arrière (9062 ; 204,35) → bas (204,35). MAC 208B : LEMAC 177,57 in, longueur 66,40 in (POH), donc 200,23 in = 34,1 % MAC et 204,35 in = 40,3 % MAC. Datum 208B : 100 in devant la face avant de la cloison pare-feu (POH).

Attention : l'EASA TCDS IM.A.226 donne pour le 208B « legacy » une limite avant 185,00 in à 6500 lb au lieu de 179,60 à 5500 lb (voir `../c208/notes.md`) ; la prolongation APE ne concerne que le segment au-dessus de 8750 lb.

### 6.3 Autres STC d'augmentation de masse du 208B (pour mémoire)

- **Blackhawk XP42A / XP140** (PT6A-42A ou PT6A-140) : l'article AOPA de juin 2014 [TIERS] indique que la modification Blackhawk « includes an Aircraft Payload Extender (APE) kit » donnant pour le 208B « a 312-pound increase, from 8,750 to 9,062 pounds », kit décrit comme « a larger main gear tire and axle assembly, stall fences, and vortex-generator-looking aerodynamic devices at the flap trailing edges » (c'est donc l'APE III + APE II AeroAcoustics, pas une STC Blackhawk propre).
- **Texas Turbine Supervan 900** (TPE331-12JR, 900 shp) : conversion moteur ; sa masse max n'a pas été vérifiée dans cette recherche (FAQ Texas Turbine non consultée). Ne pas lui attribuer les 9062 lb sans vérification.
- Aucune autre STC portant la MTOW du 208B au-delà de 9062 lb n'a été rencontrée.

## 7. Synthèse des points ouverts

1. Bras officiels des rangées et de la configuration largage : seulement dans le PSM 1-63-8 et le dossier d'aménagement de l'avion (Form 337 / STC bancs / Supplement 23). Les valeurs du § 2 sont des estimations à ± 5 in à valider avec la fiche de pesée et le devis de masse de l'avion concerné.
2. Largeur au plancher : non trouvée.
3. Stations train : ± 6 in, à recouper avec la fiche de pesée (bras des points de pesée du PSM 1-6-2 chap. 8).
4. APE : supplément AFM AeroAcoustics non obtenu (masse roulage, éventuelles vitesses, procédure), validation EASA non trouvée.
