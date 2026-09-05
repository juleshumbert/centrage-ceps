# PAC 750XL (Pacific Aerospace, NZ) : notes masse et centrage

Recherche du 2026-09-05. Toutes les valeurs ci-dessous sont en **lb et pouces (in)** sauf mention contraire : c'est l'unité native du POH. Les pages citées « p.N » sont les pages physiques du fichier PDF `PAC750XL_POH_tmorris.pdf` ; le numéro de page imprimé du POH est donné entre parenthèses (ex. « POH 2-8 »).

Convention de marquage des sources :
- **[OFF]** : lu dans un document officiel (POH approuvé CAA NZ, TCDS EASA).
- **[TIERS]** : site tiers ou page commerciale, non certifié.
- **[DÉDUIT]** : déduction ou lecture de figure faite par moi, avec la précision indiquée.

## 1. Sources

| Réf. | Document | Fichier local | Statut |
|---|---|---|---|
| S1 | Pilot's Operating Handbook PAC 750XL, Pacific Aerospace Ltd, doc AIR2825 (référence donnée par le TCDS EASA), édition 1 déc. 2003, révisions jusqu'au 4 juin 2008 (liste des pages effectives). Approuvé CAA NZ comme AFM, 278 pages. URL : http://data.tmorris.net/aviation/poh/rsv/doc/other-poh/PacificAerospace-PAC750XL-POH.pdf | `PAC750XL_POH_tmorris.pdf` (+ `POH_tmorris.txt`) | [OFF], PDF valide (pdfinfo : 278 pages) |
| S2 | Même POH, compilation plus ancienne (272 pages), URL : https://skydiverdriver.com/pdf/PAC-750-POH.pdf. Sections 2 et 6 identiques à S1 (mêmes dates de révision 17 oct. 2007 et 5 déc. 2006). | `PAC750XL_POH_skydiverdriver.pdf` (+ `POH_skydiverdriver.txt`) | [OFF], PDF valide (272 pages) |
| S3 | TCDS EASA.IM.A.081 Issue 6, 02 févr. 2022, titulaire NZSkydive Ltd trading as Pacific Aerospace. URL : https://www.easa.europa.eu/nl/downloads/7362/en | `EASA_TCDS_IM_A_081.pdf` (+ `EASA_TCDS.txt`) | [OFF], PDF valide (10 pages) |
| S4 | DiverDriver.com, page « PAC 750XL Skydiving Aircraft » (retours de pilotes largueurs). URL : https://diverdriver.com/pac-750xl/ | `diverdriver_pac750xl.html` | [TIERS] |
| S5 | NZAero (constructeur), page commerciale 750XL. URL : https://www.nzaero.com/aircraft/750xl | (pas de fichier, lecture WebFetch) | [TIERS] (page commerciale, pas un document certifié) |
| S6 | Fiche McFarlane Aviation « Pacific Aerospace Corp. 750XL » (1 page). URL : https://www.mcfarlaneaviation.com/documents/1115/pacificaerospacepac750xldatasheet.pdf. En réalité une fiche STC d'hélice MT-Propeller (masse hélice + casserole 117 lb, diamètre 98.4 in) : aucune donnée de centrage avion. | `McFarlane_PAC750XL_datasheet.pdf` | [TIERS], sans intérêt pour le centrage |

Figures rasterisées (200 dpi) depuis S1 :
- `fig_p18-018.png` : POH 1-2, Figure 1-1 « Three view drawing » (dimensions extérieures et surfaces).
- `fig_p42-042.png` : POH 2-8, Figure 2-8 « Centre of Gravity Envelope » (centrogramme).
- `fig_p154-154.png` : POH 6-4, Figure 6-2 « Airplane Arms and Stations » (stations fuselage).
- `fig_p167-167.png` : POH 6-17, Figure 6-6 « Weight and Balance Determination » (même enveloppe, abaque moment/1000).

