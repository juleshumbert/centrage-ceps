// Placement des paras sur places fixes : binaire autonome (aucune dependance).
//
//   placement entree.json [sortie.json]      (ou  placement - < entree.json)
//
// Phase 1 (exacte) : existe-t-il un placement dans l'enveloppe, au decollage et, si
//   demande, apres la sortie de chaque para ? Recherche arborescente avec bornes de
//   moment (les plus lourds sur les places les plus avant / arriere libres), dichotomie
//   sur la marge pour trouver la marge maximale.
// Phase 2 (heuristique) : parmi les placements a marge >= min(marge max, marge cible),
//   minimiser un cout de realisme (groupes compacts, premiers sortants pres de la porte,
//   tandems porteur/passager cote a cote) par recuit simule a redemarrages, chaque
//   solution retenue etant verifiee exactement.
//
// Voir README (section binaire) pour le format JSON.
mod json;
use json::{obj, Json};
use std::time::Instant;

#[derive(Clone)]
struct Seat {
    id: String,
    x: f64,
    y: f64,
    copilot: bool,
    centre: bool,          // rangee centrale : pas de tandem
    devant: Option<usize>, // place juste devant, meme cote (pour le passager tandem)
}

#[derive(Clone)]
struct Para {
    nom: String,
    m: f64,
    groupe: Option<String>,
    sortie: Option<f64>,
    tandem: Option<String>,
    porteur: bool,
    seq: usize,         // position dans l'ordre de sortie
    target: Option<f64>, // rang cible de distance a la porte
}

struct Model {
    seats: Vec<Seat>,
    paras: Vec<Para>,
    base_m: f64,   // masse hors paras
    base_mom: f64, // moment hors paras
    fwd: Vec<(f64, f64)>,
    aft: Vec<(f64, f64)>,
    mtow: f64,
    stages: Vec<Vec<usize>>, // paras restants a l'etape k (k = 0 : decollage)
    door_rank: Vec<f64>,
    groups: Vec<(String, Vec<usize>, Option<f64>)>, // nom, membres, sortie du groupe
    pairs: Vec<(usize, usize)>,                     // (porteur, passager)
    ordered: bool,
    w_g: f64,
    w_s: f64,
    w_l: f64,
    pitch: f64,
    marge_cible: f64,
    temps_max: f64,
    objectif_arriere: bool, // true : maximiser la marge arriere au decollage sous marge avant >= marge_avant_min
    marge_avant_min: f64,
    tolerance: f64,         // phase 2 : marge arriere >= max - tolerance
    etapes_label: String,   // "premier_groupe" | "toutes" | "decollage"
}

fn interp(pts: &[(f64, f64)], w: f64) -> f64 {
    if pts.is_empty() {
        return f64::NAN;
    }
    if w <= pts[0].0 {
        return pts[0].1;
    }
    for i in 1..pts.len() {
        if w <= pts[i].0 {
            let (w0, c0) = pts[i - 1];
            let (w1, c1) = pts[i];
            return c0 + (c1 - c0) * (w - w0) / (w1 - w0);
        }
    }
    pts[pts.len() - 1].1
}

fn fnum(j: &Json, k: &str, d: f64) -> f64 {
    j.get(k).and_then(|v| v.num()).unwrap_or(d)
}

