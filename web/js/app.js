// app.js : etat de l'IHM, formulaire du stick, appel du solveur (/api/placement), rendu.
import { AVIONS } from './avions.js';
import { EXEMPLE } from './exemple.js';
import * as C from './centrage.js';
import { dessinerCabine, dessinerCentrogramme, fmt } from './cabine.js';

const KEY = 'centrage-ceps:v1';
const $ = (s) => document.querySelector(s);
const $$ = (s) => [...document.querySelectorAll(s)];

// ---------------------------------------------------------------- etat
function defaut() {
  const a = AVIONS[0];
  return {
    avionId: a.id, masseVide: null, brasVide: null,
    piloteKg: a.pilote.masse_kg_defaut, carburant: a.carburant.defaut,
    paras: genererParas(10, 90),
    options: { marge_avant_min: 0.5, tolerance_marge: 0.25, etapes: 'premier_groupe', temps_max_s: 10, groupes_ordonnes: false, rapide: false },
    resultat: null, placementSolveur: null, modifie: false,
  };
}
function genererParas(n, kg) {
  return Array.from({ length: n }, (_, i) => ({ nom: `P${i + 1}`, masseKg: kg, groupe: '', sortie: '', tandem: '', role: '', interdit: [], verrou: null, place: null }));
}
function charger() {
  try { const s = JSON.parse(localStorage.getItem(KEY)); if (s && s.avionId && AVIONS.some((a) => a.id === s.avionId)) return { ...defaut(), ...s }; } catch { /* ignore */ }
  return null;
}
let state = charger() || defaut();
function sauver() { try { localStorage.setItem(KEY, JSON.stringify(state)); } catch { /* ignore */ } }

function avion() {
  const base = AVIONS.find((a) => a.id === state.avionId) || AVIONS[0];
  return { ...base, masse_vide: state.masseVide ?? base.masse_vide, bras_vide: state.brasVide ?? base.bras_vide };
}
const params = () => ({ piloteKg: Number(state.piloteKg) || 0, carburant: Number(state.carburant) || 0 });

// ---------------------------------------------------------------- rendu
function render() {
  const a = avion();
  // avion
  $('#selAvion').value = a.id;
  $('#avionType').textContent = a.type;
  $('#uniteMasse').textContent = a.unites.masse; $('#uniteBras').textContent = a.unites.bras; $('#uniteCarb').textContent = a.unites.carburant;
  $('#inMasseVide').value = a.masse_vide; $('#inBrasVide').value = a.bras_vide;
  $('#inPilote').value = state.piloteKg; $('#inCarb').value = state.carburant;
  const fm = C.carburantMasse(a, state.carburant);
  $('#carbInfo').textContent = a.unites.carburant === 'L' ? `${fm.toFixed(0)} kg, bras ${C.carburantBras(a, fm).toFixed(2)} m` : `${(fm * a.kg_par_unite_masse).toFixed(0)} kg, bras ${C.carburantBras(a, fm).toFixed(1)} in`;
  $('#carbCap').textContent = a.carburant.capacite ? `capacite ${a.carburant.capacite} ${a.unites.carburant}` : '';
  $('#avionNotes').hidden = !(a.a_verifier && a.a_verifier.length);
  if (a.a_verifier) $('#avionNotes').innerHTML = '<b>A verifier avant usage reel :</b><ul>' + a.a_verifier.map((t) => `<li>${esc(t)}</li>`).join('') + '</ul>';
  // options
  $('#optMarge').value = state.options.marge_avant_min; $('#optTol').value = state.options.tolerance_marge;
  $('#optEtapes').value = state.options.etapes; $('#optTemps').value = state.options.temps_max_s;
  $('#optGroupes').checked = !!state.options.groupes_ordonnes; $('#optRapide').checked = !!state.options.rapide;
  $('#optMargeUnit').textContent = a.unites.bras; $('#optTolUnit').textContent = a.unites.bras;
  renderParas(a);
  renderResultats(a);
  sauver();
}