Documents cherchés mais non obtenus :
- TCDS CAA NZ n° A-14 (https://www.aviation.govt.nz/assets/aircraft/type-certificates/A-14-Rev-19.pdf) : le site renvoie une page anti-robot Incapsula (curl et WebFetch). Le TCDS EASA reprend les mêmes limites et cite le TC A-14 du 23 juil. 2003.
- TCDS FAA : numéro non confirmé (le numéro « A00043CE » suggéré n'a pas pu être vérifié ; aucune recherche ne l'a fait remonter). Certification FAA le 10 mars 2004 d'après les sites tiers.
- Supplément POH n° 5 « Installation of Parachuting Kit » (pages 9-5-1 à 9-5-10, datées 17 oct. 2007 dans la liste des pages effectives, p.271 de S1) : listé mais **absent des deux PDF** (ils s'arrêtent à la page 9-0-10). Idem pour les suppléments 45 et 47 (cargo pod externe, mods PAC/XL/0151 et PAC/XL/0246), 36 (sièges Aero Twin), 56 (soute arrière).
- POH AIR3237 (numéros de série 186 et suivants, réservoirs agrandis) : non trouvé en ligne.
- Brochure Pacific Aerospace sur aeroexpo : HTTP 403.

## 2. Datum et MAC

| Donnée | Valeur | Source |
|---|---|---|
| Datum (référence) | Station fuselage STA 0.00, située **100.21 in en avant du bord d'attaque de l'aile** (2.545 m) | [OFF] S1 p.42 (POH 2-8), p.154 (POH 6-4) ; S3 §A.III.15 |
| LEMAC (bord d'attaque de la MAC) | **100.21 in** en arrière du datum (confondu avec le bord d'attaque de l'aile, section centrale rectangulaire à dièdre 0°) | [OFF] S1 p.42 (POH 2-8) |
| Longueur MAC | **85.584 in** | [OFF] S1 p.42 (POH 2-8) |
| Formule | %MAC = (bras − 100.21) / 85.584 × 100 | [DÉDUIT] vérifiée : redonne 0.3 %, 3.47 %, 13.25 %, 29.67 % du POH |
| Bras négatifs | En avant du datum (hélice à −41.5 in, casserole −47.0 in, moteur −9.6 in) | [OFF] S1 p.162 (liste d'équipement) |
| Mise à niveau | Longitudinale : rivnuts aux STA 147 et 162, côté droit (POH) ; « deux boulons sur les longerons supérieurs en avant de la porte principale gauche » (EASA). Latérale : au travers du longeron principal | [OFF] S1 p.153 (POH 6-3) ; S3 §A.III.16 |

## 3. Masses limites

| Donnée | Valeur | Source |
|---|---|---|
| Masse max au décollage (MTOW) | **7500 lb** (3402 kg) | [OFF] S1 p.42 (POH 2-8) ; S3 §A.III.13 |
| Masse max à l'atterrissage (MLW) | **7125 lb** (3232 kg) | [OFF] S1 p.42 ; S3 §A.III.13 |
| Masse max sans carburant (MZFW) | **non publiée** (ni POH ni TCDS) | [OFF] absence constatée |
| Masse à vide typique (BEW) | 3100 lb, charge utile max 4400 lb « varie selon la masse à vide » | [OFF] S1 p.22 (POH 1-6, « typical airplane weights ») |
| Exemple de pesée du POH | 3128.5 lb à 110.58 in (moment 345 949.5 lb.in), avec L = 125.44 in (empattement) et M = 140.96 in (datum à axe roues principales) | [OFF] S1 p.155 et 156 (POH 6-5, 6-6), exemple illustratif |
| BEW typique en config parachutage | 3300 lb, charge utile 4200 lb ; « 17 parachutistes » ou pilote + 9 pax | [TIERS] S4 |
| Charge plancher par compartiment | STA 82 à 115 : 1200 lb ; STA 115 à 166 : 1200 lb ; STA 166 à 240 : 800 lb | [OFF] S1 p.45 (POH 2-11) ; S3 §A.III.21 (l'EASA écrit 118.0 à 166.0 pour le second) |
| Intensité plancher | STA 82 à 187 : 136 lb/ft² (S/N 101, 102) ou 171 lb/ft² (S/N 104 et suivants) ; STA 187 à 240 (zone de la porte) : 50 lb/ft² | [OFF] S1 p.45 (POH 2-11) |
| Charge max par point d'arrimage | 166 lb (75 kg) | [OFF] S1 p.45 |
| Facteurs de charge | +3.47 / −1.39 g volets rentrés ; +3.0 / 0 g volets sortis | [OFF] S1 p.43 (POH 2-9) |
| Catégorie | Normale (Normal Category), 2 sièges de base, sièges cabine par modification | [OFF] S3 §A.I.2, §A.III.19 et note 4 |

## 4. Stations et bras (in, en arrière du datum)

### 4.1 Occupants et charges (données de chargement)

| Poste | Bras (in) | %MAC | Source |
|---|---|---|---|
| Pilote (et passager avant, sièges réglables) | **66.50** | −39.4 | [OFF] S1 p.171 (POH 6-21, Figure 6-10 « Occupants, Parachute Configuration ») |
| Paras (avec parachute), position 1 | **93.00** | −8.4 | [OFF] S1 p.171, Fig. 6-10 |
| Paras, position 2 | **107.00** | 7.9 | idem |
| Paras, position 3 | **121.00** | 24.3 | idem |
| Paras, position 4 | **135.00** | 40.7 | idem |
| Paras, position 5 | **149.00** | 57.0 | idem |
| Paras, position 6 | **163.00** | 73.4 | idem |
| Paras, position 7 | **177.00** | 89.7 | idem |
| Paras, position 8 | **191.00** | 106.1 | idem |
| Paras, position 9 | **195.00** | 110.8 | idem (second tableau) |
| Paras, position 10 | **209.00** | 127.1 | idem |
| Paras, position 11 | **223.00** | 143.5 | idem |
| Paras, position 12 | **240.00** | 163.3 | idem |
| Sièges passagers Aero Twin (mod PAC/XL/0193), 8 places | 2 à **104.34**, 2 à **144.43**, 2 à **178.32**, 2 à **226.76** | | [OFF] S3 note 4.1 |
| Idem avec sièges équipage Millennium (mod PAC/XL/0440) | 2 à **105.34**, 2 à 144.43, 2 à 178.32, 2 à 226.76 | | [OFF] S3 note 4.2 |
| Carburant réservoirs avant | **110.21** | | [OFF] S1 p.170 (Fig. 6-9) |
| Carburant réservoirs arrière | **139.15** | | [OFF] S1 p.170 (Fig. 6-9) |
| Cargo pod ventral (mods PAC/XL/0151 et 0246) | **non trouvé** (suppléments 45 et 47 absents du PDF) ; capacité commerciale 1000 lb, 70 cu ft | [TIERS] S5 pour la capacité |
| Soute arrière (supplément 56 « Aft Stowage Compartment ») | bras non trouvé ; 18 cu ft | [TIERS] S5 pour le volume |

Remarques sur la Figure 6-10 : le pas entre positions est de 14 in de 93 à 191 in, puis un second tableau donne 195, 209, 223 et 240 in. Le POH ne précise pas comment les 17 paras se répartissent entre ces 12 bras (le supplément parachutage manque). Le tableau couvre des masses individuelles de 120 à 215 lb (moment/1000 = masse × bras / 1000, vérifié : 200 lb à 93 in = 18.60). La feuille de chargement Figure 6-7 (p.168) prévoit 8 lignes « Cargo/Parachutists ».

### 4.2 Stations structurales (Figure 6-2, p.154, lecture de la figure, valeurs imprimées en clair)

| Station | Signification | Source |
|---|---|---|
| 0.00 | Datum | [OFF] Fig. 6-2 |
| 16.4 | Axe roue de nez (bras de la roue de nez dans la liste d'équipement) | [OFF] S1 p.162 |
| 42.94 | Cloison pare-feu / avant du cockpit (position sur la figure, en avant du pare-brise) | [OFF] Fig. 6-2 ; rôle [DÉDUIT] |
| 82.34 | Début du compartiment cargo / cabine (derrière les sièges pilotes), cohérent avec « STA 82 » des limites plancher | [OFF] Fig. 6-2 et p.45 |
| 100.21 | Bord d'attaque de l'aile = LEMAC | [OFF] |
| 115.34 et 118.84 | Cadres au niveau de l'aile (limite de compartiment « STA 115 », l'EASA écrit 118.0) | [OFF] Fig. 6-2 |
| 141.42 | Axe des roues principales (141.4 dans la liste d'équipement) | [OFF] Fig. 6-2 et p.162 |
| 166.53 | Cadre, limite de compartiment « STA 166 » | [OFF] |
| 187.00 | Cadre avant de la porte cargo (début de la zone « adjacent to door ») | [OFF] Fig. 6-2 et p.45 ; rôle [DÉDUIT] |
| 237.00 | Cadre arrière de la porte cargo | [OFF] Fig. 6-2 ; rôle [DÉDUIT] |
| 240.08 | Cloison arrière de cabine (fin du compartiment cargo « STA 240 ») | [OFF] Fig. 6-2 et p.45 |
| 270.0 | Batterie arrière (liste d'équipement) | [OFF] S1 p.163 |
| 312.0 | Moteur de trim de profondeur | [OFF] S1 p.163 |
| 399.6 | Feu de queue (extrémité arrière) | [OFF] S1 p.163 |

## 5. Carburant

Réservoirs standard (S/N 101 à 185 sauf 177), quatre réservoirs structuraux d'aile [OFF] S1 p.43 (POH 2-9, Figure 2-9) et S3 §A.III.9.1.1 :

| Réservoir | Capacité totale | Inutilisable | Utilisable |
|---|---|---|---|
| Avant gauche (inclut le sump 26 L) | 284 L, 499 lb, 75 US gal | 10 L, 18 lb | 274 L, 481 lb, 72 US gal |
| Avant droit | 293 L, 515 lb, 77 US gal | 10 L, 18 lb | 283 L, 497 lb, 74 US gal |
| Arrière gauche | 142 L, 249 lb, 37.5 US gal | 0 | 142 L, 249 lb |
| Arrière droit | 142 L, 249 lb, 37.5 US gal | 0 | 142 L, 249 lb |
| Total | 861 L, 1512 lb, 227 US gal | 20 L, 36 lb | **841 L, 1476 lb, 221 US gal** |

- Bras : **avant 110.21 in, arrière 139.15 in, constants quelle que soit la quantité** (tableau Figure 6-9, p.170 ; le moment est strictement proportionnel à la masse). Densité utilisée par le POH : 1.76 lb/L (40 L = 70.4 lb), soit 6.7 lb/US gal.
- Séquence : les réservoirs avant doivent être pleins avant de remplir les arrière ; le carburant arrière est consommé en premier ; le CG avance donc pendant la vidange des arrière (S1 p.166, POH 6-16).
- Placard : déséquilibre max 100 L ; utilisable avant 557 L, arrière 284 L (S1 p.50).
- Pratique parachutage [TIERS] S4 : garder entre 850 lb max et 250 lb min, soit environ 6 rotations.
- Réservoirs agrandis (mod PAC/XL/0448, S/N 177 et 186 et suivants) [OFF] S3 §9.1.2 : total 1288 L / 2267 lb, utilisable 1256 L / 2210 lb (avant 180 L utilisables chacun, arrière 448 L utilisables chacun). **Bras non trouvés** pour cette configuration (POH AIR3237 non obtenu).

## 6. Enveloppe de centrage (centrogramme)

### 6.1 Configuration standard (S/N 101 à 185 sauf 177), catégorie Normale, toutes configurations

Le POH ne publie **qu'une seule enveloppe**, valable pour toutes les configurations (passagers, cargo, parachutage). Aucune enveloppe distincte « avec cargo pod » n'est disponible (supplément absent). Sommets donnés en clair dans le texte [OFF] S1 p.42 (POH 2-8) et p.157 (POH 6-7), confirmés par S3 §A.III.14.1 ; la figure 2-8 (fichier `fig_p42-042.png`) trace exactement ces points.

| Sommet | Masse (lb) | Bras (in) | %MAC (POH) | %MAC recalculé | Remarque |
|---|---|---|---|---|---|
| A | 4209 et moins | 100.46 | 0.3 | 0.29 | limite avant verticale sous 4209 lb |
| B | 5639 | 103.18 | 3.47 | 3.47 | |
| C | 7500 | 111.55 | 13.25 | 13.25 | limite avant à MTOW |
| D | 7500 | 125.60 | 29.67 | 29.67 | limite arrière à MTOW |
| E | toutes masses | 125.60 | 29.67 | 29.67 | limite arrière verticale |

Variation linéaire entre A, B et C. La figure va de 3000 lb (bas du graphe, ce n'est pas une limite certifiée) à 7600 lb ; la ligne MLW 7125 lb est tracée en pointillé. Précision de lecture de la figure : inutile, les valeurs sont imprimées en clair sur le graphe et dans le texte.

Polygone fermé proposé pour le tracé (bas borné à 3000 lb, arbitraire) : (3000, 100.46), (4209, 100.46), (5639, 103.18), (7500, 111.55), (7500, 125.60), (3000, 125.60).

### 6.2 Configuration réservoirs agrandis (mod PAC/XL/0448, S/N 177, 186 et suivants) [OFF] S3 §A.III.14.2

| Sommet | Masse (lb) | Bras (in) | %MAC recalculé |
|---|---|---|---|
| A' | 4209 (1909 kg) | 102.18 (2.60 m) | 2.30 |
| B' | 5639 (2558 kg) | 104.90 (2.66 m) | 5.48 |
| C' | 7500 (3402 kg) | 113.27 (2.88 m) | 15.26 |
| Arrière | toutes masses | 124.60 (3.17 m) | 28.50 |

### 6.3 Exemple d'utilisation donné par le POH
À 6187 lb et 720 moment/1000, CG à 116.4 in (S1 p.42 et p.167).

## 7. Dimensions cabine, portes et extérieures

### 7.1 Extérieur [OFF] S1 p.18 (POH 1-2, Figure 1-1, lecture du PNG, cotes imprimées en clair) et S3 §A.III.4

| Donnée | Valeur |
|---|---|
| Envergure | 42 ft 0 in (12.80 m) |
| Longueur | 38 ft 10 in (11.84 m) |
| Hauteur | 13 ft 3 in (4.04 m) |
| Envergure empennage horizontal | 16 ft 3 in (4.95 m) |
| Voie du train principal | 12 ft 1 in (3.68 m) |
| Empattement | 10 ft 5 in (3.17 m) = 125 in ; cohérent avec 141.42 − 16.4 = 125.0 in |
| Diamètre hélice | 106.00 in (2692 mm) |
| Cote « 5 ft 0 in (1.52 m) » sur la vue de face | depuis l'axe, probablement demi-largeur de la section centrale d'aile [DÉDUIT, incertain] |
| Surfaces | aile brute 305.0 ft², aile nette 267.8 ft², volets 31.74, ailerons 21.94, plan fixe 33.64, gouverne de profondeur 27.92, dérive 19.40, gouverne de direction 11.70 ft² |
| Charge alaire | 24.59 lb/ft² (= 7500 / 305) |
| Dièdre | 0° section centrale, 8° panneaux externes ; calage 2° (S1 p.22) |
| Garde hélice | 7 in mini (S1 p.18) |

### 7.2 Cabine et porte [OFF] S1 p.22 (POH 1-6, §1.9) et p.194 (POH 7-16, §7.11)

| Donnée | Valeur | Source et remarque |
|---|---|---|
| Largeur cabine max | **54 in** | S1 p.22 |
| Longueur cabine | **158 in** (de derrière le siège pilote à la cloison arrière) | S1 p.22 |
| Hauteur cabine max | **56 in** | S1 p.22 |
| Largeur d'entrée (porte) | 50 in à 48 in selon le type de porte | S1 p.22 |
| Hauteur d'entrée | 47 in à 45 in à l'avant du cadre ; 41.3 in à 39.3 in à l'arrière du cadre | S1 p.22 |
| Hauteur du seuil | 44 in (amortisseurs détendus) | S1 p.22 |
| Porte passagers/cargo | côté gauche, derrière le bord de fuite de l'aile, env. **48 × 41 in**, panneaux aluminium imbriqués, coulisse vers le haut sur deux rails (porte à rouleau), ouvrable de l'intérieur et de l'extérieur, voyant DOOR UNSAFE | S1 p.194 ; S4 confirme : « environ 50 in de large, 47 in de haut à l'avant, 41 à l'arrière », s'ouvre en vol |
| Position longitudinale de la porte | STA **187.00 à 237.00** (50 in) | [DÉDUIT] : cadres 187.00 et 237.00 encadrent le dessin de la porte sur la Figure 6-2, zone plancher « adjacent to door STA 187 à 240 », largeur 50 in cohérente avec l'entrée. Précision estimée ±2 in |
| Étendue du plancher cabine | STA **82.34 à 240.08** (157.7 in) | [DÉDUIT] : 240.08 − 82.34 = 157.7 in, égal aux 158 in de longueur cabine ; compartiments plancher 82 à 240 |
| Bord d'attaque aile | STA 100.21 (soit 18 in en arrière du début de cabine) | [OFF] |
| Axe roues principales | STA 141.42 ; roue de nez STA 16.4 | [OFF] |
| Largeur au plancher | **non trouvée** (seule la largeur max 54 in est publiée) | |
| Volume cabine | 240 cu ft ; cargo pod 70 cu ft / 1000 lb ; soute arrière 18 cu ft | [TIERS] S5 |
| Capacité | 17 paras ou 6 équipes tandem ; 10 places (1 + 9) en version passagers | [TIERS] S5, S4 |
| Fenêtres | 3 par côté dans le compartiment cargo | [OFF] S1 p.193 |

## 8. Points ouverts et incertitudes

1. **Supplément 5 « Installation of Parachuting Kit »** absent : la répartition officielle des 17 paras sur les 12 bras de la Figure 6-10, les éventuels bancs, la main courante et les limitations propres au largage (porte ouverte, vitesses) ne sont pas disponibles. Les bras 93 à 240 in de la Figure 6-10 sont officiels mais leur affectation aux places reste à confirmer.
2. **Cargo pod ventral** : aucun bras ni enveloppe spécifique (suppléments 45 et 47 absents). Seule la capacité commerciale (1000 lb, 70 cu ft) est connue [TIERS].
3. **MZFW** : non publiée.
4. **Largeur cabine au plancher** et section transversale exacte : non trouvées (largeur max 54 in seulement).
5. **Position du bord de fuite de l'aile** et corde de l'emplanture : non trouvées (seule la MAC 85.584 in est donnée ; la porte est « derrière le bord de fuite », donc bord de fuite en avant de STA 187).
6. **Réservoirs agrandis (mod 0448)** : capacités et enveloppe connues via l'EASA, mais bras carburant inconnus (POH AIR3237 non obtenu).
7. **TCDS CAA NZ A-14** inaccessible (protection anti-robot) ; **TCDS FAA** : numéro non confirmé.
8. Le TCDS EASA donne la limite basse du 2e compartiment plancher à 118.0 in alors que le POH dit 115 in (cadres 115.34 et 118.84 tous deux présents sur la Figure 6-2).
9. L'exemple de pesée du POH (3128.5 lb, 110.58 in) est illustratif et ne doit pas être pris pour la masse à vide d'un avion réel. La BEW réelle d'un avion largueur se situe plutôt vers 3300 lb [TIERS].
10. La fiche McFarlane (S6) est une fiche STC d'hélice MT-Propeller : elle ne contient aucune donnée de centrage avion et peut être ignorée.
