'use strict';
/**
 * /api/placement : execute le solveur C++ `placement` (HiGHS embarque) sur un stick.
 *
 * Le binaire Linux x86_64 statique est construit par la CI (solveur/, PLACEMENT_STATIC=1)
 * et copie dans functions/bin/placement avant `firebase deploy`. La fonction lui passe
 * le JSON sur l'entree standard (`placement - --silencieux`) et renvoie sa sortie JSON.
 *
 * Acces : public, sans authentification. Protection contre l'abus (protection.js) :
 * origine du site, limiteur par IP (minute et jour), semaphore de calculs simultanes par
 * instance, cache des resultats identiques ; plus `maxInstances`, `concurrency` et le
 * plafond de temps du solveur (sanitize.js). Le cout maximal est donc borne par
 * maxInstances x simultanes x temps max.
 *
 * Routes (rewrite Hosting /api/placement{,/**} -> placement) :
 *   POST /api/placement            corps = stick JSON (voir solveur/README.md), reponse = resultat JSON
 *   GET  /api/placement/version    version du binaire et limites (sante)
 */
const { onRequest } = require('firebase-functions/v2/https');
const { setGlobalOptions } = require('firebase-functions/v2');
const logger = require('firebase-functions/logger');
const { execFile } = require('node:child_process');
const fs = require('node:fs');
const path = require('node:path');
const { sanitize, InputError, LIMITS } = require('./sanitize');
const { Limiteur, origineAutorisee, DEFAUTS } = require('./protection');

setGlobalOptions({ region: 'europe-west1', maxInstances: 3 });

const BIN = path.join(__dirname, 'bin', 'placement');
const SOLVER_TIMEOUT_MS = 50_000;   // > 2 phases x 10 s + recuit, < timeoutSeconds
const ORIGINES = ['https://ceps09-centrage.web.app', 'https://ceps09-centrage.firebaseapp.com', '*.ceps09.com', 'http://localhost:5000', 'http://127.0.0.1:5000'];
const limiteur = new Limiteur();

function ensureExecutable() {
  try { fs.chmodSync(BIN, 0o755); } catch (e) { logger.warn('chmod du binaire impossible', e.message); }
}

function runSolver(args, stdinText) {
  ensureExecutable();
  return new Promise((resolve) => {
    const child = execFile(BIN, args, { timeout: SOLVER_TIMEOUT_MS, maxBuffer: 8 * 1024 * 1024, killSignal: 'SIGKILL' },
      (err, stdout, stderr) => resolve({ code: err ? (err.killed ? 124 : err.code) : 0, stdout, stderr, err }));
    if (stdinText != null) { child.stdin.on('error', () => {}); child.stdin.end(stdinText); }
  });
}

function ipDe(req) {
  const xff = req.get('x-forwarded-for');
  return (xff ? xff.split(',')[0].trim() : req.ip) || 'inconnue';
}

exports.placement = onRequest({ cors: false, timeoutSeconds: 60, memory: '1GiB', cpu: 1, concurrency: 4 }, async (req, res) => {
  res.set('Cache-Control', 'no-store');
  const sub = req.path.replace(/^\/api\/placement/, '').replace(/^\/+|\/+$/g, '');

  if (req.method === 'GET' && sub === 'version') {
    const r = await runSolver(['--version']);
    res.status(r.code === 0 ? 200 : 500).json({ ok: r.code === 0, version: (r.stdout || '').trim(), limites: { ...LIMITS, ...DEFAUTS } });
    return;
  }
  if (req.method !== 'POST' || sub) { res.status(405).json({ ok: false, message: 'POST /api/placement attendu' }); return; }

  if (!origineAutorisee(req.get('origin'), req.get('referer'), ORIGINES)) {
    res.status(403).json({ ok: false, message: 'origine non autorisee' }); return;
  }
  const raw = req.rawBody;
  if (!raw || raw.length === 0) { res.status(400).json({ ok: false, message: 'corps JSON attendu' }); return; }
  if (raw.length > LIMITS.maxBodyBytes) { res.status(413).json({ ok: false, message: 'corps trop volumineux' }); return; }

  let stick;
  try { stick = sanitize(JSON.parse(raw.toString('utf8'))); }
  catch (e) {
    const msg = e instanceof InputError ? e.message : 'JSON invalide';
    res.status(400).json({ ok: false, message: msg }); return;
  }

  const ip = ipDe(req);
  const cle = Limiteur.empreinte(stick);
  const enCache = limiteur.cacheLire(cle);
  if (enCache) { res.set('X-Cache', 'hit'); res.status(200).json(enCache); return; }

  const adm = limiteur.admettre(ip);
  if (!adm.ok) {
    res.set('Retry-After', String(adm.retryAfterS));
    res.status(429).json({ ok: false, message: adm.raison + ', reessaie dans ' + adm.retryAfterS + ' s' }); return;
  }
  if (!limiteur.reserver()) {
    res.set('Retry-After', '5');
    res.status(429).json({ ok: false, message: 'solveur occupe, reessaie dans quelques secondes' }); return;
  }

  const t0 = Date.now();
  let r;
  try { r = await runSolver(['-', '--silencieux'], JSON.stringify(stick)); }
  finally { limiteur.liberer(); }
  const ms = Date.now() - t0;
  logger.info('placement', { paras: stick.paras.length, code: r.code, ms });

  if (r.code === 124) { res.status(504).json({ ok: false, message: 'solveur interrompu (temps depasse)' }); return; }
  let out = null;
  try { out = JSON.parse(r.stdout); } catch { /* pas de JSON : erreur du binaire */ }
  if (!out) {
    logger.error('sortie solveur illisible', { code: r.code, stderr: (r.stderr || '').slice(0, 2000), err: r.err && r.err.message });
    res.status(r.code === 2 ? 400 : 500).json({ ok: false, message: r.code === 2 ? 'entree refusee par le solveur' : 'erreur du solveur', detail: (r.stderr || '').slice(0, 500) });
    return;
  }
  out.temps_serveur_ms = ms;
  limiteur.cacheEcrire(cle, out);
  // code 0 = placement rendu, 1 = aucun placement valide (le JSON explique) : les deux sont des reponses normales.
  res.status(200).json(out);
});
