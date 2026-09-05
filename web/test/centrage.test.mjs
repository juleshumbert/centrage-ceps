import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { AVIONS } from '../js/avions.js';
import { interp, etat, etapes, bilan, stickPourSolveur, carburantBras, carburantMasse, appliquerVariante, normaliserEnveloppe } from '../js/centrage.js';

const BK = appliquerVariante(AVIONS.find((a) => a.id === 'c208b-A'), 'ape2');
const EU = appliquerVariante(AVIONS.find((a) => a.id === 'pc6-A'), 'afm');

test('interp : bornes et interieur', () => {
  const pts = [[5500, 179.6], [8000, 193.37], [9062, 199.15]];
  assert.equal(interp(pts, 1000), 179.6);
  assert.equal(interp(pts, 10000), 199.15);
  assert.ok(Math.abs(interp(pts, 6750) - 186.485) < 1e-9);
});

test('table carburant Caravan : bras 200 a 203.1 in', () => {
  assert.equal(carburantBras(BK, 34), 200.0);
  assert.equal(carburantBras(BK, 2224), 203.1);
});

test('PC-6 : litres vers kg et bras', () => {
  const m = carburantMasse(EU, 160.9);
  assert.ok(Math.abs(m - 129.6) < 1e-6);
  assert.ok(Math.abs(carburantBras(EU, m) - 4.03) < 1e-9);
});

test('etat : avion vide + pilote 80 kg Caravan (planches : 187 in environ)', () => {
  const e = etat(BK, [{ masse: 80 * 2.20462, bras: 135.5 }]);
  assert.ok(e.cg > 186 && e.cg < 188.5, `cg ${e.cg}`);
  assert.equal(e.statut, 'ok');   // sous 5500 lb la limite avant vaut 179.6 in, le CG a vide est en arriere
});

test('exemple_stick : le placement du solveur redonne les etapes publiees', () => {
  const stick = JSON.parse(readFileSync(new URL('../../solveur/exemples/exemple_stick.json', import.meta.url)));
  const res = JSON.parse(readFileSync(new URL('../../solveur/exemples/exemple_stick_resultat.json', import.meta.url)));
  // Le stick de l'exemple est deja en lb : on reconstruit un "avion" en lb a partir du stick.
  const avion = { ...BK, masse_vide: stick.avion.masse_vide, bras_vide: stick.avion.bras_vide,
    enveloppe: stick.enveloppe, mtow: stick.enveloppe.mtow, kg_par_unite_masse: 1,
    pilote: { bras: stick.pilote.bras }, carburant: { ...BK.carburant, table: [[0, stick.carburant.bras], [1e9, stick.carburant.bras]] },
    unites: { ...BK.unites, carburant: 'lb' }, places: stick.places };
  const paras = stick.paras.map((p) => ({ nom: p.nom, masseKg: p.masse, sortie: p.sortie, place: res.placement.find((q) => q.nom === p.nom).place }));
  const { etapes: et } = etapes(avion, { piloteKg: stick.pilote.masse, carburant: stick.carburant.masse }, paras, stick.places);
  assert.equal(et.length, 2);
  assert.ok(Math.abs(et[0].masse - res.etapes[0].masse) < 1e-6);
  assert.ok(Math.abs(et[0].cg - res.etapes[0].cg) < 1e-6, `${et[0].cg} vs ${res.etapes[0].cg}`);
  assert.ok(Math.abs(et[1].cg - res.etapes[1].cg) < 1e-6);
  assert.ok(Math.abs(et[0].margeAvant - res.etapes[0].marge_avant) < 1e-6);
  assert.equal(bilan(et).statut, 'ok');
});

test('stickPourSolveur : verrou = toutes les autres places interdites', () => {
  const s = stickPourSolveur(BK, { piloteKg: 80, carburant: 900 }, [
    { nom: 'A', masseKg: 90, verrou: 'D3' }, { nom: 'B', masseKg: 85, groupe: 'VR', sortie: 1, tandem: '', interdit: ['COPI'] }]);
  assert.equal(s.paras[0].interdit.length, BK.places.length - 1);
  assert.ok(!s.paras[0].interdit.includes('D3'));
  assert.deepEqual(s.paras[1].interdit, ['COPI']);
  assert.equal(s.paras[1].groupe, 'VR');
  assert.ok(Math.abs(s.paras[0].masse - 90 * 2.20462) < 1e-3);
  assert.equal(s.options.temps_max_s, 10);
});

test('variantes : POH 8750 lb contre STC APE II 9062 lb', () => {
  const base = AVIONS.find((a) => a.id === 'c208b-A');
  const poh = appliquerVariante(base, 'poh'), ape2 = appliquerVariante(base, 'ape2');
  assert.equal(poh.mtow, 8750); assert.equal(ape2.mtow, 9062);
  assert.equal(interp(poh.enveloppe.avant, 8750), 199.15);
  assert.equal(interp(ape2.enveloppe.avant, 9062), 200.23);   // STC APE II (TSB A14W0181)
  assert.equal(interp(appliquerVariante(base, 'planches').enveloppe.avant, 9062), 199.15);   // planches club, moins restrictives
  const modif = appliquerVariante(base, 'ape2', { mtow: 9000, enveloppe: { avant: [[5500, 180], [9000, 200]], arriere: [[0, 205], [9000, 205]] } });
  assert.equal(modif.mtow, 9000); assert.equal(interp(modif.enveloppe.arriere, 7000), 205);
  assert.equal(base.mtow, undefined, 'la base n est pas modifiee');
});

test('position libre : bras = x de la position, para libre verrouille = place virtuelle', () => {
  const paras = [{ nom: 'A', masseKg: 90, pos: { x: 250, y: 16 } }, { nom: 'B', masseKg: 90, place: 'D3' }];
  const { etapes: et, nonPlaces } = etapes(BK, { piloteKg: 80, carburant: 900 }, paras, BK.places);
  assert.equal(nonPlaces, 0);
  const attendu = etat(BK, [{ masse: 80 * 2.20462, bras: 135.5 }, { masse: 900, bras: carburantBras(BK, 900) }, { masse: 90 * 2.20462, bras: 250 }, { masse: 90 * 2.20462, bras: 205.9 }]);
  assert.ok(Math.abs(et[0].cg - attendu.cg) < 1e-9);
  const s = stickPourSolveur(BK, { piloteKg: 80, carburant: 900 }, [{ nom: 'A', masseKg: 90, pos: { x: 250, y: 16 }, verrou: 'libre' }, { nom: 'B', masseKg: 90, pos: { x: 220, y: 0 } }]);
  assert.ok(s.places.some((p) => p.id === 'L-A' && p.x === 250));
  assert.ok(!s.places.some((p) => p.id === 'L-B'), 'para libre non verrouille : pas de place virtuelle');
  assert.equal(s.paras[0].interdit.length, s.places.length - 1);
  assert.equal(s.paras[1].interdit, undefined);
});

test('normaliserEnveloppe trie et filtre', () => {
  const e = normaliserEnveloppe({ avant: [['9000', '199'], [5500, 179.6], ['x', 1]], arriere: [[0, 204.35]] });
  assert.deepEqual(e.avant, [[5500, 179.6], [9000, 199]]);
  assert.equal(normaliserEnveloppe({ avant: [], arriere: [] }), null);
});
