"""Figures et tableaux du rapport de verification (output/).

  fig_pivot.png      taux d'echec en fonction du pivot (lourds/legers d'abord)
  fig_carte_202.png  taux d'echec N x carburant pour le pivot 202 in
  fig_carte_235.png  idem pour le meilleur pivot fixe (235 in)
  fig_bandes.png     bande de bras moyen admissible par N (intersection de tous
                     les scenarios) et bras moyen des k premieres places
  fig_plan_*.png     plan cabine avec l'ordre de remplissage numerote
  resume.md          tableaux chiffres
"""
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

from caravan_model import SLOTS, ZONES, PILOT_ARM, order_by_pivot
from scenarios import all_scenarios, FUEL_GRID, N_GRID
from fast import Bench

OUT = Path(__file__).resolve().parent / 'output'
OUT.mkdir(exist_ok=True)

C_BLUE, C_ORANGE, C_RED, C_GREY = '#2a78d6', '#eb6834', '#e34948', '#52514e'
plt.rcParams.update({'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False,
                     'axes.grid': True, 'grid.color': '#dddddd', 'grid.linewidth': 0.6})

scs, dropped = all_scenarios()
B = Bench(scs)
NF = int(B.feasible.sum())
fuel_of = np.array([min(FUEL_GRID, key=lambda g: abs(g - s.fuel_lbs)) for s in scs])
lines = [f'# Resume chiffre\n', f'Scenarios sous MTOW : {len(scs)} (ecartes car > MTOW : {dropped}). '
         f'Tous ont au moins une affectation valide.\n']

# ---- 1. balayage du pivot ---------------------------------------------------
pivots = np.arange(190, 260.1, 1.0)
f_h = [100 * B.failures(order_by_pivot(p), True) / NF for p in pivots]
f_l = [100 * B.failures(order_by_pivot(p), False) / NF for p in pivots]
best_p = float(pivots[int(np.argmin(f_h))])
fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(pivots, f_h, color=C_BLUE, lw=2, label='plus lourds d abord')
ax.plot(pivots, f_l, color=C_ORANGE, lw=2, ls='--', label='plus legers d abord')
ax.axvline(202, color=C_GREY, lw=1, ls=':')
ax.text(202.5, 60, 'pivot 202 in\n(proposition)', color=C_GREY, fontsize=9, va='top')
ax.axvline(best_p, color=C_GREY, lw=1, ls=':')
ax.text(best_p + 0.5, 60, f'meilleur pivot\n{best_p:.0f} in', color=C_GREY, fontsize=9, va='top')
ax.set_xlabel('Pivot (in) : les places sont remplies par distance croissante a ce bras')
ax.set_ylabel('Echecs heuristiques (% des scenarios faisables)')
ax.set_title('Ordre par distance a un pivot : taux d echec selon le pivot')
ax.legend(loc='upper right', frameon=False)
fig.tight_layout(); fig.savefig(OUT / 'fig_pivot.png', dpi=160); plt.close(fig)
lines.append(f'## Balayage du pivot\n\nMeilleur pivot (lourds d abord) : {best_p:.0f} in, '
             f'{min(f_h):.1f} % d echecs. Pivot 202 in : {f_h[list(pivots).index(202.0)]:.1f} %.\n')
lines.append('| pivot (in) | echecs, lourds d abord | echecs, legers d abord |\n|---|---|---|')
for p, a, b in zip(pivots, f_h, f_l):
    if p % 5 == 0:
        lines.append(f'| {p:.0f} | {a:.1f} % | {b:.1f} % |')
lines.append('')


# ---- 1b. meme balayage sur un sous-ensemble realiste --------------------------
real_mask = np.array([s.fuel_lbs >= 320 and 70 <= np.mean(s.weights_kg) <= 110 for s in scs])
Br = Bench([s for s, m in zip(scs, real_mask) if m])
NFr = int(Br.feasible.sum())
lines.append(f'## Sous-ensemble realiste : fuel >= 320 lbs, masse moyenne des paras entre 70 et 110 kg '
             f'({NFr} scenarios)\n')
lines.append('| pivot (in) | echecs, lourds d abord | echecs, legers d abord |\n|---|---|---|')
for p in (202.0, 220.0, 225.0, 230.0, 235.0, 240.0):
    o = order_by_pivot(p)
    lines.append(f'| {p:.0f} | {100 * Br.failures(o, True) / NFr:.1f} % | {100 * Br.failures(o, False) / NFr:.1f} % |')
lines.append('')

