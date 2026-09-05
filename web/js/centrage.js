// centrage.js : moteur masse et centrage cote client, pur (aucun DOM), unites natives de
// l'avion (lb/in ou kg/m). Memes formules que le solveur : moment = masse x bras, limites
// avant et arriere interpolees lineairement en fonction de la masse.

export const LBS_PAR_KG = 2.20462;

/** Interpolation lineaire sur une ligne brisee [[masse, valeur], ...] triee par masse, bornee aux extremites. */
export function interp(points, w) {
  if (!points || points.length === 0) return NaN;
  if (w <= points[0][0]) return points[0][1];
  const n = points.length;
  if (w >= points[n - 1][0]) return points[n - 1][1];
  for (let i = 1; i < n; i++) {
    const [w0, v0] = points[i - 1], [w1, v1] = points[i];
    if (w <= w1) return w1 === w0 ? v1 : v0 + (v1 - v0) * (w - w0) / (w1 - w0);
  }
  return points[n - 1][1];
}

/** Masse d'un para en unite native de l'avion depuis des kg. */
export function masseNative(avion, kg) {
  return kg / avion.kg_par_unite_masse;
}

/** Masse de carburant en unite de masse native depuis la quantite saisie (lb, ou litres pour le PC-6). */
export function carburantMasse(avion, quantite) {
  const q = Number(quantite) || 0;
  if (avion.unites.carburant === 'L') return q * avion.carburant.kg_par_litre;
  return q;
}

/** Bras du carburant a la masse donnee, lu dans la table [[masse, bras], ...]. */
export function carburantBras(avion, masse) {
  const t = avion.carburant.table;
  return masse <= 0 ? t[0][1] : interp(t, masse);
}

export function cgVersMac(avion, cg) {
  return (cg - avion.mac.lemac) / avion.mac.longueur * 100;
}

/**
 * Etat masse / CG d'une liste de charges [{masse, bras}] ajoutees a l'avion vide.
 * Retourne {masse, moment, cg, mac, avant, arriere, margeAvant, margeArriere, statut}.
 */
export function etat(avion, charges) {
  let masse = avion.masse_vide, moment = avion.masse_vide * avion.bras_vide;
  for (const c of charges) { masse += c.masse; moment += c.masse * c.bras; }
  const cg = moment / masse;
  const avant = interp(avion.enveloppe.avant, masse);
  const arriere = interp(avion.enveloppe.arriere, masse);
  const margeAvant = cg - avant, margeArriere = arriere - cg;
  let statut = 'ok';
  if (masse > avion.mtow + 1e-9) statut = 'mtow';
  else if (margeAvant < -1e-9) statut = 'avant';
  else if (margeArriere < -1e-9) statut = 'arriere';
  return { masse, moment, cg, mac: cgVersMac(avion, cg), avant, arriere, margeAvant, margeArriere, statut };
}

/**
 * Etapes du largage pour un placement donne.
 *  avion, params = {piloteKg, carburant}, paras = [{nom, masseKg, sortie, place}], places = [{id, x, y}]
 *  mode 'premier_groupe' : decollage puis apres la sortie des paras de plus petit rang ;
 *  mode 'toutes' : decollage puis apres chaque rang de sortie.
 * Les paras sans place sont ignores (comptes dans `nonPlaces`).
 */
export function etapes(avion, params, paras, places, mode = 'premier_groupe') {
  const brasPlace = new Map(places.map((p) => [p.id, p.x]));
  const fuelMasse = carburantMasse(avion, params.carburant);
  const fixes = [
    { masse: masseNative(avion, params.piloteKg), bras: avion.pilote.bras },
    { masse: fuelMasse, bras: carburantBras(avion, fuelMasse) },
  ];
  const brasDe = (p) => (p.pos && Number.isFinite(p.pos.x) ? p.pos.x : brasPlace.get(p.place));
  const places_ = paras.filter((p) => Number.isFinite(brasDe(p)));
  const nonPlaces = paras.length - places_.length;
  const charge = (liste) => liste.map((p) => ({ masse: masseNative(avion, p.masseKg), bras: brasDe(p) }));
  const rangs = [...new Set(places_.map((p) => (p.sortie == null || p.sortie === '' ? Infinity : Number(p.sortie))))].sort((a, b) => a - b);
  const out = [{ etape: 'decollage', restants: places_.length, ...etat(avion, [...fixes, ...charge(places_)]) }];
  if (places_.length === 0) return { etapes: out, nonPlaces };
  const seuils = mode === 'toutes' ? rangs : rangs.slice(0, 1);
  for (const r of seuils) {
    const restants = places_.filter((p) => (p.sortie == null || p.sortie === '' ? Infinity : Number(p.sortie)) > r);
    const sortis = places_.length - restants.length;
    out.push({ etape: `apres la sortie du rang ${r === Infinity ? 'final' : r} (${sortis} sorti(s))`, rang: r, restants: restants.length,
      ...etat(avion, [...fixes, ...charge(restants)]) });
  }
  return { etapes: out, nonPlaces };
}