fn load(j: &Json) -> Result<Model, String> {
    let av = j.get("avion").ok_or("avion manquant")?;
    let ew = av.get("masse_vide").and_then(|v| v.num()).ok_or("avion.masse_vide manquant")?;
    let ew_mom = match (av.get("moment_vide").and_then(|v| v.num()), av.get("bras_vide").and_then(|v| v.num())) {
        (Some(m), _) => m,
        (None, Some(b)) => ew * b,
        _ => return Err("avion.moment_vide ou avion.bras_vide manquant".into()),
    };
    let env = j.get("enveloppe").ok_or("enveloppe manquante")?;
    let pts = |k: &str| -> Result<Vec<(f64, f64)>, String> {
        let a = env.get(k).and_then(|v| v.arr()).ok_or(format!("enveloppe.{} manquante", k))?;
        let mut v: Vec<(f64, f64)> = a
            .iter()
            .map(|p| {
                let q = p.arr().ok_or("point d'enveloppe invalide")?;
                Ok((q[0].num().unwrap_or(0.0), q[1].num().unwrap_or(0.0)))
            })
            .collect::<Result<_, String>>()?;
        v.sort_by(|a, b| a.0.partial_cmp(&b.0).unwrap());
        Ok(v)
    };
    let fwd = pts("avant")?;
    let aft = pts("arriere")?;
    let mtow = fnum(env, "mtow", f64::INFINITY);
    let fuel = j.get("carburant");
    let fuel_m = fuel.map(|f| fnum(f, "masse", 0.0)).unwrap_or(0.0);
    let fuel_x = fuel.map(|f| fnum(f, "bras", 0.0)).unwrap_or(0.0);
    let pil = j.get("pilote");
    let pil_m = pil.map(|f| fnum(f, "masse", 0.0)).unwrap_or(0.0);
    let pil_x = pil.map(|f| fnum(f, "bras", 0.0)).unwrap_or(0.0);
    let base_m = ew + fuel_m + pil_m;
    let base_mom = ew_mom + fuel_m * fuel_x + pil_m * pil_x;

    let mut seats: Vec<Seat> = Vec::new();
    for (i, s) in j.get("places").and_then(|v| v.arr()).ok_or("places manquantes")?.iter().enumerate() {
        seats.push(Seat {
            id: s.get("id").and_then(|v| v.str()).map(|x| x.to_string()).unwrap_or(format!("{}", i)),
            x: s.get("x").and_then(|v| v.num()).ok_or("place sans x")?,
            y: fnum(s, "y", 0.0),
            copilot: s.get("copilote").and_then(|v| v.boolean()).unwrap_or(false),
            centre: s.get("centre").and_then(|v| v.boolean()).unwrap_or(false),
            devant: None,
        });
    }
    // place devant : donnee ("devant": id) ou deduite (meme y, x immediatement inferieur)
    let ids: Vec<String> = seats.iter().map(|s| s.id.clone()).collect();
    for (i, s) in j.get("places").unwrap().arr().unwrap().iter().enumerate() {
        if let Some(d) = s.get("devant").and_then(|v| v.str()) {
            seats[i].devant = ids.iter().position(|x| x == d);
        } else {
            let (x, y) = (seats[i].x, seats[i].y);
            let mut best: Option<usize> = None;
            for (k, t) in seats.iter().enumerate() {
                if k != i && (t.y - y).abs() < 1e-6 && t.x < x - 1e-6 && !t.copilot && !t.centre {
                    if best.map_or(true, |b| t.x > seats[b].x) {
                        best = Some(k);
                    }
                }
            }
            seats[i].devant = best;
        }
        if seats[i].copilot || seats[i].centre {
            seats[i].devant = None;
        }
    }
    let door = j.get("porte");
    let (dx, dy) = door.map(|d| (fnum(d, "x", 0.0), fnum(d, "y", 0.0))).unwrap_or((seats.iter().map(|s| s.x).fold(f64::MIN, f64::max), 0.0));
    let mut d: Vec<(f64, usize)> = seats.iter().enumerate().map(|(i, s)| (((s.x - dx).powi(2) + (s.y - dy).powi(2)).sqrt(), i)).collect();
    d.sort_by(|a, b| a.partial_cmp(b).unwrap());
    let mut door_rank = vec![0.0; seats.len()];
    for (r, (_, i)) in d.iter().enumerate() {
        door_rank[*i] = (r + 1) as f64;
    }

    let mut paras: Vec<Para> = Vec::new();
    for p in j.get("paras").and_then(|v| v.arr()).ok_or("paras manquants")?.iter() {
        paras.push(Para {
            nom: p.get("nom").and_then(|v| v.str()).unwrap_or("?").to_string(),
            m: p.get("masse").and_then(|v| v.num()).ok_or("para sans masse")?,
            groupe: p.get("groupe").and_then(|v| v.str()).map(|s| s.to_string()),
            sortie: p.get("sortie").and_then(|v| v.num()),
            tandem: p.get("tandem").and_then(|v| v.str()).map(|s| s.to_string()),
            porteur: p.get("role").and_then(|v| v.str()).map(|r| r == "porteur").unwrap_or(false),
            seq: 0,
            target: None,
        });
    }
    let n = paras.len();
    if n > seats.len() {
        return Err(format!("{} paras pour {} places", n, seats.len()));
    }
    // ordre de sortie : classes, puis sans rang en dernier ; rang cible = rang moyen des ex aequo
    let mut order: Vec<usize> = (0..n).collect();
    order.sort_by(|&a, &b| {
        let ka = paras[a].sortie.unwrap_or(f64::INFINITY);
        let kb = paras[b].sortie.unwrap_or(f64::INFINITY);
        ka.partial_cmp(&kb).unwrap().then(a.cmp(&b))
    });
    for (k, &p) in order.iter().enumerate() {
        paras[p].seq = k;
    }
    let ranked: Vec<usize> = order.iter().cloned().filter(|&p| paras[p].sortie.is_some()).collect();
    let mut pos = 0;
    while pos < ranked.len() {
        let v = paras[ranked[pos]].sortie.unwrap();
        let mut e = pos;
        while e < ranked.len() && paras[ranked[e]].sortie.unwrap() == v {
            e += 1;
        }
        let mean = (pos + 1 + e) as f64 / 2.0;
        for i in pos..e {
            paras[ranked[i]].target = Some(mean);
        }
        pos = e;
    }
    let opts = j.get("options");
    let sequence = opts.and_then(|o| o.get("sequence")).and_then(|v| v.boolean()).unwrap_or(true);
    let objectif_arriere = opts
        .and_then(|o| o.get("objectif"))
        .and_then(|v| v.str())
        .map(|t| t == "marge_arriere")
        .unwrap_or(false);
    let etapes_label: String = opts
        .and_then(|o| o.get("etapes"))
        .and_then(|v| v.str())
        .map(|t| t.to_string())
        .unwrap_or_else(|| if objectif_arriere { "premier_groupe".to_string() } else { "toutes".to_string() });
    let mut stages: Vec<Vec<usize>> = vec![(0..n).collect()];
    if sequence && n > 1 {
        if etapes_label == "premier_groupe" {
            // une seule etape apres le decollage : la sortie du premier groupe
            // (tous les paras qui partagent la plus petite valeur de `sortie`)
            let first: Option<f64> = paras.iter().filter_map(|p| p.sortie).fold(None, |a: Option<f64>, v| Some(a.map_or(v, |x| x.min(v))));
            if let Some(f) = first {
                let rest: Vec<usize> = order.iter().cloned().filter(|&p| paras[p].sortie != Some(f)).collect();
                if !rest.is_empty() && rest.len() < n {
                    stages.push(rest);
                }
            }
        } else if etapes_label == "toutes" {
            for k in 1..n {
                stages.push(order[k..].to_vec());
            }
        }
    }
    let etapes_label = if !sequence { "decollage".to_string() } else { etapes_label };
    // groupes
    let mut groups: Vec<(String, Vec<usize>, Option<f64>)> = Vec::new();
    for (i, p) in paras.iter().enumerate() {
        if let Some(g) = &p.groupe {
            if let Some(e) = groups.iter_mut().find(|e| &e.0 == g) {
                e.1.push(i);
            } else {
                groups.push((g.clone(), vec![i], None));
            }
        }
    }
    groups.retain(|g| g.1.len() >= 2);
    for g in groups.iter_mut() {
        let s: Vec<f64> = g.1.iter().filter_map(|&p| paras[p].sortie).collect();
        g.2 = if s.len() == g.1.len() { s.iter().cloned().fold(None, |a: Option<f64>, v| Some(a.map_or(v, |x| x.min(v)))) } else { None };
    }
    // tandems
    let mut pairs = Vec::new();
    let tids: Vec<String> = {
        let mut v: Vec<String> = paras.iter().filter_map(|p| p.tandem.clone()).collect();
        v.sort();
        v.dedup();
        v
    };
    for t in tids {
        let por: Vec<usize> = (0..n).filter(|&i| paras[i].tandem.as_deref() == Some(&t) && paras[i].porteur).collect();
        let pas: Vec<usize> = (0..n).filter(|&i| paras[i].tandem.as_deref() == Some(&t) && !paras[i].porteur).collect();
        if por.len() != 1 || pas.len() != 1 {
            return Err(format!("tandem {} : il faut exactement un porteur et un passager", t));
        }
        pairs.push((por[0], pas[0]));
    }
    Ok(Model {
        seats,
        paras,
        base_m,
        base_mom,
        fwd,
        aft,
        mtow,
        stages,
        door_rank,
        groups,
        pairs,
        ordered: opts.and_then(|o| o.get("groupes_ordonnes")).and_then(|v| v.boolean()).unwrap_or(false),
        w_g: opts.map(|o| fnum(o, "poids_groupe", 2.0)).unwrap_or(2.0),
        w_s: opts.map(|o| fnum(o, "poids_sortie", 1.0)).unwrap_or(1.0),
        w_l: opts.map(|o| fnum(o, "poids_lateral", 0.5)).unwrap_or(0.5),
        pitch: opts.map(|o| fnum(o, "pas", 25.0)).unwrap_or(25.0),
        marge_cible: opts.map(|o| fnum(o, "marge_cible", 0.5)).unwrap_or(0.5),
        temps_max: opts.map(|o| fnum(o, "temps_max_s", 1.5)).unwrap_or(1.5),
        objectif_arriere,
        marge_avant_min: opts.map(|o| fnum(o, "marge_avant_min", 0.5)).unwrap_or(0.5),
        tolerance: opts.map(|o| fnum(o, "tolerance_marge", 0.25)).unwrap_or(0.25),
        etapes_label,
    })
}