function renderParas(a) {
  const tb = $('#tblParas tbody'); tb.replaceChildren();
  const placesOpts = ['<option value="">auto</option>', ...a.places.map((p) => `<option value="${esc(p.id)}">${esc(p.id)}</option>`)].join('');
  state.paras.forEach((p, i) => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td><input type="text" data-i="${i}" data-k="nom" value="${esc(p.nom)}" size="7"></td>
      <td><input type="number" data-i="${i}" data-k="masseKg" value="${p.masseKg}" min="30" max="200" step="0.5" style="width:5.2em"></td>
      <td><input type="text" data-i="${i}" data-k="groupe" value="${esc(p.groupe || '')}" size="4" placeholder="-"></td>
      <td><input type="number" data-i="${i}" data-k="sortie" value="${p.sortie ?? ''}" min="1" max="99" style="width:4em" placeholder="-"></td>
      <td><input type="text" data-i="${i}" data-k="tandem" value="${esc(p.tandem || '')}" size="4" placeholder="-"></td>
      <td><select data-i="${i}" data-k="role" ${p.tandem ? '' : 'disabled'}><option value="porteur" ${p.role !== 'passager' ? 'selected' : ''}>porteur</option><option value="passager" ${p.role === 'passager' ? 'selected' : ''}>passager</option></select></td>
      <td><input type="checkbox" data-i="${i}" data-k="copi" ${(p.interdit || []).includes('COPI') ? 'checked' : ''} title="place copilote interdite" ${a.places.some((s) => s.copilote) ? '' : 'disabled'}></td>
      <td><select data-i="${i}" data-k="verrou">${placesOpts}</select></td>
      <td class="mono">${p.place ? esc(p.place) : '<span class="muted">-</span>'}</td>
      <td><button class="btn ghost mini" data-i="${i}" data-k="suppr" title="retirer ce para">x</button></td>`;
    tr.querySelector('select[data-k="verrou"]').value = p.verrou || '';
    tb.appendChild(tr);
  });
  $('#nbParas').textContent = state.paras.length;
  const total = state.paras.reduce((s, p) => s + (Number(p.masseKg) || 0), 0);
  $('#totalParas').textContent = `${total.toFixed(0)} kg`;
}

function parasPlaces(a) {
  return state.paras.map((p) => ({ ...p, sortie: p.sortie === '' ? null : p.sortie }));
}

function renderResultats(a) {
  const ps = parasPlaces(a);
  const mode = state.options.etapes === 'toutes' ? 'toutes' : 'premier_groupe';
  const { etapes, nonPlaces } = C.etapes(a, params(), ps, a.places, mode);
  const b = C.bilan(etapes);
  const u = a.unites.bras;
  const dec = etapes[0];
  const nbPlaces = ps.length - nonPlaces;
  // statut
  const bar = $('#statut');
  bar.className = 'status-bar ' + (nbPlaces === 0 ? 'status-warn' : b.statut === 'ok' ? 'status-ok' : 'status-danger');
  const libelle = { ok: 'dans l enveloppe a toutes les etapes', avant: 'trop centre AVANT', arriere: 'trop centre ARRIERE', mtow: 'au-dessus de la MTOW' }[b.statut];
  bar.textContent = nbPlaces === 0 ? 'Aucun para place : lance le solveur ou glisse les paras sur les places.'
    : `${nbPlaces}/${ps.length} paras places : ${libelle}` + (nonPlaces ? ` (${nonPlaces} sans place, non comptes)` : '') + (state.modifie ? ' · placement modifie a la main' : state.resultat ? ' · placement du solveur' : '');
  // readouts
  const ro = (id, v, cls) => { const e = $(id); e.querySelector('.val').textContent = v; e.className = 'readout' + (cls ? ' ' + cls : ''); };
  ro('#roMasse', `${dec.masse.toFixed(0)}`, dec.masse > a.mtow ? 'danger' : 'ok'); $('#roMasse .unit').textContent = `${a.unites.masse} · ${(dec.masse * a.kg_par_unite_masse).toFixed(0)} kg · MTOW ${a.mtow}`;
  ro('#roCg', u === 'm' ? dec.cg.toFixed(3) : dec.cg.toFixed(2)); $('#roCg .unit').textContent = `${u} · ${dec.mac.toFixed(1)} % MAC`;
  ro('#roAvant', fmtMarge(b.margeAvant, u), b.margeAvant < 0 ? 'danger' : b.margeAvant < state.options.marge_avant_min ? 'warn' : 'ok'); $('#roAvant .unit').textContent = `${u} · minimum sur les etapes (cible ${state.options.marge_avant_min})`;
  ro('#roArriere', fmtMarge(b.margeArriere, u), b.margeArriere < 0 ? 'danger' : b.margeArriere < 0.5 ? 'warn' : 'ok'); $('#roArriere .unit').textContent = `${u} · minimum sur les etapes`;
  // table etapes
  const tb = $('#tblEtapes tbody'); tb.replaceChildren();
  for (const e of etapes) {
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${esc(e.etape)}</td><td>${e.restants}</td><td>${e.masse.toFixed(0)}</td><td>${u === 'm' ? e.cg.toFixed(3) : e.cg.toFixed(2)}</td><td>${e.mac.toFixed(1)}</td><td>${fmtMarge(e.margeAvant, u)}</td><td>${fmtMarge(e.margeArriere, u)}</td><td><span class="pill ${e.statut === 'ok' ? 'ok' : 'danger'}">${e.statut}</span></td>`;
    tb.appendChild(tr);
  }
  // infos solveur
  const r = state.resultat;
  const inf = $('#solveurInfo');
  if (!r) inf.textContent = 'Pas encore de calcul.';
  else if (!r.ok) inf.innerHTML = `<span class="pill danger">aucun placement valide</span> ${esc(r.message || '')}` + (r.marge_avant_max_possible != null ? ` (marge avant max possible ${fmtMarge(r.marge_avant_max_possible, u)} ${u})` : '') + (r.placement_au_mieux ? ' · le meilleur compromis a ete applique sur le plan.' : '');
  else inf.innerHTML = `<span class="pill ok">solveur</span> marge arriere max ${fmtMarge(r.marge_arriere_max, u)} ${u} (phase 1 ${esc(r.phase1 || '')}, phase 2 ${esc(r.phase2 || '')}), realisme ${Number(r.cout_realisme).toFixed(1)}, ${Number(r.temps_s).toFixed(1)} s de calcul` + (r.temps_serveur_ms ? ` (${(r.temps_serveur_ms / 1000).toFixed(1)} s serveur)` : '') + (r.premier_groupe ? ` · premier groupe : ${esc(r.premier_groupe.join(', '))}` : '');
  $('#btnRevenir').disabled = !state.placementSolveur || !state.modifie;
  // dessins
  dessinerCabine($('#svgCabine'), a, ps, { onDeplacer: deplacer, onClic: basculerVerrou });
  const base = C.etat(a, [{ masse: C.masseNative(a, params().piloteKg), bras: a.pilote.bras }, { masse: C.carburantMasse(a, state.carburant), bras: C.carburantBras(a, C.carburantMasse(a, state.carburant)) }]);
  const pts = [...etapes.map((e, i) => ({ label: i === 0 ? 'decollage' : e.rang === Infinity ? 'fin' : `sortie ${e.rang}`, masse: e.masse, cg: e.cg, statut: e.statut })), { label: 'sans paras', masse: base.masse, cg: base.cg, statut: base.statut }];
  dessinerCentrogramme($('#svgCentro'), a, nbPlaces ? pts : [pts[pts.length - 1]]);
}
const fmtMarge = (v, u) => (Number.isFinite(v) ? (v >= 0 ? '+' : '') + (u === 'm' ? v.toFixed(3) : v.toFixed(2)) : '-');
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

