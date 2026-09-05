# Cessna 208 Caravan (675 SHP) et 208B Grand Caravan : notes masse et centrage

Dossier : `scratchpad/poh/c208/`. Toutes les valeurs sont en pouces (in) depuis le datum et en livres (lb), sauf mention contraire.
Convention de marquage des sources : **[OFF]** = lu dans un document officiel (POH/AFM Cessna, TCDS FAA ou EASA, Spec & Description Cessna) ; **[TIERS]** = site ou document tiers ; **[CALC]** = valeur dérivée par calcul à partir de valeurs officielles (jamais une valeur inventée).

## 1. Sources

| Réf. | Fichier local | Origine (URL) | Nature | Pages utiles |
|---|---|---|---|---|
| S1 | `C208B_G1000_POH_208BPHBUS-01_caravannation.pdf` (536 p., valide) | https://caravannation.com/208BG1000POH.pdf | **[OFF]** POH/AFM Cessna Model 208B G1000 (PT6A-114A, 675 SHP), P/N 208BPHBUS-00/-01 (2008). Texte extrait dans `C208B_G1000_POH.txt` (numéro de page PDF = page POH + 330 pour la section 6) | Sect. 1 : PDF p. 16, 25 à 26 ; Sect. 2 : PDF p. 52 à 53 (POH 2-12, 2-13) ; Sect. 6 : PDF p. 331 à 382 (POH 6-1 à 6-52) |
| S2 | `TCDS_FAA_A37CE_Rev22_2017_via_paracleteaviation.pdf` (12 p.) | https://paracleteaviation.com/wp-content/uploads/2017/10/Cessna-Caravan-208.pdf | **[OFF]** FAA TCDS A37CE Rev. 22 (31 oct. 2017), modèles 208, 208B, 208B S/N 208B2197 et 208B5000+ (EX). Texte : `TCDS_FAA_A37CE_Rev22.txt` | p. 3 à 8 |
| S3 | `TCDS_EASA_IM.A.226.pdf` (26 p.) | https://www.easa.europa.eu/en/downloads/7230/en | **[OFF]** EASA TCDS IM.A.226 Issue 15 (18 sept. 2025). Texte : `TCDS_EASA_IM.A.226.txt` | p. 7 à 8 (208), 17 à 18 (208B), 21 à 22 (208B EX) |
| S4 | `TCDS_UKCAA_IM.A.226_issue10.pdf` (25 p.) | https://www.caa.co.uk/Documents/Download/3934/... | **[OFF]** copie UK CAA de l'EASA TCDS Issue 10 (2018), non exploitée en détail (doublon de S3) | |
| S5 | `C208_SpecDescription_675_TAdistributors_2016.pdf` (29 p.) | https://tadistributors.com/wp-content/uploads/2016/03/SD-675-Unit-0580-to-TBD-2016-Feb.pdf | **[OFF]** Cessna « Specification and Description, Caravan (208), Rev. D, fév. 2016 ». Texte : `C208_SpecDescription.txt` | p. 4 (fig. I ext.), p. 5 (fig. II intérieur), p. 6 (§1.2, 1.3) |
| S6 | `C208_675_POH_excerpt_wsimg.pdf` (15 p. PDF, scan OCR) | https://img1.wsimg.com/blobby/go/1ecb10a4-49e9-4fe5-a6bc-f0f227949dd2/downloads/cessna_208_caravan_pilot_operating_handbook.pdf | **[OFF, partiel]** extrait scanné « For Training Purposes Only » du POH Cessna Model 208 (675 SHP), 208PHTR03, pages datées 1998 à 2004 : sections 1 à 4 seulement, **pas de section 6**. Texte OCR : `C208_675_POH_excerpt_wsimg.txt` | Sect. 2 Limitations (poids, CG, placards zones) |
| S7 | `RSV_C208_Load_Sheet.pdf` (1 p.) | http://www.aeroelectric.com/Reference_Docs/Cessna/cessna-misc/C208_Load_Sheet.pdf | **[TIERS]** feuille de chargement 208B (RSV Aviation, 2005), formules index/%MAC | |
| S8 | `Martinaire_208B_icing_supplement_D1329-S1-10.pdf` (56 p.) | https://www.martinaire.com/wp-content/uploads/2021/06/Revision-10-Icing-Supplement-1.pdf | **[OFF]** supplément givrage POH 208B (D1329-S1-10), non exploité pour le centrage | |
| S9 | Caravan Nation, « Flying Skydivers in the C208B » | https://caravanpilots.blogspot.com/2014/10/flying-skydivers-in-c208b-grand-caravan.html | **[TIERS]** blog pilote parachutisme | |
| Fig. | `fig/c208b_p357.png` (dim. cabine cargo, fig. 6-4 sh.1), `p366` (zones cargo, fig. 6-11 sh.1), `p367`, `p368` (sièges commuter, fig. 6-11 sh.2 et 3), `p372` à `p378` (tables poids/moment fig. 6-15 sh.1 à 7, montages `montage_373_375.png`, `montage_376_378.png`), `p379` (problème de chargement type, fig. 6-16), `p381` (limites CG, fig. 6-17), `p382` (enveloppe moment, fig. 6-18) | rendus pdftoppm 150 à 200 dpi de S1 | | |

