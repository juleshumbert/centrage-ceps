'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { handleApi } = require('./api');
const { Limiteur } = require('./protection');

// faux solveur : place les paras dans l'ordre des places, ou repond selon l'option de test
function fauxSolveur(args, stdin) {
  if (args[0] === '--version') return { code: 0, stdout: 'placement test\n', stderr: '' };
  const stick = JSON.parse(stdin);
  const libres = stick.places.filter((p) => !p.libre);
  const placement = stick.paras.map((p, i) => { const forced = p.interdit && p.interdit.length === stick.places.length - 1 ? stick.places.find((s) => !p.interdit.includes(s.id)) : null; const s = forced || libres[i]; return { nom: p.nom, place: s.id, x: s.x, y: s.y, rang_porte: i }; });
  return { code: 0, stdout: JSON.stringify({ ok: true, placement, phase1: 'optimum', phase2: 'optimum', marge_arriere_max: 1, etapes: [] }), stderr: '' };
}
function req(method, p, body) { const raw = body == null ? null : Buffer.from(JSON.stringify(body)); return { method, path: p, rawBody: raw, get: () => undefined }; }
function res() { const r = { code: 200, headers: {}, body: null, set(k, v) { this.headers[k] = v; }, status(c) { this.code = c; return this; }, json(o) { this.body = o; return this; }, send(s) { this.body = s; return this; } }; return r; }
const deps = () => ({ runSolver: async (a, s) => fauxSolveur(a, s), limiteur: new Limiteur(), ip: '1.2.3.4' });

test('GET /avions et /avions/{id}', async () => {
  const r = res(); await handleApi(req('GET', '/api/v1/avions'), r, deps());
  assert.equal(r.code, 200); assert.ok(r.body.avions.length >= 5); assert.ok(r.body.avions.some((a) => a.id === 'c208b'));
  assert.equal(r.headers['Access-Control-Allow-Origin'], '*');
  const r2 = res(); await handleApi(req('GET', '/api/v1/avions/pc6'), r2, deps());
  assert.equal(r2.code, 200); assert.equal(r2.body.avion.unites.bras, 'm'); assert.ok(r2.body.avion.places.length === 10);
  const r3 = res(); await handleApi(req('GET', '/api/v1/avions/inconnu'), r3, deps()); assert.equal(r3.code, 404);
});

test('GET /version et /openapi.json', async () => {
  const r = res(); await handleApi(req('GET', '/api/v1/version'), r, deps());
  assert.equal(r.code, 200); assert.equal(r.body.solveur, 'placement test'); assert.equal(r.body.limites.parMinute, 12);
  const r2 = res(); await handleApi(req('GET', '/api/v1/openapi.json'), r2, deps());
  assert.equal(r2.code, 200); assert.equal(JSON.parse(r2.body).openapi, '3.0.3');
});

test('POST /avions/c208b/centrage : etapes coherentes avec le solveur de reference', async () => {
  const stick = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'solveur', 'exemples', 'exemple_stick.json')));
  const ref = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'solveur', 'exemples', 'exemple_stick_resultat.json')));
  const paras = stick.paras.map((p) => ({ nom: p.nom, masse_kg: p.masse / 2.20462, sortie: p.sortie, place: ref.placement.find((q) => q.nom === p.nom).place }));
  const body = { variante: 'ape2', pesee: 'A', pilote_kg: stick.pilote.masse / 2.20462, carburant: 900, paras };
  const r = res(); await handleApi(req('POST', '/api/v1/avions/c208b/centrage', body), r, deps());
  assert.equal(r.code, 200, JSON.stringify(r.body));
  assert.equal(r.body.etapes.length, 2);
  // meme avion, meme pesee (4890 lb a 188.99 in), meme carburant : le CG de decollage du solveur est retrouve a 0.05 in pres
  assert.ok(Math.abs(r.body.etapes[0].cg - ref.etapes[0].cg) < 0.05, `${r.body.etapes[0].cg} vs ${ref.etapes[0].cg}`);
  // avec la limite avant du STC APE II (200.23 in a 9062 lb) ce placement, optimise avec l'ancienne enveloppe des
  // planches, est legerement trop avant : le calcul doit le dire
  assert.equal(r.body.bilan.statut, 'avant');
  assert.ok(r.body.etapes[0].marge_avant < 0 && r.body.etapes[0].marge_avant > -1.2, String(r.body.etapes[0].marge_avant));
});