// ---------------------------------------------------------------- actions
function deplacer(nom, placeId) {
  const p = state.paras.find((q) => q.nom === nom); if (!p) return;
  const occ = state.paras.find((q) => q.place === placeId && q !== p);
  if (occ) { occ.place = p.place; if (occ.verrou) occ.verrou = occ.place; }
  p.place = placeId; if (p.verrou) p.verrou = placeId;
  state.modifie = true; render();
}
function basculerVerrou(nom) {
  const p = state.paras.find((q) => q.nom === nom); if (!p || !p.place) return;
  p.verrou = p.verrou ? null : p.place; render();
}

async function calculer() {
  const a = avion();
  const btn = $('#btnCalculer'); const st = $('#calcStatut');
  const noms = new Set(); for (const p of state.paras) { if (!p.nom.trim()) { st.textContent = 'Chaque para doit avoir un nom.'; return; } if (noms.has(p.nom)) { st.textContent = `Nom en double : ${p.nom}`; return; } noms.add(p.nom); }
  if (state.paras.length === 0) { st.textContent = 'Ajoute au moins un para.'; return; }
  if (state.paras.length > a.places.length) { st.textContent = `${state.paras.length} paras pour ${a.places.length} places.`; return; }
  const options = { ...state.options }; delete options.rapide; if (state.options.rapide) options.rapide = true;
  const stick = C.stickPourSolveur(a, params(), state.paras, options);
  btn.disabled = true; st.textContent = 'Calcul en cours (solveur HiGHS)...'; const t0 = performance.now();
  try {
    const headers = { 'Content-Type': 'application/json' };
    const user = window.briefingAuth && window.briefingAuth.currentUser();
    if (user) headers.Authorization = 'Bearer ' + await user.getIdToken();
    const rep = await fetch('/api/placement', { method: 'POST', headers, body: JSON.stringify(stick) });
    const out = await rep.json().catch(() => ({ ok: false, message: `reponse ${rep.status} illisible` }));
    if (!rep.ok && !out.placement && !out.placement_au_mieux) { st.textContent = `Erreur ${rep.status} : ${out.message || ''} ${out.detail || ''}`; state.resultat = out; render(); return; }
    state.resultat = out; state.derniereEntree = stick;
    const pl = out.placement || out.placement_au_mieux;
    if (pl) {
      for (const p of state.paras) { const q = pl.find((x) => x.nom === p.nom); p.place = q ? q.place : null; }
      state.placementSolveur = Object.fromEntries(pl.map((q) => [q.nom, q.place]));
      state.modifie = false;
    }
    st.textContent = out.ok ? `Placement calcule en ${((performance.now() - t0) / 1000).toFixed(1)} s.` : `Aucun placement valide : ${out.message || ''}`;
  } catch (e) {
    st.textContent = 'Appel du solveur impossible : ' + (e && e.message ? e.message : e);
  } finally { btn.disabled = false; render(); }
}