impl Model {
    fn n(&self) -> usize {
        self.paras.len()
    }
    /// (masse, cg, marge avant, marge arriere) a l'etape k.
    fn stage_margins(&self, seat_of: &[usize], k: usize) -> (f64, f64, f64, f64) {
        let mut w = self.base_m;
        let mut mom = self.base_mom;
        for &p in &self.stages[k] {
            w += self.paras[p].m;
            mom += self.paras[p].m * self.seats[seat_of[p]].x;
        }
        let cg = mom / w;
        (w, cg, cg - interp(&self.fwd, w), interp(&self.aft, w) - cg)
    }
    /// Objectif "marge_arriere" : deficit des contraintes (marge avant >= marge_avant_min a
    /// toutes les etapes, enveloppe arriere respectee apres le decollage). 0 si tout est tenu.
    fn shortfall(&self, seat_of: &[usize]) -> f64 {
        let mut d = 0.0;
        for k in 0..self.stages.len() {
            let (_, _, fw, af) = self.stage_margins(seat_of, k);
            if fw < self.marge_avant_min {
                d += self.marge_avant_min - fw;
            }
            if k > 0 && af < 0.0 {
                d += -af;
            }
        }
        d
    }
    /// Score a maximiser (unite de bras) pour un placement complet :
    ///  - symetrique : minimum sur les etapes de min(marge avant, marge arriere) ;
    ///  - marge_arriere : marge arriere au decollage, fortement penalisee si les
    ///    contraintes avant (et arriere apres le decollage) ne sont pas tenues.
    fn margin(&self, seat_of: &[usize]) -> f64 {
        if self.objectif_arriere {
            let (_, _, _, af0) = self.stage_margins(seat_of, 0);
            return af0 - 1000.0 * self.shortfall(seat_of);
        }
        let mut worst = f64::INFINITY;
        for k in 0..self.stages.len() {
            let (_, _, fw, af) = self.stage_margins(seat_of, k);
            let mg = fw.min(af);
            if mg < worst {
                worst = mg;
            }
        }
        worst
    }
    fn stage_info(&self, seat_of: &[usize], k: usize) -> (f64, f64, f64) {
        let rest = &self.stages[k];
        let mut w = self.base_m;
        let mut mom = self.base_mom;
        for &p in rest {
            w += self.paras[p].m;
            mom += self.paras[p].m * self.seats[seat_of[p]].x;
        }
        let cg = mom / w;
        (w, cg, (cg - interp(&self.fwd, w)).min(interp(&self.aft, w) - cg))
    }
    /// Violation de l'ordre des groupes (somme des chevauchements, en bras).
    fn order_violation(&self, seat_of: &[usize]) -> f64 {
        if !self.ordered {
            return 0.0;
        }
        let mut v = 0.0;
        for (i, g) in self.groups.iter().enumerate() {
            for (j, h) in self.groups.iter().enumerate() {
                if i == j {
                    continue;
                }
                if let (Some(rg), Some(rh)) = (g.2, h.2) {
                    if rg < rh {
                        let mn_g = g.1.iter().map(|&p| self.seats[seat_of[p]].x).fold(f64::INFINITY, f64::min);
                        let mx_h = h.1.iter().map(|&p| self.seats[seat_of[p]].x).fold(f64::MIN, f64::max);
                        if mx_h > mn_g {
                            v += mx_h - mn_g;
                        }
                    }
                }
            }
        }
        v
    }
    fn realism(&self, seat_of: &[usize]) -> (f64, f64, f64) {
        let mut boxes = 0.0;
        for g in &self.groups {
            let xs: Vec<f64> = g.1.iter().map(|&p| self.seats[seat_of[p]].x).collect();
            let ys: Vec<f64> = g.1.iter().map(|&p| self.seats[seat_of[p]].y).collect();
            let sx = xs.iter().cloned().fold(f64::MIN, f64::max) - xs.iter().cloned().fold(f64::INFINITY, f64::min);
            let sy = ys.iter().cloned().fold(f64::MIN, f64::max) - ys.iter().cloned().fold(f64::INFINITY, f64::min);
            boxes += (sx + self.w_l * sy) / self.pitch;
        }
        let mut exit = 0.0;
        for (p, pa) in self.paras.iter().enumerate() {
            if let Some(t) = pa.target {
                exit += (self.door_rank[seat_of[p]] - t).abs();
            }
        }
        (self.w_g * boxes + self.w_s * exit, boxes, exit)
    }
    fn tandem_ok(&self, seat_of: &[usize]) -> bool {
        self.pairs.iter().all(|&(po, pa)| {
            let s = seat_of[po];
            !self.seats[s].copilot && self.seats[s].devant == Some(seat_of[pa])
        })
    }
}