Non obtenus (voir §8) : POH complet du 208 court avec sa section 6, POH 208B EX (208BPHCUS), FAA TCDS Rev. 23 en PDF (le site DRS renvoie une page HTML), suppléments W&B des conversions parachutisme (Texas Turbine, Blackhawk, portes de largage).

## 2. Datum et MAC

| Donnée | 208 (675 SHP) | 208B | Source |
|---|---|---|---|
| Datum | plan vertical 100 in en avant de la face avant de la cloison pare-feu | idem | S1 PDF p. 26 et 53 (208B) [OFF] ; S6 sect. 2 (208) [OFF] ; TCDS S2/S3 : « 100 in forward of center of nose gear jack point » (le point de levage nez est sous la cloison pare-feu, cf. S1 PDF p. 337), formulation équivalente [OFF] |
| Station de la cloison pare-feu | FS 100.0 | FS 100.0 | S1 PDF p. 348 (« floor is flat from the firewall at Fuselage Station 100.0 ») [OFF] |
| LEMAC (bord d'attaque de la MAC) | 157.57 in | 177.57 in | S6 (208) [OFF, OCR lisible] ; S1 PDF p. 53 (208B) [OFF] |
| Longueur MAC | 66.40 in | 66.40 in | idem |
| Formule %MAC | %MAC = (CG − 157.57) / 66.40 × 100 | %MAC = (CG − 177.57) / 66.40 × 100 | [CALC] à partir des valeurs ci-dessus ; vérifié : 179.60 → 3.06 %, 193.37 → 23.80 %, 199.15 → 32.50 %, 204.35 → 40.33 % (208B) ; 162.41 → 7.29 %, 174.06 → 24.83 %, 184.35 → 40.33 % (208) |
| Surface alaire | 279.4 ft² | 279.4 ft² | S5 p. 4 ; S1 PDF p. 16 [OFF] |
| Empattement (wheel base) | 11 ft 7 1/2 in (139.5 in) | 13 ft 3 1/2 in (159.5 in) | S5 p. 4 ; S1 PDF p. 16 [OFF]. Écart 20 in = décalage LEMAC 208 → 208B (cohérent) [CALC] |

Note : la feuille RSV (S7, tiers) utilise index = (bras − 192) × poids / 500 et %MAC = (CG − 177.57)/0.664, cohérent avec le POH.

## 3. Masses limites

| Masse | 208 landplane | 208 amphibie (Wipline 8000) | 208B (PT6A-114A) | 208B EX (S/N 208B2197, 208B5000+) | Source |
|---|---|---|---|---|---|
| Max ramp | 8035 | 7635 | 8785 | 8842 (8785 avec carénage TKS) | S2, S3 [OFF] ; S1 PDF p. 52 (208B) |
| Max décollage | 8000 | 7600 | 8750 | 8807 (8750 avec TKS) | idem |
| Max atterrissage | 7800 | 7300 | 8500 | 8500 | idem |
| Max zero fuel | non publiée (aucune MZFW dans POH 208B ni TCDS) | | non publiée | non publiée | S1, S2, S3 |
| Charge cabine max derrière la barrière cargo | 2900 lb (placard) | | 3400 lb | | S6 placards 29/30 (208) ; S1 PDF p. 341, 349 (208B) [OFF] |
| 208B en givrage connu (FIKI) | | | PT6A-114 : 8000 avec pod / 8450 sans pod ; PT6A-114A : 8550 avec pod / 8750 sans pod ; avec TKS : 8750 | | S2 p. 6 [OFF] |
| Masse à vide standard (estimation constructeur) | 4230 lb (est.) ; charge utile 3805 lb (est.) | | | | S5 §1.3 (2016) [OFF] |
| Masse à vide exemple POH | | | BEW 5005 lb, bras 185.69 in, moment 929.4 (exemple de chargement) | | S1 PDF p. 342, 379 [OFF] |
| Masse à vide avion parachutisme | | | 4570 lb (avion du blogueur, config. para) | | S9 [TIERS] |
| Huile pleine | 29 lb à +69.2 | | 29 lb à +69.2 | | S2/S3 Note 1 [OFF] |
| Carburant inutilisable (BEW) | 24.1 lb à +186.4 (S/N 20800131+) | | 24.1 lb à +206.4 (S/N 208B0090+) | | S2/S3 Note 1 [OFF] |

MTOW 9062 lb par STC : **non trouvé** dans cette recherche (aucun document).

## 4. Stations et bras (208B, POH S1) 

Toutes les valeurs ci-dessous sont **[OFF]** (S1, fig. 6-11 feuilles 1 à 3 = PDF p. 366 à 368, fig. 6-12 p. 369, tableau p. 352, fig. 6-15 p. 372 à 378, fig. 6-16 p. 379).

| Poste | Bras (in) | Plage / limites | Remarques |
|---|---|---|---|
| Pilote (siège 1) | 135.5 | 133.5 à 146.5 | siège réglable, verrou à FS 145.0 pour occupant moyen ; CG occupant = 9 in en avant de l'intersection assise/dossier (PDF p. 340) |
| Passager avant (siège 2) | 135.5 | 133.5 à 146.5 | idem |
| Rangée commuter 1 (sièges 3 et 4, ou banc 3-4-5) | 173.9 | | plongeurs de pieds avant sur rails à FS 163.5 |
| Rangée 2 (sièges 5 et 6, ou banc 6-7-8) | 209.9 | | plongeurs à FS 199.5 |
| Rangée 3 (sièges 7 et 8, ou banc 9-10-11) | 245.9 | | plongeurs à FS 235.5 |
| Rangée 4 (sièges 9 et 10, 10 places seulement) | 281.9 | | plongeurs à FS 271.5 ; pas de siège à 281.9 en 11 places |
| Zone cargo 1 | 172.1 | FS 155.4 à 188.7 | 52.9 ft³ ; max 1780 lb arrimé / 415 lb non arrimé (cloisons) |
| Zone 2 | 217.8 | 188.7 à 246.8 | 109.0 ft³ ; 3100 / 860 lb |
| Zone 3 | 264.4 | 246.8 à 282.0 | 63.0 ft³ ; 1900 / 495 lb |
| Zone 4 | 294.5 | 282.0 à 307.0 | 43.5 ft³ ; 1380 / 340 lb |
| Zone 5 | 319.5 | 307.0 à 332.0 | 40.1 ft³ ; 1270 / 315 lb ; filet requis si > 400 lb |
| Zone 6 (plancher surélevé) | 344.0 | 332.0 à 356.0 | 31.5 ft³ ; 320 / 245 lb ; plancher 5 in au-dessus du plancher principal |
| Pod cargo zone A | 132.4 | 100.00 à 154.75 | 23.4 ft³ ; 230 lb |
| Pod zone B | 182.1 | 154.75 à 209.35 | 31.5 ft³ ; 310 lb |
| Pod zone C | 233.4 | 209.35 à 257.35 | 27.8 ft³ ; 270 lb |
| Pod zone D | 287.6 | 257.35 à 332.00 | 28.8 ft³ ; 280 lb ; pod : 111.5 ft³, 1090 lb max, 30 lb/ft² |
| Barrière cargo | 153.0 (pied, sur rails) à ~166.0 (plafond) | | PDF p. 349 |
| Rails de siège avant (zone passager avant) | FS 125.00 à 159.98 | | rails « I », PDF p. 348 |
| Rails de siège arrière | FS 158.00 jusqu'au plancher surélevé | | fixations rapides tous les 1 in |
| Face avant du plancher surélevé | 332.0 | | repère pratique de mesure |
| Cloison arrière cabine | 356.0 | | |
| Carburant (réservoirs) | +203.8 (TCDS FAA) ; table POH : 202.4 à 203.4 selon quantité | | voir §5 |
| Carburant de roulage (35 lb) | 200.0 (POH : −7.0 pour −35 lb) | | S1 PDF p. 379 |
| Plancher cabine | 200 lb/ft² | | PDF p. 348 |

Stations 208 court (peu de données officielles trouvées) : pilote et passager avant 133.5 à 146.5 (S2) ; réservoirs +183.8 (S2) ; carburant inutilisable +186.4 ; placards zones cargo 208 (S6, OCR) : zone 1 max 1410 lb, zone 2 1430, zone 3 1410, zone 4 1380, zone 5 1270, zone 6 320, bagages zone 6 (version passagers) 325 lb, charge max derrière barrière 2900 lb. **Bornes FS des zones du 208 et bras des sièges arrière du 208 : non trouvés** (section 6 du POH 208 manquante). Par analogie constructive [CALC, à confirmer] : zone 6 du 208 = plancher surélevé FS 284 à 308 (mêmes 24 in que 332 à 356 sur 208B).

## 5. Carburant

| Donnée | 208 | 208B | 208B EX | Source |
|---|---|---|---|---|
| Capacité totale | 335 gal (335.6 selon S5/S6) | 335 gal | 339.1 gal | S2, S3, S5 [OFF] |
| Utilisable | 332 gal = 2224 lb à 6.7 lb/gal | 332 gal = 2224 lb | 335.3 gal | idem |
| Bras réservoirs (TCDS FAA) | +183.8 | +203.8 | +203.8 | S2 [OFF]. L'EASA (S3) écrit « +183 in » pour le 208B, probable coquille (le POH 208B donne ~203) |
| Déséquilibre max en vol | 200 lb | 200 lb | | S6 placard, S9 |

Table poids/moment carburant 208B (S1 fig. 6-15 sheet 4, PDF p. 375, Jet A 6.7 lb/gal à 60 °F ; bras = moment×1000/poids [CALC], précision ±0.1 in au-delà de 100 gal, ±0.5 in en dessous à cause de l'arrondi du moment) :

| gal | lb | moment/1000 | bras calc. (in) |
|---|---|---|---|
| 5 | 34 | 6.8 | 200.0 |
| 10 | 67 | 13.6 | 203.0 |
| 25 | 168 | 34.0 | 202.4 |
| 50 | 335 | 68.0 | 203.0 |
| 75 | 503 | 102.0 | 202.8 |
| 100 | 670 | 136.1 | 203.1 |
| 125 | 838 | 170.2 | 203.1 |
| 150 | 1005 | 204.3 | 203.3 |
| 175 | 1173 | 238.4 | 203.2 |
| 200 | 1340 | 272.5 | 203.4 |
| 225 | 1508 | 306.5 | 203.2 |
| 250 | 1675 | 340.5 | 203.3 |
| 275 | 1843 | 374.5 | 203.2 |
| 300 | 2010 | 408.4 | 203.2 |
| 325 | 2178 | 442.4 | 203.1 |
| 332 | 2224 | 451.7 | 203.1 |

Conclusion pratique : sur le 208B le bras carburant est quasi constant (203.0 à 203.4 in) ; un bras unique de 203.2 in donne une erreur < 0.1 in sur le CG avion. La table complète (pas de 5 gal) est lisible dans `fig/montage_373_375.png` (feuille 4) ; la feuille 5 (PDF p. 376) donne la même table pour de l'essence aviation à 6.0 lb/gal. Table carburant du 208 court : **non trouvée** (utiliser +183.8 in du TCDS en attendant).

## 6. Enveloppe de centrage (sommets)

### 208B (PT6A-114A, 675 SHP), catégorie normale, avec ou sans pod. S1 PDF p. 53 (texte) et p. 381 (fig. 6-17) ; S2 p. 5 à 6 [OFF]

| Sommet | Poids (lb) | Bras (in) | %MAC | Remarque |
|---|---|---|---|---|
| Avant, bas | ≤ 5500 | 179.60 | 3.06 | limite verticale sous 5500 lb (le graphe commence à 4000 lb, aucune masse mini publiée) |
| Avant, coude | 8000 | 193.37 | 23.80 | variation linéaire entre sommets |
| Avant, MTOW | 8750 | 199.15 | 32.50 | décollage et vol |
| Avant, atterrissage | 8500 | 197.22 | 29.60 | limite atterrissage = même droite coupée à 8500 lb [CALC : 197.22 est sur la droite 8000 → 8750] |
| Arrière | tous poids jusqu'à 8750 | 204.35 | 40.33 | verticale |
| Zone d'alerte arrière | | 38.33 % à 40.33 % MAC (203.02 à 204.35 in) | | hachurée sur fig. 6-17/6-18, utilisable seulement avec CG déterminé précisément (PDF p. 353, 382) |

Lecture graphique de la fig. 6-17 (200 dpi) : cohérente avec le texte à ±0.3 in / ±50 lb ; les valeurs retenues sont celles du texte.

Divergence à signaler : l'EASA TCDS Issue 15 (S3, 2025) donne pour le 208B « legacy » (S/N 208B0001 à 2196) une limite avant **185.00 in à 6500 lb** (décollage) et 185.00 à 5500 lb (atterrissage) au lieu de 179.60 à 5500 lb ; le FAA TCDS Rev. 22 (2017) et le POH 208BPHBUS (2008) donnent 179.60 à 5500 lb. Vérifier la révision du POH de l'avion concerné.

### 208B EX (S/N 208B2197, 208B5000 et suivants, PT6A-140). S2 p. 7 à 8, S3 p. 21 à 22 [OFF]

| Cas | Sommets (poids lb, bras in) |
|---|---|
| Décollage et vol, avec ou sans pod | (6500, 185.00) ; (8000, 193.37) ; (8807, 199.15) ; arrière 204.35 à tous poids ; sous 6500 lb : 185.00 |
| Décollage et vol, carénage TKS | (5500, 185.00) ; (8000, 193.37) ; (8750, 199.15) ; arrière 204.35 |
| Atterrissage (les deux cas) | (5500, 185.00) ; (8000, 193.37) ; (8500, 197.22) ; arrière 204.35 |

%MAC 185.00 = 11.19 % en supposant la même MAC (177.57 / 66.40) [CALC, hypothèse non vérifiée dans un POH EX].

### 208 (675 SHP), landplane, catégorie normale. S2 p. 3, S3 p. 7 à 8, S6 sect. 2 [OFF]

| Sommet | Poids (lb) | Bras (in) | %MAC |
|---|---|---|---|
| Avant, bas | ≤ 4200 | 162.41 | 7.29 |
| Avant, MTOW | 8000 | 174.06 | 24.83 |
| Avant, atterrissage | 7800 | 173.44 | 23.90 [CALC] |
| Arrière | tous poids jusqu'à 8000 | 184.35 | 40.33 |

Le POH S6 (OCR) écrit « 162.41 inches (7.29% MAC) ... 174.06 inches (24.83% MAC) ... Aft: 184.35 inches (40.33% MAC) », identique au TCDS.

### 208 amphibie (Wipline 8000), pour mémoire. S2 [OFF]
Décollage : (5200, 165.47) ; (7600, 172.83) ; arrière 182.68. Atterrissage : (5200, 165.47) ; (7300, 171.91) ; arrière 182.68.

Catégorie restreinte / cargo : aucune enveloppe distincte publiée (les versions Cargo et Passenger partagent la même enveloppe dans S1 et S2). Enveloppe avec MTOW 9062 lb ou winglets : non trouvée.

## 7. Dimensions cabine et portes

### 208B, version cargo (S1 fig. 6-4 sheet 1, PDF p. 357 = POH 6-27) [OFF]

| Élément | Valeur |
|---|---|
| Stations repères (de l'avant vers l'arrière) | FS 100.0 (pare-feu) ; 118.0 ; 166.0 ; 282.0 ; 332.0 ; 356.0 (cloison arrière) |
| Segments | 18 in (100 → 118) ; 48 in (118 → 166, zone portes équipage) ; 116 in (166 → 282) ; 50 in (282 → 332, porte cargo) ; 24 in (332 → 356, plancher surélevé) |
| Longueur cabine pare-feu → cloison arrière | 256 in (21 ft 4 in) [CALC 356 − 100] |
| Hauteur cabine | 51 in (vers FS 200) ; 54 in (à FS 282) ; 52 in (à FS 332) ; 46 in (zone arrière 332 à 356) |
| Largeur cockpit | 53 in |
| Largeur cabine (max « breadth » / au plancher) | 62 / 54 in (vers FS 200) ; 64 / 59.5 in (à FS 282) ; 53 / 51 in (à FS 332) ; 46 / 42 in (arrière) |
| Porte cargo (gauche, deux vantaux) | ouverture 49 in de large × 50 in de haut (haut, milieu, bas identiques) ; située entre FS 282.0 et 332.0 |
| Portes équipage (une de chaque côté) | largeur haut 11 7/8 in, milieu/hors tout 35 5/8 in, bas 31 7/8 in ; hauteur avant 24 3/8 in, milieu/hors tout 41 3/4 in, arrière 44 3/4 in ; situées dans le segment FS 118 à 166 |
| Volume cargo derrière barrière | 340 ft³ |
| Position des rails de siège | avant : FS 125.00 à 159.98 ; arrière : FS 158.00 jusqu'à 332 |
| Barrière cargo | FS 153.0 (bas) à ~166.0 (haut) |
| Bord d'attaque MAC (aile) | FS 177.57, soit à 77.6 in derrière le pare-feu, dans la zone cargo 1 (155.4 à 188.7) |
| Empattement | 159.5 in (13 ft 3 1/2 in) ; station des roues principales non publiée (estimation ~FS 255 à 260 si axe de roue avant proche de FS 100 ; à confirmer sur la fiche de pesée fig. 6-1, PDF p. 334, non lue) |
| Porte passagers airstair (droite, version passagers) | dimensions et position : non lues (fig. 6-4 sheet 2, PDF p. 358, non rendue) |

### 208 court (S5 fig. II p. 5 et §1.2 p. 6 ; texte §4 p. 8) [OFF]

| Élément | Valeur |
|---|---|
| Stations repères | FS 100 ; 118 ; 180 ; 234 ; 284 ; 308 (cloison arrière) |
| Segments | 18 in (100 → 118) ; 13 ft 10 in = 166 in (118 → 284) ; 24 in (284 → 308) |
| Longueur cabine pare-feu → cloison arrière | 17 ft 4 in = 208 in (texte S5) ; = 308 − 100 [CALC] |
| Hauteur | 51 in (vers FS 180) ; 54 in (FS 234) ; 52 in (FS 284) ; 46 in (arrière) ; « 4 ft 3 in plancher → plafond » (§1.2) |
| Largeur | cockpit 53 in ; 54 (plancher) / 62 (fenêtres) in vers FS 180 ; 59.5 / 64 in à FS 234 ; 51 / 53 in à FS 284 ; 42 / 46 in arrière ; « 5 ft 2 in max » (§1.2) |
| Porte cargo (gauche) | 49 in × 50 in ; entre FS 234 et 284 [lecture figure : bornes 234 / 284 avec cote 50 in] |
| Portes équipage | mêmes cotes que 208B (11 7/8, 35 5/8, 31 7/8 ; 24 3/8, 41 3/4, 44 3/4) ; « max 35.65 in × 44.75 in » (texte S5) |
| Porte passagers airstair (droite, arrière de l'aile) | cotes « 24 in » et « 50 in » visibles sur la fig. II, attribution incertaine (OCR de figure) |
| LEMAC | FS 157.57 (57.6 in derrière le pare-feu) |
| Empattement | 139.5 in (11 ft 7 1/2 in) |
| Dimensions extérieures | longueur 37 ft 7 in ; hauteur 14 ft 10 in ; envergure 52 ft 1 in (S6) |

Différence 208 → 208B : allongement total 48 in (4 ft), réparti en 20 in en avant de l'aile (LEMAC 157.57 → 177.57, empattement +20 in) et 28 in entre l'aile et la porte cargo (porte cargo 234/284 → 282/332) [CALC à partir des stations officielles].

### Parachutisme (aucun document officiel trouvé)
- S9 [TIERS] : jusqu'à 17 paras ; assis à califourchon sur deux bancs longitudinaux face à l'arrière ; consigne de ne personne asseoir contre la cloison arrière (sensibilité CG constatée aux charges lourdes) ; ouverture de la porte cargo limitée à 155 KIAS ; masse à vide de l'avion du blogueur 4570 lb.
- Porte de largage à rouleau (roll-up jump door) : dimensions, STC et supplément W&B **non trouvés** (diverdriver.com inaccessible, 403). Les conversions Texas Turbine (Supervan 900) et Blackhawk sont des remotorisations ; aucun supplément masse et centrage trouvé en PDF direct.

## 8. Points ouverts et incertitudes

1. **POH 208 court, section 6** : non obtenu (seul un extrait scanné sections 1 à 4). Manquent : bornes FS des zones cargo 208, bras des sièges arrière 208, table carburant 208, dimensions cabine version passagers, fiche de pesée. Les limites CG et masses du 208 sont couvertes par les TCDS FAA/EASA et confirmées par l'extrait.
2. **Limite avant 208B legacy** : 179.60 à 5500 lb (POH 2008, FAA TCDS Rev. 22) contre 185.00 à 6500 lb (EASA TCDS Issue 15, 2025). À trancher avec le POH de l'avion réel.
3. **Station du train principal** : non publiée dans les extraits lus ; seuls les empattements sont connus. La fiche de pesée (S1 PDF p. 334, image) donne les cotes A et B à mesurer, pas une station fixe.
4. **Porte airstair passagers** : position et cotes non confirmées (fig. 6-4 sheet 2 non rendue).
5. **208B EX** : pas de POH ; MAC supposée identique pour le calcul %MAC.
6. **MZFW** : inexistante dans les documents (aucune limite de masse sans carburant publiée pour 208/208B).
7. **MTOW 9062 lb, winglets, conversions parachutisme** : rien trouvé.
8. **Lecture des figures** : valeurs de stations et cotes lues sur rendus 150 à 200 dpi, texte net ; précision de lecture des graphiques CG ±0.3 in / ±50 lb, mais tous les sommets retenus proviennent du texte du POH ou des TCDS.