function revenirSolveur() {
  if (!state.placementSolveur) return;
  for (const p of state.paras) p.place = state.placementSolveur[p.nom] || null;
  state.modifie = false; render();
}

function telecharger() {
  const a = avion();
  const data = { avion: a.id, parametres: params(), paras: state.paras, options: state.options, entree_solveur: state.derniereEntree || C.stickPourSolveur(a, params(), state.paras, state.options), resultat_solveur: state.resultat,
    placement_actuel: state.paras.map((p) => ({ nom: p.nom, place: p.place })), etapes_actuelles: C.etapes(a, params(), parasPlaces(a), a.places, state.options.etapes === 'toutes' ? 'toutes' : 'premier_groupe').etapes };
  const blob = new Blob([JSON.stringify(data, null, 1)], { type: 'application/json' });
  const url = URL.createObjectURL(blob); const l = document.createElement('a'); l.href = url; l.download = `centrage_${a.id}_${new Date().toISOString().slice(0, 16).replace(/[:T]/g, '-')}.json`; l.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
}

function changerAvion(id) {
  const a = AVIONS.find((x) => x.id === id); if (!a) return;
  state.avionId = id; state.masseVide = null; state.brasVide = null; state.carburant = a.carburant.defaut; state.piloteKg = a.pilote.masse_kg_defaut;
  for (const p of state.paras) { p.place = null; p.verrou = null; }
  state.resultat = null; state.placementSolveur = null; state.modifie = false; render();
}