// ---------------------------------------------------------------- phase 1 : exact
struct Dfs<'a> {
    m: &'a Model,
    group_of: Vec<Option<usize>>,   // indice de groupe par para
    gmin: Vec<f64>,                 // min / max des bras places par groupe
    gmax: Vec<f64>,
    gcount: Vec<usize>,
    mu: f64,
    lo: Vec<f64>, // bornes de moment paras par etape (avec marge)
    hi: Vec<f64>,
    partial: Vec<f64>,
    seat_of: Vec<usize>,
    used: Vec<bool>,
    units: Vec<Vec<usize>>, // unites a placer : [porteur, passager] ou [para]
    nodes: u64,
    limit: u64,
    found: bool,
}

impl<'a> Dfs<'a> {
    fn new(m: &'a Model, mu: f64, limit: u64) -> Self {
        let mut lo = Vec::new();
        let mut hi = Vec::new();
        for (k, rest) in m.stages.iter().enumerate() {
            let w: f64 = m.base_m + rest.iter().map(|&p| m.paras[p].m).sum::<f64>();
            if m.objectif_arriere {
                // marge avant >= marge_avant_min partout ; marge arriere >= mu au decollage seulement
                lo.push((interp(&m.fwd, w) + m.marge_avant_min) * w - m.base_mom);
                hi.push((interp(&m.aft, w) - if k == 0 { mu } else { 0.0 }) * w - m.base_mom);
            } else {
                lo.push((interp(&m.fwd, w) + mu) * w - m.base_mom);
                hi.push((interp(&m.aft, w) - mu) * w - m.base_mom);
            }
        }
        let mut units: Vec<Vec<usize>> = Vec::new();
        let mut in_pair = vec![false; m.n()];
        for &(po, pa) in &m.pairs {
            units.push(vec![po, pa]);
            in_pair[po] = true;
            in_pair[pa] = true;
        }
        let mut singles: Vec<usize> = (0..m.n()).filter(|&p| !in_pair[p]).collect();
        singles.sort_by(|&a, &b| m.paras[b].m.partial_cmp(&m.paras[a].m).unwrap());
        for p in singles {
            units.push(vec![p]);
        }
        let mut group_of = vec![None; m.n()];
        for (gi, g) in m.groups.iter().enumerate() {
            for &p in &g.1 {
                group_of[p] = Some(gi);
            }
        }
        let ng = m.groups.len();
        Dfs { m, group_of, gmin: vec![f64::INFINITY; ng], gmax: vec![f64::NEG_INFINITY; ng], gcount: vec![0; ng], mu, lo, hi, partial: vec![0.0; m.stages.len()], seat_of: vec![usize::MAX; m.n()], used: vec![false; m.seats.len()], units, nodes: 0, limit, found: false }
    }
    /// Bornes : pour chaque etape, moment mini/maxi atteignable par les paras non places.
    fn bounds_ok(&self, from_unit: usize) -> bool {
        let m = self.m;
        let mut free: Vec<f64> = (0..m.seats.len()).filter(|&s| !self.used[s]).map(|s| m.seats[s].x).collect();
        free.sort_by(|a, b| a.partial_cmp(b).unwrap());
        let mut unplaced = vec![false; m.n()];
        for u in &self.units[from_unit..] {
            for &p in u {
                unplaced[p] = true;
            }
        }
        for (k, rest) in m.stages.iter().enumerate() {
            let mut ms: Vec<f64> = rest.iter().filter(|&&p| unplaced[p]).map(|&p| m.paras[p].m).collect();
            if ms.is_empty() {
                if self.partial[k] < self.lo[k] - 1e-9 || self.partial[k] > self.hi[k] + 1e-9 {
                    return false;
                }
                continue;
            }
            ms.sort_by(|a, b| b.partial_cmp(a).unwrap());
            let mut lb = 0.0;
            let mut ub = 0.0;
            for (i, &w) in ms.iter().enumerate() {
                lb += w * free[i];
                ub += w * free[free.len() - 1 - i];
            }
            if self.partial[k] + ub < self.lo[k] - 1e-9 || self.partial[k] + lb > self.hi[k] + 1e-9 {
                return false;
            }
        }
        true
    }
    /// L'ordre des groupes est-il encore respectable si p prend la place s ?
    fn order_ok(&self, p: usize, s: usize) -> bool {
        let m = self.m;
        if !m.ordered {
            return true;
        }
        let g = match self.group_of[p] {
            Some(g) => g,
            None => return true,
        };
        let rg = match m.groups[g].2 {
            Some(r) => r,
            None => return true,
        };
        let x = m.seats[s].x;
        for (h, gh) in m.groups.iter().enumerate() {
            if h == g || self.gcount[h] == 0 {
                continue;
            }
            if let Some(rh) = gh.2 {
                if rg < rh && x < self.gmax[h] - 1e-9 {
                    return false; // g sort avant h : g doit etre en arriere de tout h
                }
                if rh < rg && x > self.gmin[h] + 1e-9 {
                    return false;
                }
            }
        }
        true
    }
    fn place(&mut self, p: usize, s: usize, sign: f64) {
        let m = self.m;
        let c = m.paras[p].m * m.seats[s].x;
        for (k, rest) in m.stages.iter().enumerate() {
            if rest.contains(&p) {
                self.partial[k] += sign * c;
            }
        }
        if sign > 0.0 {
            self.seat_of[p] = s;
            self.used[s] = true;
            if let Some(g) = self.group_of[p] {
                self.gcount[g] += 1;
                if self.gcount[g] == 1 {
                    self.gmin[g] = m.seats[s].x;
                    self.gmax[g] = m.seats[s].x;
                } else {
                    self.gmin[g] = self.gmin[g].min(m.seats[s].x);
                    self.gmax[g] = self.gmax[g].max(m.seats[s].x);
                }
            }
        } else {
            self.seat_of[p] = usize::MAX;
            self.used[s] = false;
            if let Some(g) = self.group_of[p] {
                self.gcount[g] -= 1;
                // recalcul du min/max a partir des membres encore places
                self.gmin[g] = f64::INFINITY;
                self.gmax[g] = f64::NEG_INFINITY;
                for &q in &m.groups[g].1 {
                    if self.seat_of[q] != usize::MAX {
                        self.gmin[g] = self.gmin[g].min(m.seats[self.seat_of[q]].x);
                        self.gmax[g] = self.gmax[g].max(m.seats[self.seat_of[q]].x);
                    }
                }
            }
        }
    }
    fn go(&mut self, u: usize) -> bool {
        self.nodes += 1;
        if self.nodes > self.limit {
            return false;
        }
        if !self.bounds_ok(u) {
            return false;
        }
        if u == self.units.len() {
            self.found = true;
            return true;
        }
        let unit = self.units[u].clone();
        let m = self.m;
        // candidats tries : places dont le bras rapproche le CG de decollage du centre de bande
        let mut cands: Vec<usize> = (0..m.seats.len()).filter(|&s| !self.used[s]).collect();
        if unit.len() == 2 {
            cands.retain(|&s| !m.seats[s].copilot && m.seats[s].devant.map_or(false, |d| !self.used[d]));
        } else {
            // seules comptent la masse et le bras : une place par valeur de bras distincte
            // (on garde, a bras egal, la place la plus a l'exterieur : sans effet sur le CG)
            let mut seen: Vec<f64> = Vec::new();
            cands.retain(|&s| {
                let x = m.seats[s].x;
                if seen.iter().any(|&v| (v - x).abs() < 1e-6) {
                    false
                } else {
                    seen.push(x);
                    true
                }
            });
        }
        cands.retain(|&s| self.order_ok(unit[0], s) && (unit.len() == 1 || self.order_ok(unit[1], m.seats[s].devant.unwrap())));
        let center0 = (self.lo[0] + self.hi[0]) / 2.0;
        let mut ordered: Vec<(f64, usize)> = cands
            .iter()
            .map(|&s| {
                let extra = m.paras[unit[0]].m * m.seats[s].x
                    + if unit.len() == 2 { m.paras[unit[1]].m * m.seats[m.seats[s].devant.unwrap()].x } else { 0.0 };
                ((self.partial[0] + extra - center0).abs(), s)
            })
            .collect();
        ordered.sort_by(|a, b| a.partial_cmp(b).unwrap());
        for (_, s) in ordered {
            self.place(unit[0], s, 1.0);
            if unit.len() == 2 {
                self.place(unit[1], m.seats[s].devant.unwrap(), 1.0);
            }
            if self.go(u + 1) {
                return true;
            }
            if unit.len() == 2 {
                self.place(unit[1], m.seats[s].devant.unwrap(), -1.0);
            }
            self.place(unit[0], s, -1.0);
            if self.nodes > self.limit {
                return false;
            }
        }
        false
    }
}

