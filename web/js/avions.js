// Genere par web/tools/gen_avions.py depuis avions/*/planches_club.json et avions/*/envelope.json.
// Ne pas editer a la main : corriger la source puis relancer le script. Aucune immatriculation ici.
export const AVIONS = [
 {
  "id": "c208b-A",
  "libelle": "Caravan 208B · avion A",
  "type": "Cessna 208B Grand Caravan",
  "famille": "c208b",
  "unites": {
   "masse": "lb",
   "bras": "in",
   "carburant": "lb"
  },
  "kg_par_unite_masse": 0.45359290943563974,
  "masse_vide": 4890,
  "bras_vide": 188.99,
  "mac": {
   "lemac": 177.57,
   "longueur": 66.4
  },
  "pilote": {
   "bras": 135.5,
   "masse_kg_defaut": 80
  },
  "carburant": {
   "capacite": 2224,
   "par_rotation": 120,
   "reserve": 200,
   "defaut": 900,
   "table": [
    [
     34.0,
     200.0
    ],
    [
     67.0,
     202.99
    ],
    [
     101.0,
     201.98
    ],
    [
     134.0,
     202.99
    ],
    [
     168.0,
     202.38
    ],
    [
     201.0,
     202.99
    ],
    [
     235.0,
     202.55
    ],
    [
     268.0,
     202.99
    ],
    [
     302.0,
     202.65
    ],
    [
     335.0,
     202.99
    ],
    [
     369.0,
     202.71
    ],
    [
     402.0,
     202.99
    ],
    [
     436.0,
     202.75
    ],
    [
     469.0,
     202.99
    ],
    [
     503.0,
     202.78
    ],
    [
     536.0,
     202.99
    ],
    [
     570.0,
     202.98
    ],
    [
     603.0,
     203.15
    ],
    [
     637.0,
     202.98
    ],
    [
     670.0,
     203.13
    ],
    [
     704.0,
     202.98
    ],
    [
     737.0,
     203.12
    ],
    [
     771.0,
     203.11
    ],
    [
     804.0,
     203.23
    ],
    [
     838.0,
     203.1
    ],
    [
     871.0,
     203.21
    ],
    [
     905.0,
     203.09
    ],
    [
     938.0,
     203.2
    ],
    [
     972.0,
     203.19
    ],
    [
     1039.0,
     203.18
    ],
    [
     1072.0,
     203.26
    ],
    [
     1139.0,
     203.25
    ],
    [
     1173.0,
     203.24
    ],
    [
     1206.0,
     203.32
    ],
    [
     1240.0,
     203.23
    ],
    [
     1273.0,
     203.3
    ],
    [
     1307.0,
     203.29
    ],
    [
     1340.0,
     203.36
    ],
    [
     1374.0,
     203.28
    ],
    [
     1407.0,
     203.34
    ],
    [
     1441.0,
     203.26
    ],
    [
     1474.0,
     203.32
    ],
    [
     1508.0,
     203.25
    ],
    [
     1541.0,
     203.31
    ],
    [
     1575.0,
     203.24
    ],
    [
     1608.0,
     203.3
    ],
    [
     1642.0,
     203.23
    ],
    [
     1675.0,
     203.28
    ],
    [
     1709.0,
     203.22
    ],
    [
     1742.0,
     203.27
    ],
    [
     1776.0,
     203.21
    ],
    [
     1809.0,
     203.26
    ],
    [
     1843.0,
     203.2
    ],
    [
     1876.0,
     203.2
    ],
    [
     1910.0,
     203.14
    ],
    [
     1943.0,
     203.19
    ],
    [
     1977.0,
     203.14
    ],
    [
     2010.0,
     203.18
    ],
    [
     2044.0,
     203.13
    ],
    [
     2077.0,
     203.18
    ],
    [
     2144.0,
     203.17
    ],
    [
     2178.0,
     203.12
    ],
    [
     2189.0,
     203.15
    ],
    [
     2211.0,
     203.12
    ],
    [
     2224.0,
     203.1
    ]
   ]
  },
  "porte": {
   "x": 307.0,
   "y": -32.0,
   "cote": "gauche"
  },
  "places": [
   {
    "id": "COPI",
    "x": 135.5,
    "y": 16.0,
    "copilote": true
   },
   {
    "id": "D1",
    "x": 155.4,
    "y": 16.0
   },
   {
    "id": "D2",
    "x": 180.7,
    "y": 16.0
   },
   {
    "id": "D3",
    "x": 205.9,
    "y": 16.0
   },
   {
    "id": "D4",
    "x": 231.2,
    "y": 16.0
   },
   {
    "id": "D5",
    "x": 256.5,
    "y": 16.0
   },
   {
    "id": "D6",
    "x": 281.7,
    "y": 16.0
   },
   {
    "id": "D7",
    "x": 307.0,
    "y": 16.0
   },
   {
    "id": "C1",
    "x": 168.0,
    "y": 0.0,
    "centre": true
   },
   {
    "id": "C2",
    "x": 199.6,
    "y": 0.0,
    "centre": true
   },
   {
    "id": "C3",
    "x": 231.2,
    "y": 0.0,
    "centre": true
   },
   {
    "id": "C4",
    "x": 262.8,
    "y": 0.0,
    "centre": true
   },
   {
    "id": "C5",
    "x": 294.4,
    "y": 0.0,
    "centre": true
   },
   {
    "id": "G1",
    "x": 155.4,
    "y": -16.0
   },
   {
    "id": "G2",
    "x": 180.7,
    "y": -16.0
   },
   {
    "id": "G3",
    "x": 205.9,
    "y": -16.0
   },
   {
    "id": "G4",
    "x": 231.2,
    "y": -16.0
   },
   {
    "id": "G5",
    "x": 256.5,
    "y": -16.0
   },
   {
    "id": "G6",
    "x": 281.7,
    "y": -16.0
   },
   {
    "id": "G7",
    "x": 307.0,
    "y": -16.0
   }
  ],
  "rangees": [
   {
    "id": "D",
    "libelle": "droite",
    "y": 16.0,
    "xmin": 128.0,
    "xmax": 352.0
   },
   {
    "id": "C",
    "libelle": "centre",
    "y": 0.0,
    "xmin": 140.0,
    "xmax": 352.0
   },
   {
    "id": "G",
    "libelle": "gauche",
    "y": -16.0,
    "xmin": 154.0,
    "xmax": 352.0
   }
  ],
  "cabine": {
   "x0": 100.0,
   "x1": 356.0,
   "zones": [
    {
     "nom": "ZONE 0",
     "x0": 118.0,
     "x1": 155.4,
     "largeur": 53.0
    },
    {
     "nom": "ZONE 1",
     "x0": 155.4,
     "x1": 188.7,
     "largeur": 62.0
    },
    {
     "nom": "ZONE 2",
     "x0": 188.7,
     "x1": 246.8,
     "largeur": 62.0
    },
    {
     "nom": "ZONE 3",
     "x0": 246.8,
     "x1": 282.0,
     "largeur": 64.0
    },
    {
     "nom": "ZONE 4",
     "x0": 282.0,
     "x1": 307.0,
     "largeur": 57.0
    },
    {
     "nom": "ZONE 5",
     "x0": 307.0,
     "x1": 332.0,
     "largeur": 53.0
    },
    {
     "nom": "ZONE 6",
     "x0": 332.0,
     "x1": 356.0,
     "largeur": 46.0
    },
    {
     "nom": "ZONE -1",
     "x0": 100.0,
     "x1": 118.0,
     "largeur": 53.0
    }
   ],
   "porte": {
    "x0": 282.0,
    "x1": 332.0,
    "cote": "gauche"
   }
  },
  "variantes": [
   {
    "id": "poh",
    "libelle": "POH, MTOW 8750 lb",
    "mtow": 8750,
    "enveloppe": {
     "avant": [
      [
       5500.0,
       179.6
      ],
      [
       8000.0,
       193.37
      ],
      [
       8750.0,
       199.15
      ]
     ],
     "arriere": [
      [
       0.0,
       204.35
      ],
      [
       8750.0,
       204.35
      ]
     ]
    },
    "source": "POH 208BPHBUS-00 p.2-13 (PDF p.53) text and Fig. 6-17 (PDF p.381); FAA TCDS A37CE Rev22 p.5"
   },
   {
    "id": "ape2",
    "libelle": "APE II : STC SA00392SE, MTOW 9062 lb",
    "mtow": 9062,
    "enveloppe": {
     "avant": [
      [
       5500.0,
       179.6
      ],
      [
       8000.0,
       193.37
      ],
      [
       8750.0,
       199.15
      ],
      [
       9062.0,
       200.23
      ]
     ],
     "arriere": [
      [
       0.0,
       204.35
      ],
      [
       9062.0,
       204.35
      ]
     ]
    },
    "source": "avions/c208b/stc_ape.json : Aircraft Payload Extender II (APE II), STC FAA SA00392SE ; limites CG du rapport TSB A14W0181 (limite avant prolongee jusqu'a 200.23 in a 9062 lb, arriere 204.35 in)"
   },
   {
    "id": "ape3",
    "libelle": "APE III : STC SA01213SE, MTOW 9062 lb, MLW 9000 lb",
    "mtow": 9062,
    "enveloppe": {
     "avant": [
      [
       5500.0,
       179.6
      ],
      [
       8000.0,
       193.37
      ],
      [
       8750.0,
       199.15
      ],
      [
       9062.0,
       200.23
      ]
     ],
     "arriere": [
      [
       0.0,
       204.35
      ],
      [
       9062.0,
       204.35
      ]
     ]
    },
    "source": "avions/c208b/stc_ape.json : Aircraft Payload Extender III (APE III), STC FAA SA01213SE ; limites CG du rapport TSB A14W0181 (limite avant prolongee jusqu'a 200.23 in a 9062 lb, arriere 204.35 in) ; MLW 9000 lb (non modelisee ici)"
   },
   {
    "id": "planches",
    "libelle": "Planches club (MTOW 9062 lb, limite avant des planches)",
    "mtow": 9062,
    "enveloppe": {
     "avant": [
      [
       5500,
       179.6
      ],
      [
       8000,
       193.37
      ],
      [
       9062,
       199.15
      ]
     ],
     "arriere": [
      [
       0,
       204.35
      ],
      [
       9062,
       204.35
      ]
     ]
    },
    "source": "planches club (avions/c208b/planches_club.json) : limite avant interpolee de (8000, 193.37) a (9062, 199.15), moins restrictive que le STC APE II au-dessus de 8000 lb",
    "a_verifier": true
   }
  ],
  "variante_defaut": "ape2",
  "source": "avions/c208b/planches_club.json (planches club) ; porte cargo FS 282 a 332 (POH 208B)"
 },
 {
  "id": "c208b-B",
  "libelle": "Caravan 208B · avion B",
  "type": "Cessna 208B Grand Caravan",
  "famille": "c208b",
  "unites": {
   "masse": "lb",
   "bras": "in",
   "carburant": "lb"
  },
  "kg_par_unite_masse": 0.45359290943563974,
  "masse_vide": 4986,
  "bras_vide": 186.54,
  "mac": {
   "lemac": 177.57,
   "longueur": 66.4
  },
  "pilote": {
   "bras": 135.5,
   "masse_kg_defaut": 80
  },
  "carburant": {
   "capacite": 2224,
   "par_rotation": 120,
   "reserve": 200,
   "defaut": 900,
   "table": [
    [
     34.0,
     200.0
    ],
    [
     67.0,
     202.99
    ],
    [
     101.0,
     201.98
    ],
    [
     134.0,
     202.99
    ],
    [
     168.0,
     202.38
    ],
    [
     201.0,
     202.99
    ],
    [
     235.0,
     202.55
    ],
    [
     268.0,
     202.99
    ],
    [
     302.0,
     202.65
    ],
    [
     335.0,
     202.99
    ],
    [
     369.0,
     202.71
    ],
    [
     402.0,
     202.99
    ],
    [
     436.0,
     202.75
    ],
    [
     469.0,
     202.99
    ],
    [
     503.0,
     202.78
    ],
    [
     536.0,
     202.99
    ],
    [
     570.0,
     202.98
    ],
    [
     603.0,
     203.15
    ],
    [
     637.0,
     202.98
    ],
    [
     670.0,
     203.13
    ],
    [
     704.0,
     202.98
    ],
    [
     737.0,
     203.12
    ],
    [
     771.0,
     203.11
    ],
    [
     804.0,
     203.23
    ],
    [
     838.0,
     203.1
    ],
    [
     871.0,
     203.21
    ],
    [
     905.0,
     203.09
    ],
    [
     938.0,
     203.2
    ],
    [
     972.0,
     203.19
    ],
    [
     1039.0,
     203.18
    ],
    [
     1072.0,
     203.26
    ],
    [
     1139.0,
     203.25
    ],
    [
     1173.0,
     203.24
    ],
    [
     1206.0,
     203.32
    ],
    [
     1240.0,
     203.23
    ],
    [
     1273.0,
     203.3
    ],
    [
     1307.0,
     203.29
    ],
    [
     1340.0,
     203.36
    ],
    [
     1374.0,
     203.28
    ],
    [
     1407.0,
     203.34
    ],
    [
     1441.0,
     203.26
    ],
    [
     1474.0,
     203.32
    ],
    [
     1508.0,
     203.25
    ],
    [
     1541.0,
     203.31
    ],
    [
     1575.0,
     203.24
    ],
    [
     1608.0,
     203.3
    ],
    [
     1642.0,
     203.23
    ],
    [
     1675.0,
     203.28
    ],
    [
     1709.0,
     203.22
    ],
    [
     1742.0,
     203.27
    ],
    [
     1776.0,
     203.21
    ],
    [
     1809.0,
     203.26
    ],
    [
     1843.0,
     203.2
    ],
    [
     1876.0,
     203.2
    ],
    [
     1910.0,
     203.14
    ],
    [
     1943.0,
     203.19
    ],
    [
     1977.0,
     203.14
    ],
    [
     2010.0,
     203.18
    ],
    [
     2044.0,
     203.13
    ],
    [
     2077.0,
     203.18
    ],
    [
     2144.0,
     203.17
    ],
    [
     2178.0,
     203.12
    ],
    [
     2189.0,
     203.15
    ],
    [
     2211.0,
     203.12
    ],
    [
     2224.0,
     203.1
    ]
   ]
  },
  "porte": {
   "x": 307.0,
   "y": -32.0,
   "cote": "gauche"
  },
  "places": [
   {
    "id": "COPI",
    "x": 135.5,
    "y": 16.0,
    "copilote": true
   },
   {
    "id": "D1",
    "x": 155.4,
    "y": 16.0
   },
   {
    "id": "D2",
    "x": 180.7,
    "y": 16.0
   },
   {
    "id": "D3",
    "x": 205.9,
    "y": 16.0
   },
   {
    "id": "D4",
    "x": 231.2,
    "y": 16.0
   },
   {
    "id": "D5",
    "x": 256.5,
    "y": 16.0
   },
   {
    "id": "D6",
    "x": 281.7,
    "y": 16.0
   },
   {
    "id": "D7",
    "x": 307.0,
    "y": 16.0
   },
   {
    "id": "C1",
    "x": 168.0,
    "y": 0.0,
    "centre": true
   },
   {
    "id": "C2",
    "x": 199.6,
    "y": 0.0,
    "centre": true
   },
   {
    "id": "C3",
    "x": 231.2,
    "y": 0.0,
    "centre": true
   },
   {
    "id": "C4",
    "x": 262.8,
    "y": 0.0,
    "centre": true
   },
   {
    "id": "C5",
    "x": 294.4,
    "y": 0.0,
    "centre": true
   },
   {
    "id": "G1",
    "x": 155.4,
    "y": -16.0
   },
   {
    "id": "G2",
    "x": 180.7,
    "y": -16.0
   },
   {
    "id": "G3",
    "x": 205.9,
    "y": -16.0
   },
   {
    "id": "G4",
    "x": 231.2,
    "y": -16.0
   },
   {
    "id": "G5",
    "x": 256.5,
    "y": -16.0
   },
   {
    "id": "G6",
    "x": 281.7,
    "y": -16.0
   },
   {
    "id": "G7",
    "x": 307.0,
    "y": -16.0
   }
  ],
  "rangees": [
   {
    "id": "D",
    "libelle": "droite",
    "y": 16.0,
    "xmin": 128.0,
    "xmax": 352.0
   },
   {
    "id": "C",
    "libelle": "centre",
    "y": 0.0,
    "xmin": 140.0,
    "xmax": 352.0
   },
   {
    "id": "G",
    "libelle": "gauche",
    "y": -16.0,
    "xmin": 154.0,
    "xmax": 352.0
   }
  ],
  "cabine": {
   "x0": 100.0,
   "x1": 356.0,
   "zones": [
    {
     "nom": "ZONE 0",
     "x0": 118.0,
     "x1": 155.4,
     "largeur": 53.0
    },
    {
     "nom": "ZONE 1",
     "x0": 155.4,
     "x1": 188.7,
     "largeur": 62.0
    },
    {
     "nom": "ZONE 2",
     "x0": 188.7,
     "x1": 246.8,
     "largeur": 62.0
    },
    {
     "nom": "ZONE 3",
     "x0": 246.8,
     "x1": 282.0,
     "largeur": 64.0
    },
    {
     "nom": "ZONE 4",
     "x0": 282.0,
     "x1": 307.0,
     "largeur": 57.0
    },
    {
     "nom": "ZONE 5",
     "x0": 307.0,
     "x1": 332.0,
     "largeur": 53.0
    },
    {
     "nom": "ZONE 6",
     "x0": 332.0,
     "x1": 356.0,
     "largeur": 46.0
    },
    {
     "nom": "ZONE -1",
     "x0": 100.0,
     "x1": 118.0,
     "largeur": 53.0
    }
   ],
   "porte": {
    "x0": 282.0,
    "x1": 332.0,
    "cote": "gauche"
   }
  },
  "variantes": [
   {
    "id": "poh",
    "libelle": "POH, MTOW 8750 lb",
    "mtow": 8750,
    "enveloppe": {
     "avant": [
      [
       5500.0,
       179.6
      ],
      [
       8000.0,
       193.37
      ],
      [
       8750.0,
       199.15
      ]
     ],
     "arriere": [
      [
       0.0,
       204.35
      ],
      [
       8750.0,
       204.35
      ]
     ]
    },
    "source": "POH 208BPHBUS-00 p.2-13 (PDF p.53) text and Fig. 6-17 (PDF p.381); FAA TCDS A37CE Rev22 p.5"
   },
   {
    "id": "ape2",
    "libelle": "APE II : STC SA00392SE, MTOW 9062 lb",
    "mtow": 9062,
    "enveloppe": {
     "avant": [
      [
       5500.0,
       179.6
      ],
      [
       8000.0,
       193.37
      ],
      [
       8750.0,
       199.15
      ],
      [
       9062.0,
       200.23
      ]
     ],
     "arriere": [
      [
       0.0,
       204.35
      ],
      [
       9062.0,
       204.35
      ]
     ]
    },
    "source": "avions/c208b/stc_ape.json : Aircraft Payload Extender II (APE II), STC FAA SA00392SE ; limites CG du rapport TSB A14W0181 (limite avant prolongee jusqu'a 200.23 in a 9062 lb, arriere 204.35 in)"
   },
   {
    "id": "ape3",
    "libelle": "APE III : STC SA01213SE, MTOW 9062 lb, MLW 9000 lb",
    "mtow": 9062,
    "enveloppe": {
     "avant": [
      [
       5500.0,
       179.6
      ],
      [
       8000.0,
       193.37
      ],
      [
       8750.0,
       199.15
      ],
      [
       9062.0,
       200.23
      ]
     ],
     "arriere": [
      [
       0.0,
       204.35
      ],
      [
       9062.0,
       204.35
      ]
     ]
    },
    "source": "avions/c208b/stc_ape.json : Aircraft Payload Extender III (APE III), STC FAA SA01213SE ; limites CG du rapport TSB A14W0181 (limite avant prolongee jusqu'a 200.23 in a 9062 lb, arriere 204.35 in) ; MLW 9000 lb (non modelisee ici)"
   },
   {
    "id": "planches",
    "libelle": "Planches club (MTOW 9062 lb, limite avant des planches)",
    "mtow": 9062,
    "enveloppe": {
     "avant": [
      [
       5500,
       179.6
      ],
      [
       8000,
       193.37
      ],
      [
       9062,
       199.15
      ]
     ],
     "arriere": [
      [
       0,
       204.35
      ],
      [
       9062,
       204.35
      ]
     ]
    },
    "source": "planches club (avions/c208b/planches_club.json) : limite avant interpolee de (8000, 193.37) a (9062, 199.15), moins restrictive que le STC APE II au-dessus de 8000 lb",
    "a_verifier": true
   }
  ],
  "variante_defaut": "ape2",
  "source": "avions/c208b/planches_club.json (planches club) ; porte cargo FS 282 a 332 (POH 208B)"
 },
 {
  "id": "pc6-A",
  "libelle": "Pilatus PC-6 B2-H4 · avion A",
  "type": "Pilatus PC-6/B2-H4",
  "famille": "pc6",
  "unites": {
   "masse": "kg",
   "bras": "m",
   "carburant": "L"
  },
  "kg_par_unite_masse": 1.0,
  "masse_vide": 1365,
  "bras_vide": 3.396,
  "mac": {
   "lemac": 3.0,
   "longueur": 1.9
  },
  "pilote": {
   "bras": 3.05,
   "masse_kg_defaut": 80
  },
  "carburant": {
   "capacite": 640,
   "par_rotation": 50,
   "reserve": 70,
   "defaut": 250,
   "kg_par_litre": 0.805469235550031,
   "table": [
    [
     129.6,
     4.03
    ],
    [
     259.2,
     3.93
    ],
    [
     388.9,
     3.917
    ],
    [
     518.5,
     3.93
    ]
   ]
  },
  "porte": {
   "x": 5.3,
   "y": 0.9,
   "cote": "droite"
  },
  "places": [
   {
    "id": "D1",
    "x": 2.9,
    "y": 0.45
   },
   {
    "id": "D2",
    "x": 3.4,
    "y": 0.45
   },
   {
    "id": "D3",
    "x": 3.9,
    "y": 0.45
   },
   {
    "id": "D4",
    "x": 4.4,
    "y": 0.45
   },
   {
    "id": "D5",
    "x": 5.2,
    "y": 0.45
   },
   {
    "id": "G1",
    "x": 3.4,
    "y": -0.45
   },
   {
    "id": "G2",
    "x": 3.875,
    "y": -0.45
   },
   {
    "id": "G3",
    "x": 4.35,
    "y": -0.45
   },
   {
    "id": "G4",
    "x": 4.825,
    "y": -0.45
   },
   {
    "id": "G5",
    "x": 5.3,
    "y": -0.45
   }
  ],
  "rangees": [
   {
    "id": "D",
    "libelle": "droite",
    "y": 0.45,
    "xmin": 2.6,
    "xmax": 5.65
   },
   {
    "id": "G",
    "libelle": "gauche",
    "y": -0.45,
    "xmin": 3.3,
    "xmax": 5.65
   }
  ],
  "cabine": {
   "x0": 2.5,
   "x1": 5.7,
   "zones": [
    {
     "nom": "cabine",
     "x0": 2.5,
     "x1": 5.7,
     "largeur": 1.16
    }
   ],
   "porte": {
    "x0": 4.2,
    "x1": 5.5,
    "cote": "droite"
   }
  },
  "variantes": [
   {
    "id": "afm",
    "libelle": "AFM B2-H4, MTOW 2800 kg",
    "mtow": 2800,
    "enveloppe": {
     "avant": [
      [
       1450,
       3.209
      ],
      [
       2800,
       3.608
      ]
     ],
     "arriere": [
      [
       0,
       3.722
      ],
      [
       2800,
       3.722
      ]
     ]
    },
    "source": "planches club, identique au TCDS OFAC F 56-10"
   }
  ],
  "variante_defaut": "afm",
  "source": "avions/pc6-b2h4/planches_club.json (planches club) ; cabine et porte : ordre de grandeur, voir avions/pc6-b2h4/notes.md"
 },
 {
  "id": "pc6-B",
  "libelle": "Pilatus PC-6 B2-H4 · avion B",
  "type": "Pilatus PC-6/B2-H4",
  "famille": "pc6",
  "unites": {
   "masse": "kg",
   "bras": "m",
   "carburant": "L"
  },
  "kg_par_unite_masse": 1.0,
  "masse_vide": 1355.5,
  "bras_vide": 3.424,
  "mac": {
   "lemac": 3.0,
   "longueur": 1.9
  },
  "pilote": {
   "bras": 3.05,
   "masse_kg_defaut": 80
  },
  "carburant": {
   "capacite": 640,
   "par_rotation": 50,
   "reserve": 70,
   "defaut": 250,
   "kg_par_litre": 0.805469235550031,
   "table": [
    [
     129.6,
     4.03
    ],
    [
     259.2,
     3.93
    ],
    [
     388.9,
     3.917
    ],
    [
     518.5,
     3.93
    ]
   ]
  },
  "porte": {
   "x": 5.3,
   "y": 0.9,
   "cote": "droite"
  },
  "places": [
   {
    "id": "D1",
    "x": 2.9,
    "y": 0.45
   },
   {
    "id": "D2",
    "x": 3.4,
    "y": 0.45
   },
   {
    "id": "D3",
    "x": 3.9,
    "y": 0.45
   },
   {
    "id": "D4",
    "x": 4.4,
    "y": 0.45
   },
   {
    "id": "D5",
    "x": 5.2,
    "y": 0.45
   },
   {
    "id": "G1",
    "x": 3.4,
    "y": -0.45
   },
   {
    "id": "G2",
    "x": 3.875,
    "y": -0.45
   },
   {
    "id": "G3",
    "x": 4.35,
    "y": -0.45
   },
   {
    "id": "G4",
    "x": 4.825,
    "y": -0.45
   },
   {
    "id": "G5",
    "x": 5.3,
    "y": -0.45
   }
  ],
  "rangees": [
   {
    "id": "D",
    "libelle": "droite",
    "y": 0.45,
    "xmin": 2.6,
    "xmax": 5.65
   },
   {
    "id": "G",
    "libelle": "gauche",
    "y": -0.45,
    "xmin": 3.3,
    "xmax": 5.65
   }
  ],
  "cabine": {
   "x0": 2.5,
   "x1": 5.7,
   "zones": [
    {
     "nom": "cabine",
     "x0": 2.5,
     "x1": 5.7,
     "largeur": 1.16
    }
   ],
   "porte": {
    "x0": 4.2,
    "x1": 5.5,
    "cote": "droite"
   }
  },
  "variantes": [
   {
    "id": "afm",
    "libelle": "AFM B2-H4, MTOW 2800 kg",
    "mtow": 2800,
    "enveloppe": {
     "avant": [
      [
       1450,
       3.209
      ],
      [
       2800,
       3.608
      ]
     ],
     "arriere": [
      [
       0,
       3.722
      ],
      [
       2800,
       3.722
      ]
     ]
    },
    "source": "planches club, identique au TCDS OFAC F 56-10"
   }
  ],
  "variante_defaut": "afm",
  "source": "avions/pc6-b2h4/planches_club.json (planches club) ; cabine et porte : ordre de grandeur, voir avions/pc6-b2h4/notes.md"
 },
 {
  "id": "pac750xl",
  "libelle": "PAC 750XL (generique)",
  "type": "Pacific Aerospace 750XL",
  "famille": "pac750xl",
  "unites": {
   "masse": "lb",
   "bras": "in",
   "carburant": "lb"
  },
  "kg_par_unite_masse": 0.45359290943563974,
  "masse_vide": 3300,
  "bras_vide": 110.58,
  "mac": {
   "lemac": 100.21,
   "longueur": 85.584
  },
  "pilote": {
   "bras": 66.5,
   "masse_kg_defaut": 80
  },
  "carburant": {
   "capacite": 1476,
   "par_rotation": null,
   "reserve": null,
   "defaut": 500,
   "table": [
    [
     0,
     110.21
    ],
    [
     1476,
     110.21
    ]
   ]
  },
  "porte": {
   "x": 212.0,
   "y": -27.0,
   "cote": "gauche"
  },
  "places": [
   {
    "id": "P1",
    "x": 93.0,
    "y": 0.0
   },
   {
    "id": "P2",
    "x": 107.0,
    "y": 0.0
   },
   {
    "id": "P3",
    "x": 121.0,
    "y": 0.0
   },
   {
    "id": "P4",
    "x": 135.0,
    "y": 0.0
   },
   {
    "id": "P5",
    "x": 149.0,
    "y": 0.0
   },
   {
    "id": "P6",
    "x": 163.0,
    "y": 0.0
   },
   {
    "id": "P7",
    "x": 177.0,
    "y": 0.0
   },
   {
    "id": "P8",
    "x": 191.0,
    "y": 0.0
   },
   {
    "id": "P9",
    "x": 195.0,
    "y": 0.0
   },
   {
    "id": "P10",
    "x": 209.0,
    "y": 0.0
   },
   {
    "id": "P11",
    "x": 223.0,
    "y": 0.0
   },
   {
    "id": "P12",
    "x": 240.0,
    "y": 0.0
   }
  ],
  "rangees": [
   {
    "id": "D",
    "libelle": "droite",
    "y": 18.0,
    "xmin": 85.0,
    "xmax": 238.0
   },
   {
    "id": "C",
    "libelle": "centre",
    "y": 0.0,
    "xmin": 85.0,
    "xmax": 238.0
   },
   {
    "id": "G",
    "libelle": "gauche",
    "y": -18.0,
    "xmin": 85.0,
    "xmax": 238.0
   }
  ],
  "cabine": {
   "x0": 82.34,
   "x1": 240.08,
   "zones": [
    {
     "nom": "cabine",
     "x0": 82.34,
     "x1": 240.08,
     "largeur": 54
    }
   ],
   "porte": {
    "x0": 187.0,
    "x1": 237.0,
    "cote": "gauche"
   }
  },
  "variantes": [
   {
    "id": "std",
    "libelle": "POH, all configurations, standard tanks (S/N 101 to 185 except 177), MTOW 7500 lb",
    "mtow": 7500,
    "enveloppe": {
     "avant": [
      [
       4209.0,
       100.46
      ],
      [
       5639.0,
       103.18
      ],
      [
       7500.0,
       111.55
      ]
     ],
     "arriere": [
      [
       0.0,
       125.6
      ],
      [
       7500.0,
       125.6
      ]
     ]
    },
    "source": "POH p.42 (POH 2-8, Figure 2-8) and p.157 (POH 6-7); EASA TCDS EASA.IM.A.081 Issue 6 A.III.14.1"
   },
   {
    "id": "gros_reservoirs",
    "libelle": "POH, enlarged fuel tanks (mod PAC/XL/0448, S/N 177 and 186 onwards), MTOW 7500 lb",
    "mtow": 7500,
    "enveloppe": {
     "avant": [
      [
       4209.0,
       102.18
      ],
      [
       5639.0,
       104.9
      ],
      [
       7500.0,
       113.27
      ]
     ],
     "arriere": [
      [
       0.0,
       124.6
      ],
      [
       7500.0,
       124.6
      ]
     ]
    },
    "source": "EASA TCDS EASA.IM.A.081 Issue 6 A.III.14.2, file EASA_TCDS_IM_A_081.pdf"
   }
  ],
  "variante_defaut": "std",
  "a_verifier": [
   "masse a vide 3300 lb et bras 110.58 in : ordre de grandeur (tiers / exemple POH), saisir la pesee reelle",
   "bras carburant : reservoir avant 110.21 in, arriere 139.15 in ; sequence de remplissage non connue",
   "positions paras 1 a 12 sur l axe (figure 6-10 du POH), pas de position laterale publiee"
  ],
  "source": "avions/pac750xl/envelope.json (POH PAC 750XL, TCDS EASA)"
 },
 {
  "id": "dhc6-300",
  "libelle": "DHC-6 Twin Otter 300 (generique)",
  "type": "de Havilland DHC-6-300 Twin Otter",
  "famille": "dhc6",
  "unites": {
   "masse": "lb",
   "bras": "in",
   "carburant": "lb"
  },
  "kg_par_unite_masse": 0.45359290943563974,
  "masse_vide": 7400,
  "bras_vide": 200.0,
  "mac": {
   "lemac": 188.24,
   "longueur": 78.0
  },
  "pilote": {
   "bras": 95.0,
   "masse_kg_defaut": 80,
   "nombre": 2
  },
  "carburant": {
   "capacite": 2532,
   "par_rotation": null,
   "reserve": null,
   "defaut": 1200,
   "table": [
    [
     0,
     162.5
    ],
    [
     1213,
     162.5
    ],
    [
     2533,
     202.89
    ]
   ]
  },
  "porte": {
   "x": 298.0,
   "y": -40.0,
   "cote": "gauche"
  },
  "places": [
   {
    "id": "D1",
    "x": 125.0,
    "y": 20.0
   },
   {
    "id": "D2",
    "x": 145.0,
    "y": 20.0
   },
   {
    "id": "D3",
    "x": 165.0,
    "y": 20.0
   },
   {
    "id": "D4",
    "x": 185.0,
    "y": 20.0
   },
   {
    "id": "D5",
    "x": 205.0,
    "y": 20.0
   },
   {
    "id": "D6",
    "x": 225.0,
    "y": 20.0
   },
   {
    "id": "D7",
    "x": 245.0,
    "y": 20.0
   },
   {
    "id": "D8",
    "x": 265.0,
    "y": 20.0
   },
   {
    "id": "D9",
    "x": 285.0,
    "y": 20.0
   },
   {
    "id": "D10",
    "x": 305.0,
    "y": 20.0
   },
   {
    "id": "D11",
    "x": 325.0,
    "y": 20.0
   },
   {
    "id": "G1",
    "x": 125.0,
    "y": -20.0
   },
   {
    "id": "G2",
    "x": 145.0,
    "y": -20.0
   },
   {
    "id": "G3",
    "x": 165.0,
    "y": -20.0
   },
   {
    "id": "G4",
    "x": 185.0,
    "y": -20.0
   },
   {
    "id": "G5",
    "x": 205.0,
    "y": -20.0
   },
   {
    "id": "G6",
    "x": 225.0,
    "y": -20.0
   },
   {
    "id": "G7",
    "x": 245.0,
    "y": -20.0
   },
   {
    "id": "G8",
    "x": 265.0,
    "y": -20.0
   },
   {
    "id": "G9",
    "x": 285.0,
    "y": -20.0
   },
   {
    "id": "G10",
    "x": 305.0,
    "y": -20.0
   },
   {
    "id": "G11",
    "x": 325.0,
    "y": -20.0
   }
  ],
  "rangees": [
   {
    "id": "D",
    "libelle": "droite",
    "y": 20.0,
    "xmin": 117.32,
    "xmax": 326.0
   },
   {
    "id": "C",
    "libelle": "centre",
    "y": 0.0,
    "xmin": 117.32,
    "xmax": 326.0
   },
   {
    "id": "G",
    "libelle": "gauche",
    "y": -20.0,
    "xmin": 117.32,
    "xmax": 326.0
   }
  ],
  "cabine": {
   "x0": 109.32,
   "x1": 332.0,
   "zones": [
    {
     "nom": "cabine",
     "x0": 109.32,
     "x1": 332.0,
     "largeur": 69
    }
   ],
   "porte": {
    "x0": 270.0,
    "x1": 326.0,
    "cote": "gauche"
   },
   "train_principal": 232,
   "train_avant": 53,
   "rangees_sieges_commuter": [
    129,
    159,
    189,
    219,
    249,
    280,
    315
   ]
  },
  "variantes": [
   {
    "id": "decollage",
    "libelle": "TCDS A9EA, take-off, max 12500 lb",
    "mtow": 12500,
    "enveloppe": {
     "avant": [
      [
       9000.0,
       203.84
      ],
      [
       11600.0,
       203.84
      ],
      [
       12500.0,
       207.74
      ]
     ],
     "arriere": [
      [
       0.0,
       216.32
      ],
      [
       12500.0,
       216.32
      ]
     ]
    },
    "source": "FAA TCDS A9EA Rev 15 p. 12, figure 'C.G. range (Landing gear fixed)', values printed on the figure (file FAA_TCDS_A9EA_paraclete_1.pdf, raster tcds_p12-12.png); identical figure redrawn to 6000 lb in MSFS2024 AOM p. 44 (third party)"
   },
   {
    "id": "atterrissage",
    "libelle": "TCDS A9EA, landing, max 12300 lb",
    "mtow": 12300,
    "enveloppe": {
     "avant": [
      [
       9000.0,
       203.84
      ],
      [
       11000.0,
       203.84
      ],
      [
       12300.0,
       207.74
      ]
     ],
     "arriere": [
      [
       0.0,
       216.32
      ],
      [
       12300.0,
       216.32
      ]
     ]
    },
    "source": "FAA TCDS A9EA Rev 15 p. 12"
   }
  ],
  "variante_defaut": "decollage",
  "a_verifier": [
   "masse a vide 7400 lb et bras 200 in : ordre de grandeur, saisir la pesee reelle",
   "positions des paras au sol : hypothese (deux files, pas 20 in, FS 125 a 325), le manuel de masse et centrage PSM 1-63-8 n a pas ete trouve ; rangees commuter mesurees sur plan FS 129 a 315 (+/- 5 in)",
   "ordre de remplissage des reservoirs (avant puis arriere) suppose pour le bras carburant",
   "porte gauche FS 270 a 326 et trains (FS 232 et 53) mesures sur les plans FlightSafety, +/- 5 in"
  ],
  "source": "avions/dhc6/envelope.json (TCDS FAA A9EA, Viking) et avions/dhc6/stations.json (mesures sur plans)"
 }
];
