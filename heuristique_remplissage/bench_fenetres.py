"""Formulation "fenetres" (doc_placement_milp.html, section 5.10) : une variable binaire u[g,w] par groupe et fenetre candidate
(intervalle de bras x intervalle lateral contenant au moins n_g places), cout de cohesion
exact par fenetre, x[p,s] <= somme des u des fenetres contenant s, et somme_{s in w} x[p,s] >= u[g,w].
Compare borne LP et MILP 60 s a la formulation 'boite'."""
import json, sys, time, itertools
import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds
from scipy.sparse import csr_matrix
from placement_milp import Placement, PITCH

class Windows(Placement):
    def _windows(self, n_g):
        A = sorted(set(self.xs.tolist())); Y = sorted(set(self.ys.tolist()))
        out = []
        for i, alo in enumerate(A):
            for ahi in A[i:]:
                for j, ylo in enumerate(Y):
                    for yhi in Y[j:]:
                        inside = [s for s in range(self.S) if alo <= self.xs[s] <= ahi and ylo <= self.ys[s] <= yhi]
                        if len(inside) < n_g:
                            continue
                        xi = self.xs[inside]; yi = self.ys[inside]
                        if xi.min() != alo or xi.max() != ahi or yi.min() != ylo or yi.max() != yhi:
                            continue          # bornes non atteintes : fenetre dominee
                        out.append((alo, ahi, ylo, yhi, inside))
        return out

    def build(self, phase, mu_min=None, cost_cap=None):
        N, S = self.N, self.S
        self.ix = lambda p, s: p * S + s
        n = N * S
        self.win = {g: self._windows(len(m)) for g, m in self.groups.items()}
        self.iu = {}
        for g, ws in self.win.items():
            self.iu[g] = n; n += len(ws)
        self.imu = n; nvar = n + 1
        R, C, V, lbs, ubs = [], [], [], [], []
        nrow = [0]
        def add(coefs, lb, ub):
            for j, v in coefs:
                R.append(nrow[0]); C.append(j); V.append(v)
            lbs.append(lb); ubs.append(ub); nrow[0] += 1
        lb_v = np.zeros(nvar); ub_v = np.ones(nvar)
        integrality = np.ones(nvar); integrality[self.imu] = 0
        for p in range(N):
            add([(self.ix(p, s), 1.0) for s in range(S)], 1, 1)
        for s in range(S):
            add([(self.ix(p, s), 1.0) for p in range(N)], -np.inf, 1)
        W = self.w0 + self.masses_lbs.sum()
        from caravan_model import fwd_limit, AFT_CG
        lo = fwd_limit(W) * W / 1000 - self.m0; hi = AFT_CG * W / 1000 - self.m0
        self.cmom = [(self.ix(p, s), self.masses_lbs[p] * self.xs[s] / 1000) for p in range(N) for s in range(S)]
        add(self.cmom + [(self.imu, -W / 1000)], lo, np.inf)
        add(self.cmom + [(self.imu, W / 1000)], -np.inf, hi)
        self.W = W
        for rest in self._stage_sets():
            Wk = self.w0 + self.masses_lbs[rest].sum()
            lok = fwd_limit(Wk) * Wk / 1000 - self.m0; hik = AFT_CG * Wk / 1000 - self.m0
            add([(self.ix(p, s), self.masses_lbs[p] * self.xs[s] / 1000) for p in rest for s in range(S)], lok, hik)
        # fenetres
        for g, members in self.groups.items():
            ws = self.win[g]; u0 = self.iu[g]
            add([(u0 + k, 1.0) for k in range(len(ws))], 1, 1)
            contains = {s: [k for k, w in enumerate(ws) if s in w[4]] for s in range(S)}
            for p in members:
                for s in range(S):
                    add([(self.ix(p, s), 1.0)] + [(u0 + k, -1.0) for k in contains[s]], -np.inf, 0)
                for k, w in enumerate(ws):
                    add([(self.ix(p, s), 1.0) for s in w[4]] + [(u0 + k, -1.0)], 0, np.inf)
        if self.groupes_ordonnes:
            gl = [(g, self._group_exit_rank(g)) for g in self.groups]
            for g, rg in gl:
                for h, rh in gl:
                    if rg is not None and rh is not None and rg < rh:
                        add([(self.iu[g] + k, w[0]) for k, w in enumerate(self.win[g])] +
                            [(self.iu[h] + k, -w[1]) for k, w in enumerate(self.win[h])], 0, np.inf)
        real = np.zeros(nvar)
        for p, r in self.targets.items():
            for s in range(S):
                real[self.ix(p, s)] += self.w_s * abs(self.door_rank[s] - r)
        for g, ws in self.win.items():
            for k, (alo, ahi, ylo, yhi, _) in enumerate(ws):
                real[self.iu[g] + k] = self.w_g * ((ahi - alo) + self.w_l * (yhi - ylo)) / PITCH
        self.real = real
        if cost_cap is not None:
            add([(j, real[j]) for j in np.nonzero(real)[0]], -np.inf, cost_cap)
        lb_v[self.imu] = -50.0 if mu_min is None else mu_min; ub_v[self.imu] = 50.0
        cost = np.zeros(nvar)
        if phase == 1:
            cost[self.imu] = -1.0
        elif phase == 2:
            cost = real.copy(); cost[self.imu] = -1e-3
        else:
            for j, v in self.cmom:
                cost[j] += v
        A = csr_matrix((V, (R, C)), shape=(nrow[0], nvar))
        return cost, LinearConstraint(A, lbs, ubs), Bounds(lb_v, ub_v), integrality

man = json.loads(open('manifestes/exemple_groupes.json').read())
for ordonnes in (False, True):
    pl = Windows(man, sequence=True, groupes_ordonnes=ordonnes)
    cost, cons, bnd, integ = pl.build(phase=1)
    r1 = milp(cost, constraints=cons, bounds=bnd, integrality=integ, options=dict(time_limit=60))
    mu = r1.x[pl.imu]; mu_min = min(mu, 0.5) - 1e-6
    cost, cons, bnd, integ = pl.build(phase=2, mu_min=mu_min)
    nwin = {g: len(w) for g, w in pl.win.items()}
    print(f'fenetres ordonnes={ordonnes}: fenetres par groupe {nwin}, nvar={len(cost)} (binaires {int(integ.sum())}), ncontraintes={cons.A.shape[0]}, nnz={cons.A.nnz}, mu*={mu:.3f}', flush=True)
    t = time.time(); rlp = milp(cost, constraints=cons, bounds=bnd, integrality=np.zeros_like(integ))
    print(f'  relaxation LP phase 2 : {rlp.fun:.3f} ({time.time()-t:.2f} s)', flush=True)
    t = time.time(); r2 = milp(cost, constraints=cons, bounds=bnd, integrality=integ, options=dict(time_limit=60, mip_rel_gap=0.01))
    x = r2.x[:pl.N * pl.S].reshape(pl.N, pl.S); seat_of = [int(np.argmax(x[p])) for p in range(pl.N)]
    mt = pl.metrics(seat_of)
    print(f'  MILP 60 s : cout {r2.fun:.3f}, status {r2.status}, gap {getattr(r2, "mip_gap", None)}, borne duale {getattr(r2, "mip_dual_bound", None)}, noeuds {getattr(r2, "mip_node_count", None)} ({time.time()-t:.1f} s) ; boites {mt["boites"]:.2f} sortie {mt["sortie"]:.0f}', flush=True)
