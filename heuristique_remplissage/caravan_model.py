"""Modele masse & centrage du Caravan sur 20 places fixes (projet heuristique).

Objectif : etudier des heuristiques de remplissage a places FIXES (les 20 places
de la disposition N=20 des planches), avec des paras de masses individuelles
quelconques, pour n'importe quel nombre de paras et n'importe quel carburant.

La geometrie cabine, la table carburant et les positions N=20 sont relues dans
le notebook C208B-A (cellules 0 a 5), snapshot du depot centrage_c208 place dans
reference/notebooks/ (voir son README) : rien n'est recopie a la main. Les deux Caravan (BK / LA) partagent la meme
cabine, seuls EW et moment a vide changent.

Convention : bras en inches, masses en lbs en interne, kg en entree/sortie.
"""
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
NB_BK = ROOT / 'reference' / 'notebooks' / 'planche_c208b_A.ipynb'

LBS2KG = 2.20462
DENSITY_FUEL_LBS_PER_GAL = 6.7
FUEL_MAX_GAL = 332
FUEL_MAX_LBS = 2224
MTOW_LBS = 9062
DATUM_LINE = 177.57
MAC = 66.40
PILOT_ARM = 135.5

# Enveloppe de centrage C208B (cellule 2 des notebooks) : limite avant en
# fonction de la masse, limite arriere constante.
FWD_MASS = np.array([5500., 8000., MTOW_LBS])
FWD_CG = np.array([179.6, 193.37, 199.15])
AFT_CG = 204.35
CG_TOLERANCE = 1e-6

AIRCRAFT = {
    'C208B-A': dict(ew=4890., ew_moment=924.161),
    'C208B-B': dict(ew=4986., ew_moment=930.11184),
}


def cg_to_mac(cg_in):
    return (cg_in - DATUM_LINE) / MAC * 100


def fwd_limit(mass_lbs):
    """Limite avant du CG (in) a la masse donnee."""
    return float(np.interp(mass_lbs, FWD_MASS, FWD_CG))


def _load_notebook_namespace():
    nb = json.loads(NB_BK.read_text())
    ns = {}
    for cell in nb['cells'][:6]:
        exec(''.join(cell['source']), ns)
    return ns


_NS = _load_notebook_namespace()
ZONES = _NS['get_slots_bk']()[3]


@dataclass(frozen=True)
class Slot:
    idx: int      # 0..19, numerotation interne stable
    x: float      # bras (in)
    y: float      # position laterale (in), pour les dessins
    row: str      # 'copilote', 'droite', 'centre', 'gauche'


def slots_n20():
    """Les 20 places de la disposition N=20 des planches (independantes des masses)."""
    pos = _NS['_get_para_positions_caravan'](
        20, ZONES, AIRCRAFT['C208B-A']['ew'], AIRCRAFT['C208B-A']['ew_moment'],
        MTOW_LBS, 80, 90)
    h = ZONES[3]['height']
    rows = {round(h / 4, 6): 'droite', 0.0: 'centre', round(-h / 4, 6): 'gauche'}
    slots = []
    for i, (x, y) in enumerate(pos):
        row = 'copilote' if i == 0 else rows[round(y, 6)]
        slots.append(Slot(i, float(x), float(y), row))
    return slots


SLOTS = slots_n20()


def fuel_state(fuel_lbs):
    """(moment/1000, masse) du carburant via la table du notebook."""
    gal = fuel_lbs / DENSITY_FUEL_LBS_PER_GAL
    m, w, _ = _NS['compute_moment']([], 0.0, 0.0, 0, 0, gal)
    return m, w


def base_state(immat, pilot_kg, fuel_lbs):
    """(moment/1000, masse) avion vide + pilote + carburant."""
    ac = AIRCRAFT[immat]
    fm, fw = fuel_state(fuel_lbs)
    pilot_lbs = pilot_kg * LBS2KG
    return ac['ew_moment'] + fm + pilot_lbs * PILOT_ARM / 1000, ac['ew'] + fw + pilot_lbs


def mass_cg(immat, pilot_kg, fuel_lbs, placement):
    """placement : liste de (bras_in, masse_kg). Retourne (masse_lbs, cg_in)."""
    m, w = base_state(immat, pilot_kg, fuel_lbs)
    for x, kg in placement:
        lbs = kg * LBS2KG
        m += lbs * x / 1000
        w += lbs
    return w, m / w * 1000


def envelope_status(mass_lbs, cg_in):
    """'ok' | 'mtow' | 'avant' | 'arriere'."""
    if mass_lbs > MTOW_LBS + CG_TOLERANCE:
        return 'mtow'
    if cg_in < fwd_limit(mass_lbs) - CG_TOLERANCE:
        return 'avant'
    if cg_in > AFT_CG + CG_TOLERANCE:
        return 'arriere'
    return 'ok'


# ---------------------------------------------------------------------------
# Heuristiques : un ordre de places (liste d'index) + une regle d'affectation
# ---------------------------------------------------------------------------

def order_by_pivot(pivot_in, slots=SLOTS):
    """Places triees par distance croissante au pivot (egalite : avant d'abord)."""
    return [s.idx for s in sorted(slots, key=lambda s: (abs(s.x - pivot_in), s.x, s.idx))]


def assign(order, weights_kg, heaviest_first=True, slots=SLOTS):
    """Affecte les paras aux `len(weights)` premieres places de `order`.

    heaviest_first=True : le plus lourd sur la premiere place de l'ordre.
    Retourne [(bras_in, kg), ...] et la liste d'index de places utilisees.
    """
    n = len(weights_kg)
    ws = sorted(weights_kg, reverse=heaviest_first)
    used = order[:n]
    by_idx = {s.idx: s for s in slots}
    return [(by_idx[i].x, w) for i, w in zip(used, ws)], used


