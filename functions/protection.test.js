'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const { Limiteur, origineAutorisee } = require('./protection');

test('limite par minute puis reprise', () => {
  let t = 0; const L = new Limiteur({ parMinute: 3, parJour: 100 }, () => t);
  assert.ok(L.admettre('a').ok); assert.ok(L.admettre('a').ok); assert.ok(L.admettre('a').ok);
  const r = L.admettre('a'); assert.equal(r.ok, false); assert.ok(r.retryAfterS >= 1);
  assert.ok(L.admettre('b').ok, 'autre IP independante');
  t = 61 * 1000; assert.ok(L.admettre('a').ok);
});

test('quota journalier', () => {
  let t = 0; const L = new Limiteur({ parMinute: 1000, parJour: 5 }, () => t);
  for (let i = 0; i < 5; i++) { assert.ok(L.admettre('a').ok); t += 70 * 1000; }
  assert.equal(L.admettre('a').ok, false);
  t += 25 * 3600 * 1000; assert.ok(L.admettre('a').ok);
});

test('semaphore de calculs simultanes', () => {
  const L = new Limiteur({ simultanes: 2 });
  assert.ok(L.reserver()); assert.ok(L.reserver()); assert.equal(L.reserver(), false);
  L.liberer(); assert.ok(L.reserver());
});

test('cache par empreinte, avec TTL', () => {
  let t = 0; const L = new Limiteur({ cacheTtlMs: 1000 }, () => t);
  const k = Limiteur.empreinte({ a: 1 });
  assert.equal(L.cacheLire(k), null);
  L.cacheEcrire(k, { ok: true }); assert.deepEqual(L.cacheLire(k), { ok: true });
  t = 2000; assert.equal(L.cacheLire(k), null);
  assert.notEqual(Limiteur.empreinte({ a: 1 }), Limiteur.empreinte({ a: 2 }));
});

test('table des IP bornee', () => {
  const L = new Limiteur({ ipsMax: 3 });
  for (const ip of ['1', '2', '3', '4']) L.admettre(ip);
  assert.equal(L.ips.size, 3); assert.ok(!L.ips.has('1'));
});

test('origine', () => {
  const ok = ['https://ceps09-centrage.web.app', '*.ceps09.com'];
  assert.ok(origineAutorisee('https://ceps09-centrage.web.app', null, ok));
  assert.ok(origineAutorisee(null, 'https://centrage.ceps09.com/index.html', ok));
  assert.ok(origineAutorisee(null, null, ok), 'sans en-tete : laisse passer');
  assert.equal(origineAutorisee('https://evil.example', null, ok), false);
});