/** Pire statut sur toutes les etapes et marges minimales. */
export function bilan(etapesListe) {
  const ordre = { ok: 0, arriere: 1, avant: 2, mtow: 3 };
  let statut = 'ok', margeAvant = Infinity, margeArriere = Infinity;
  for (const e of etapesListe) {
    if (ordre[e.statut] > ordre[statut]) statut = e.statut;
    margeAvant = Math.min(margeAvant, e.margeAvant);
    margeArriere = Math.min(margeArriere, e.margeArriere);
  }
  return { statut, margeAvant, margeArriere };
}

/**
 * Construit le stick JSON attendu par le solveur (voir solveur/README.md).
 *  paras : [{nom, masseKg, groupe, sortie, tandem, role, verrou (id de place ou null)}]
 */
export function stickPourSolveur(avion, params, paras, options = {}) {
  const fuelMasse = carburantMasse(avion, params.carburant);
  const places = avion.places.map((p) => ({ ...p }));
  for (const p of paras) {   // para verrouille sur une position libre : place virtuelle a ses coordonnees
    if (p.verrou === 'libre' && p.pos && Number.isFinite(p.pos.x)) {
      places.push({ id: `L-${p.nom}`, x: Math.round(p.pos.x * 1000) / 1000, y: Math.round((p.pos.y || 0) * 1000) / 1000, libre: true });
    }
  }
  const ids = places.map((p) => p.id);
  return {
    unites: { masse: avion.unites.masse, bras: avion.unites.bras },
    avion: { immat: avion.immat, masse_vide: avion.masse_vide, bras_vide: avion.bras_vide },
    enveloppe: { avant: avion.enveloppe.avant, arriere: avion.enveloppe.arriere, mtow: avion.mtow },
    carburant: { masse: fuelMasse, bras: carburantBras(avion, fuelMasse) },
    pilote: { masse: masseNative(avion, params.piloteKg), bras: avion.pilote.bras },
    porte: { x: avion.porte.x, y: avion.porte.y },
    places,
    paras: paras.map((p) => {
      const q = { nom: p.nom, masse: Math.round(masseNative(avion, p.masseKg) * 1000) / 1000 };
      if (p.groupe) q.groupe = p.groupe;
      if (p.sortie != null && p.sortie !== '') q.sortie = Number(p.sortie);
      if (p.tandem) { q.tandem = p.tandem; q.role = p.role || 'porteur'; }
      if (p.devant_de) q.devant_de = p.devant_de;
      const interdit = [...(p.interdit || [])];
      const cible = p.verrou === 'libre' ? `L-${p.nom}` : p.verrou;
      if (cible && ids.includes(cible)) interdit.push(...ids.filter((id) => id !== cible));
      if (interdit.length) q.interdit = [...new Set(interdit)];
      return q;
    }),
    options: { etapes: 'premier_groupe', marge_avant_min: 0.5, tolerance_marge: 0.25, groupes_ordonnes: false, temps_max_s: 10, ...options },
  };
}

/**
 * Avion effectif : variante choisie (MTOW et enveloppe) puis surcharge eventuelle
 * {mtow, enveloppe} editee dans l'application. Ne modifie pas l'objet d'origine.
 */
export function appliquerVariante(avion, varianteId, surcharge) {
  const v = (avion.variantes || []).find((x) => x.id === varianteId) || (avion.variantes || [])[0];
  const out = { ...avion };
  if (v) { out.mtow = v.mtow; out.enveloppe = JSON.parse(JSON.stringify(v.enveloppe)); out.variante = v; }
  if (surcharge) {
    if (Number.isFinite(surcharge.mtow)) out.mtow = surcharge.mtow;
    if (surcharge.enveloppe) out.enveloppe = JSON.parse(JSON.stringify(surcharge.enveloppe));
  }
  return out;
}

/** Nettoie une enveloppe editee : nombres, tri par masse, au moins deux points par limite. */
export function normaliserEnveloppe(env) {
  const clean = (pts) => (pts || []).map((p) => [Number(p[0]), Number(p[1])]).filter((p) => Number.isFinite(p[0]) && Number.isFinite(p[1])).sort((a, b) => a[0] - b[0]);
  const avant = clean(env.avant), arriere = clean(env.arriere);
  if (avant.length < 1 || arriere.length < 1) return null;
  return { avant, arriere };
}