# ---------------------------------------------------------------------------
# Oracle : existe-t-il UNE affectation dans l'enveloppe ?
# ---------------------------------------------------------------------------

def para_moment_bounds(weights_kg, slots=SLOTS):
    """Moment paras (lbs.in/1000) min et max atteignables sur les places."""
    xs = sorted(s.x for s in slots)
    n = len(weights_kg)
    ws = sorted(w * LBS2KG for w in weights_kg)          # croissant
    # min : les plus lourds le plus en avant -> lourds (fin de ws) sur xs[:n] croissant inverse
    m_min = sum(w * x for w, x in zip(ws[::-1], xs[:n])) / 1000
    m_max = sum(w * x for w, x in zip(ws, xs[-n:])) / 1000
    return m_min, m_max


def feasible_exists(immat, pilot_kg, fuel_lbs, weights_kg, slots=SLOTS):
    """Vrai si au moins une affectation des paras aux places tombe dans l'enveloppe.

    La masse totale est fixee ; le CG est monotone dans le moment paras, donc
    la condition est l'intersection de deux intervalles. Le moment paras est
    discret mais les pas (echange de deux paras) sont petits devant la
    largeur de l'enveloppe, on confirme avec une recherche locale.
    """
    m0, w0 = base_state(immat, pilot_kg, fuel_lbs)
    mass = w0 + sum(weights_kg) * LBS2KG
    if mass > MTOW_LBS + CG_TOLERANCE:
        return False, None
    r_lo = fwd_limit(mass) * mass / 1000 - m0
    r_hi = AFT_CG * mass / 1000 - m0
    m_min, m_max = para_moment_bounds(weights_kg, slots)
    if m_max < r_lo - CG_TOLERANCE or m_min > r_hi + CG_TOLERANCE:
        return False, None
    placement = local_search(immat, pilot_kg, fuel_lbs, weights_kg, slots)
    if placement is None:
        return False, None
    return True, placement


def local_search(immat, pilot_kg, fuel_lbs, weights_kg, slots=SLOTS, max_iter=200):
    """Descente par echanges vers le centre de la bande CG admissible.

    Retourne une liste [(slot_idx, kg)] dans l'enveloppe, ou None.
    """
    m0, w0 = base_state(immat, pilot_kg, fuel_lbs)
    mass = w0 + sum(weights_kg) * LBS2KG
    target = (fwd_limit(mass) + AFT_CG) / 2 * mass / 1000 - m0   # moment paras vise
    xs = np.array([s.x for s in slots])
    n = len(weights_kg)
    ws = np.array(sorted(weights_kg, reverse=True)) * LBS2KG
    # depart : les plus lourds au plus pres du bras moyen vise
    xbar = target * 1000 / ws.sum()
    pos = list(np.argsort(np.abs(xs - xbar))[:n])   # pos[k] = place du para k

    def moment(p):
        return float((ws * xs[p]).sum() / 1000)

    def ok(mom):
        cg = (m0 + mom) / mass * 1000
        return envelope_status(mass, cg) == 'ok'

    cur = moment(pos)
    if ok(cur):
        return list(zip(pos, ws / LBS2KG))
    free = [i for i in range(len(slots)) if i not in pos]
    for _ in range(max_iter):
        best, best_move = abs(cur - target), None
        # echange para k <-> para l
        for k in range(n):
            for l in range(k + 1, n):
                d = (ws[k] - ws[l]) * (xs[pos[l]] - xs[pos[k]]) / 1000
                if abs(cur + d - target) < best - 1e-9:
                    best, best_move = abs(cur + d - target), ('swap', k, l)
            for f in free:
                d = ws[k] * (xs[f] - xs[pos[k]]) / 1000
                if abs(cur + d - target) < best - 1e-9:
                    best, best_move = abs(cur + d - target), ('move', k, f)
        if best_move is None:
            break
        if best_move[0] == 'swap':
            _, k, l = best_move
            pos[k], pos[l] = pos[l], pos[k]
        else:
            _, k, f = best_move
            free.remove(f)
            free.append(pos[k])
            pos[k] = f
        cur = moment(pos)
        if ok(cur):
            return list(zip(pos, ws / LBS2KG))
    return list(zip(pos, ws / LBS2KG)) if ok(cur) else None


# ---------------------------------------------------------------------------
# Un scenario = (immat, pilote, carburant, masses paras)
# ---------------------------------------------------------------------------

def evaluate(order, immat, pilot_kg, fuel_lbs, weights_kg, heaviest_first=True,
             slots=SLOTS):
    """Statut de l'heuristique sur un scenario : (statut, masse, cg, %MAC)."""
    placement, _ = assign(order, weights_kg, heaviest_first, slots)
    mass, cg = mass_cg(immat, pilot_kg, fuel_lbs, placement)
    return envelope_status(mass, cg), mass, cg, cg_to_mac(cg)


if __name__ == '__main__':
    print('Places N=20 (bras in, rangee) :')
    for s in SLOTS:
        print(f'  {s.idx:2d}  x={s.x:6.1f}  y={s.y:+6.1f}  {s.row}')
    print('\nOrdre par distance a 202 in :')
    for rank, i in enumerate(order_by_pivot(202.0), 1):
        s = SLOTS[i]
        print(f'  {rank:2d}. place {i:2d}  x={s.x:6.1f} ({abs(s.x-202):5.1f})  {s.row}')