# ---- 2. cartes N x carburant ------------------------------------------------
def carte(order, name, title):
    st = B.status(order, True)
    M = np.full((len(N_GRID), len(FUEL_GRID)), np.nan)
    for i, n in enumerate(N_GRID):
        for j, f in enumerate(FUEL_GRID):
            sel = (B.n == n) & (fuel_of == f) & B.feasible
            if sel.sum():
                M[i, j] = 100 * ((st != 0) & sel).sum() / sel.sum()
    fig, ax = plt.subplots(figsize=(9, 6.5))
    ax.grid(False)
    im = ax.imshow(M, cmap='Blues', vmin=0, vmax=100, aspect='auto', origin='lower')
    ax.set_xticks(range(len(FUEL_GRID))); ax.set_xticklabels(FUEL_GRID, rotation=90, fontsize=8)
    ax.set_yticks(range(len(N_GRID))); ax.set_yticklabels(N_GRID, fontsize=8)
    ax.set_xlabel('Carburant au decollage (lbs)'); ax.set_ylabel('Nombre de paras a bord')
    ax.set_title(title)
    for i in range(M.shape[0]):
        for j in range(M.shape[1]):
            v = M[i, j]
            if np.isnan(v):
                ax.text(j, i, 'x', ha='center', va='center', fontsize=6, color='#999999')
            elif v > 0:
                ax.text(j, i, f'{v:.0f}', ha='center', va='center', fontsize=6.5,
                        color='white' if v > 55 else '#0b0b0b')
    cb = fig.colorbar(im, ax=ax, fraction=0.03, pad=0.02)
    cb.set_label('% de scenarios faisables hors enveloppe')
    ax.text(0, -0.13, 'x : aucun scenario sous MTOW dans la case', transform=ax.transAxes,
            fontsize=8, color=C_GREY)
    fig.tight_layout(); fig.savefig(OUT / f'fig_carte_{name}.png', dpi=160); plt.close(fig)


carte(order_by_pivot(202.0), '202', 'Pivot 202 in, plus lourds d abord : ou l heuristique echoue')
carte(order_by_pivot(best_p), f'{best_p:.0f}', f'Pivot {best_p:.0f} in, plus lourds d abord : ou l heuristique echoue')

# ---- 3. bandes admissibles par N ------------------------------------------------
lo_max, hi_min = [], []
for n in N_GRID:
    idx = [i for i, sc in enumerate(scs) if sc.n == n and sc.family.startswith('uniforme')]
    lo_max.append(max(B.r_lo[i] * 1000 / B.W_desc[i, :n].sum() for i in idx))
    hi_min.append(min(B.r_hi[i] * 1000 / B.W_desc[i, :n].sum() for i in idx))
lo_max, hi_min = np.array(lo_max), np.array(hi_min)
fig, ax = plt.subplots(figsize=(8, 4.8))
ok = hi_min >= lo_max
ax.fill_between(N_GRID, lo_max, np.maximum(hi_min, lo_max), color=C_BLUE, alpha=0.18,
                label='bras moyen admissible pour TOUS les scenarios')
ax.plot(N_GRID, lo_max, color=C_BLUE, lw=1.5)
ax.plot(N_GRID, hi_min, color=C_BLUE, lw=1.5, ls='--')
ax.text(20.2, lo_max[-1], 'mini', color=C_BLUE, fontsize=8, va='center')
ax.text(20.2, hi_min[-1], 'maxi', color=C_BLUE, fontsize=8, va='center')
for n, l, h in zip(N_GRID, lo_max, hi_min):
    if h < l:
        ax.plot([n, n], [h, l], color=C_RED, lw=3, solid_capstyle='butt')
ax.plot([], [], color=C_RED, lw=3, label='intersection vide : aucun ordre fixe ne couvre ce N')
for p, c, ls in [(202.0, C_ORANGE, '-'), (best_p, C_ORANGE, '--')]:
    o = order_by_pivot(p)
    xb = [np.mean([SLOTS[i].x for i in o[:n]]) for n in N_GRID]
    ax.plot(N_GRID, xb, color=c, lw=1.8, ls=ls, marker='o', ms=3,
            label=f'bras moyen des k premieres places, pivot {p:.0f} in')
ax.set_xlabel('Nombre de paras a bord (k)'); ax.set_ylabel('Bras moyen des paras (in)')
ax.set_xticks(N_GRID); ax.set_ylim(150, 320)
ax.set_title('Ce que le bras moyen des paras doit valoir, selon N (masses uniformes 60 a 120 kg,\n'
             'carburant 200 a 2224 lbs, BK et LA, pilote 80 et 86 kg)', fontsize=10)
ax.legend(loc='upper right', frameon=False, fontsize=8)
fig.tight_layout(); fig.savefig(OUT / 'fig_bandes.png', dpi=160); plt.close(fig)
lines.append('## Bande de bras moyen admissible par N (masses uniformes)\n')
lines.append('| N | bras mini (in) | bras maxi (in) | largeur (in) |\n|---|---|---|---|')
for n, l, h in zip(N_GRID, lo_max, hi_min):
    lines.append(f'| {n} | {l:.1f} | {h:.1f} | {h - l:+.1f} |')
