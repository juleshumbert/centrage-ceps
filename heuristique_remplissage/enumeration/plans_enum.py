"""Plans cabine des meilleurs ordres issus de l enumeration (places legacy et N=20)."""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from caravan_model import ZONES, PILOT_ARM, SLOTS
from ordre_origine import legacy_slots, FILLING_ORDER

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / 'output'
best = json.loads((OUT / 'enumeration_meilleurs_ordres.json').read_text())
C_BLUE, C_ORANGE, C_GREY = '#2a78d6', '#eb6834', '#52514e'


def legacy_xy():
    x = legacy_slots('C208B-A')
    ys = [16] * 8 + [0] * 5 + [-16] * 7
    return list(zip(x, ys))


N20_XY = [(s.x, s.y) for s in SLOTS]


def draw(ax, xy, order, title):
    for i in range(6):
        z, z1 = ZONES[i], ZONES[i + 1]
        ax.add_patch(patches.Polygon([(z['x0'], -z['height'] / 2), (z['x0'], z['height'] / 2),
                                      (z['x1'], z1['height'] / 2), (z['x1'], -z1['height'] / 2)],
                                     lw=1.0, fill=False, edgecolor='#0b0b0b'))
    ax.plot([ZONES[4]['x0'], ZONES[6]['x0']], [-ZONES[4]['height'] / 2 - 2] * 2, color=C_ORANGE, lw=3)
    ax.add_patch(patches.Circle((PILOT_ARM, -16), 5.5, color=C_GREY, zorder=3))
    ax.text(PILOT_ARM, -16, 'P', ha='center', va='center', color='white', fontsize=8, fontweight='bold', zorder=4)
    rank = {idx: r + 1 for r, idx in enumerate(order)}
    for idx, (x, y) in enumerate(xy):
        ax.add_patch(patches.Circle((x, y), 5.8, color=C_BLUE, zorder=3))
        ax.text(x, y, str(rank[idx]), ha='center', va='center', color='white', fontsize=8, fontweight='bold', zorder=4)
        ax.text(x, y - 9.5, f'{x:.0f}', ha='center', va='top', fontsize=5.5, color=C_GREY,
                bbox=dict(facecolor='white', edgecolor='none', pad=0.3), zorder=5)
    ax.set_xlim(98, 360); ax.set_ylim(-42, 40); ax.set_aspect('equal'); ax.axis('off')
    ax.set_title(title, fontsize=8.5, fontweight='bold', pad=1)


cases = [
    ('legacy', None, [FILLING_ORDER.index(r) for r in range(1, 21)],
     'Ordre d origine des planches (filling_order_bon, places legacy)\nforfait OK ; poids moyen 70 a 110 kg : 2 a 4 % d echecs'),
    ('legacy', 'legacy | deux avions | forfait 90 kg, pilote 80 | enveloppe complete',
     None, 'Enumeration, places legacy, deux avions, forfait 90 kg\nordre de marge maximale : 1,50 in de CG'),
    ('legacy', 'legacy | deux avions | moyen 70-110 kg, pilotes 80/86 | enveloppe complete',
     None, 'Enumeration, places legacy, deux avions, poids moyen 70 a 110 kg,\ntout carburant, pilotes 80/86 : marge 0,24 in'),
    ('legacy', 'legacy | deux avions | moyen 75-105 kg, pilotes 80/86, fuel 320-1900 | enveloppe complete',
     None, 'Enumeration, places legacy, deux avions, poids moyen 75 a 105 kg,\ncarburant 320 a 1900 lbs : marge 0,64 in'),
    ('n20', 'n20 | C208B-A | moyen 70-110 kg, pilotes 80/86 | enveloppe complete',
     None, 'Enumeration, places N=20, C208B-A seul, poids moyen 70 a 110 kg,\ntout carburant, pilotes 80/86 : marge 0,73 in'),
    ('n20', 'n20 | C208B-B | moyen 70-110 kg, pilotes 80/86 | enveloppe complete',
     None, 'Enumeration, places N=20, C208B-B seul, poids moyen 70 a 110 kg,\ntout carburant, pilotes 80/86 : marge 0,43 in'),
]
fig, axes = plt.subplots(3, 2, figsize=(13, 9.5))
for ax, (sl, key, order, title) in zip(axes.T.flatten(), cases):
    if order is None:
        order = best[key]['ordre']
    draw(ax, legacy_xy() if sl == 'legacy' else N20_XY, order, title)
fig.suptitle('Ordres uniques issus de l enumeration exhaustive (le para le plus lourd sur la place 1)', fontsize=11, fontweight='bold')
fig.tight_layout(); fig.savefig(OUT / 'fig_enumeration_ordres.png', dpi=150); plt.close(fig)
print('ok')
