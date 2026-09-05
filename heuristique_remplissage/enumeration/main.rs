// Enumeration exhaustive des configurations de remplissage (places fixes, masses uniformes).
//
// Entree (texte, prepare.py) : pour chaque cas, les 20 bras et, pour N = 1..20, la bande
// admissible [lo, hi] de la SOMME des bras des N places occupees (intersection sur tous
// les scenarios du domaine ; -inf/+inf si aucune contrainte).
//
// Pour chaque cas :
//   - parcours des 2^20 sous-ensembles S : valide(S) <=> somme(S) dans [lo_N, hi_N] ;
//   - programmation dynamique sur les chaines emboitees S_1 c S_2 c ... (un ordre de
//     remplissage) : nombre exact d'ordres valides, sous-ensembles atteignables, et
//     chaine maximisant la marge minimale (marge = distance a la bande, en in de bras moyen).
//
// Compilation : rustc -O main.rs -o enumere ; usage : ./enumere input.txt output.json
use std::fs;
use std::io::Write;

struct Case {
    name: String,
    slots: Vec<f64>,
    lo: Vec<f64>,
    hi: Vec<f64>,
}

fn parse(path: &str) -> Vec<Case> {
    let txt = fs::read_to_string(path).expect("lecture input");
    let mut cases = Vec::new();
    let mut cur: Option<Case> = None;
    for line in txt.lines() {
        let t: Vec<&str> = line.split_whitespace().collect();
        if t.is_empty() {
            continue;
        }
        match t[0] {
            "CASE" => {
                if let Some(c) = cur.take() {
                    cases.push(c);
                }
                cur = Some(Case { name: t[1..].join(" "), slots: vec![], lo: vec![0.0; 21], hi: vec![0.0; 21] });
            }
            "SLOTS" => {
                cur.as_mut().unwrap().slots = t[1..].iter().map(|s| s.parse().unwrap()).collect();
            }
            "N" => {
                let n: usize = t[1].parse().unwrap();
                let c = cur.as_mut().unwrap();
                c.lo[n] = t[2].parse().unwrap();
                c.hi[n] = t[3].parse().unwrap();
            }
            _ => {}
        }
    }
    if let Some(c) = cur.take() {
        cases.push(c);
    }
    cases
}

fn run(c: &Case) -> String {
    let k = c.slots.len();
    let total: usize = 1 << k;
    let eps = 1e-6;
    // somme des bras par sous-ensemble
    let mut sums = vec![0.0f64; total];
    for s in 1..total {
        let low = s.trailing_zeros() as usize;
        sums[s] = sums[s & (s - 1)] + c.slots[low];
    }
    let mut valid = vec![false; total];
    let mut orders = vec![0u128; total]; // nombre de chaines valides menant a S
    let mut best = vec![f64::NEG_INFINITY; total]; // marge minimale max sur une chaine menant a S
    let mut arg = vec![255u8; total];
    orders[0] = 1;
    best[0] = f64::INFINITY;
    let mut valid_per_n = vec![0u64; k + 1];
    let mut reach_per_n = vec![0u64; k + 1];
    let mut orders_per_n = vec![0u128; k + 1];
    let mut best_per_n = vec![f64::NEG_INFINITY; k + 1];
    let mut best_set_per_n = vec![0usize; k + 1];
    for s in 1..total {
        let n = s.count_ones() as usize;
        let sum = sums[s];
        let ok = sum >= c.lo[n] - eps && sum <= c.hi[n] + eps;
        if !ok {
            continue;
        }
        valid[s] = true;
        valid_per_n[n] += 1;
        let marg = (sum - c.lo[n]).min(c.hi[n] - sum) / n as f64;
        let mut cnt: u128 = 0;
        let mut bm = f64::NEG_INFINITY;
        let mut bi = 255u8;
        let mut bits = s;
        while bits != 0 {
            let i = bits.trailing_zeros() as usize;
            bits &= bits - 1;
            let p = s ^ (1 << i);
            cnt += orders[p];
            if best[p] > bm {
                bm = best[p];
                bi = i as u8;
            }
        }
        orders[s] = cnt;
        if cnt > 0 {
            reach_per_n[n] += 1;
            orders_per_n[n] += cnt;
            let b = marg.min(bm);
            best[s] = b;
            arg[s] = bi;
            if b > best_per_n[n] {
                best_per_n[n] = b;
                best_set_per_n[n] = s;
            }
        }
    }
    // reconstruction de la meilleure chaine jusqu'au N max atteignable
    let mut nmax = 0;
    for n in 1..=k {
        if reach_per_n[n] > 0 {
            nmax = n;
        }
    }
    let mut order: Vec<usize> = Vec::new();
    let mut margins: Vec<f64> = Vec::new();
    if nmax > 0 {
        let mut s = best_set_per_n[nmax];
        while s != 0 {
            let i = arg[s] as usize;
            order.push(i);
            let n = s.count_ones() as usize;
            let sum = sums[s];
            margins.push((sum - c.lo[n]).min(c.hi[n] - sum) / n as f64);
            s ^= 1 << i;
        }
        order.reverse();
        margins.reverse();
    }
    let fmt_list = |v: &Vec<u64>| v[1..].iter().map(|x| x.to_string()).collect::<Vec<_>>().join(",");
    let fmt_u128 = |v: &Vec<u128>| v[1..].iter().map(|x| format!("\"{}\"", x)).collect::<Vec<_>>().join(",");
    let fmt_f = |v: &Vec<f64>| v.iter().map(|x| if x.is_finite() { format!("{:.3}", x) } else { "null".to_string() }).collect::<Vec<_>>().join(",");
    format!(
        "{{\"name\":\"{}\",\"valid_per_n\":[{}],\"reach_per_n\":[{}],\"orders_per_n\":[{}],\"best_margin_per_n\":[{}],\"n_max\":{},\"best_order\":[{}],\"best_margins\":[{}]}}",
        c.name,
        fmt_list(&valid_per_n),
        fmt_list(&reach_per_n),
        fmt_u128(&orders_per_n),
        fmt_f(&best_per_n[1..].to_vec()),
        nmax,
        order.iter().map(|x| x.to_string()).collect::<Vec<_>>().join(","),
        fmt_f(&margins)
    )
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let cases = parse(&args[1]);
    let mut out = fs::File::create(&args[2]).unwrap();
    write!(out, "[").unwrap();
    for (i, c) in cases.iter().enumerate() {
        let t0 = std::time::Instant::now();
        let js = run(c);
        eprintln!("{} : {:.2} s", c.name, t0.elapsed().as_secs_f64());
        if i > 0 {
            write!(out, ",\n").unwrap();
        }
        write!(out, "{}", js).unwrap();
    }
    write!(out, "]\n").unwrap();
}