// ---------------------------------------------------------------- branchements
function brancher() {
  $('#selAvion').innerHTML = AVIONS.map((a) => `<option value="${esc(a.id)}">${esc(a.immat)} · ${esc(a.type)}</option>`).join('');
  $('#selAvion').addEventListener('change', (e) => changerAvion(e.target.value));
  $('#inMasseVide').addEventListener('change', (e) => { state.masseVide = Number(e.target.value) || null; state.resultat = null; render(); });
  $('#inBrasVide').addEventListener('change', (e) => { state.brasVide = Number(e.target.value) || null; state.resultat = null; render(); });
  $('#btnPesee').addEventListener('click', () => { state.masseVide = null; state.brasVide = null; render(); });
  $('#inPilote').addEventListener('change', (e) => { state.piloteKg = Number(e.target.value) || 0; render(); });
  $('#inCarb').addEventListener('change', (e) => { state.carburant = Number(e.target.value) || 0; render(); });
  for (const [id, k, f] of [['#optMarge', 'marge_avant_min', Number], ['#optTol', 'tolerance_marge', Number], ['#optEtapes', 'etapes', String], ['#optTemps', 'temps_max_s', Number]])
    $(id).addEventListener('change', (e) => { state.options[k] = f(e.target.value); render(); });
  $('#optGroupes').addEventListener('change', (e) => { state.options.groupes_ordonnes = e.target.checked; sauver(); });
  $('#optRapide').addEventListener('change', (e) => { state.options.rapide = e.target.checked; sauver(); });
  $('#tblParas').addEventListener('change', (e) => {
    const t = e.target; const i = Number(t.dataset.i), k = t.dataset.k; if (!(i >= 0) || !k) return;
    const p = state.paras[i];
    if (k === 'copi') { p.interdit = t.checked ? [...new Set([...(p.interdit || []), 'COPI'])] : (p.interdit || []).filter((x) => x !== 'COPI'); }
    else if (k === 'verrou') { p.verrou = t.value || null; if (p.verrou) { const occ = state.paras.find((q) => q !== p && q.place === p.verrou); if (occ) occ.place = p.place; p.place = p.verrou; state.modifie = true; } }
    else if (k === 'masseKg' || k === 'sortie') { p[k] = t.value === '' ? '' : Number(t.value); }
    else { p[k] = t.value.trim(); if (k === 'tandem' && !p.tandem) p.role = ''; if (k === 'tandem' && p.tandem && !p.role) p.role = 'porteur'; }
    render();
  });
  $('#tblParas').addEventListener('click', (e) => {
    const b = e.target.closest('button[data-k="suppr"]'); if (!b) return;
    state.paras.splice(Number(b.dataset.i), 1); render();
  });
  $('#btnAjouter').addEventListener('click', () => { const n = state.paras.length + 1; state.paras.push({ ...genererParas(1, Number($('#genKg').value) || 90)[0], nom: `P${n}` }); render(); });
  $('#btnGenerer').addEventListener('click', () => { state.paras = genererParas(Number($('#genN').value) || 10, Number($('#genKg').value) || 90); state.resultat = null; state.placementSolveur = null; state.modifie = false; render(); });
  $('#btnVider').addEventListener('click', () => { for (const p of state.paras) { p.place = null; p.verrou = null; } state.modifie = !!state.placementSolveur; render(); });
  $('#btnExemple').addEventListener('click', () => { state = { ...defaut(), avionId: EXEMPLE.avionId, piloteKg: EXEMPLE.piloteKg, carburant: EXEMPLE.carburant, paras: EXEMPLE.paras.map((p) => ({ groupe: '', sortie: '', tandem: '', role: '', interdit: [], verrou: null, place: null, ...p })) }; render(); });
  $('#btnCalculer').addEventListener('click', calculer);
  $('#btnRevenir').addEventListener('click', revenirSolveur);
  $('#btnJson').addEventListener('click', telecharger);
  $('#btnReset').addEventListener('click', () => { localStorage.removeItem(KEY); state = defaut(); render(); });
}

brancher();
render();
