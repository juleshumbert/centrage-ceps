// placement : placement des paras sur places fixes par programme lineaire en nombres
// entiers (HiGHS embarque). Modele : MODELE.md ; mode d'emploi : placement --help.
//
// Objectif : CG le plus avant possible au decollage (marge arriere maximale), sous marge
// avant garantie a la sortie du premier groupe (et au decollage), puis, a marge arriere
// quasi egale, placement realiste (groupes compacts, premiers sortants pres de la porte,
// tandems porteur / passager cote a cote sur un bord).
#include <algorithm>
#include <array>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <ctime>
#include <fstream>
#include <iostream>
#include <map>
#include <set>
#include <sstream>
#include <string>
#include <vector>

#include "Highs.h"
#include "json.hpp"

using json = nlohmann::json;

static const char* VERSION = "1.0";

static const char* HELP = R"(placement : ou s'assoit chaque para pour un centrage valide et realiste

Usage :
  placement ENTREE.json [options]
  placement - [options]              (entree lue sur l'entree standard)
  placement --help | --version

Options :
  --sortie FICHIER.json      resultat JSON (defaut : sortie standard)
  --pdf FICHIER.pdf          planche PDF : plan cabine, CG et limites, tableaux
  --etapes MODE              premier_groupe (defaut) : marge avant garantie apres la
                             sortie du premier groupe ; toutes : apres chaque sortie ;
                             decollage : decollage seulement
  --marge-avant M            marge avant minimale, unite des bras (defaut 0.5)
  --tolerance T              tolerance sur la marge arriere en phase 2 (defaut 0.25)
  --groupes-ordonnes         un groupe qui sort avant est entierement en arriere
  --temps S                  temps limite par phase, secondes (defaut 10)
  --gap G                    ecart relatif accepte a l'optimum en phase 2 (defaut 0.05)
  --recuit S                 duree du recuit simule qui amorce la phase 2 (defaut 1 s, 0 = sans)
  --rapide                   phase 2 par recuit seul, sans solveur (reponse en 1 a 2 s)
  --silencieux               pas de resume sur la sortie d'erreur
Les options de la ligne de commande priment sur le bloc "options" du JSON.

Entree (masses et bras dans des unites coherentes, moment = masse x bras) :
  avion      masse_vide, bras_vide (ou moment_vide)
  enveloppe  avant / arriere : lignes brisees [[masse, cg], ...], mtow
  carburant  masse, bras          pilote  masse, bras          porte  x, y
  places     [{id, x, y, copilote, centre, devant, interdit_tandem}, ...]
  paras      [{nom, masse, groupe, sortie, tandem, role, devant_de, interdit}, ...]
  options    marge_avant_min, tolerance_marge, etapes, groupes_ordonnes,
             poids_groupe, poids_sortie, poids_lateral, pas, temps_max_s, gap
Voir README.md pour le detail et exemple_stick.json pour un exemple complet.

Sortie JSON : ok, marge_arriere_max, marge_arriere, marge_avant_min_obtenue,
  placement [{nom, place, x, y}], etapes [{masse, cg, marge_avant, marge_arriere}],
  cout_realisme, phases, temps. Code de retour 0 si un placement est rendu, 1 sinon.
Phase 1 : marge arriere maximale (exacte). Phase 2 : realisme sous marge arriere
>= max - tolerance, amorcee par un recuit simule puis confiee a HiGHS ; a la limite
de temps, la meilleure solution trouvee est rendue.
)";

struct Seat {
    std::string id;
    double x = 0, y = 0;
    bool copilot = false, centre = false, no_tandem = false;
    int devant = -1;
};

struct Para {
    std::string nom;
    double m = 0;
    std::string groupe, tandem, role, devant_de;
    std::vector<std::string> interdit;
    bool has_sortie = false;
    double sortie = 0;
    double target = -1;
};

struct Model {
    std::vector<Seat> seats;
    std::vector<Para> paras;
    double base_m = 0, base_mom = 0, mtow = 1e300;
    std::string immat;
    std::vector<std::pair<double, double>> fwd, aft;
    std::vector<std::vector<int>> stages;
    std::vector<std::string> stage_names;
    std::vector<int> first_group;
    std::vector<double> door_rank;
    bool has_door = false;
    double door_x = 0, door_y = 0;
    std::vector<std::pair<std::string, std::vector<int>>> groups;
    std::vector<double> group_exit;
    std::vector<std::pair<int, int>> pairs;  // (arriere, devant) : devant est juste devant arriere
    std::vector<std::pair<int, int>> tandems;
    std::string etapes = "premier_groupe";
    bool ordered = false;
    double marge_avant = 0.5, tolerance = 0.25, w_g = 2.0, w_s = 1.0, w_l = 0.5, pitch = 25.0;
    double temps_max = 10.0, gap = 0.05, recuit_s = 1.0;
    bool rapide = false;
};

static double interp(const std::vector<std::pair<double, double>>& pts, double w) {
    if (pts.empty()) return NAN;
    if (w <= pts.front().first) return pts.front().second;
    for (size_t i = 1; i < pts.size(); ++i)
        if (w <= pts[i].first) {
            auto [w0, c0] = pts[i - 1];
            auto [w1, c1] = pts[i];
            return c0 + (c1 - c0) * (w - w0) / (w1 - w0);
        }
    return pts.back().second;
}

static double opt(const json& o, const char* k, double d) {
    return (o.is_object() && o.contains(k) && o[k].is_number()) ? o[k].get<double>() : d;
}
static std::string sopt(const json& o, const char* k) {
    if (!o.is_object() || !o.contains(k) || o[k].is_null()) return "";
    if (o[k].is_string()) return o[k].get<std::string>();
    if (o[k].is_number_integer()) return std::to_string(o[k].get<long>());
    return o[k].dump();
}

