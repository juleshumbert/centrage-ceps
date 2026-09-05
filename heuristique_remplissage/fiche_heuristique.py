"""Heuristique retenue : fiche une page (PDF + PNG), JSON des ordres, evaluation.

Regle :
  1. masse totale des paras equipes (manifeste) et carburant au decollage ;
  2. la table donne le plan (A a E) ;
  3. remplir les places du plan dans l'ordre des numeros, le para le plus lourd
     sur la place 1, le suivant sur la 2, etc. (les lourds au pivot, ce qui rend
     le bras moyen insensible a la repartition des masses).

Chaque plan est l'ordre "equilibre" autour d'un pivot (pivot_regimes.order_balanced).
Variante simplifiee (masse seule, 4 plans) donnee en annexe du README.
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np

from caravan_model import SLOTS, ZONES, PILOT_ARM, evaluate as ev_direct, fwd_limit, AFT_CG
from scenarios import all_scenarios, FUEL_GRID, N_GRID
from fast import Bench, XS
from pivot_regimes import order_balanced, margins

OUT = Path(__file__).resolve().parent / 'output'

# --- Heuristique retenue ---------------------------------------------------------
MASS_EDGES = [800, 1200, 1400]        # kg, masse totale des paras equipes
FUEL_EDGE = 1600                      # lbs
PLANS = {'A': 225.0, 'B': 227.5, 'C': 232.5, 'D': 240.0, 'E': 252.5}
# (classe carburant, classe masse) -> plan ; classes masse : 0 <800, 1 800-1200, 2 1200-1400, 3 >=1400
TABLE = {(0, 0): 'D', (0, 1): 'C', (0, 2): 'B', (0, 3): 'A',
         (1, 0): 'E', (1, 1): 'D'}
MASS_LABELS = ['moins de 800 kg', '800 a 1200 kg', '1200 a 1400 kg', '1400 kg et plus']
FUEL_LABELS = [f'carburant < {FUEL_EDGE} lbs', f'carburant >= {FUEL_EDGE} lbs']
# Variante simplifiee : masse seule
TABLE_SIMPLE = {0: 245.0, 1: 232.5, 2: 227.5, 3: 225.0}
MASS_EDGES_SIMPLE = [900, 1200, 1400]

C_BLUE, C_ORANGE, C_GREY, C_RED = '#2a78d6', '#eb6834', '#52514e', '#e34948'


def plan_for(total_kg, fuel_lbs):
    km = int(np.digitize(total_kg, MASS_EDGES))
    kf = int(fuel_lbs >= FUEL_EDGE)
    return TABLE.get((kf, km))       # None : au-dessus de la MTOW de toute facon


def draw_plan(ax, order, title, small=False):
    fs = 7 if small else 9
    for i in range(6):
        z, z1 = ZONES[i], ZONES[i + 1]
        ax.add_patch(patches.Polygon(
            [(z['x0'], -z['height'] / 2), (z['x0'], z['height'] / 2),
             (z['x1'], z1['height'] / 2), (z['x1'], -z1['height'] / 2)],
            lw=1.0, fill=False, edgecolor='#0b0b0b'))
    ax.plot([ZONES[4]['x0'], ZONES[6]['x0']], [-ZONES[4]['height'] / 2 - 2] * 2,
            color=C_ORANGE, lw=3, solid_capstyle='butt')
    ax.text((ZONES[4]['x0'] + ZONES[6]['x0']) / 2, -ZONES[4]['height'] / 2 - 5, 'porte',
            ha='center', va='top', fontsize=fs - 1, color=C_ORANGE)
    ax.add_patch(patches.Circle((PILOT_ARM, -16), 5.5, color=C_GREY, zorder=3))
    ax.text(PILOT_ARM, -16, 'P', ha='center', va='center', color='white', fontsize=fs,
            fontweight='bold', zorder=4)
    ax.annotate('', xy=(110, 30), xytext=(135, 30), arrowprops=dict(arrowstyle='->', color=C_GREY, lw=1))
    ax.text(122, 33, 'avant', ha='center', va='bottom', fontsize=fs - 1, color=C_GREY)
    rank = {idx: r + 1 for r, idx in enumerate(order)}
    for s in SLOTS:
        ax.add_patch(patches.Circle((s.x, s.y), 5.8, color=C_BLUE, zorder=3))
        ax.text(s.x, s.y, str(rank[s.idx]), ha='center', va='center', color='white',
                fontsize=fs, fontweight='bold', zorder=4)
    ax.set_xlim(98, 360); ax.set_ylim(-42, 42); ax.set_aspect('equal')
    ax.set_xticks([]); ax.set_yticks([]); ax.grid(False)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.set_title(title, fontsize=fs + 1, fontweight='bold', pad=1)


def fiche(pdf_path, png_path):
    fig = plt.figure(figsize=(11.69, 8.27), dpi=200)
    fig.patch.set_facecolor('white')
    fig.text(0.5, 0.965, 'Remplissage du Caravan a places fixes (C208B-A, C208B-B) : heuristique',
             ha='center', va='center', fontsize=15, fontweight='bold')
    fig.text(0.5, 0.935, 'Etude heuristique_remplissage, verifiee sur 18 867 scenarios (1 a 20 paras, '
             '60 a 120 kg, carburant 200 a 2224 lbs, pilote 65 a 110 kg) : 0 sortie d enveloppe',
             ha='center', va='center', fontsize=8.5, color=C_GREY)

    # Regle (gauche)
    regle = ('1. Masse totale des paras equipes (manifeste)\n'
             '    et carburant au decollage.\n'
             '2. La table donne le plan a utiliser.\n'
             '3. Remplir les places du plan dans l ordre des\n'
             '    numeros : le para le plus lourd sur la place 1,\n'
             '    le suivant sur la 2, et ainsi de suite.\n'
             '    Ne pas sauter de numero.')
    fig.text(0.035, 0.895, 'Regle', fontsize=11, fontweight='bold', va='top')
    fig.text(0.035, 0.865, regle, fontsize=8.2, va='top', linespacing=1.45)
    fig.text(0.50, 0.685, 'Forfait 90 kg : moins de 800 kg = 1 a 8 paras, 800 a 1200 kg = 9 a 13,\n'
             '1200 a 1400 kg = 14 ou 15, 1400 kg et plus = 16 a 20.\n'
             'Forfait 80 kg : 1 a 9 / 10 a 14 / 15 a 17 / 18 a 20.',
             fontsize=7.6, va='top', color='#0b0b0b', linespacing=1.4)

    # Table (droite)
    ax_t = fig.add_axes([0.50, 0.70, 0.47, 0.19])
    ax_t.axis('off')
    cells = [[MASS_LABELS[km]] + [TABLE.get((kf, km), 'au-dessus de la MTOW') for kf in (0, 1)]
             for km in range(4)]
    for row in cells:
        for j in (1, 2):
            if row[j] in PLANS:
                row[j] = f'plan {row[j]}  (pivot {PLANS[row[j]]:g} in)'
    tb = ax_t.table(cellText=cells, colLabels=['masse totale des paras'] + FUEL_LABELS,
                    loc='center', cellLoc='center')
    tb.auto_set_font_size(False); tb.set_fontsize(8.5); tb.scale(1, 1.55)
    for (r, c), cell in tb.get_celld().items():
        cell.set_edgecolor('#999999')
        if r == 0:
            cell.set_facecolor('#2C5F8A'); cell.get_text().set_color('white'); cell.get_text().set_fontweight('bold')
        elif c == 0:
            cell.set_facecolor('#E4EBF5')
        elif 'MTOW' in cell.get_text().get_text():
            cell.get_text().set_color(C_GREY)
    ax_t.set_title('Quel plan ?', fontsize=11, fontweight='bold', loc='left')

    # Plans : 5 vignettes sur 3 lignes x 2 colonnes, la 6e case pour le commentaire
    pos = {'A': (0.03, 0.43), 'B': (0.52, 0.43), 'C': (0.03, 0.23), 'D': (0.52, 0.23),
           'E': (0.03, 0.03)}
    for name, (x0, y0) in pos.items():
        ax = fig.add_axes([x0, y0, 0.45, 0.19])
        order = order_balanced(PLANS[name])
        usage = {'A': 'charge lourde, 1400 kg et plus', 'B': '1200 a 1400 kg',
                 'C': '800 a 1200 kg, carburant < 1600 lbs',
                 'D': '< 800 kg, ou 800 a 1200 kg avec carburant >= 1600 lbs',
                 'E': '< 800 kg avec carburant >= 1600 lbs'}[name]
        draw_plan(ax, order, f'Plan {name} : {usage}', small=False)
    fig.text(0.535, 0.19, 'Pourquoi pas autour de la cible CG (202 in) ?\n'
             'L avion vide + pilote est a 187 in et le carburant vers 202 in :\n'
             'les paras doivent se placer en arriere pour compenser, d autant\n'
             'plus que la charge est legere et le carburant abondant.\n'
             'Le para le plus lourd au pivot rend le bras moyen insensible\n'
             'a la repartition des masses.',
             fontsize=8.2, va='top', color='#0b0b0b', linespacing=1.45)
    fig.text(0.535, 0.04, 'Places fixes = disposition N=20 des planches.\n'
             'Etude : heuristique_remplissage/ (depot centrage_c208). Version du '
             + __import__('datetime').date.today().strftime('%d/%m/%Y') + '.',
             fontsize=7.2, va='bottom', color=C_GREY, linespacing=1.4)
    with PdfPages(pdf_path) as pdf:
        pdf.savefig(fig)
    fig.savefig(png_path, dpi=150)
    plt.close(fig)


def evaluation():
    scs, dropped = all_scenarios(seed=0, k_per_cell=6)
    B = Bench(scs)
    feas = B.feasible
    orders = {k: order_balanced(p) for k, p in PLANS.items()}
    Mp = {k: margins(B, o) for k, o in orders.items()}
    plan = [plan_for(sum(s.weights_kg), s.fuel_lbs) for s in scs]
    assert all(p is not None for p, f in zip(plan, feas) if f), 'scenario faisable sans plan'
    mg = np.array([Mp[p][i] if p else np.nan for i, p in enumerate(plan)])
    fails = int(((mg < 0) & feas).sum())
    print(f'Heuristique retenue : {fails} sorties d enveloppe sur {int(feas.sum())} scenarios ; '
          f'marge min {np.nanmin(mg[feas]):+.2f} in, 1 % {np.nanpercentile(mg[feas], 1):.2f}, '
          f'5 % {np.nanpercentile(mg[feas], 5):.2f}, mediane {np.nanmedian(mg[feas]):.2f} in')
    # verification directe (non vectorisee) sur un echantillon
    rng = np.random.default_rng(1)
    for i in rng.choice(np.where(feas)[0], 300, replace=False):
        s = scs[i]
        st, mass, cg, _ = ev_direct(orders[plan[i]], s.immat, s.pilot_kg, s.fuel_lbs, s.weights_kg)
        assert st == 'ok', (s, st, cg)
    print('verification directe ok (300 scenarios)')
    # carte N x carburant : marge minimale
    fuel_of = np.array([min(FUEL_GRID, key=lambda g: abs(g - s.fuel_lbs)) for s in scs])
    Mmin = np.full((len(N_GRID), len(FUEL_GRID)), np.nan)
    for i, n in enumerate(N_GRID):
        for j, f in enumerate(FUEL_GRID):
            sel = (B.n == n) & (fuel_of == f) & feas
            if sel.any():
                Mmin[i, j] = mg[sel].min()
    fig, ax = plt.subplots(figsize=(9, 6.5))
    ax.grid(False)
    im = ax.imshow(Mmin, cmap='Blues', vmin=0, vmax=6, aspect='auto', origin='lower')
    ax.set_xticks(range(len(FUEL_GRID))); ax.set_xticklabels(FUEL_GRID, rotation=90, fontsize=8)
    ax.set_yticks(range(len(N_GRID))); ax.set_yticklabels(N_GRID, fontsize=8)
    ax.set_xlabel('Carburant au decollage (lbs)'); ax.set_ylabel('Nombre de paras a bord')
    ax.set_title('Heuristique retenue : marge CG minimale (in) par case, tous scenarios confondus')
    for i in range(Mmin.shape[0]):
        for j in range(Mmin.shape[1]):
            v = Mmin[i, j]
            if np.isnan(v):
                ax.text(j, i, 'x', ha='center', va='center', fontsize=6, color='#999999')
            else:
                ax.text(j, i, f'{v:.1f}', ha='center', va='center', fontsize=6,
                        color='white' if v > 3.3 else '#0b0b0b')
    cb = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
    cb.set_label('marge minimale (in de CG, 1 in = 1,5 %MAC)')
    ax.text(0, -0.13, 'x : aucun scenario sous MTOW dans la case', transform=ax.transAxes,
            fontsize=8, color=C_GREY)
    fig.tight_layout(); fig.savefig(OUT / 'fig_marge_retenue.png', dpi=160); plt.close(fig)

    # variante simplifiee
    plan_s = [TABLE_SIMPLE[int(np.digitize(sum(s.weights_kg), MASS_EDGES_SIMPLE))] for s in scs]
    Ms = {p: margins(B, order_balanced(p)) for p in set(plan_s)}
    mg_s = np.array([Ms[p][i] for i, p in enumerate(plan_s)])
    print(f'Variante masse seule : {int(((mg_s < 0) & feas).sum())} sorties, marge min {mg_s[feas].min():+.2f} in')

    (OUT / 'heuristique_retenue.json').write_text(json.dumps(dict(
        regle='ordre equilibre autour d un pivot, para le plus lourd sur la place 1',
        seuils_masse_kg=MASS_EDGES, seuil_carburant_lbs=FUEL_EDGE,
        table={f'fuel{kf}_masse{km}': v for (kf, km), v in TABLE.items()},
        plans={k: dict(pivot_in=p, ordre_places=[int(i) for i in orders[k]],
                       bras_in=[float(XS[i]) for i in orders[k]]) for k, p in PLANS.items()},
        places=[dict(idx=s.idx, bras_in=s.x, y_in=s.y, rangee=s.row) for s in SLOTS],
        variante_masse_seule=dict(seuils_masse_kg=MASS_EDGES_SIMPLE,
                                  pivots={str(k): v for k, v in TABLE_SIMPLE.items()}),
    ), indent=1))


if __name__ == '__main__':
    fiche(OUT / 'Fiche_heuristique_remplissage_Caravan.pdf', OUT / 'fiche_heuristique.png')
    evaluation()
    print('fiche et evaluation ecrites dans', OUT)