/// Existe-t-il un placement a marge >= mu ? (Some(placement) / None / Err si limite de noeuds)
fn feasible(m: &Model, mu: f64, limit: u64) -> Result<Option<Vec<usize>>, ()> {
    let mut d = Dfs::new(m, mu, limit);
    let ok = d.go(0);
    if ok {
        Ok(Some(d.seat_of))
    } else if d.nodes > limit {
        Err(())
    } else {
        Ok(None)
    }
}

// ---------------------------------------------------------------- phase 2 : recuit
struct Rng(u64);
impl Rng {
    fn next(&mut self) -> u64 {
        self.0 ^= self.0 << 13;
        self.0 ^= self.0 >> 7;
        self.0 ^= self.0 << 17;
        self.0
    }
    fn f(&mut self) -> f64 {
        (self.next() >> 11) as f64 / (1u64 << 53) as f64
    }
    fn below(&mut self, n: usize) -> usize {
        (self.next() % n as u64) as usize
    }
}

fn penalty(m: &Model, seat_of: &[usize], mu_min: f64) -> f64 {
    let mut pen = 0.0;
    if m.objectif_arriere {
        let (_, _, _, af0) = m.stage_margins(seat_of, 0);
        if af0 < mu_min {
            pen += mu_min - af0;
        }
        pen += m.shortfall(seat_of);
    } else {
        for k in 0..m.stages.len() {
            let (_, _, mg) = m.stage_info(seat_of, k);
            if mg < mu_min {
                pen += mu_min - mg;
            }
        }
    }
    pen * 200.0 + m.order_violation(seat_of) / m.pitch * 50.0
}