static Model load(const json& j, const json& cli) {
    Model m;
    const auto& av = j.at("avion");
    m.immat = sopt(av, "immat");
    double ew = av.at("masse_vide").get<double>();
    double ew_mom = av.contains("moment_vide") ? av["moment_vide"].get<double>() : ew * av.at("bras_vide").get<double>();
    auto pts = [&](const char* k) {
        std::vector<std::pair<double, double>> v;
        for (const auto& p : j.at("enveloppe").at(k)) v.emplace_back(p[0].get<double>(), p[1].get<double>());
        std::sort(v.begin(), v.end());
        return v;
    };
    m.fwd = pts("avant");
    m.aft = pts("arriere");
    m.mtow = opt(j["enveloppe"], "mtow", 1e300);
    double fuel_m = j.contains("carburant") ? opt(j["carburant"], "masse", 0) : 0;
    double fuel_x = j.contains("carburant") ? opt(j["carburant"], "bras", 0) : 0;
    double pil_m = j.contains("pilote") ? opt(j["pilote"], "masse", 0) : 0;
    double pil_x = j.contains("pilote") ? opt(j["pilote"], "bras", 0) : 0;
    m.base_m = ew + fuel_m + pil_m;
    m.base_mom = ew_mom + fuel_m * fuel_x + pil_m * pil_x;

    int i = 0;
    for (const auto& s : j.at("places")) {
        Seat st;
        st.id = s.contains("id") ? sopt(s, "id") : std::to_string(i);
        st.x = s.at("x").get<double>();
        st.y = opt(s, "y", 0);
        st.copilot = s.value("copilote", false);
        st.centre = s.value("centre", false);
        st.no_tandem = s.value("interdit_tandem", false);
        m.seats.push_back(st);
        ++i;
    }
    i = 0;
    for (const auto& s : j.at("places")) {
        Seat& st = m.seats[i];
        if (s.contains("devant") && !s["devant"].is_null()) {
            std::string d = sopt(s, "devant");
            for (size_t k = 0; k < m.seats.size(); ++k)
                if (m.seats[k].id == d) st.devant = (int)k;
        } else {
            for (size_t k = 0; k < m.seats.size(); ++k) {
                const Seat& t = m.seats[k];
                if ((int)k != i && std::fabs(t.y - st.y) < 1e-6 && t.x < st.x - 1e-6 && !t.copilot && !t.centre && !t.no_tandem)
                    if (st.devant < 0 || t.x > m.seats[st.devant].x) st.devant = (int)k;
            }
        }
        if (st.copilot || st.centre || st.no_tandem) st.devant = -1;
        ++i;
    }
    double dx = -1e300, dy = 0;
    for (const auto& s : m.seats) dx = std::max(dx, s.x);
    if (j.contains("porte")) {
        m.has_door = true;
        dx = opt(j["porte"], "x", dx);
        dy = opt(j["porte"], "y", dy);
    }
    m.door_x = dx;
    m.door_y = dy;
    std::vector<std::pair<double, int>> d;
    for (size_t k = 0; k < m.seats.size(); ++k) d.emplace_back(std::hypot(m.seats[k].x - dx, m.seats[k].y - dy), (int)k);
    std::sort(d.begin(), d.end());
    m.door_rank.assign(m.seats.size(), 0);
    for (size_t r = 0; r < d.size(); ++r) m.door_rank[d[r].second] = (double)(r + 1);

    for (const auto& p : j.at("paras")) {
        Para pa;
        pa.nom = p.value("nom", std::string("?"));
        pa.m = p.at("masse").get<double>();
        pa.groupe = sopt(p, "groupe");
        pa.tandem = sopt(p, "tandem");
        pa.role = sopt(p, "role");
        pa.devant_de = sopt(p, "devant_de");
        if (p.contains("interdit") && p["interdit"].is_array())
            for (const auto& s : p["interdit"]) pa.interdit.push_back(s.is_string() ? s.get<std::string>() : s.dump());
        if (p.contains("sortie") && p["sortie"].is_number()) {
            pa.has_sortie = true;
            pa.sortie = p["sortie"].get<double>();
        }
        m.paras.push_back(pa);
    }
    int n = (int)m.paras.size();
    if (n == 0) throw std::runtime_error("aucun para");
    if (n > (int)m.seats.size()) throw std::runtime_error(std::to_string(n) + " paras pour " + std::to_string(m.seats.size()) + " places");
    std::vector<int> order(n);
    for (int k = 0; k < n; ++k) order[k] = k;
    std::stable_sort(order.begin(), order.end(), [&](int a, int b) {
        double ka = m.paras[a].has_sortie ? m.paras[a].sortie : 1e300;
        double kb = m.paras[b].has_sortie ? m.paras[b].sortie : 1e300;
        return ka < kb;
    });
    std::vector<int> ranked;
    for (int p : order)
        if (m.paras[p].has_sortie) ranked.push_back(p);
    for (size_t pos = 0; pos < ranked.size();) {
        size_t e = pos;
        while (e < ranked.size() && m.paras[ranked[e]].sortie == m.paras[ranked[pos]].sortie) ++e;
        double mean = (double)(pos + 1 + e) / 2.0;
        for (size_t q = pos; q < e; ++q) m.paras[ranked[q]].target = mean;
        pos = e;
    }
    json o = j.contains("options") && j["options"].is_object() ? j["options"] : json::object();
    for (auto it = cli.begin(); it != cli.end(); ++it) o[it.key()] = it.value();
    m.etapes = o.value("etapes", std::string("premier_groupe"));
    m.ordered = o.value("groupes_ordonnes", false);
    m.marge_avant = opt(o, "marge_avant_min", 0.5);
    m.tolerance = opt(o, "tolerance_marge", 0.25);
    m.w_g = opt(o, "poids_groupe", 2.0);
    m.w_s = opt(o, "poids_sortie", 1.0);
    m.w_l = opt(o, "poids_lateral", 0.5);
    m.pitch = opt(o, "pas", 25.0);
    m.temps_max = opt(o, "temps_max_s", 10.0);
    m.gap = opt(o, "gap", 0.05);
    m.recuit_s = opt(o, "recuit_s", 1.0);
    m.rapide = o.value("rapide", false);
    m.stages.push_back(order);
    m.stage_names.push_back("decollage");
    if (!ranked.empty()) {
        size_t g1 = 0;
        while (g1 < ranked.size() && m.paras[ranked[g1]].sortie == m.paras[ranked[0]].sortie) ++g1;
        m.first_group.assign(ranked.begin(), ranked.begin() + g1);
    }
    if (m.etapes == "toutes") {
        for (int k = 1; k < n; ++k) {
            m.stages.emplace_back(order.begin() + k, order.end());
            m.stage_names.push_back("apres " + std::to_string(k) + " sortie(s)");
        }
    } else if (m.etapes == "premier_groupe") {
        if (!m.first_group.empty() && (int)m.first_group.size() < n) {
            m.stages.emplace_back(order.begin() + m.first_group.size(), order.end());
            m.stage_names.push_back("apres le premier groupe (" + std::to_string(m.first_group.size()) + " sorti(s))");
        }
    } else if (m.etapes != "decollage") {
        throw std::runtime_error("etapes : premier_groupe, toutes ou decollage");
    }
    std::map<std::string, std::vector<int>> gm;
    for (int p = 0; p < n; ++p)
        if (!m.paras[p].groupe.empty()) gm[m.paras[p].groupe].push_back(p);
    for (auto& [g, members] : gm)
        if (members.size() >= 2) {
            m.groups.emplace_back(g, members);
            double r = NAN;
            bool all = true;
            for (int p : members) {
                if (!m.paras[p].has_sortie) all = false;
                else r = std::isnan(r) ? m.paras[p].sortie : std::min(r, m.paras[p].sortie);
            }
            m.group_exit.push_back(all ? r : NAN);
        }
    std::map<std::string, std::pair<int, int>> tm;
    for (int p = 0; p < n; ++p)
        if (!m.paras[p].tandem.empty()) {
            auto& pr = tm.emplace(m.paras[p].tandem, std::make_pair(-1, -1)).first->second;
            if (m.paras[p].role == "porteur") pr.first = p;
            else pr.second = p;
        }
    for (auto& [t, pr] : tm) {
        if (pr.first < 0 || pr.second < 0) throw std::runtime_error("tandem " + t + " : il faut un porteur et un passager");
        m.tandems.push_back(pr);
        m.pairs.emplace_back(pr.first, pr.second);
    }
    for (int p = 0; p < n; ++p)
        if (!m.paras[p].devant_de.empty()) {
            int q = -1;
            for (int r = 0; r < n; ++r)
                if (m.paras[r].nom == m.paras[p].devant_de) q = r;
            if (q < 0) throw std::runtime_error("devant_de : para inconnu " + m.paras[p].devant_de);
            m.pairs.emplace_back(q, p);
        }
    return m;
}

// ------------------------------------------------------------------ MILP
struct Lp {
    std::vector<double> lo, up, cost;
    std::vector<HighsVarType> type;
    std::vector<double> rlo, rup;
    std::vector<std::vector<std::pair<int, double>>> rows;
    int add_var(double l, double u, bool integer = false) {
        lo.push_back(l); up.push_back(u); cost.push_back(0);
        type.push_back(integer ? HighsVarType::kInteger : HighsVarType::kContinuous);
        return (int)lo.size() - 1;
    }
    void add_row(std::vector<std::pair<int, double>> coefs, double l, double u) {
        rows.push_back(std::move(coefs)); rlo.push_back(l); rup.push_back(u);
    }
};

struct Built {
    Lp lp;
    int S = 0, N = 0, imu = -1;
    std::vector<std::array<int, 4>> ibox;
    std::vector<double> realism;
};

static double min_span(std::vector<double> c, size_t n) {
    std::sort(c.begin(), c.end());
    double best = 1e300;
    for (size_t i = 0; i + n <= c.size(); ++i) best = std::min(best, c[i + n - 1] - c[i]);
    return best;
}

