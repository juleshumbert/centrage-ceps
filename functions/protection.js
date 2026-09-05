'use strict';
/**
 * Protection de la fonction sans authentification : le solveur est couteux (CPU), l'URL est
 * publique. Trois garde-fous, tous en memoire d'instance (chaque instance Cloud Run a les
 * siens ; `maxInstances` borne le total) :
 *   - limiteur par adresse IP : fenetre glissante, N requetes par minute et par jour ;
 *   - semaphore de calculs simultanes par instance (au-dela : 429 tout de suite, pas de file) ;
 *   - cache des resultats par empreinte du stick (une meme demande repetee ne recalcule pas).
 * Logique pure, testee dans protection.test.js.
 */
const crypto = require('node:crypto');

const DEFAUTS = Object.freeze({
  parMinute: 12,          // requetes de calcul par IP et par minute
  parJour: 300,           // par IP et par jour (une journee de largage = quelques dizaines de calculs)
  simultanes: 2,          // calculs en parallele par instance
  cacheTaille: 200,
  cacheTtlMs: 6 * 60 * 60 * 1000,
  ipsMax: 5000,           // taille maximale de la table des IP (eviction des plus anciennes)
});

class Limiteur {
  constructor(opts = {}, now = Date.now) {
    this.o = { ...DEFAUTS, ...opts }; this.now = now;
    this.ips = new Map();          // ip -> [timestamps]
    this.enCours = 0;
    this.cache = new Map();        // empreinte -> {t, valeur}
  }

  /** Verifie et consomme un jeton pour l'IP. Retourne {ok, raison, retryAfterS}. */
  admettre(ip) {
    const t = this.now();
    let hist = this.ips.get(ip);
    if (!hist) {
      if (this.ips.size >= this.o.ipsMax) this.ips.delete(this.ips.keys().next().value);
      hist = []; this.ips.set(ip, hist);
    }
    const jour = t - 24 * 3600 * 1000, minute = t - 60 * 1000;
    while (hist.length && hist[0] < jour) hist.shift();
    const recents = hist.filter((x) => x >= minute).length;
    if (recents >= this.o.parMinute) return { ok: false, raison: 'trop de requetes (par minute)', retryAfterS: Math.ceil((hist[hist.length - this.o.parMinute] + 60 * 1000 - t) / 1000) || 1 };
    if (hist.length >= this.o.parJour) return { ok: false, raison: 'quota journalier atteint', retryAfterS: 3600 };
    hist.push(t);
    // la table bouge : remettre l'IP en fin de Map pour une eviction FIFO approximative
    this.ips.delete(ip); this.ips.set(ip, hist);
    return { ok: true };
  }

  /** Semaphore : reserve un slot de calcul ou refuse. */
  reserver() {
    if (this.enCours >= this.o.simultanes) return false;
    this.enCours += 1; return true;
  }
  liberer() { this.enCours = Math.max(0, this.enCours - 1); }

  static empreinte(objet) {
    return crypto.createHash('sha256').update(JSON.stringify(objet)).digest('hex').slice(0, 32);
  }
  cacheLire(cle) {
    const e = this.cache.get(cle);
    if (!e) return null;
    if (this.now() - e.t > this.o.cacheTtlMs) { this.cache.delete(cle); return null; }
    return e.valeur;
  }
  cacheEcrire(cle, valeur) {
    if (this.cache.size >= this.o.cacheTaille) this.cache.delete(this.cache.keys().next().value);
    this.cache.set(cle, { t: this.now(), valeur });
  }
}

/** Origine autorisee ? (defense legere contre les appels depuis d'autres sites ; un script direct passe, le limiteur prend le relais) */
function origineAutorisee(origin, referer, autorisees) {
  const src = origin || (referer ? referer.replace(/^(https?:\/\/[^/]+).*$/, '$1') : '');
  if (!src) return true;   // curl, applications natives : pas d'en-tete, on laisse le limiteur decider
  return autorisees.some((a) => src === a || (a.startsWith('*.') && src.endsWith(a.slice(1))));
}

module.exports = { Limiteur, origineAutorisee, DEFAUTS };
