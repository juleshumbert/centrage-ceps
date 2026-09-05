'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const { sanitize, InputError, LIMITS } = require('./sanitize');

const base = () => ({
  avion: { masse_vide: 4890, bras_vide: 188.99 },
  enveloppe: { avant: [[5500, 179.6], [9062, 199.15]], arriere: [[0, 204.35], [9062, 204.35]], mtow: 9062 },
  carburant: { masse: 900, bras: 203.3 }, pilote: { masse: 176, bras: 135.5 },
  places: [{ id: 'A', x: 150, y: 16 }, { id: 'B', x: 200, y: 0 }],
  paras: [{ nom: 'X', masse: 200 }],
  options: { temps_max_s: 999, recuit_s: -3 },
});

test('plafonne les temps', () => {
  const s = sanitize(base());
  assert.equal(s.options.temps_max_s, LIMITS.tempsMax);
  assert.equal(s.options.recuit_s, 0);
});

test('options absentes : valeurs par defaut', () => {
  const b = base(); delete b.options;
  const s = sanitize(b);
  assert.equal(s.options.temps_max_s, 10);
  assert.equal(s.options.recuit_s, 1);
});

test('refuse plus de paras que de places', () => {
  const b = base(); b.paras = [{ nom: 'X', masse: 1 }, { nom: 'Y', masse: 1 }, { nom: 'Z', masse: 1 }];
  assert.throws(() => sanitize(b), InputError);
});

test('refuse une masse non numerique', () => {
  const b = base(); b.paras[0].masse = 'lourd';
  assert.throws(() => sanitize(b), InputError);
});

test('ne modifie pas l entree', () => {
  const b = base(); const copy = JSON.stringify(b);
  sanitize(b);
  assert.equal(JSON.stringify(b), copy);
});