static Built build(const Model& m, int phase, double mu_ar_min, double marge_avant) {
    Built b;
    b.S = (int)m.seats.size();
    b.N = (int)m.paras.size();
    const int S = b.S, N = b.N;
    Lp& lp = b.lp;
    auto iz = [S](int p, int s) { return p * S + s; };
    for (int p = 0; p < N; ++p)
        for (int s = 0; s < S; ++s) lp.add_var(0, 1, true);
    double xmin = 1e300, xmax = -1e300, ymin = 1e300, ymax = -1e300;
    std::vector<double> xs, ys;
    for (const auto& s : m.seats) {
        xmin = std::min(xmin, s.x); xmax = std::max(xmax, s.x);
        ymin = std::min(ymin, s.y); ymax = std::max(ymax, s.y);
        xs.push_back(s.x); ys.push_back(s.y);
    }
    for (size_t g = 0; g < m.groups.size(); ++g)
        b.ibox.push_back({lp.add_var(xmin, xmax), lp.add_var(xmin, xmax), lp.add_var(ymin, ymax), lp.add_var(ymin, ymax)});
    b.imu = lp.add_var(std::max(mu_ar_min, 0.0), 1e3);

    for (int p = 0; p < N; ++p) {
        std::vector<std::pair<int, double>> r;
        for (int s = 0; s < S; ++s) r.emplace_back(iz(p, s), 1.0);
        lp.add_row(r, 1, 1);
    }
    for (int s = 0; s < S; ++s) {
        std::vector<std::pair<int, double>> r;
        for (int p = 0; p < N; ++p) r.emplace_back(iz(p, s), 1.0);
        lp.add_row(r, -kHighsInf, 1);
    }
    for (int p = 0; p < N; ++p)
        for (const auto& id : m.paras[p].interdit)
            for (int s = 0; s < S; ++s)
                if (m.seats[s].id == id) lp.up[iz(p, s)] = 0;
    for (auto [back, front] : m.pairs) {
        std::vector<bool> is_front(S, false);
        for (int s = 0; s < S; ++s)
            if (m.seats[s].devant >= 0) is_front[m.seats[s].devant] = true;
        for (int s = 0; s < S; ++s) {
            if (m.seats[s].devant < 0) lp.up[iz(back, s)] = 0;
            if (!is_front[s]) lp.up[iz(front, s)] = 0;
        }
        for (int s = 0; s < S; ++s)
            if (m.seats[s].devant >= 0) lp.add_row({{iz(front, m.seats[s].devant), 1.0}, {iz(back, s), -1.0}}, 0, 0);
    }
    for (size_t k = 0; k < m.stages.size(); ++k) {
        double W = m.base_m;
        for (int p : m.stages[k]) W += m.paras[p].m;
        double L = interp(m.fwd, W), U = interp(m.aft, W);
        std::vector<std::pair<int, double>> c;
        for (int p : m.stages[k])
            for (int s = 0; s < S; ++s) c.emplace_back(iz(p, s), m.paras[p].m * m.seats[s].x);
        lp.add_row(c, (L + marge_avant) * W - m.base_mom, kHighsInf);
        if (k == 0) {
            auto c2 = c;
            c2.emplace_back(b.imu, W);
            lp.add_row(c2, -kHighsInf, U * W - m.base_mom);
        } else {
            lp.add_row(c, -kHighsInf, U * W - m.base_mom);
        }
    }
    for (size_t g = 0; g < m.groups.size(); ++g) {
        auto [Xn, Xx, Yn, Yx] = b.ibox[g];
        const auto& members = m.groups[g].second;
        lp.add_row({{Xx, 1.0}, {Xn, -1.0}}, min_span(xs, members.size()), kHighsInf);
        lp.add_row({{Yx, 1.0}, {Yn, -1.0}}, min_span(ys, members.size()), kHighsInf);
        for (int p : members) {
            std::vector<std::pair<int, double>> rx, ry;
            for (int s = 0; s < S; ++s) {
                rx.emplace_back(iz(p, s), m.seats[s].x);
                ry.emplace_back(iz(p, s), m.seats[s].y);
                lp.add_row({{iz(p, s), m.seats[s].x - xmin}, {Xx, -1.0}}, -kHighsInf, -xmin);
                lp.add_row({{iz(p, s), m.seats[s].x - xmax}, {Xn, -1.0}}, -xmax, kHighsInf);
                lp.add_row({{iz(p, s), m.seats[s].y - ymin}, {Yx, -1.0}}, -kHighsInf, -ymin);
                lp.add_row({{iz(p, s), m.seats[s].y - ymax}, {Yn, -1.0}}, -ymax, kHighsInf);
            }
            auto rx2 = rx, ry2 = ry;
            rx.emplace_back(Xx, -1.0); rx2.emplace_back(Xn, -1.0);
            ry.emplace_back(Yx, -1.0); ry2.emplace_back(Yn, -1.0);
            lp.add_row(rx, -kHighsInf, 0); lp.add_row(rx2, 0, kHighsInf);
            lp.add_row(ry, -kHighsInf, 0); lp.add_row(ry2, 0, kHighsInf);
        }
    }
    if (m.ordered)
        for (size_t g = 0; g < m.groups.size(); ++g)
            for (size_t h = 0; h < m.groups.size(); ++h)
                if (g != h && !std::isnan(m.group_exit[g]) && !std::isnan(m.group_exit[h]) && m.group_exit[g] < m.group_exit[h])
                    lp.add_row({{b.ibox[g][0], 1.0}, {b.ibox[h][1], -1.0}}, 0, kHighsInf);
    b.realism.assign(lp.lo.size(), 0.0);
    for (int p = 0; p < N; ++p)
        if (m.paras[p].target >= 0)
            for (int s = 0; s < S; ++s) b.realism[iz(p, s)] += m.w_s * std::fabs(m.door_rank[s] - m.paras[p].target);
    for (size_t g = 0; g < m.groups.size(); ++g) {
        auto [Xn, Xx, Yn, Yx] = b.ibox[g];
        b.realism[Xx] += m.w_g / m.pitch; b.realism[Xn] -= m.w_g / m.pitch;
        b.realism[Yx] += m.w_g * m.w_l / m.pitch; b.realism[Yn] -= m.w_g * m.w_l / m.pitch;
    }
    if (phase == 1) lp.cost[b.imu] = -1.0;
    else { lp.cost = b.realism; lp.cost[b.imu] = -1e-3; }
    return b;
}

struct Solved {
    bool ok = false;
    HighsModelStatus status = HighsModelStatus::kNotset;
    std::vector<double> x;
    double gap = 0, time = 0;
};

static Solved solve(const Lp& lp, double time_limit, double gap, const std::vector<double>* start = nullptr) {
    Highs h;
    h.setOptionValue("output_flag", false);
    h.setOptionValue("time_limit", time_limit);
    h.setOptionValue("mip_rel_gap", gap);
    int nv = (int)lp.lo.size();
    h.addVars(nv, lp.lo.data(), lp.up.data());
    for (int c = 0; c < nv; ++c) {
        h.changeColCost(c, lp.cost[c]);
        if (lp.type[c] == HighsVarType::kInteger) h.changeColIntegrality(c, HighsVarType::kInteger);
    }
    for (size_t r = 0; r < lp.rows.size(); ++r) {
        std::vector<HighsInt> idx;
        std::vector<double> val;
        for (auto [i, v] : lp.rows[r]) { idx.push_back(i); val.push_back(v); }
        h.addRow(lp.rlo[r], lp.rup[r], (HighsInt)idx.size(), idx.data(), val.data());
    }
    if (start && (int)start->size() == nv) {
        HighsSolution init;
        init.col_value = *start;
        init.value_valid = true;
        h.setSolution(init);
    }
    auto t0 = std::chrono::steady_clock::now();
    h.run();
    Solved s;
    s.status = h.getModelStatus();
    s.time = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();
    const auto& sol = h.getSolution();
    if (sol.value_valid) {
        s.x = sol.col_value;
        s.gap = h.getInfo().mip_gap;
        s.ok = true;
    }
    return s;
}

