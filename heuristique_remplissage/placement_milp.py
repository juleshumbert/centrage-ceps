"""Placement des paras sur les places fixes par programmation lineaire en nombres entiers.

Variables : x[p, s] = 1 si le para p occupe la place s (binaire).
Contraintes :
  - chaque para a une place, chaque place au plus un para ;
  - centrage au decollage dans l'enveloppe (masse totale fixee, le moment est lineaire
    en x), avec une marge mu (in de CG) ;
  - option sequence : centrage encore dans l'enveloppe apres la sortie des k premiers
    paras, pour tout k (les autres restent a leur place) ;
  - tandems : porteur sur une place laterale, passager sur la place juste devant du
    meme cote (jamais au centre ni en siege copilote) ; fixer le porteur fixe le passager ;
  - cohesion des groupes, au choix :
      'boite' : boite englobante (bras mini/maxi, lateral mini/maxi) avec borne inferieure
                exacte sur sa taille ;
      'ancre' : une place d'ancrage par groupe, chaque membre paie sa distance a l'ancre
                (formulation type localisation, relaxation continue plus serree) ;
  - option groupes_ordonnes : coupe dure, un groupe qui sort avant est entierement en
    arriere d'un groupe qui sort apres.
Resolution (HiGHS via scipy.optimize.milp) :
  1. marge maximale mu* ;
  2. sous mu >= min(mu*, marge cible), minimiser le cout de realisme :
       poids_groupe x cohesion + poids_sortie x somme |rang porte de la place - rang de sortie| ;
  3. option cg_avant : sous cout de realisme <= (1 + tolerance) x cout de la phase 2,
     minimiser le moment, donc pousser le CG vers la limite avant (a la marge pres).

Manifeste JSON :
  {"immat": "C208B-A", "pilote_kg": 80, "fuel_lbs": 900,
   "paras": [{"nom": "A1", "kg": 95, "groupe": "A", "sortie": 1},
             {"nom": "T1p", "kg": 92, "tandem": "T1", "role": "porteur", "sortie": 2},
             {"nom": "T1x", "kg": 70, "tandem": "T1", "role": "passager", "sortie": 2}, ...]}
  "groupe", "sortie", "tandem"/"role" sont facultatifs ; "sortie" peut avoir des ex aequo.

Usage : python3 placement_milp.py manifeste.json [--sequence] [--marge 0.5] [--cohesion boite|ancre]
                                   [--groupes-ordonnes] [--cg-avant] [--temps 60] [--legacy]
"""
import argparse
import json
import time
from pathlib import Path

import numpy as np
from scipy.optimize import milp, LinearConstraint, Bounds
from scipy.sparse import csr_matrix

from caravan_model import (SLOTS, ZONES, PILOT_ARM, LBS2KG, MTOW_LBS, AFT_CG, fwd_limit,
                           base_state, cg_to_mac)

OUT = Path(__file__).resolve().parent / 'output'
DOOR = (307.0, -32.0)          # milieu de la porte (cote gauche, zones 4 a 6)
PITCH = 25.0                   # pas entre deux places, pour normaliser les couts


def seats(legacy=False):
    if legacy:
        from ordre_origine import legacy_slots
        xs = legacy_slots('C208B-A')
        ys = [16.0] * 8 + [0.0] * 5 + [-16.0] * 7
        return [(float(x), y) for x, y in zip(xs, ys)]
    return [(s.x, s.y) for s in SLOTS]


# rangees laterales (indices de places, de l'avant vers l'arriere) et siege copilote
SIDE_ROWS = {False: dict(copilot=0, droite=list(range(1, 8)), gauche=list(range(13, 20))),
             True: dict(copilot=0, droite=list(range(1, 8)), gauche=list(range(13, 20)))}