fn cost(m: &Model, seat_of: &[usize], mu_min: f64) -> f64 {
    m.realism(seat_of).0 + penalty(m, seat_of, mu_min)
}

/// Placement initial valide structurellement (tandems respectes), sans souci de CG.
fn initial(m: &Model) -> Vec<usize> {
    let n = m.n();
    let mut seat_of = vec![usize::MAX; n];
    let mut used = vec![false; m.seats.len()];
    for &(po, pa) in &m.pairs {
        for s in 0..m.seats.len() {
            if used[s] || m.seats[s].copilot {
                continue;
            }
            if let Some(d) = m.seats[s].devant {
                if !used[d] {
                    seat_of[po] = s;
                    seat_of[pa] = d;
                    used[s] = true;
                    used[d] = true;
                    break;
                }
            }
        }
    }
    for p in 0..n {
        if seat_of[p] == usize::MAX {
            let s = (0..m.seats.len()).find(|&s| !used[s]).expect("plus de place");
            seat_of[p] = s;
            used[s] = true;
        }
    }
    seat_of
}

/// Recuit maximisant la marge minimale sur les etapes (phase 0, borne inferieure de mu*).
fn anneal_margin(m: &Model, start: &[usize], seed: u64, iters: usize) -> (Vec<usize>, f64) {
    let mut rng = Rng(seed.wrapping_mul(0x9E3779B97F4A7C15) | 1);
    let n = m.n();
    let ns = m.seats.len();
    let in_pair: Vec<Option<usize>> = (0..n).map(|p| m.pairs.iter().position(|&(a, b)| a == p || b == p)).collect();
    let mut cur = start.to_vec();
    let mut c_cur = -m.margin(&cur) + 10.0 * m.order_violation(&cur) / m.pitch;
    let mut best = cur.clone();
    let mut c_best = c_cur;
    let mut occ = vec![usize::MAX; ns];
    for (p, &s) in cur.iter().enumerate() {
        occ[s] = p;
    }
    let (t0, t1) = (1.0f64, 0.01f64);
    for it in 0..iters {
        let t = t0 * (t1 / t0).powf(it as f64 / iters as f64);
        let p = rng.below(n);
        if in_pair[p].is_some() {
            continue;
        }
        let s_new = rng.below(ns);
        if s_new == cur[p] {
            continue;
        }
        let o = occ[s_new];
        if o != usize::MAX && in_pair[o].is_some() {
            continue;
        }
        let mut cand = cur.clone();
        if o != usize::MAX {
            cand[o] = cur[p];
        }
        cand[p] = s_new;
        let c = -m.margin(&cand) + 10.0 * m.order_violation(&cand) / m.pitch;
        if c <= c_cur || rng.f() < ((c_cur - c) / t).exp() {
            if o != usize::MAX {
                occ[cur[p]] = o;
            } else {
                occ[cur[p]] = usize::MAX;
            }
            occ[s_new] = p;
            cur = cand;
            c_cur = c;
            if c < c_best {
                best = cur.clone();
                c_best = c;
            }
        }
    }
    (best, -c_best)
}

