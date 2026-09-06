'use strict';
/**
 * API REST /api/v1 (voir docs/API.md et docs/openapi.json).
 *
 *   GET  /api/v1/version                      versions et limites
 *   GET  /api/v1/openapi.json                 specification OpenAPI 3
 *   GET  /api/v1/avions                       liste des modeles (resume)
 *   GET  /api/v1/avions/{id}                  un modele complet (places, rangees, variantes, pesees...)
 *   POST /api/v1/avions/{id}/centrage         etapes de centrage d'un placement donne (calcul pur, sans solveur)
 *   POST /api/v1/avions/{id}/placement        placement optimal par le solveur a partir du modele
 *   POST /api/v1/placement                    stick brut au format du solveur (voir solveur/README.md)
 *
 * Le routeur est une fonction pure de (req, res, deps) pour etre testable sans Firebase.
 */
const path = require('node:path');
const fs = require('node:fs');
const { sanitize, InputError, LIMITS } = require('./sanitize');
const { Limiteur } = require('./protection');

const VERSION_API = '1.0';
let modules = null;
async function lib() {
  if (!modules) {
    const [av, ce] = await Promise.all([import('./lib/avions.mjs'), import('./lib/centrage.mjs')]);
    modules = { AVIONS: av.AVIONS, C: ce };
  }
  return modules;
}

class HttpError extends Error { constructor(status, message) { super(message); this.status = status; } }

function resumeAvion(a) {
  return { id: a.id, libelle: a.libelle, type: a.type, famille: a.famille, unites: a.unites, nb_places: a.places.length,
    variantes: a.variantes.map((v) => ({ id: v.id, libelle: v.libelle, mtow: v.mtow })), variante_defaut: a.variante_defaut,
    pesees: a.pesees.map((p) => ({ id: p.id, libelle: p.libelle, masse_vide: p.masse_vide, bras_vide: p.bras_vide })) };
}

function num(v, nom, opts = {}) {
  if (v == null || v === '') { if (opts.defaut !== undefined) return opts.defaut; throw new HttpError(400, `${nom} manquant`); }
  const x = Number(v);
  if (!Number.isFinite(x)) throw new HttpError(400, `${nom} : nombre attendu`);
  if (opts.min != null && x < opts.min) throw new HttpError(400, `${nom} : minimum ${opts.min}`);
  if (opts.max != null && x > opts.max) throw new HttpError(400, `${nom} : maximum ${opts.max}`);
  return x;
}

/** Corps commun des deux POST par avion : avion effectif, parametres, paras normalises. */
function preparer({ AVIONS, C }, id, corps) {
  const base = AVIONS.find((a) => a.id === id);
  if (!base) throw new HttpError(404, `avion inconnu : ${id} (voir GET /api/v1/avions)`);
  if (!corps || typeof corps !== 'object' || Array.isArray(corps)) throw new HttpError(400, 'objet JSON attendu');
  const varianteId = corps.variante || base.variante_defaut;
  if (!base.variantes.some((v) => v.id === varianteId)) throw new HttpError(400, `variante inconnue : ${varianteId}`);
  const peseeId = corps.pesee || base.pesees[0].id;
  if (!base.pesees.some((p) => p.id === peseeId)) throw new HttpError(400, `pesee inconnue : ${peseeId}`);
  let surcharge = null;
  if (corps.enveloppe) {
    const n = C.normaliserEnveloppe(corps.enveloppe);
    if (!n) throw new HttpError(400, 'enveloppe : avant et arriere doivent contenir des couples [masse, bras]');
    surcharge = { mtow: corps.enveloppe.mtow != null ? num(corps.enveloppe.mtow, 'enveloppe.mtow', { min: 1 }) : undefined, enveloppe: n };
  }
  const avion = C.appliquerVariante(base, varianteId, surcharge, peseeId);
  if (corps.masse_vide != null) avion.masse_vide = num(corps.masse_vide, 'masse_vide', { min: 1 });
  if (corps.bras_vide != null) avion.bras_vide = num(corps.bras_vide, 'bras_vide');
  const params = {
    piloteKg: num(corps.pilote_kg, 'pilote_kg', { defaut: avion.pilote.masse_kg_defaut, min: 30, max: 200 }),
    carburant: num(corps.carburant, 'carburant', { defaut: 0, min: 0 }),
    porteOuverte: !!corps.porte_ouverte,
  };
  if (!Array.isArray(corps.paras) || corps.paras.length === 0) throw new HttpError(400, 'paras : liste non vide attendue');
  if (corps.paras.length > LIMITS.maxParas) throw new HttpError(400, `paras : au plus ${LIMITS.maxParas}`);
  const ids = new Set(avion.places.map((p) => p.id));
  const noms = new Set();
  const paras = corps.paras.map((p, i) => {
    if (!p || typeof p !== 'object') throw new HttpError(400, `paras[${i}] : objet attendu`);
    const nom = String(p.nom || `P${i + 1}`);
    if (noms.has(nom)) throw new HttpError(400, `paras : nom en double ${nom}`);
    noms.add(nom);
    const q = { nom, masseKg: num(p.masse_kg, `paras[${i}].masse_kg`, { min: 20, max: 250 }), groupe: p.groupe ? String(p.groupe) : '',
      sortie: p.sortie == null || p.sortie === '' ? '' : num(p.sortie, `paras[${i}].sortie`, { min: 1 }), tandem: p.tandem ? String(p.tandem) : '',
      role: p.role === 'passager' ? 'passager' : (p.tandem ? 'porteur' : ''), interdit: Array.isArray(p.interdit) ? p.interdit.map(String) : [],
      verrou: null, place: null, pos: null };
    if (p.devant_de) q.devant_de = String(p.devant_de);
    if (p.place != null) { if (!ids.has(p.place)) throw new HttpError(400, `paras[${i}].place inconnue : ${p.place}`); q.place = p.place; }
    if (p.pos && p.pos.x != null) q.pos = { x: num(p.pos.x, `paras[${i}].pos.x`), y: num(p.pos.y, `paras[${i}].pos.y`, { defaut: 0 }) };
    if (p.verrou === true) q.verrou = q.place || (q.pos ? 'libre' : null);
    else if (p.verrou) { if (p.verrou !== 'libre' && !ids.has(p.verrou)) throw new HttpError(400, `paras[${i}].verrou inconnu : ${p.verrou}`); q.verrou = p.verrou; if (p.verrou !== 'libre') q.place = p.verrou; }
    return q;
  });
  const mode = corps.options && corps.options.etapes === 'toutes' ? 'toutes' : 'premier_groupe';
  return { avion, base, varianteId, peseeId, params, paras, mode };
}

