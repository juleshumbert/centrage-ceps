'use strict';
/**
 * Garde-fous sur l'entree du solveur, cote serveur : tailles bornees, options de
 * temps plafonnees (le solveur tourne dans une Cloud Function facturee au temps CPU).
 * Logique pure, testee dans sanitize.test.js.
 */
const LIMITS = Object.freeze({
  maxParas: 30,
  maxPlaces: 40,
  maxBodyBytes: 256 * 1024,
  tempsMin: 0.5,
  tempsMax: 10,      // par phase ; la fonction a 60 s de timeout
  recuitMax: 5,
});

class InputError extends Error {}

function num(v, name) {
  const x = Number(v);
  if (!Number.isFinite(x)) throw new InputError(`${name} : nombre attendu`);
  return x;
}

/** Valide la forme du stick et renvoie une copie avec les options plafonnees. */
function sanitize(input) {
  if (!input || typeof input !== 'object' || Array.isArray(input)) throw new InputError('objet JSON attendu');
  const out = { ...input };
  if (!out.avion || typeof out.avion !== 'object') throw new InputError('avion manquant');
  if (!out.enveloppe || typeof out.enveloppe !== 'object') throw new InputError('enveloppe manquante');
  if (!Array.isArray(out.places) || out.places.length === 0) throw new InputError('places manquantes');
  if (out.places.length > LIMITS.maxPlaces) throw new InputError(`trop de places (max ${LIMITS.maxPlaces})`);
  if (!Array.isArray(out.paras) || out.paras.length === 0) throw new InputError('paras manquants');
  if (out.paras.length > LIMITS.maxParas) throw new InputError(`trop de paras (max ${LIMITS.maxParas})`);
  if (out.paras.length > out.places.length) throw new InputError('plus de paras que de places');
  for (const p of out.places) {
    if (!p || typeof p.id !== 'string' || !p.id) throw new InputError('place sans id');
    num(p.x, `place ${p.id} x`); num(p.y, `place ${p.id} y`);
  }
  for (const p of out.paras) {
    if (!p || typeof p.nom !== 'string' || !p.nom) throw new InputError('para sans nom');
    if (num(p.masse, `para ${p.nom} masse`) <= 0) throw new InputError(`para ${p.nom} : masse positive attendue`);
  }
  const o = { ...(out.options && typeof out.options === 'object' ? out.options : {}) };
  const clamp = (v, lo, hi, d) => {
    const x = Number(v);
    return Number.isFinite(x) ? Math.min(hi, Math.max(lo, x)) : d;
  };
  o.temps_max_s = clamp(o.temps_max_s, LIMITS.tempsMin, LIMITS.tempsMax, 10);
  o.recuit_s = clamp(o.recuit_s, 0, LIMITS.recuitMax, 1);
  out.options = o;
  return out;
}

module.exports = { sanitize, InputError, LIMITS };