static std::vector<int> seats_of(const Built& b, const std::vector<double>& x) {
    std::vector<int> seat(b.N, -1);
    for (int p = 0; p < b.N; ++p) {
        double best = -1;
        for (int s = 0; s < b.S; ++s)
            if (x[p * b.S + s] > best) { best = x[p * b.S + s]; seat[p] = s; }
    }
    return seat;
}

struct Stage {
    std::string nom;
    double W, cg, av, ar;
    size_t restants;
};

static std::vector<Stage> stage_values(const Model& m, const std::vector<int>& seat) {
    std::vector<Stage> out;
    for (size_t k = 0; k < m.stages.size(); ++k) {
        double W = m.base_m, M = m.base_mom;
        for (int p : m.stages[k]) { W += m.paras[p].m; M += m.paras[p].m * m.seats[seat[p]].x; }
        double cg = M / W;
        out.push_back({m.stage_names[k], W, cg, cg - interp(m.fwd, W), interp(m.aft, W) - cg, m.stages[k].size()});
    }
    return out;
}

static std::string status_txt(HighsModelStatus st) {
    switch (st) {
        case HighsModelStatus::kOptimal: return "optimum";
        case HighsModelStatus::kInfeasible: return "infaisable";
        case HighsModelStatus::kTimeLimit: return "temps limite";
        default: return "autre";
    }
}

// ------------------------------------------------------------------ PDF minimal
struct Pdf {
    std::string c;
    static std::string latin1(const std::string& u) {
        std::string o;
        for (size_t i = 0; i < u.size();) {
            unsigned char b = u[i];
            unsigned cp; int len;
            if (b < 0x80) { cp = b; len = 1; }
            else if ((b >> 5) == 6 && i + 1 < u.size()) { cp = ((b & 0x1F) << 6) | (u[i + 1] & 0x3F); len = 2; }
            else if ((b >> 4) == 14 && i + 2 < u.size()) { cp = ((b & 0x0F) << 12) | ((u[i + 1] & 0x3F) << 6) | (u[i + 2] & 0x3F); len = 3; }
            else { cp = '?'; len = 4; }
            i += len;
            if (cp == '(' || cp == ')' || cp == '\\') { o += '\\'; o += (char)cp; }
            else if (cp < 256 && cp >= 32) o += (char)cp;
            else o += '?';
        }
        return o;
    }
    static std::string f(double v) { char b[32]; snprintf(b, sizeof b, "%.2f", v); return b; }
    void color(double r, double g, double bl, bool fill) { c += f(r) + " " + f(g) + " " + f(bl) + (fill ? " rg\n" : " RG\n"); }
    void width(double w) { c += f(w) + " w\n"; }
    void dash(bool on) { c += on ? "[3 2] 0 d\n" : "[] 0 d\n"; }
    void line(double x1, double y1, double x2, double y2) { c += f(x1) + " " + f(y1) + " m " + f(x2) + " " + f(y2) + " l S\n"; }
    void rect(double x, double y, double w, double h, bool fill) { c += f(x) + " " + f(y) + " " + f(w) + " " + f(h) + (fill ? " re f\n" : " re S\n"); }
    void poly(const std::vector<std::pair<double, double>>& p, bool fill, bool close = true) {
        for (size_t i = 0; i < p.size(); ++i) c += f(p[i].first) + " " + f(p[i].second) + (i ? " l\n" : " m\n");
        c += fill ? "f\n" : (close ? "s\n" : "S\n");
    }
    void circle(double cx, double cy, double r, bool fill) {
        const double k = 0.5523 * r;
        c += f(cx + r) + " " + f(cy) + " m\n";
        c += f(cx + r) + " " + f(cy + k) + " " + f(cx + k) + " " + f(cy + r) + " " + f(cx) + " " + f(cy + r) + " c\n";
        c += f(cx - k) + " " + f(cy + r) + " " + f(cx - r) + " " + f(cy + k) + " " + f(cx - r) + " " + f(cy) + " c\n";
        c += f(cx - r) + " " + f(cy - k) + " " + f(cx - k) + " " + f(cy - r) + " " + f(cx) + " " + f(cy - r) + " c\n";
        c += f(cx + k) + " " + f(cy - r) + " " + f(cx + r) + " " + f(cy - k) + " " + f(cx + r) + " " + f(cy) + " c\n";
        c += fill ? "f\n" : "s\n";
    }
    void text(double x, double y, double size, const std::string& s, int align = 0, bool bold = false) {
        std::string t = latin1(s);
        double w = 0.52 * size * (double)t.size();
        if (align == 1) x -= w / 2; else if (align == 2) x -= w;
        c += "BT /" + std::string(bold ? "F2" : "F1") + " " + f(size) + " Tf " + f(x) + " " + f(y) + " Td (" + t + ") Tj ET\n";
    }
    std::string build() {
        std::vector<std::string> objs;
        objs.push_back("<< /Type /Catalog /Pages 2 0 R >>");
        objs.push_back("<< /Type /Pages /Kids [3 0 R] /Count 1 >>");
        objs.push_back("<< /Type /Page /Parent 2 0 R /MediaBox [0 0 842 595] /Contents 4 0 R /Resources << /Font << /F1 5 0 R /F2 6 0 R >> >> >>");
        objs.push_back("<< /Length " + std::to_string(c.size()) + " >>\nstream\n" + c + "\nendstream");
        objs.push_back("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>");
        objs.push_back("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>");
        std::string out = "%PDF-1.4\n%\xE2\xE3\xCF\xD3\n";
        std::vector<size_t> off;
        for (size_t i = 0; i < objs.size(); ++i) {
            off.push_back(out.size());
            out += std::to_string(i + 1) + " 0 obj\n" + objs[i] + "\nendobj\n";
        }
        size_t xref = out.size();
        out += "xref\n0 " + std::to_string(objs.size() + 1) + "\n0000000000 65535 f \n";
        for (size_t o : off) { char b[32]; snprintf(b, sizeof b, "%010zu 00000 n \n", o); out += b; }
        out += "trailer\n<< /Size " + std::to_string(objs.size() + 1) + " /Root 1 0 R >>\nstartxref\n" + std::to_string(xref) + "\n%%EOF\n";
        return out;
    }
};

static const double PALETTE[8][3] = {{0.16, 0.47, 0.84}, {0.92, 0.41, 0.20}, {0.11, 0.69, 0.48}, {0.93, 0.63, 0.00},
                                     {0.91, 0.48, 0.64}, {0.00, 0.51, 0.00}, {0.29, 0.23, 0.65}, {0.89, 0.29, 0.28}};

static std::string num(double v, int dec = 1) { char b[32]; snprintf(b, sizeof b, "%.*f", dec, v); return b; }