def exit_targets(paras):
    """Rang cible (1..N) par para selon 'sortie' (ex aequo : rang moyen) ; vide si absent."""
    ranked = [i for i, p in enumerate(paras) if p.get('sortie') is not None]
    if not ranked:
        return {}
    order = sorted(ranked, key=lambda i: paras[i]['sortie'])
    targets, pos = {}, 0
    while pos < len(order):
        same = [order[pos]]
        while pos + len(same) < len(order) and paras[order[pos + len(same)]]['sortie'] == paras[order[pos]]['sortie']:
            same.append(order[pos + len(same)])
        mean_rank = (2 * pos + len(same) + 1) / 2
        for i in same:
            targets[i] = mean_rank
        pos += len(same)
    return targets


class Placement:
    def __init__(self, manifest, legacy=False, sequence=False, marge_cible=0.5,
                 poids_groupe=2.0, poids_sortie=1.0, poids_lateral=0.5,
                 cohesion='boite', groupes_ordonnes=False, cg_avant=False, tolerance=0.05):
        self.m = manifest
        self.paras = manifest['paras']
        self.N = len(self.paras)
        self.seats = seats(legacy)
        self.S = len(self.seats)
        self.rows = SIDE_ROWS[legacy]
        self.sequence = sequence
        self.marge_cible = marge_cible
        self.w_g, self.w_s, self.w_l = poids_groupe, poids_sortie, poids_lateral
        self.cohesion = cohesion
        self.groupes_ordonnes = groupes_ordonnes
        self.cg_avant = cg_avant
        self.tolerance = tolerance
        self.immat = manifest['immat']
        self.pilot = manifest['pilote_kg']
        self.fuel = manifest['fuel_lbs']
        self.masses_lbs = np.array([p['kg'] for p in self.paras]) * LBS2KG
        self.m0, self.w0 = base_state(self.immat, self.pilot, self.fuel)
        self.groups = {}
        for i, p in enumerate(self.paras):
            g = p.get('groupe')
            if g is not None:
                self.groups.setdefault(g, []).append(i)
        self.groups = {g: m for g, m in self.groups.items() if len(m) >= 2}
        self.targets = exit_targets(self.paras)
        self.xs = np.array([s[0] for s in self.seats]); self.ys = np.array([s[1] for s in self.seats])
        d = np.hypot(self.xs - DOOR[0], self.ys - DOOR[1])
        self.door_rank = d.argsort().argsort() + 1
        self.dist = np.hypot(self.xs[:, None] - self.xs[None, :], self.ys[:, None] - self.ys[None, :])
        # tandems : (porteur, passager)
        tand = {}
        for i, p in enumerate(self.paras):
            if p.get('tandem') is not None:
                tand.setdefault(p['tandem'], {})[p.get('role', 'porteur')] = i
        self.tandems = []
        for tid, d_ in tand.items():
            if 'porteur' not in d_ or 'passager' not in d_:
                raise ValueError(f'tandem {tid} : il faut un porteur et un passager')
            self.tandems.append((d_['porteur'], d_['passager']))
        # places porteur autorisees -> place passager (juste devant, meme cote)
        self.tandem_pairs = {}
        for row in ('droite', 'gauche'):
            r = self.rows[row]
            for k in range(1, len(r)):
                self.tandem_pairs[r[k]] = r[k - 1]

    # --- utilitaires --------------------------------------------------------------------
    @staticmethod
    def _min_span(coords, n):
        c = np.sort(coords)
        return float(min(c[i + n - 1] - c[i] for i in range(len(c) - n + 1)))

    def _group_exit_rank(self, g):
        ranks = [self.paras[p].get('sortie') for p in self.groups[g]]
        return None if any(r is None for r in ranks) else min(ranks)

    def _stage_sets(self):
        if not self.sequence or not self.targets:
            return []
        order = sorted(self.targets, key=lambda i: (self.paras[i]['sortie'], i))
        rest = [i for i in range(self.N) if i not in self.targets]
        seq = order + rest
        return [seq[k:] for k in range(1, self.N)]

    # --- construction ----------------------------------------------------------------
    def _index(self):
        N, S = self.N, self.S
        self.ix = lambda p, s: p * S + s
        n = N * S
        self.ig = {}
        use_boxes = self.cohesion == 'boite' or self.groupes_ordonnes
        if use_boxes:
            for g in self.groups:
                self.ig[g] = (n, n + 1, n + 2, n + 3)
                n += 4
        self.iz, self.iy = {}, {}
        if self.cohesion == 'ancre':
            for g, members in self.groups.items():
                self.iz[g] = n; n += S                       # z[g, t]
                for p in members:
                    self.iy[p] = n; n += S * S               # y[p, s, t] = n + s*S + t
        self.imu = n
        return n + 1

    def build(self, phase, mu_min=None, cost_cap=None):
        nvar = self._index()
        N, S = self.N, self.S
        R, C, V, lbs, ubs = [], [], [], [], []
        nrow = [0]

        def add(coefs, lb, ub):
            for j, v in coefs:
                R.append(nrow[0]); C.append(j); V.append(v)
            lbs.append(lb); ubs.append(ub); nrow[0] += 1

        lb_v = np.zeros(nvar); ub_v = np.ones(nvar)
        integrality = np.zeros(nvar); integrality[:N * S] = 1

        for p in range(N):
            add([(self.ix(p, s), 1.0) for s in range(S)], 1, 1)
        for s in range(S):
            add([(self.ix(p, s), 1.0) for p in range(N)], -np.inf, 1)

        # tandems
        for m_, q in self.tandems:
            allowed_q = set(self.tandem_pairs.values())
            for s in range(S):
                if s not in self.tandem_pairs:
                    ub_v[self.ix(m_, s)] = 0
                if s not in allowed_q:
                    ub_v[self.ix(q, s)] = 0
            for s, sq in self.tandem_pairs.items():
                add([(self.ix(q, sq), 1.0), (self.ix(m_, s), -1.0)], 0, 0)

        # centrage au decollage avec marge mu
        W = self.w0 + self.masses_lbs.sum()
        lo = fwd_limit(W) * W / 1000 - self.m0
        hi = AFT_CG * W / 1000 - self.m0
        self.cmom = [(self.ix(p, s), self.masses_lbs[p] * self.xs[s] / 1000) for p in range(N) for s in range(S)]
        add(self.cmom + [(self.imu, -W / 1000)], lo, np.inf)
        add(self.cmom + [(self.imu, W / 1000)], -np.inf, hi)
        self.W = W

        # meme marge mu pendant le largage : la marge rendue est le minimum sur toutes les etapes
        for rest in self._stage_sets():
            Wk = self.w0 + self.masses_lbs[rest].sum()
            lok = fwd_limit(Wk) * Wk / 1000 - self.m0
            hik = AFT_CG * Wk / 1000 - self.m0
            ck = [(self.ix(p, s), self.masses_lbs[p] * self.xs[s] / 1000) for p in rest for s in range(S)]
            add(ck + [(self.imu, -Wk / 1000)], lok, np.inf)
            add(ck + [(self.imu, Wk / 1000)], -np.inf, hik)

        # boites englobantes
        xmin, xmax = self.xs.min(), self.xs.max()
        ymin, ymax = self.ys.min(), self.ys.max()
        for g, (Mn, Mx, Yn, Yx) in self.ig.items():
            members = self.groups[g]
            lb_v[[Mn, Mx]] = xmin; ub_v[[Mn, Mx]] = xmax
            lb_v[[Yn, Yx]] = ymin; ub_v[[Yn, Yx]] = ymax
            n_g = len(members)
            add([(Mx, 1.0), (Mn, -1.0)], self._min_span(self.xs, n_g), np.inf)
            add([(Yx, 1.0), (Yn, -1.0)], self._min_span(self.ys, n_g), np.inf)
            for p in members:
                add([(self.ix(p, s), self.xs[s]) for s in range(S)] + [(Mx, -1.0)], -np.inf, 0)
                add([(self.ix(p, s), self.xs[s]) for s in range(S)] + [(Mn, -1.0)], 0, np.inf)
                for s in range(S):
                    add([(self.ix(p, s), self.xs[s] - xmin), (Mx, -1.0)], -np.inf, -xmin)
                    add([(self.ix(p, s), self.xs[s] - xmax), (Mn, -1.0)], -xmax, np.inf)
                    add([(self.ix(p, s), self.ys[s] - ymin), (Yx, -1.0)], -np.inf, -ymin)
                    add([(self.ix(p, s), self.ys[s] - ymax), (Yn, -1.0)], -ymax, np.inf)

        # groupes ordonnes : sortie plus tot => entierement en arriere
        if self.groupes_ordonnes:
            gl = [(g, self._group_exit_rank(g)) for g in self.groups]
            for g, rg in gl:
                for h, rh in gl:
                    if rg is not None and rh is not None and rg < rh:
                        add([(self.ig[g][0], 1.0), (self.ig[h][1], -1.0)], 0, np.inf)   # Mn_g >= Mx_h

        # cohesion par ancre
        if self.cohesion == 'ancre':
            for g, members in self.groups.items():
                z0 = self.iz[g]
                integrality[z0:z0 + S] = 1
                add([(z0 + t, 1.0) for t in range(S)], 1, 1)
                for p in members:
                    y0 = self.iy[p]
                    for s in range(S):
                        add([(y0 + s * S + t, 1.0) for t in range(S)] + [(self.ix(p, s), -1.0)], 0, 0)
                        for t in range(S):
                            add([(y0 + s * S + t, 1.0), (z0 + t, -1.0)], -np.inf, 0)

        # cout de realisme (phase 2), reutilise comme contrainte en phase 3
        real = np.zeros(nvar)
        for p, r in self.targets.items():
            for s in range(S):
                real[self.ix(p, s)] += self.w_s * abs(self.door_rank[s] - r)
        if self.cohesion == 'boite':
            for g, (Mn, Mx, Yn, Yx) in self.ig.items():
                real[Mx] += self.w_g / PITCH; real[Mn] -= self.w_g / PITCH
                real[Yx] += self.w_g * self.w_l / PITCH; real[Yn] -= self.w_g * self.w_l / PITCH
        else:
            for g, members in self.groups.items():
                for p in members:
                    y0 = self.iy[p]
                    for s in range(S):
                        for t in range(S):
                            real[y0 + s * S + t] += self.w_g * self.dist[s, t] / PITCH
        self.real = real
        if cost_cap is not None:
            nz = [(j, real[j]) for j in np.nonzero(real)[0]]
            add(nz, -np.inf, cost_cap)

        lb_v[self.imu] = -50.0 if mu_min is None else mu_min
        ub_v[self.imu] = 50.0

        cost = np.zeros(nvar)
        if phase == 1:
            cost[self.imu] = -1.0
        elif phase == 2:
            cost = real.copy()
            cost[self.imu] = -1e-3
        else:                                   # phase 3 : CG le plus avant
            for j, v in self.cmom:
                cost[j] += v
        A = csr_matrix((V, (R, C)), shape=(nrow[0], nvar))
        return cost, LinearConstraint(A, lbs, ubs), Bounds(lb_v, ub_v), integrality

    # --- resolution ---------------------------------------------------------------------
    def solve(self, time_limit=60.0, gap=0.01, verbose=False):
        opts = dict(time_limit=time_limit, mip_rel_gap=gap, disp=verbose)
        t0 = time.time()
        W = self.w0 + self.masses_lbs.sum()
        if W > MTOW_LBS + 1e-6:
            return dict(ok=False, message=f'masse au decollage {W:.0f} lbs > MTOW {MTOW_LBS} '
                        f'(depassement {(W - MTOW_LBS) / LBS2KG:.0f} kg)', temps=0.0)
        cost, cons, bnd, integ = self.build(phase=1)
        r1 = milp(cost, constraints=cons, bounds=bnd, integrality=integ, options=opts)
        t1 = time.time() - t0
        if r1.x is None:
            return dict(ok=False, message='aucun placement dans l enveloppe' +
                        (' (y compris pendant le largage)' if self.sequence else '') +
                        (' avec ces tandems / cet ordre de groupes' if self.tandems or self.groupes_ordonnes else ''),
                        temps=t1)
        mu_star = r1.x[self.imu]
        if mu_star < -1e-6:
            # la phase 1 est toujours faisable (mu libre) : mu* < 0 veut dire qu'aucun
            # placement ne tient dans l'enveloppe ; on rend le moins mauvais
            x = r1.x[:self.N * self.S].reshape(self.N, self.S)
            seat_of = [int(np.argmax(x[p])) for p in range(self.N)]
            return dict(ok=False, message=f'aucun placement dans l enveloppe : au mieux {-mu_star:.2f} in dehors'
                        + (' (largage compris)' if self.sequence else ''),
                        mu_max=mu_star, seat_of=seat_of, etapes=self.check(seat_of), temps=t1)
        mu_min = min(mu_star, self.marge_cible) - 1e-6
        cost, cons, bnd, integ = self.build(phase=2, mu_min=mu_min)
        t2a = time.time()
        r2 = milp(cost, constraints=cons, bounds=bnd, integrality=integ, options=opts)
        t2 = time.time() - t2a
        if r2.x is None:
            return dict(ok=False, message='phase 2 infaisable (inattendu)', temps=time.time() - t0)
        xbest, fun2 = r2.x, float(self.real @ r2.x)
        res = dict(ok=True, mu_max=mu_star, optimal=(r2.status == 0), gap=getattr(r2, 'mip_gap', None),
                   temps_phase1=t1, temps_phase2=t2, cout=fun2)
        if self.cg_avant:
            cap = fun2 + self.tolerance * abs(fun2) + 1e-6
            cost, cons, bnd, integ = self.build(phase=3, mu_min=mu_min, cost_cap=cap)
            t3a = time.time()
            r3 = milp(cost, constraints=cons, bounds=bnd, integrality=integ, options=opts)
            res['temps_phase3'] = time.time() - t3a
            if r3.x is not None:
                xbest = r3.x
                res['optimal3'] = (r3.status == 0)
                res['cout'] = float(self.real @ xbest)
        x = xbest[:self.N * self.S].reshape(self.N, self.S)
        seat_of = [int(np.argmax(x[p])) for p in range(self.N)]
        res.update(seat_of=seat_of, mu=xbest[self.imu], temps=time.time() - t0)
        res['etapes'] = self.check(seat_of)
        res['metriques'] = self.metrics(seat_of)
        return res

    def check(self, seat_of):
        order = sorted(self.targets, key=lambda i: (self.paras[i]['sortie'], i))
        seq = order + [i for i in range(self.N) if i not in self.targets]
        out = []
        for k in range(0, self.N + 1):
            rest = seq[k:]
            W = self.w0 + self.masses_lbs[rest].sum()
            M = self.m0 + sum(self.masses_lbs[p] * self.xs[seat_of[p]] / 1000 for p in rest)
            cg = M / W * 1000
            marge = min(cg - fwd_limit(W), AFT_CG - cg)
            out.append(dict(k=k, restants=len(rest), masse_lbs=W, cg_in=cg, mac=cg_to_mac(cg), marge_in=marge,
                            ok=(W <= MTOW_LBS + 1e-6 and marge >= -1e-6)))
        return out

    def metrics(self, seat_of):
        """Metriques de realisme independantes de la formulation."""
        boites = 0.0
        for g, members in self.groups.items():
            xs = [self.xs[seat_of[p]] for p in members]; ys = [self.ys[seat_of[p]] for p in members]
            boites += (max(xs) - min(xs) + self.w_l * (max(ys) - min(ys))) / PITCH
        sortie = sum(abs(self.door_rank[seat_of[p]] - r) for p, r in self.targets.items())
        return dict(boites=boites, sortie=sortie)

    # --- sortie ------------------------------------------------------------------------
    def report(self, res):
        print(f"{self.immat}, pilote {self.pilot} kg, carburant {self.fuel} lbs, {self.N} paras "
              f"({sum(p['kg'] for p in self.paras):.0f} kg), groupes {list(self.groups) or 'aucun'}, "
              f"tandems {len(self.tandems)}, cohesion {self.cohesion}"
              f"{', groupes ordonnes' if self.groupes_ordonnes else ''}{', CG avant' if self.cg_avant else ''}")
        if not res['ok']:
            print('  ECHEC :', res['message'], f"({res['temps']:.2f} s)")
            return
        etat = 'optimum prouve' if res['optimal'] else (
            f"temps limite, ecart {res['gap']:.1%}" if res['gap'] is not None else 'temps limite')
        print(f"  marge max possible {res['mu_max']:+.2f} in ; phase 1 {res['temps_phase1']:.1f} s, "
              f"phase 2 {res['temps_phase2']:.1f} s ({etat})"
              + (f", phase 3 {res['temps_phase3']:.1f} s" if 'temps_phase3' in res else ''))
        mt = res['metriques']
        print(f"  realisme : boites {mt['boites']:.2f} pas, ecart de sortie {mt['sortie']:.1f} rangs ; cout {res['cout']:.2f}")
        print(f"  {'para':8s} {'kg':>5s} {'groupe':7s} {'tandem':7s} {'sortie':>6s}   place  bras   cote     rang porte")
        cote = {16.0: 'droite', 0.0: 'centre', -16.0: 'gauche'}
        for p in sorted(range(self.N), key=lambda p: (self.paras[p].get('sortie', 99), p)):
            s = res['seat_of'][p]
            pr = self.paras[p]
            print(f"  {pr['nom']:8s} {pr['kg']:5.0f} {str(pr.get('groupe', '-')):7s} {str(pr.get('tandem', '-')):7s} "
                  f"{str(pr.get('sortie', '-')):>6s}   {s:3d}    {self.xs[s]:4.0f}   {cote.get(self.ys[s], '?'):7s}  {self.door_rank[s]:3d}")
        e0 = res['etapes'][0]
        print(f"  decollage : {e0['masse_lbs']:.0f} lbs, CG {e0['cg_in']:.2f} in ({e0['mac']:.2f} %MAC), "
              f"marge {e0['marge_in']:+.2f} in (limite avant {fwd_limit(e0['masse_lbs']):.2f}, arriere {AFT_CG})")
        if self.sequence and self.targets:
            worst = min(res['etapes'][1:-1], key=lambda e: e['marge_in'], default=None)
            if worst:
                print(f"  largage : marge minimale {worst['marge_in']:+.2f} in apres {worst['k']} sorties "
                      f"({worst['restants']} restants, CG {worst['cg_in']:.2f} in)")

    def draw(self, res, path, title=None):
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches
        fig, ax = plt.subplots(figsize=(11, 4))
        for i in range(6):
            z, z1 = ZONES[i], ZONES[i + 1]
            ax.add_patch(patches.Polygon([(z['x0'], -z['height'] / 2), (z['x0'], z['height'] / 2),
                                          (z['x1'], z1['height'] / 2), (z['x1'], -z1['height'] / 2)],
                                         lw=1.0, fill=False, edgecolor='#0b0b0b'))
        ax.plot([ZONES[4]['x0'], ZONES[6]['x0']], [-ZONES[4]['height'] / 2 - 2] * 2, color='#eb6834', lw=4)
        ax.text(DOOR[0], DOOR[1] - 4, 'porte', ha='center', va='top', fontsize=8, color='#eb6834')
        ax.add_patch(patches.Circle((PILOT_ARM, -16), 5.5, color='#52514e', zorder=3))
        ax.text(PILOT_ARM, -16, 'P', ha='center', va='center', color='white', fontsize=8, fontweight='bold', zorder=4)
        palette = ['#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#e87ba4', '#008300', '#4a3aa7', '#e34948']
        gcol = {g: palette[i % len(palette)] for i, g in enumerate(self.groups)}
        for s, (x, y) in enumerate(self.seats):
            ax.add_patch(patches.Circle((x, y), 5.8, fill=False, edgecolor='#bbbbbb', lw=0.8, zorder=2))
        for m_, q in self.tandems:
            (x1, y1), (x2, y2) = self.seats[res['seat_of'][m_]], self.seats[res['seat_of'][q]]
            ax.plot([x1, x2], [y1, y2], color='#0b0b0b', lw=2.5, zorder=2.5)
        for p in range(self.N):
            s = res['seat_of'][p]; x, y = self.seats[s]
            pr = self.paras[p]
            col = gcol.get(pr.get('groupe'), '#52514e')
            ax.add_patch(patches.Circle((x, y), 5.8, color=col, zorder=3))
            lab = str(pr.get('etiquette', pr['sortie'])) if pr.get('sortie') is not None else '-'
            ax.text(x, y, lab, ha='center', va='center', color='white', fontsize=8, fontweight='bold', zorder=4)
            ax.text(x, y - 9.5, f"{pr['nom']} {pr['kg']:.0f}", ha='center', va='top', fontsize=5.5, color='#52514e',
                    bbox=dict(facecolor='white', edgecolor='none', pad=0.3), zorder=5)
        for g, c in gcol.items():
            ax.plot([], [], 'o', color=c, label=f'groupe {g}')
        if self.tandems:
            ax.plot([], [], '-', color='#0b0b0b', lw=2.5, label='tandem')
        if gcol or self.tandems:
            ax.legend(loc='lower left', fontsize=7, frameon=False)
        e0 = res['etapes'][0]
        ax.set_title(title or f"{self.immat}, carburant {self.fuel} lbs, {self.N} paras : CG {e0['cg_in']:.1f} in "
                     f"({e0['mac']:.1f} %MAC), marge {e0['marge_in']:+.2f} in. Numero = ordre de sortie", fontsize=9)
        ax.set_xlim(98, 360); ax.set_ylim(-44, 40); ax.set_aspect('equal'); ax.axis('off')
        fig.tight_layout(); fig.savefig(path, dpi=160); plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('manifeste')
    ap.add_argument('--sequence', action='store_true', help='centrage verifie a chaque sortie')
    ap.add_argument('--marge', type=float, default=0.5, help='marge CG cible (in)')
    ap.add_argument('--legacy', action='store_true', help='places legacy (get_slots_bk)')
    ap.add_argument('--cohesion', choices=['boite', 'ancre'], default='boite')
    ap.add_argument('--groupes-ordonnes', action='store_true', help='groupe sortant avant = entierement en arriere')
    ap.add_argument('--cg-avant', action='store_true', help='phase 3 : CG le plus avant possible a realisme quasi egal')
    ap.add_argument('--tolerance', type=float, default=0.05, help='tolerance sur le cout de realisme en phase 3')
    ap.add_argument('--poids-groupe', type=float, default=2.0)
    ap.add_argument('--poids-sortie', type=float, default=1.0)
    ap.add_argument('--png', default=None)
    ap.add_argument('--temps', type=float, default=60.0, help='temps limite par phase (s)')
    ap.add_argument('--gap', type=float, default=0.01, help='ecart relatif accepte a l optimum')
    a = ap.parse_args()
    man = json.loads(Path(a.manifeste).read_text())
    pl = Placement(man, legacy=a.legacy, sequence=a.sequence, marge_cible=a.marge,
                   poids_groupe=a.poids_groupe, poids_sortie=a.poids_sortie, cohesion=a.cohesion,
                   groupes_ordonnes=a.groupes_ordonnes, cg_avant=a.cg_avant, tolerance=a.tolerance)
    res = pl.solve(time_limit=a.temps, gap=a.gap)
    pl.report(res)
    if res['ok']:
        png = a.png or OUT / f"placement_{Path(a.manifeste).stem}.png"
        pl.draw(res, png)
        print('  plan :', png)


if __name__ == '__main__':
    main()