fn anneal(m: &Model, start: &[usize], mu_min: f64, seed: u64, iters: usize) -> (Vec<usize>, f64) {
    let mut rng = Rng(seed.wrapping_mul(0x9E3779B97F4A7C15) | 1);
    let n = m.n();
    let ns = m.seats.len();
    let mut cur = start.to_vec();
    let mut c_cur = cost(m, &cur, mu_min);
    let mut best = cur.clone();
    let mut c_best = if penalty(m, &cur, mu_min) < 1e-9 { c_cur } else { f64::INFINITY };
    let in_pair: Vec<Option<usize>> = (0..n).map(|p| m.pairs.iter().position(|&(a, b)| a == p || b == p)).collect();
    let t0 = 3.0f64;
    let t1 = 0.02f64;
    let mut occ = vec![usize::MAX; ns];
    for (p, &s) in cur.iter().enumerate() {
        occ[s] = p;
    }
    for it in 0..iters {
        let t = t0 * (t1 / t0).powf(it as f64 / iters as f64);
        let p = rng.below(n);
        let mut cand = cur.clone();
        if let Some(pi) = in_pair[p] {
            // deplacer le tandem entier vers une autre place porteur valide
            let (po, pa) = m.pairs[pi];
            let s_new = rng.below(ns);
            let d_new = match m.seats[s_new].devant {
                Some(d) if !m.seats[s_new].copilot => d,
                _ => continue,
            };
            // qui occupe s_new et d_new ? on echange avec les places actuelles du tandem
            let (s_old, d_old) = (cur[po], cur[pa]);
            if s_new == s_old {
                continue;
            }
            let o1 = occ[s_new];
            let o2 = occ[d_new];
            if (o1 != usize::MAX && in_pair[o1].is_some() && o1 != po && o1 != pa) || (o2 != usize::MAX && in_pair[o2].is_some() && o2 != po && o2 != pa) {
                continue; // ne pas casser un autre tandem
            }
            cand[po] = s_new;
            cand[pa] = d_new;
            if o1 != usize::MAX && o1 != po && o1 != pa {
                cand[o1] = s_old;
            }
            if o2 != usize::MAX && o2 != po && o2 != pa {
                cand[o2] = if o1 != usize::MAX && o1 != po && o1 != pa { d_old } else { s_old };
                if o1 == usize::MAX || o1 == po || o1 == pa {
                    // s_old libre, d_old aussi : o2 prend s_old, ok
                } 
            }
            // cas d_new == s_old ou s_new == d_old : les echanges ci-dessus restent coherents
        } else {
            let s_new = rng.below(ns);
            if s_new == cur[p] {
                continue;
            }
            let o = occ[s_new];
            if o != usize::MAX {
                if in_pair[o].is_some() {
                    continue;
                }
                cand[o] = cur[p];
            }
            cand[p] = s_new;
        }
        // coherence : places distinctes
        let mut seen = vec![false; ns];
        let mut okc = true;
        for &s in &cand {
            if seen[s] {
                okc = false;
                break;
            }
            seen[s] = true;
        }
        if !okc || !m.tandem_ok(&cand) {
            continue;
        }
        let c = cost(m, &cand, mu_min);
        if c <= c_cur || rng.f() < ((c_cur - c) / t).exp() {
            cur = cand;
            c_cur = c;
            for s in occ.iter_mut() {
                *s = usize::MAX;
            }
            for (q, &s) in cur.iter().enumerate() {
                occ[s] = q;
            }
            if c < c_best && penalty(m, &cur, mu_min) < 1e-9 {
                best = cur.clone();
                c_best = c;
            }
        }
    }
    (best, c_best)
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let text = if args.len() < 2 || args[1] == "-" {
        let mut s = String::new();
        std::io::Read::read_to_string(&mut std::io::stdin(), &mut s).unwrap();
        s
    } else {
        std::fs::read_to_string(&args[1]).unwrap_or_else(|e| {
            eprintln!("lecture {} : {}", args[1], e);
            std::process::exit(2)
        })
    };
    let t0 = Instant::now();
    let out = match run(&text, t0) {
        Ok(j) => j,
        Err(e) => obj(vec![("ok", Json::Bool(false)), ("message", Json::Str(e))]),
    };
    let s = out.dump();
    if args.len() >= 3 {
        std::fs::write(&args[2], &s).unwrap();
    } else {
        println!("{}", s);
    }
}