function etapesDe(C, avion, params, paras, mode) {
  const ps = paras.map((p) => ({ ...p, sortie: p.sortie === '' ? null : p.sortie }));
  const { etapes, nonPlaces } = C.etapes(avion, params, ps, avion.places, mode);
  return { etapes: etapes.map((e) => ({ etape: e.etape, rang: e.rang === Infinity ? null : (e.rang ?? null), paras_a_bord: e.restants, masse: e.masse, cg: e.cg, pct_mac: e.mac,
    limite_avant: e.avant, limite_arriere: e.arriere, marge_avant: e.margeAvant, marge_arriere: e.margeArriere, statut: e.statut })),
    bilan: C.bilan(etapes), paras_sans_place: nonPlaces };
}

function enteteAvion(avion, varianteId, peseeId) {
  return { id: avion.id, libelle: avion.libelle, variante: varianteId, pesee: peseeId, unites: avion.unites, mtow: avion.mtow, masse_vide: avion.masse_vide, bras_vide: avion.bras_vide, enveloppe: avion.enveloppe };
}

/**
 * Traite une requete. deps : { runSolver(args, stdin) -> {code, stdout, stderr}, limiteur, ip }.
 * Repond via res.status(n).json(obj) ; retourne une promesse.
 */
async function handleApi(req, res, deps) {
  res.set('Cache-Control', 'no-store');
  res.set('Access-Control-Allow-Origin', '*');
  res.set('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.set('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') { res.status(204).send(''); return; }
  const sub = req.path.replace(/^\/api\/v1/, '').replace(/^\/+|\/+$/g, '');
  const parts = sub ? sub.split('/') : [];
  try {
    const { AVIONS, C } = await lib();
    // ---- GET
    if (req.method === 'GET') {
      if (parts.length === 0 || sub === 'version') {
        const r = await deps.runSolver(['--version']);
        res.status(200).json({ ok: true, api: VERSION_API, solveur: (r.stdout || '').trim(), limites: { ...LIMITS, ...deps.limiteur.o }, documentation: 'https://github.com/juleshumbert/centrage-ceps/blob/main/docs/API.md' });
        return;
      }
      if (sub === 'openapi.json') {
        const p = path.join(__dirname, 'lib', 'openapi.json');
        if (!fs.existsSync(p)) throw new HttpError(404, 'specification absente');
        res.set('Content-Type', 'application/json'); res.status(200).send(fs.readFileSync(p, 'utf8')); return;
      }
      if (parts[0] === 'avions' && parts.length === 1) { res.status(200).json({ ok: true, avions: AVIONS.map(resumeAvion) }); return; }
      if (parts[0] === 'avions' && parts.length === 2) {
        const a = AVIONS.find((x) => x.id === parts[1]);
        if (!a) throw new HttpError(404, `avion inconnu : ${parts[1]}`);
        res.status(200).json({ ok: true, avion: a }); return;
      }
      throw new HttpError(404, 'route inconnue');
    }
    if (req.method !== 'POST') throw new HttpError(405, 'methode non autorisee');
    // ---- POST : corps JSON
    const raw = req.rawBody;
    if (!raw || raw.length === 0) throw new HttpError(400, 'corps JSON attendu');
    if (raw.length > LIMITS.maxBodyBytes) throw new HttpError(413, 'corps trop volumineux');
    let corps;
    try { corps = JSON.parse(raw.toString('utf8')); } catch { throw new HttpError(400, 'JSON invalide'); }

    if (parts[0] === 'avions' && parts.length === 3 && parts[2] === 'centrage') {
      const { avion, varianteId, peseeId, params, paras, mode } = preparer({ AVIONS, C }, parts[1], corps);
      res.status(200).json({ ok: true, avion: enteteAvion(avion, varianteId, peseeId), parametres: params, ...etapesDe(C, avion, params, paras, mode) });
      return;
    }
    let stick, contexte = null;
    if (parts[0] === 'avions' && parts.length === 3 && parts[2] === 'placement') {
      contexte = preparer({ AVIONS, C }, parts[1], corps);
      const options = { ...(corps.options || {}) };
      stick = C.stickPourSolveur(contexte.avion, contexte.params, contexte.paras, options);
    } else if (sub === 'placement') {
      stick = corps;
    } else throw new HttpError(404, 'route inconnue');
    try { stick = sanitize(stick); } catch (e) { throw new HttpError(400, e instanceof InputError ? e.message : 'stick invalide'); }

    const cle = Limiteur.empreinte(stick);
    let out = deps.limiteur.cacheLire(cle);
    if (out) res.set('X-Cache', 'hit');
    else {
      const adm = deps.limiteur.admettre(deps.ip);
      if (!adm.ok) { res.set('Retry-After', String(adm.retryAfterS)); throw new HttpError(429, `${adm.raison}, reessaie dans ${adm.retryAfterS} s`); }
      if (!deps.limiteur.reserver()) { res.set('Retry-After', '5'); throw new HttpError(429, 'solveur occupe, reessaie dans quelques secondes'); }
      const t0 = Date.now(); let r;
      try { r = await deps.runSolver(['-', '--silencieux'], JSON.stringify(stick)); } finally { deps.limiteur.liberer(); }
      if (r.code === 124) throw new HttpError(504, 'solveur interrompu (temps depasse)');
      try { out = JSON.parse(r.stdout); } catch { out = null; }
      if (!out) throw new HttpError(r.code === 2 ? 400 : 500, r.code === 2 ? `entree refusee par le solveur : ${(r.stderr || '').slice(0, 300)}` : 'erreur du solveur');
      out.temps_serveur_ms = Date.now() - t0;
      deps.limiteur.cacheEcrire(cle, out);
    }
    if (!contexte) { res.status(200).json(out); return; }
    // reponse enrichie : placement applique au modele, etapes recalculees
    const { avion, varianteId, peseeId, params, paras, mode } = contexte;
    const pl = out.placement || out.placement_au_mieux || [];
    const places = new Map(stick.places.map((p) => [p.id, p]));
    for (const p of paras) {
      const q = pl.find((x) => x.nom === p.nom);
      if (!q) { p.place = null; }
      else if (q.place === `L-${p.nom}`) { p.place = null; }
      else { p.place = q.place; p.pos = null; }
    }
    res.status(200).json({ ok: !!out.ok, avion: enteteAvion(avion, varianteId, peseeId), parametres: params, solveur: out,
      placement: paras.map((p) => { const s = p.place ? places.get(p.place) : null; return { nom: p.nom, masse_kg: p.masseKg, place: p.place, x: s ? s.x : (p.pos ? p.pos.x : null), y: s ? s.y : (p.pos ? p.pos.y : null), verrou: p.verrou || null }; }),
      ...etapesDe(C, avion, params, paras, mode) });
  } catch (e) {
    if (e instanceof HttpError) { res.status(e.status).json({ ok: false, message: e.message }); return; }
    console.error(e); res.status(500).json({ ok: false, message: 'erreur interne' });
  }
}

module.exports = { handleApi, preparer, resumeAvion, HttpError, VERSION_API };