lines.append('')

# ---- 4. deux regimes carburant, ordre par pivot -------------------------------
lines.append('## Deux pivots selon le carburant (ordre par distance au pivot, lourds d abord)\n')
lines.append('| seuil (lbs) | pivot si fuel < seuil | echecs | pivot si fuel >= seuil | echecs | total |\n|---|---|---|---|---|---|')
best_two = None
for T in (1000, 1200, 1400, 1600):
    lo_mask = np.array([s.fuel_lbs < T for s in scs])
    res = []
    for mask in (lo_mask, ~lo_mask):
        Bm = Bench([s for s, m in zip(scs, mask) if m])
        fails = [(Bm.failures(order_by_pivot(p), True), p) for p in np.arange(215, 256, 1.0)]
        f, p = min(fails)
        res.append((p, f, int(Bm.feasible.sum())))
    tot = res[0][1] + res[1][1]
    lines.append(f'| {T} | {res[0][0]:.0f} | {res[0][1]} / {res[0][2]} | {res[1][0]:.0f} | '
                 f'{res[1][1]} / {res[1][2]} | {tot} ({100 * tot / NF:.2f} %) |')
    if best_two is None or tot < best_two[0]:
        best_two = (tot, T, res)
lines.append('')

# ---- 5. plans cabine ------------------------------------------------------------
def plan(order, name, title):
    fig, ax = plt.subplots(figsize=(10, 3.6))
    ax.grid(False)
    for i in range(6):
        z, z1 = ZONES[i], ZONES[i + 1]
        ax.add_patch(patches.Polygon(
            [(z['x0'], -z['height'] / 2), (z['x0'], z['height'] / 2),
             (z['x1'], z1['height'] / 2), (z['x1'], -z1['height'] / 2)],
            lw=1.2, fill=False, edgecolor='#0b0b0b'))
        ax.text(z['arm'], 34, z['label'], ha='center', va='bottom',
                fontsize=7, color=C_GREY)
    # porte cote gauche (bas), zones 4 a 6
    ax.plot([ZONES[4]['x0'], ZONES[6]['x0']], [-ZONES[4]['height'] / 2 - 2] * 2,
            color=C_ORANGE, lw=4, solid_capstyle='butt')
    ax.text((ZONES[4]['x0'] + ZONES[6]['x0']) / 2, -ZONES[4]['height'] / 2 - 6, 'porte',
            ha='center', va='top', fontsize=8, color=C_ORANGE)
    ax.add_patch(patches.Circle((PILOT_ARM, -16), 5.5, color=C_GREY, zorder=3))
    ax.text(PILOT_ARM, -16, 'P', ha='center', va='center', color='white', fontsize=8,
            fontweight='bold', zorder=4)
    rank = {idx: r + 1 for r, idx in enumerate(order)}
    for s in SLOTS:
        ax.add_patch(patches.Circle((s.x, s.y), 5.5, color=C_BLUE, zorder=3))
        ax.text(s.x, s.y, str(rank[s.idx]), ha='center', va='center', color='white',
                fontsize=9, fontweight='bold', zorder=4)
        ax.text(s.x, s.y - 9.5, f'{s.x:.0f}', ha='center', va='top', fontsize=6.5, color=C_GREY,
                bbox=dict(facecolor='white', edgecolor='none', pad=0.6), zorder=5)
    ax.set_xlim(95, 360); ax.set_ylim(-42, 44); ax.set_aspect('equal')
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.set_title(title, fontsize=10)
    fig.tight_layout(); fig.savefig(OUT / f'fig_plan_{name}.png', dpi=170); plt.close(fig)


plan(order_by_pivot(202.0), '202', 'Ordre de remplissage par distance a 202 in (proposition) : numero = rang, bras en gris')
plan(order_by_pivot(best_p), f'{best_p:.0f}',
     f'Ordre de remplissage par distance a {best_p:.0f} in (meilleur pivot fixe) : numero = rang, bras en gris')
tot, T, res = best_two
plan(order_by_pivot(res[0][0]), f'fuel_lt_{T}', f'Carburant < {T} lbs : ordre par distance a {res[0][0]:.0f} in')
plan(order_by_pivot(res[1][0]), f'fuel_ge_{T}', f'Carburant >= {T} lbs : ordre par distance a {res[1][0]:.0f} in')

(OUT / 'resume.md').write_text('\n'.join(lines) + '\n')
print('\n'.join(lines))
print('best_two', best_two)