fn run(text: &str, t0: Instant) -> Result<Json, String> {
    let j = json::parse(text)?;
    let m = load(&j)?;
    let n = m.n();
    let total: f64 = m.base_m + m.paras.iter().map(|p| p.m).sum::<f64>();
    if total > m.mtow + 1e-9 {
        return Ok(obj(vec![
            ("ok", Json::Bool(false)),
            ("message", Json::Str(format!("masse au decollage {:.0} > MTOW {:.0}", total, m.mtow))),
            ("masse_decollage", Json::Num(total)),
        ]));
    }
    // phase 0 : recuit sur la marge minimale (borne inferieure de mu*, placement de depart)
    let start = initial(&m);
    let mut best_sol = start.clone();
    let mut best_mu = m.margin(&best_sol);
    if m.ordered && m.order_violation(&best_sol) > 0.0 {
        best_mu = f64::NEG_INFINITY;
    }
    for seed in 1..=4u64 {
        let (s, mu) = anneal_margin(&m, &start, seed, 20_000 + 3_000 * n);
        if mu > best_mu && (!m.ordered || m.order_violation(&s) < 1e-9) {
            best_mu = mu;
            best_sol = s;
        }
    }
    // phase 1 : la recherche exacte tente de faire mieux, avec un budget de noeuds ;
    // si elle prouve qu'on ne peut pas depasser mu + 0.05, la marge max est prouvee.
    let step = 0.05f64;
    let mut proven = false;
    let debug = std::env::var("PLACEMENT_DEBUG").is_ok();
    let mut budget: u64 = 1_200_000;
    let mut hi = if best_mu.is_finite() { best_mu + step } else { m.marge_cible };
    loop {
        let limit = budget.min(300_000);
        let mut d = Dfs::new(&m, hi, limit);
        let ok = d.go(0);
        if debug {
            eprintln!("DFS mu={:.3} noeuds={} trouve={}", hi, d.nodes, ok);
        }
        if ok {
            let mu = m.margin(&d.seat_of);
            if mu > best_mu {
                best_mu = mu;
                best_sol = d.seat_of.clone();
            }
            hi = best_mu + step;
            budget = budget.saturating_sub(d.nodes.min(limit));
        } else if d.nodes > limit {
            break; // budget epuise sans preuve : la marge max n'est pas prouvee
        } else {
            proven = true;
            break;
        }
        if budget == 0 {
            break;
        }
    }
    let t1 = t0.elapsed().as_secs_f64();
    if m.objectif_arriere && best_mu.is_finite() && m.shortfall(&best_sol) > 1e-6 {
        let mut fw_min = f64::INFINITY;
        for k in 0..m.stages.len() {
            fw_min = fw_min.min(m.stage_margins(&best_sol, k).2);
        }
        return Ok(obj(vec![
            ("ok", Json::Bool(false)),
            ("message", Json::Str(format!(
                "aucun placement avec marge avant >= {:.2} aux etapes considerees ({}) ; au mieux {:.2}",
                m.marge_avant_min, m.etapes_label, fw_min))),
            ("marge_avant_min", Json::Num(m.marge_avant_min)),
            ("marge_avant_max_possible", Json::Num(fw_min)),
            ("marge_max_prouvee", Json::Bool(proven)),
            ("objectif", Json::Str("marge_arriere".to_string())),
            ("etapes", Json::Str(m.etapes_label.clone())),
            ("temps_s", Json::Num(t1)),
        ]));
    }
    if !best_mu.is_finite() || best_mu < -5.0 {
        return Ok(obj(vec![
            ("ok", Json::Bool(false)),
            ("message", Json::Str(format!("aucun placement dans l enveloppe{}", if m.stages.len() > 1 { " (largage compris)" } else { "" }))),
            ("marge_max_prouvee", Json::Bool(proven)),
            ("temps_s", Json::Num(t1)),
        ]));
    }
    let sol1 = best_sol.clone();
    if best_mu < 0.0 {
        let (cr, boxes, exit) = m.realism(&sol1);
        let _ = (cr, boxes, exit);
        return Ok(obj(vec![
            ("ok", Json::Bool(false)),
            ("message", Json::Str(format!("aucun placement dans l enveloppe : au mieux {:.2} dehors{}", -best_mu, if m.stages.len() > 1 { " (largage compris)" } else { "" }))),
            ("marge_max", Json::Num(best_mu)),
            ("marge_max_prouvee", Json::Bool(proven)),
            ("temps_s", Json::Num(t1)),
        ]));
    }
    let mu_exact = m.margin(&sol1);
    let mu_min = if m.objectif_arriere { mu_exact - m.tolerance - 1e-6 } else { mu_exact.min(m.marge_cible) - 1e-6 };
    let mut best = sol1.clone();
    let mut c_best = cost(&m, &best, mu_min);
    let budget = m.temps_max;
    let iters = 40_000 + 6_000 * n;
    let mut seed = 1u64;
    let mut restarts = 0;
    while t0.elapsed().as_secs_f64() < t1 + budget {
        let (s, c) = anneal(&m, &best, mu_min, seed, iters);
        if c < c_best - 1e-9 {
            best = s;
            c_best = c;
        }
        seed += 1;
        restarts += 1;
        if restarts >= 200 {
            break;
        }
    }
    // sortie
    let (cr, boxes, exit) = m.realism(&best);
    let mut placement = Vec::new();
    for (p, pa) in m.paras.iter().enumerate() {
        let s = &m.seats[best[p]];
        placement.push(obj(vec![
            ("nom", Json::Str(pa.nom.clone())),
            ("place", Json::Str(s.id.clone())),
            ("x", Json::Num(s.x)),
            ("y", Json::Num(s.y)),
            ("rang_porte", Json::Num(m.door_rank[best[p]])),
        ]));
    }
    let mut etapes = Vec::new();
    let mut fw_min = f64::INFINITY;
    for k in 0..m.stages.len() {
        let (w, cg, fw, af) = m.stage_margins(&best, k);
        fw_min = fw_min.min(fw);
        etapes.push(obj(vec![
            ("sorties", Json::Num(if k == 0 { 0.0 } else { (n - m.stages[k].len()) as f64 })),
            ("restants", Json::Num(m.stages[k].len() as f64)),
            ("masse", Json::Num(w)),
            ("cg", Json::Num(cg)),
            ("marge", Json::Num(fw.min(af))),
            ("marge_avant", Json::Num(fw)),
            ("marge_arriere", Json::Num(af)),
        ]));
    }
    let (_, _, _, af0) = m.stage_margins(&best, 0);
    Ok(obj(vec![
        ("ok", Json::Bool(true)),
        ("objectif", Json::Str(if m.objectif_arriere { "marge_arriere".to_string() } else { "symetrique".to_string() })),
        ("etapes_mode", Json::Str(m.etapes_label.clone())),
        ("marge_max", Json::Num(best_mu.max(mu_exact))),
        ("marge_max_prouvee", Json::Bool(proven)),
        ("marge", Json::Num(m.margin(&best))),
        ("marge_arriere", Json::Num(af0)),
        ("marge_avant_min_obtenue", Json::Num(fw_min)),
        ("marge_avant_min", Json::Num(m.marge_avant_min)),
        ("cout_realisme", Json::Num(cr)),
        ("boites", Json::Num(boxes)),
        ("ecart_sortie", Json::Num(exit)),
        ("violation_ordre", Json::Num(m.order_violation(&best))),
        ("placement", Json::Arr(placement)),
        ("etapes", Json::Arr(etapes)),
        ("temps_phase1_s", Json::Num(t1)),
        ("temps_s", Json::Num(t0.elapsed().as_secs_f64())),
        ("redemarrages_recuit", Json::Num(restarts as f64)),
    ]))
}
