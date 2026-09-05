"""Evaluation vectorisee d'un ordre de remplissage sur tous les scenarios.

Pour un scenario, la masse totale est fixee ; seule compte la somme des
moments paras. On precalcule pour chaque scenario la bande de moment paras
admissible [r_lo, r_hi] (limite avant a la masse du jour, limite arriere) et
les masses triees. Un ordre de places donne alors le moment paras en un
produit matriciel.
"""
import numpy as np

from caravan_model import (SLOTS, LBS2KG, AFT_CG, fwd_limit, base_state,
                           para_moment_bounds)

XS = np.array([s.x for s in SLOTS])


class Bench:
    def __init__(self, scenarios):
        self.scs = scenarios
        S = len(scenarios)
        self.W_desc = np.zeros((S, 20))     # masses lbs triees decroissantes, 0 au-dela de n
        self.W_asc = np.zeros((S, 20))
        self.n = np.zeros(S, dtype=int)
        self.mass = np.zeros(S)
        self.r_lo = np.zeros(S)
        self.r_hi = np.zeros(S)
        self.m_min = np.zeros(S)
        self.m_max = np.zeros(S)
        for i, sc in enumerate(scenarios):
            m0, w0 = base_state(sc.immat, sc.pilot_kg, sc.fuel_lbs)
            ws = np.array(sorted(sc.weights_kg, reverse=True)) * LBS2KG
            n = len(ws)
            self.n[i] = n
            self.W_desc[i, :n] = ws
            self.W_asc[i, :n] = ws[::-1]
            mass = w0 + ws.sum()
            self.mass[i] = mass
            self.r_lo[i] = fwd_limit(mass) * mass / 1000 - m0
            self.r_hi[i] = AFT_CG * mass / 1000 - m0
            self.m_min[i], self.m_max[i] = para_moment_bounds(sc.weights_kg)
        # faisabilite (intervalle) : identique pour tous les ordres
        self.feasible = (self.m_max >= self.r_lo - 1e-6) & (self.m_min <= self.r_hi + 1e-6)
        self.center = (self.r_lo + self.r_hi) / 2
        self.half = (self.r_hi - self.r_lo) / 2

    def moments(self, order, heaviest_first=True):
        W = self.W_desc if heaviest_first else self.W_asc
        return W @ XS[np.asarray(order)] / 1000

    def status(self, order, heaviest_first=True):
        """0 ok, -1 avant, +1 arriere (sur tous les scenarios)."""
        m = self.moments(order, heaviest_first)
        st = np.zeros(len(m), dtype=int)
        st[m < self.r_lo - 1e-6] = -1
        st[m > self.r_hi + 1e-6] = 1
        return st

    def failures(self, order, heaviest_first=True):
        """Nombre d'echecs heuristiques (scenario faisable mais hors enveloppe)."""
        st = self.status(order, heaviest_first)
        return int(((st != 0) & self.feasible).sum())

    def margin_loss(self, order, heaviest_first=True):
        """Perte continue : depassement normalise, cumule sur les scenarios faisables."""
        m = self.moments(order, heaviest_first)
        exc = np.maximum(np.abs(m - self.center) - self.half, 0) / self.half
        return float((exc * self.feasible).sum())

    def min_margin_mac(self, order, heaviest_first=True):
        """Marge minimale (in de CG, signe : + dedans) sur les scenarios faisables."""
        m = self.moments(order, heaviest_first)
        marg = (self.half - np.abs(m - self.center)) * 1000 / self.mass   # en inches de CG
        return float(marg[self.feasible].min())


# ---------------------------------------------------------------------------
# Critere robuste : pire affectation des masses sur les places utilisees.
# Pour un ordre donne et n paras, les n premieres places sont fixees ; le
# moment paras varie entre "les plus lourds devant" et "les plus lourds
# derriere". Si les deux extremes sont dans la bande, n'importe quel ordre
# d'embarquement convient.
# ---------------------------------------------------------------------------

def _used_arms_sorted(order):
    """Xasc[n], Xdesc[n] : bras des n premieres places de l'ordre, tries, padded 0."""
    xs = XS[np.asarray(order)]
    Xasc = np.zeros((21, 20))
    Xdesc = np.zeros((21, 20))
    for n in range(1, 21):
        u = np.sort(xs[:n])
        Xasc[n, :n] = u
        Xdesc[n, :n] = u[::-1]
    return Xasc, Xdesc


class BenchRobust(Bench):
    def moments_range(self, order):
        Xasc, Xdesc = _used_arms_sorted(order)
        m_lo = np.einsum('ij,ij->i', self.W_desc, Xasc[self.n]) / 1000   # lourds devant
        m_hi = np.einsum('ij,ij->i', self.W_desc, Xdesc[self.n]) / 1000  # lourds derriere
        return m_lo, m_hi

    def status_worst(self, order):
        """0 ok pour toute affectation ; -1 une affectation sort par l'avant ;
        +1 par l'arriere ; 2 les deux."""
        m_lo, m_hi = self.moments_range(order)
        st = np.zeros(len(m_lo), dtype=int)
        av = m_lo < self.r_lo - 1e-6
        ar = m_hi > self.r_hi + 1e-6
        st[av] = -1
        st[ar] = 1
        st[av & ar] = 2
        return st

    def failures_worst(self, order):
        return int(((self.status_worst(order) != 0) & self.feasible).sum())

    def margin_worst(self, order):
        """Marge minimale (in de CG) sur les scenarios faisables, pire affectation."""
        m_lo, m_hi = self.moments_range(order)
        marg = np.minimum(m_lo - self.r_lo, self.r_hi - m_hi) * 1000 / self.mass
        return marg

    def cost_worst(self, order, target_margin_in=0.0):
        """Echecs (avec marge cible) + terme continu de depassement."""
        marg = self.margin_worst(order)[self.feasible]
        short = np.maximum(target_margin_in - marg, 0)
        return int((short > 0).sum()) + 0.5 * float(short.sum())