static void draw_pdf(const Model& m, const std::vector<int>& seat, const std::vector<Stage>& st, const json& info, const std::string& path) {
    Pdf pdf;
    pdf.color(0, 0, 0, true);
    std::string title = "Placement des paras" + (m.immat.empty() ? "" : " - " + m.immat);
    pdf.text(30, 565, 15, title, 0, true);
    std::time_t now = std::time(nullptr);
    char date[64]; std::strftime(date, sizeof date, "%d/%m/%Y %H:%M", std::localtime(&now));
    pdf.text(812, 567, 8, std::string("genere le ") + date + " par placement " + VERSION, 2);
    std::string sub = std::to_string(m.paras.size()) + " paras ; objectif : CG le plus avant possible au decollage, marge avant >= " +
                      num(m.marge_avant, 2) + " " + (m.etapes == "premier_groupe" ? "apres la sortie du premier groupe" : m.etapes == "toutes" ? "apres chaque sortie" : "au decollage");
    pdf.text(30, 550, 8.5, sub);

    double xmin = 1e300, xmax = -1e300, ymin = 1e300, ymax = -1e300;
    for (const auto& s : m.seats) { xmin = std::min(xmin, s.x); xmax = std::max(xmax, s.x); ymin = std::min(ymin, s.y); ymax = std::max(ymax, s.y); }
    double lo_x = std::min(xmin, st[0].cg - st[0].av) - 18;
    double hi_x = std::max(xmax, std::max(st[0].cg + st[0].ar, m.has_door ? m.door_x : xmax)) + 18;
    const double PX0 = 40, PX1 = 560, PY0 = 330, PY1 = 520;
    double yr = std::max(ymax - ymin, 1.0);
    auto mx = [&](double x) { return PX0 + (x - lo_x) / (hi_x - lo_x) * (PX1 - PX0); };
    auto my = [&](double y) { return PY0 + 25 + (y - ymin) / yr * (PY1 - PY0 - 50); };
    pdf.color(0.35, 0.35, 0.35, false); pdf.width(1.0);
    std::vector<std::pair<double, double>> fus = {{PX0, PY0 + 50}, {PX0 + 45, PY0 + 5}, {PX1, PY0 + 5}, {PX1, PY1 - 5}, {PX0 + 45, PY1 - 5}, {PX0, PY1 - 50}};
    pdf.poly(fus, false);
    pdf.color(0.35, 0.35, 0.35, true);
    pdf.text(PX0 + 8, PY1 - 62, 7, "avant");
    if (m.has_door) {
        pdf.color(0.92, 0.41, 0.20, false); pdf.width(3.5);
        bool low = m.door_y < (ymin + ymax) / 2;
        double dy = low ? PY0 + 3 : PY1 - 3;
        pdf.line(mx(m.door_x) - 22, dy, mx(m.door_x) + 22, dy);
        pdf.color(0.92, 0.41, 0.20, true);
        pdf.text(mx(m.door_x), low ? dy - 10 : dy + 4, 7, "porte", 1);
    }
    // etiquettes ecartees : limite avant a gauche de son trait, limite arriere a droite,
    // CG decollage a gauche en bas, CG apres le premier groupe a droite en bas
    auto vline = [&](double x, double r, double g, double b, const std::string& lab, double ty, int align, bool dashed) {
        pdf.color(r, g, b, false); pdf.width(1.2); pdf.dash(dashed);
        pdf.line(mx(x), PY0 + 8, mx(x), PY1 - 8);
        pdf.dash(false);
        pdf.color(r, g, b, true);
        pdf.text(mx(x) + (align == 2 ? -3 : align == 0 ? 3 : 0), ty, 6.5, lab, align);
    };
    vline(st[0].cg - st[0].av, 0.16, 0.47, 0.84, "limite avant " + num(st[0].cg - st[0].av) + " |", PY1 - 3, 2, true);
    vline(st[0].cg + st[0].ar, 0.16, 0.47, 0.84, "| limite arriere " + num(st[0].cg + st[0].ar), PY1 - 3, 0, true);
    vline(st[0].cg, 0.89, 0.29, 0.28, "CG decollage " + num(st[0].cg) + " |", PY0 - 2, 2, false);
    if (st.size() > 1) vline(st[1].cg, 0.92, 0.41, 0.20, "| CG apres 1er groupe " + num(st[1].cg), PY0 - 2, 0, false);
    std::map<std::string, int> gcol;
    for (size_t g = 0; g < m.groups.size(); ++g) gcol[m.groups[g].first] = (int)(g % 8);
    std::vector<int> occ(m.seats.size(), -1);
    for (size_t p = 0; p < seat.size(); ++p) occ[seat[p]] = (int)p;
    for (auto [back, front] : m.pairs) {
        pdf.color(0.1, 0.1, 0.1, false); pdf.width(2.2);
        pdf.line(mx(m.seats[seat[back]].x), my(m.seats[seat[back]].y), mx(m.seats[seat[front]].x), my(m.seats[seat[front]].y));
    }
    for (size_t s = 0; s < m.seats.size(); ++s) {
        double cx = mx(m.seats[s].x), cy = my(m.seats[s].y);
        int p = occ[s];
        if (p < 0) {
            pdf.color(0.75, 0.75, 0.75, false); pdf.width(0.8); pdf.circle(cx, cy, 8.5, false);
            pdf.color(0.6, 0.6, 0.6, true); pdf.text(cx, cy - 2, 5.5, m.seats[s].id, 1);
            continue;
        }
        const Para& pa = m.paras[p];
        if (!pa.groupe.empty() && gcol.count(pa.groupe)) { const double* col = PALETTE[gcol[pa.groupe]]; pdf.color(col[0], col[1], col[2], true); }
        else pdf.color(0.32, 0.32, 0.31, true);
        pdf.circle(cx, cy, 8.5, true);
        pdf.color(1, 1, 1, true);
        std::string lab = pa.has_sortie ? num(pa.sortie, pa.sortie == std::floor(pa.sortie) ? 0 : 1) : "-";
        pdf.text(cx, cy - 2.5, 7, lab, 1, true);
        pdf.color(0.1, 0.1, 0.1, true);
        pdf.text(cx, cy - 15, 5.5, pa.nom + " " + num(pa.m, 0), 1);
        pdf.color(0.45, 0.45, 0.45, true);
        pdf.text(cx, cy + 10.5, 5, m.seats[s].id + " (" + num(m.seats[s].x, 0) + ")", 1);
    }
    double ly = PY0 - 24;
    for (size_t g = 0; g < m.groups.size(); ++g) {
        const double* col = PALETTE[g % 8];
        pdf.color(col[0], col[1], col[2], true); pdf.circle(PX0 + 6 + (double)(g % 6) * 85, ly - (double)(g / 6) * 10, 3.5, true);
        pdf.color(0.1, 0.1, 0.1, true); pdf.text(PX0 + 13 + (double)(g % 6) * 85, ly - 2.5 - (double)(g / 6) * 10, 6.5, "groupe " + m.groups[g].first);
    }
    pdf.color(0.1, 0.1, 0.1, true);
    pdf.text(PX1, ly - 2.5 - (double)((m.groups.size() + 5) / 6) * 10, 6.5, "numero = rang de sortie ; trait = paire porteur / passager", 2);

    const double EX0 = 600, EX1 = 810, EY0 = 345, EY1 = 520;
    double cmin = 1e300, cmax = -1e300, wmin = 1e300, wmax = -1e300;
    for (auto& p : m.fwd) { cmin = std::min(cmin, p.second); wmin = std::min(wmin, p.first); wmax = std::max(wmax, p.first); }
    for (auto& p : m.aft) { cmax = std::max(cmax, p.second); wmin = std::min(wmin, p.first); wmax = std::max(wmax, p.first); }
    for (auto& s : st) { wmin = std::min(wmin, s.W); wmax = std::max(wmax, s.W); cmin = std::min(cmin, s.cg); cmax = std::max(cmax, s.cg); }
    wmin = std::min(wmin, m.base_m);
    if (m.mtow < 1e299) wmax = std::max(wmax, m.mtow);
    cmin -= 2; cmax += 2; double wr = wmax - wmin; wmin -= 0.05 * wr; wmax += 0.05 * wr;
    auto ex = [&](double c) { return EX0 + (c - cmin) / (cmax - cmin) * (EX1 - EX0); };
    auto ey = [&](double w) { return EY0 + (w - wmin) / (wmax - wmin) * (EY1 - EY0); };
    pdf.color(0.6, 0.6, 0.6, false); pdf.width(0.6); pdf.rect(EX0, EY0, EX1 - EX0, EY1 - EY0, false);
    auto env_line = [&](const std::vector<std::pair<double, double>>& pts) {
        std::vector<std::pair<double, double>> pl;
        double w0 = std::max(wmin, std::min(m.base_m, pts.front().first));
        pl.emplace_back(ex(interp(pts, w0)), ey(w0));
        for (auto& p : pts) if (p.first >= w0) pl.emplace_back(ex(p.second), ey(p.first));
        double w1 = std::min(wmax, m.mtow < 1e299 ? m.mtow : wmax);
        pl.emplace_back(ex(interp(pts, w1)), ey(w1));
        pdf.poly(pl, false, false);
    };
    pdf.color(0.16, 0.47, 0.84, false); pdf.width(1.4);
    env_line(m.fwd); env_line(m.aft);
    if (m.mtow < 1e299) { pdf.dash(true); pdf.line(EX0, ey(m.mtow), EX1, ey(m.mtow)); pdf.dash(false); pdf.color(0.16, 0.47, 0.84, true); pdf.text(EX0 + 3, ey(m.mtow) + 2, 6, "MTOW " + num(m.mtow, 0)); }
    pdf.color(0.4, 0.4, 0.4, false); pdf.width(1.0);
    for (size_t k = 1; k < st.size(); ++k) pdf.line(ex(st[k - 1].cg), ey(st[k - 1].W), ex(st[k].cg), ey(st[k].W));
    for (size_t k = 0; k < st.size(); ++k) {
        if (k == 0) pdf.color(0.89, 0.29, 0.28, true); else pdf.color(0.92, 0.41, 0.20, true);
        pdf.circle(ex(st[k].cg), ey(st[k].W), 3.2, true);
    }
    pdf.color(0.1, 0.1, 0.1, true);
    pdf.text((EX0 + EX1) / 2, EY1 + 6, 7.5, "Centrogramme : masse (haut) contre CG", 1, true);
    pdf.text((EX0 + EX1) / 2, EY0 - 10, 6.5, "CG  " + num(cmin + 2) + " ... " + num(cmax - 2), 1);
    pdf.text(EX0 - 3, EY1 - 4, 6, num(wmax, 0), 2); pdf.text(EX0 - 3, EY0, 6, num(wmin, 0), 2);
    pdf.text(EX0, EY0 - 20, 6, "rouge : decollage ; orange : apres le premier groupe");

    double ty = 280;
    pdf.color(0.1, 0.1, 0.1, true);
    pdf.text(30, ty, 8.5, "Placement (rang de sortie, para, masse, groupe, place, bras, cote)", 0, true);
    std::vector<int> order(m.paras.size());
    for (size_t i = 0; i < order.size(); ++i) order[i] = (int)i;
    std::stable_sort(order.begin(), order.end(), [&](int a, int b) {
        double ka = m.paras[a].has_sortie ? m.paras[a].sortie : 1e300, kb = m.paras[b].has_sortie ? m.paras[b].sortie : 1e300;
        return ka < kb;
    });
    double rowy = ty - 12;
    int col = 0;
    for (int p : order) {
        const Para& pa = m.paras[p];
        const Seat& s = m.seats[seat[p]];
        std::string cote = std::fabs(s.y) < 1e-6 ? "centre" : (s.y > 0 ? "droite" : "gauche");
        std::string line = (pa.has_sortie ? num(pa.sortie, 0) : "-") + "  " + pa.nom + "  " + num(pa.m, 0) + "  " + (pa.groupe.empty() ? "-" : pa.groupe) +
                           (pa.tandem.empty() ? "" : " (" + pa.role + " " + pa.tandem + ")") + "  place " + s.id + "  " + num(s.x, 0) + "  " + cote;
        pdf.text(30 + col * 270, rowy, 7, line);
        rowy -= 9.5;
        if (rowy < 40) { rowy = ty - 12; ++col; }
    }
    double sy = 280, sx = 600;
    pdf.text(sx, sy, 8.5, "Masse, CG et marges", 0, true);
    sy -= 12;
    for (const auto& s : st) {
        pdf.text(sx, sy, 7, s.nom + " (" + std::to_string(s.restants) + " a bord)", 0, true); sy -= 9.5;
        pdf.text(sx, sy, 7, "masse " + num(s.W, 0) + "   CG " + num(s.cg, 2)); sy -= 9.5;
        pdf.text(sx, sy, 7, "marge avant " + num(s.av, 2) + "   marge arriere " + num(s.ar, 2)); sy -= 12;
    }
    pdf.text(sx, sy, 7, "marge arriere max possible : " + num(info.value("marge_arriere_max", 0.0), 2) + " (" + info.value("phase1", std::string("?")) + ")"); sy -= 9.5;
    pdf.text(sx, sy, 7, "phase 2 (realisme) : " + info.value("phase2", std::string("?"))); sy -= 9.5;
    pdf.text(sx, sy, 7, "boites " + num(info.value("boites", 0.0), 2) + "   ecart de sortie " + num(info.value("ecart_sortie", 0.0), 0) + "   temps " + num(info.value("temps_s", 0.0), 1) + " s");
    std::ofstream f(path, std::ios::binary);
    f << pdf.build();
}