test('POST /avions/{id}/placement : stick construit, verrou respecte, etapes renvoyees', async () => {
  const body = { pilote_kg: 80, carburant: 800, paras: [{ nom: 'A', masse_kg: 90, sortie: 1, verrou: 'D3' }, { nom: 'B', masse_kg: 85, sortie: 2 }, { nom: 'C', masse_kg: 95, sortie: 2, pos: { x: 250, y: -16 }, verrou: 'libre' }] };
  const r = res(); await handleApi(req('POST', '/api/v1/avions/c208b/placement', body), r, deps());
  assert.equal(r.code, 200, JSON.stringify(r.body));
  assert.equal(r.body.ok, true);
  assert.equal(r.body.placement.find((p) => p.nom === 'A').place, 'D3');
  assert.equal(r.body.placement.find((p) => p.nom === 'C').x, 250);
  assert.equal(r.body.etapes[0].paras_a_bord, 3);
  assert.equal(r.body.avion.mtow, 9062);
  const r2 = res(); await handleApi(req('POST', '/api/v1/avions/c208b/placement', body), r2, deps()); // meme demande, meme limiteur ? non : nouveau limiteur, pas de cache
  assert.equal(r2.code, 200);
});

test('erreurs : corps invalide, para trop lourd, variante inconnue, limite par minute', async () => {
  let r = res(); await handleApi(req('POST', '/api/v1/avions/c208b/placement', { paras: [] }), r, deps()); assert.equal(r.code, 400);
  r = res(); await handleApi(req('POST', '/api/v1/avions/c208b/centrage', { paras: [{ masse_kg: 500 }] }), r, deps()); assert.equal(r.code, 400);
  r = res(); await handleApi(req('POST', '/api/v1/avions/c208b/centrage', { variante: 'x', paras: [{ masse_kg: 90 }] }), r, deps()); assert.equal(r.code, 400);
  const d = deps(); d.limiteur = new Limiteur({ parMinute: 1 });
  r = res(); await handleApi(req('POST', '/api/v1/avions/c208b/placement', { paras: [{ masse_kg: 90 }] }), r, d); assert.equal(r.code, 200);
  r = res(); await handleApi(req('POST', '/api/v1/avions/c208b/placement', { paras: [{ masse_kg: 91 }] }), r, d); assert.equal(r.code, 429);
  r = res(); await handleApi(req('POST', '/api/v1/avions/c208b/placement', { paras: [{ masse_kg: 90 }] }), r, d); assert.equal(r.code, 200); assert.equal(r.headers['X-Cache'], 'hit');
});

test('lib/ synchronise avec web/js et docs/ (relancer web/tools/gen_avions.py sinon)', () => {
  const web = path.join(__dirname, '..', 'web', 'js');
  if (!fs.existsSync(web)) return;   // paquet deploye : pas de web/
  assert.equal(fs.readFileSync(path.join(__dirname, 'lib', 'centrage.mjs'), 'utf8'), fs.readFileSync(path.join(web, 'centrage.js'), 'utf8'));
  assert.equal(fs.readFileSync(path.join(__dirname, 'lib', 'avions.mjs'), 'utf8'), fs.readFileSync(path.join(web, 'avions.js'), 'utf8'));
  assert.equal(fs.readFileSync(path.join(__dirname, 'lib', 'openapi.json'), 'utf8'), fs.readFileSync(path.join(__dirname, '..', 'docs', 'openapi.json'), 'utf8'));
});