// ------------------------------------------------------------------ recuit simule
// Point de depart de qualite pour la phase 2 (ou phase 2 complete en mode rapide) :
// meme cout de realisme que le MILP, contraintes en penalite, solutions verifiees.
struct Rng {
    uint64_t s;
    explicit Rng(uint64_t seed) : s(seed * 0x9E3779B97F4A7C15ULL | 1) {}
    uint64_t next() { s ^= s << 13; s ^= s >> 7; s ^= s << 17; return s; }
    double f() { return (double)(next() >> 11) / 9007199254740992.0; }
    int below(int n) { return (int)(next() % (uint64_t)n); }
};

static double realism_of(const Model& m, const std::vector<int>& seat) {
    double r = 0;
    for (size_t p = 0; p < m.paras.size(); ++p)
        if (m.paras[p].target >= 0) r += m.w_s * std::fabs(m.door_rank[seat[p]] - m.paras[p].target);
    for (const auto& g : m.groups) {
        double xn = 1e300, xx = -1e300, yn = 1e300, yx = -1e300;
        for (int p : g.second) {
            xn = std::min(xn, m.seats[seat[p]].x); xx = std::max(xx, m.seats[seat[p]].x);
            yn = std::min(yn, m.seats[seat[p]].y); yx = std::max(yx, m.seats[seat[p]].y);
        }
        r += m.w_g * (xx - xn + m.w_l * (yx - yn)) / m.pitch;
    }
    return r;
}

// violation des contraintes (0 si le placement est admissible) : marges par etape, ordre
static double violation_of(const Model& m, const std::vector<int>& seat, double mu_ar_min, double marge_avant) {
    double v = 0;
    for (size_t k = 0; k < m.stages.size(); ++k) {
        double W = m.base_m, M = m.base_mom;
        for (int p : m.stages[k]) { W += m.paras[p].m; M += m.paras[p].m * m.seats[seat[p]].x; }
        double cg = M / W;
        double av = cg - interp(m.fwd, W), ar = interp(m.aft, W) - cg;
        if (av < marge_avant) v += marge_avant - av;
        double ar_min = k == 0 ? mu_ar_min : 0.0;
        if (ar < ar_min) v += ar_min - ar;
    }
    if (m.ordered)
        for (size_t g = 0; g < m.groups.size(); ++g)
            for (size_t h = 0; h < m.groups.size(); ++h)
                if (g != h && !std::isnan(m.group_exit[g]) && !std::isnan(m.group_exit[h]) && m.group_exit[g] < m.group_exit[h]) {
                    double mn = 1e300, mx = -1e300;
                    for (int p : m.groups[g].second) mn = std::min(mn, m.seats[seat[p]].x);
                    for (int p : m.groups[h].second) mx = std::max(mx, m.seats[seat[p]].x);
                    if (mx > mn) v += (mx - mn) / m.pitch;
                }
    return v;
}

static bool structure_ok(const Model& m, const std::vector<int>& seat) {
    std::vector<int> occ(m.seats.size(), -1);
    for (size_t p = 0; p < seat.size(); ++p) {
        if (seat[p] < 0 || occ[seat[p]] >= 0) return false;
        occ[seat[p]] = (int)p;
        for (const auto& id : m.paras[p].interdit)
            if (m.seats[seat[p]].id == id) return false;
    }
    for (auto [back, front] : m.pairs)
        if (m.seats[seat[back]].devant != seat[front]) return false;
    return true;
}

static std::vector<int> anneal(const Model& m, const std::vector<int>& start, double mu_ar_min, double marge_avant,
                               double seconds, uint64_t seed, double* best_cost_out) {
    const int N = (int)m.paras.size(), S = (int)m.seats.size();
    Rng rng(seed);
    std::vector<int> in_pair(N, -1);
    for (size_t i = 0; i < m.pairs.size(); ++i) { in_pair[m.pairs[i].first] = (int)i; in_pair[m.pairs[i].second] = (int)i; }
    auto cost = [&](const std::vector<int>& st) { return realism_of(m, st) + 200.0 * violation_of(m, st, mu_ar_min, marge_avant); };
    std::vector<int> cur = start, best = start;
    double c_cur = cost(cur);
    double c_best = violation_of(m, cur, mu_ar_min, marge_avant) < 1e-9 ? c_cur : 1e300;
    std::vector<int> occ(S, -1);
    for (int p = 0; p < N; ++p) occ[cur[p]] = p;
    auto t0 = std::chrono::steady_clock::now();
    const double T0 = 3.0, T1 = 0.02;
    long it = 0;
    double frac = 0;
    while (true) {
        if ((it & 255) == 0) {
            frac = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count() / seconds;
            if (frac >= 1.0) break;
        }
        ++it;
        double T = T0 * std::pow(T1 / T0, frac);
        int p = rng.below(N);
        std::vector<int> cand = cur;
        if (in_pair[p] >= 0) {
            auto [back, front] = m.pairs[in_pair[p]];
            int s_new = rng.below(S);
            if (m.seats[s_new].devant < 0 || s_new == cur[back]) continue;
            int d_new = m.seats[s_new].devant;
            int o1 = occ[s_new], o2 = occ[d_new];
            if ((o1 >= 0 && in_pair[o1] >= 0 && o1 != back && o1 != front) || (o2 >= 0 && in_pair[o2] >= 0 && o2 != back && o2 != front)) continue;
            int s_old = cur[back], d_old = cur[front];
            cand[back] = s_new; cand[front] = d_new;
            std::vector<int> displaced;
            if (o1 >= 0 && o1 != back && o1 != front) displaced.push_back(o1);
            if (o2 >= 0 && o2 != back && o2 != front) displaced.push_back(o2);
            std::vector<int> freed;
            if (s_old != s_new && s_old != d_new) freed.push_back(s_old);
            if (d_old != s_new && d_old != d_new) freed.push_back(d_old);
            for (size_t i = 0; i < displaced.size(); ++i) {
                if (i >= freed.size()) { cand.clear(); break; }
                cand[displaced[i]] = freed[i];
            }
            if (cand.empty()) continue;
        } else {
            int s_new = rng.below(S);
            if (s_new == cur[p]) continue;
            int o = occ[s_new];
            if (o >= 0 && in_pair[o] >= 0) continue;
            if (o >= 0) cand[o] = cur[p];
            cand[p] = s_new;
        }
        if (!structure_ok(m, cand)) continue;
        double c = cost(cand);
        if (c <= c_cur || rng.f() < std::exp((c_cur - c) / T)) {
            cur = cand; c_cur = c;
            std::fill(occ.begin(), occ.end(), -1);
            for (int q = 0; q < N; ++q) occ[cur[q]] = q;
            if (c < c_best && violation_of(m, cur, mu_ar_min, marge_avant) < 1e-9) { best = cur; c_best = c; }
        }
    }
    if (best_cost_out) *best_cost_out = c_best;
    return best;
}

// vecteur de variables MILP complet correspondant a un placement (pour setSolution)
static std::vector<double> lp_vector(const Model& m, const Built& b, const std::vector<int>& seat) {
    std::vector<double> x(b.lp.lo.size(), 0.0);
    for (int p = 0; p < b.N; ++p) x[p * b.S + seat[p]] = 1.0;
    for (size_t g = 0; g < m.groups.size(); ++g) {
        double xn = 1e300, xx = -1e300, yn = 1e300, yx = -1e300;
        for (int p : m.groups[g].second) {
            xn = std::min(xn, m.seats[seat[p]].x); xx = std::max(xx, m.seats[seat[p]].x);
            yn = std::min(yn, m.seats[seat[p]].y); yx = std::max(yx, m.seats[seat[p]].y);
        }
        x[b.ibox[g][0]] = xn; x[b.ibox[g][1]] = xx; x[b.ibox[g][2]] = yn; x[b.ibox[g][3]] = yx;
    }
    double W = m.base_m, M = m.base_mom;
    for (int p = 0; p < b.N; ++p) { W += m.paras[p].m; M += m.paras[p].m * m.seats[seat[p]].x; }
    x[b.imu] = std::max(0.0, interp(m.aft, W) - M / W);
    return x;
}

int main(int argc, char** argv) {
    auto t_start = std::chrono::steady_clock::now();
    std::string in_path, out_path, pdf_path;
    json cli = json::object();
    bool quiet = false;
    for (int i = 1; i < argc; ++i) {
        std::string a = argv[i];
        auto val = [&](const char* name) -> std::string {
            if (i + 1 >= argc) { std::cerr << "option " << name << " : valeur manquante\n"; std::exit(2); }
            return argv[++i];
        };
        if (a == "--help" || a == "-h") { std::cout << HELP; return 0; }
        else if (a == "--version") { std::cout << "placement " << VERSION << "\n"; return 0; }
        else if (a == "--sortie") out_path = val("--sortie");
        else if (a == "--pdf") pdf_path = val("--pdf");
        else if (a == "--etapes") cli["etapes"] = val("--etapes");
        else if (a == "--marge-avant") cli["marge_avant_min"] = std::stod(val("--marge-avant"));
        else if (a == "--tolerance") cli["tolerance_marge"] = std::stod(val("--tolerance"));
        else if (a == "--groupes-ordonnes") cli["groupes_ordonnes"] = true;
        else if (a == "--temps") cli["temps_max_s"] = std::stod(val("--temps"));
        else if (a == "--gap") cli["gap"] = std::stod(val("--gap"));
        else if (a == "--recuit") cli["recuit_s"] = std::stod(val("--recuit"));
        else if (a == "--rapide") cli["rapide"] = true;
        else if (a == "--silencieux") quiet = true;
        else if (a.size() > 1 && a[0] == '-' && a != "-") { std::cerr << "option inconnue : " << a << "\n" << HELP; return 2; }
        else if (in_path.empty()) in_path = a;
        else if (out_path.empty()) out_path = a;
        else { std::cerr << "argument en trop : " << a << "\n"; return 2; }
    }
    if (in_path.empty()) { std::cerr << HELP; return 2; }
    std::string text;
    if (in_path == "-") { std::stringstream ss; ss << std::cin.rdbuf(); text = ss.str(); }
    else {
        std::ifstream f(in_path);
        if (!f) { std::cerr << "lecture impossible : " << in_path << "\n"; return 2; }
        std::stringstream ss; ss << f.rdbuf(); text = ss.str();
    }
    json out;
    int rc = 0;
    try {
        json j = json::parse(text);
        Model m = load(j, cli);
        double total = m.base_m;
        for (const auto& p : m.paras) total += p.m;
        json fg = json::array();
        for (int p : m.first_group) fg.push_back(m.paras[p].nom);
        if (total > m.mtow + 1e-9) {
            out = {{"ok", false}, {"message", "masse au decollage " + num(total, 0) + " > MTOW " + num(m.mtow, 0)}, {"masse_decollage", total}, {"mtow", m.mtow}};
            rc = 1;
        } else {
            Built b1 = build(m, 1, 0.0, m.marge_avant);
            Solved s1 = solve(b1.lp, m.temps_max, m.gap);
            if (!s1.ok) {
                double lo = -6.0, hi = m.marge_avant, best_mu_av = NAN;
                Solved best;
                for (int it = 0; it < 5; ++it) {
                    double mid = (lo + hi) / 2;
                    Built bt = build(m, 1, 0.0, mid);
                    Solved stt = solve(bt.lp, std::min(m.temps_max, 3.0), 0.05);
                    if (stt.ok) { best = stt; best_mu_av = mid; lo = mid; } else hi = mid;
                }
                out = {{"ok", false}, {"marge_avant_min", m.marge_avant}, {"etapes_mode", m.etapes}, {"premier_groupe", fg}};
                rc = 1;
                if (best.ok) {
                    out["message"] = "aucun placement avec marge avant >= " + num(m.marge_avant, 2) + " ; au mieux " + num(best_mu_av, 2);
                    out["marge_avant_max_possible"] = best_mu_av;
                    Built bb = build(m, 1, 0.0, best_mu_av);
                    auto seat = seats_of(bb, best.x);
                    json pl = json::array();
                    for (int p = 0; p < bb.N; ++p) pl.push_back({{"nom", m.paras[p].nom}, {"place", m.seats[seat[p]].id}, {"x", m.seats[seat[p]].x}, {"y", m.seats[seat[p]].y}});
                    out["placement_au_mieux"] = pl;
                    json et = json::array();
                    for (const auto& s : stage_values(m, seat)) et.push_back({{"etape", s.nom}, {"restants", s.restants}, {"masse", s.W}, {"cg", s.cg}, {"marge_avant", s.av}, {"marge_arriere", s.ar}});
                    out["etapes_au_mieux"] = et;
                } else {
                    out["message"] = "aucun placement dans l enveloppe, meme sans marge avant";
                }
            } else {
                double mu_star = s1.x[b1.imu];
                double mu_min = mu_star - m.tolerance;
                Built b2 = build(m, 2, mu_min, m.marge_avant);
                // amorcage : recuit simule depuis la solution de phase 1
                auto seat1 = seats_of(b1, s1.x);
                std::vector<int> seat_h = seat1;
                double c_h = 1e300, t_rec = 0;
                std::string phase2_txt;
                if (m.recuit_s > 0 || m.rapide) {
                    auto tr = std::chrono::steady_clock::now();
                    double budget = m.rapide ? std::max(m.recuit_s, 1.0) : m.recuit_s;
                    for (uint64_t sd = 1; sd <= (m.rapide ? 4u : 2u); ++sd) {
                        double c;
                        auto sh = anneal(m, seat1, mu_min - 1e-9, m.marge_avant - 1e-9, budget / (m.rapide ? 4.0 : 2.0), sd, &c);
                        if (c < c_h) { c_h = c; seat_h = sh; }
                    }
                    t_rec = std::chrono::duration<double>(std::chrono::steady_clock::now() - tr).count();
                }
                Solved s2;
                if (!m.rapide) {
                    std::vector<double> start = (c_h < 1e299) ? lp_vector(m, b2, seat_h) : s1.x;
                    s2 = solve(b2.lp, m.temps_max, m.gap, &start);
                    if (s2.ok) {
                        double c2 = 0;
                        for (size_t c = 0; c < b2.realism.size(); ++c) c2 += b2.realism[c] * s2.x[c];
                        if (c_h < 1e299 && c_h < c2 - 1e-6) { s2.ok = false; }   // le recuit avait fait mieux : on le garde
                    }
                }
                bool use_h = !s2.ok && c_h < 1e299;
                if (s2.ok) phase2_txt = status_txt(s2.status);
                else if (use_h) phase2_txt = m.rapide ? "recuit (mode rapide)" : "recuit (meilleur que le solveur)";
                else phase2_txt = "echec, placement de la phase 1";
                const Built& bf = s2.ok ? b2 : b1;
                std::vector<int> seat = s2.ok ? seats_of(bf, s2.x) : (use_h ? seat_h : seat1);
                std::vector<double> xf = s2.ok ? s2.x : lp_vector(m, bf, seat);
                Solved sf = s2.ok ? s2 : Solved{};
                sf.x = xf;
                sf.time = s2.ok ? s2.time : 0.0;
                double realism = 0, boites = 0, ecart = 0;
                for (size_t c = 0; c < bf.realism.size(); ++c) realism += bf.realism[c] * sf.x[c];
                for (size_t g = 0; g < m.groups.size(); ++g) {
                    double xn = 1e300, xx = -1e300, yn = 1e300, yx = -1e300;
                    for (int p : m.groups[g].second) {
                        xn = std::min(xn, m.seats[seat[p]].x); xx = std::max(xx, m.seats[seat[p]].x);
                        yn = std::min(yn, m.seats[seat[p]].y); yx = std::max(yx, m.seats[seat[p]].y);
                    }
                    boites += (xx - xn + m.w_l * (yx - yn)) / m.pitch;
                }
                for (int p = 0; p < bf.N; ++p)
                    if (m.paras[p].target >= 0) ecart += std::fabs(m.door_rank[seat[p]] - m.paras[p].target);
                json pl = json::array();
                for (int p = 0; p < bf.N; ++p)
                    pl.push_back({{"nom", m.paras[p].nom}, {"place", m.seats[seat[p]].id}, {"x", m.seats[seat[p]].x}, {"y", m.seats[seat[p]].y}, {"rang_porte", m.door_rank[seat[p]]}});
                auto st = stage_values(m, seat);
                json et = json::array();
                double av_min = 1e300;
                for (const auto& s : st) { et.push_back({{"etape", s.nom}, {"restants", s.restants}, {"masse", s.W}, {"cg", s.cg}, {"marge_avant", s.av}, {"marge_arriere", s.ar}}); av_min = std::min(av_min, s.av); }
                out = {{"ok", true}, {"objectif", "marge arriere maximale au decollage sous marge avant garantie"}, {"etapes_mode", m.etapes},
                       {"premier_groupe", fg}, {"marge_arriere_max", mu_star}, {"phase1", status_txt(s1.status)},
                       {"marge_arriere", st[0].ar}, {"marge_avant_min", m.marge_avant}, {"marge_avant_min_obtenue", av_min},
                       {"phase2", phase2_txt}, {"ecart_phase2", s2.ok ? s2.gap : 0.0},
                       {"cout_realisme", realism}, {"boites", boites}, {"ecart_sortie", ecart}, {"placement", pl}, {"etapes", et},
                       {"masse_decollage", total}, {"temps_phase1_s", s1.time}, {"temps_recuit_s", t_rec}, {"temps_phase2_s", s2.time},
                       {"cout_recuit", c_h < 1e299 ? c_h : -1.0}};
                out["temps_s"] = std::chrono::duration<double>(std::chrono::steady_clock::now() - t_start).count();
                if (!pdf_path.empty()) { draw_pdf(m, seat, st, out, pdf_path); out["pdf"] = pdf_path; }
                if (!quiet) {
                    std::cerr << "placement : " << m.paras.size() << " paras, CG decollage " << num(st[0].cg, 2) << " (marge avant " << num(st[0].av, 2)
                              << ", arriere " << num(st[0].ar, 2) << ")";
                    if (st.size() > 1) std::cerr << ", apres le premier groupe : marge avant " << num(st[1].av, 2);
                    std::cerr << " ; phase 1 " << status_txt(s1.status) << ", phase 2 " << phase2_txt << ", " << num(out["temps_s"].get<double>(), 1) << " s\n";
                }
            }
        }
    } catch (const std::exception& e) {
        out = {{"ok", false}, {"message", std::string("erreur : ") + e.what()}};
        rc = 2;
    }
    if (!out.contains("temps_s")) out["temps_s"] = std::chrono::duration<double>(std::chrono::steady_clock::now() - t_start).count();
    std::string s = out.dump(1);
    if (!out_path.empty()) { std::ofstream f(out_path); f << s << "\n"; }
    else std::cout << s << "\n";
    if (!out.value("ok", false) && !quiet) std::cerr << "placement : " << out.value("message", std::string("echec")) << "\n";
    return rc;
}
