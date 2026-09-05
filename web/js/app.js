// app.js : etat de l'IHM, formulaire du stick, appel du solveur (/api/placement), rendu.
import { AVIONS } from './avions.js';
import { EXEMPLE } from './exemple.js';
import * as C from './centrage.js';
import { dessinerCabine, dessinerCentrogramme, fmt } from './cabine.js';

const KEY = 'centrage-ceps:v3';
const $ = (s) => document.querySelector(s);

// ---------------------------------------------------------------- etat
function defaut() {
  const a = AVIONS[0];
  return {
    avionId: a.id, varianteId: a.variante_defaut, peseeId: (a.pesees && a.pesees[0] ? a.pesees[0].id : null), nomLocal: '', masseVide: null, brasVide: null,
    piloteKg: a.pilote.masse_kg_defaut, carburant: a.carburant.defaut, porteOuverte: false,
    paras: genererParas(10, 90),
    options: { marge_avant_min: 0.5, tolerance_marge: 0.25, etapes: 'premier_groupe', temps_max_s: 8, groupes_ordonnes: false, rapide: false },
    enveloppes: {},            // cle avionId:varianteId -> {mtow, enveloppe} modifies dans l'application
    resultat: null, placementSolveur: null, modifie: false, derniereEntree: null,
  };
}
function genererParas(n, kg) {
  return Array.from({ length: n }, (_, i) => ({ nom: `P${i + 1}`, masseKg: kg, groupe: '', sortie: '', tandem: '', role: '', interdit: [], verrou: null, place: null, pos: null }));
}
function charger() {
  try { const s = JSON.parse(localStorage.getItem(KEY)); if (s && s.avionId && AVIONS.some((a) => a.id === s.avionId)) return { ...defaut(), ...s }; } catch { /* ignore */ }
  return null;
}
let state = charger() || defaut();
function sauver() { try { localStorage.setItem(KEY, JSON.stringify(state)); } catch { /* ignore */ } }

const base = () => AVIONS.find((a) => a.id === state.avionId) || AVIONS[0];
const cleEnv = () => `${state.avionId}:${state.varianteId}`;
function avion() {
  const b = base();
  const a = C.appliquerVariante(b, state.varianteId, state.enveloppes[cleEnv()], state.peseeId);
  return { ...a, masse_vide: state.masseVide ?? a.masse_vide, bras_vide: state.brasVide ?? a.bras_vide };
}
const params = () => ({ piloteKg: Number(state.piloteKg) || 0, carburant: Number(state.carburant) || 0, porteOuverte: !!state.porteOuverte });
const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const fmtMarge = (v, u) => (Number.isFinite(v) ? (v >= 0 ? '+' : '') + (u === 'm' ? v.toFixed(3) : v.toFixed(2)) : '-');

// ---------------------------------------------------------------- rendu
function render() {
  const a = avion(); const b = base();
  $('#selAvion').value = a.id;
  const sel = $('#selVariante'); sel.innerHTML = (b.variantes || []).map((v) => `<option value="${esc(v.id)}">${esc(v.libelle)}</option>`).join(''); sel.value = state.varianteId;
  $('#varianteSource').textContent = a.variante ? a.variante.source || '' : '';
  const selP = $('#selPesee'); selP.innerHTML = (b.pesees || []).map((q) => `<option value="${esc(q.id)}">${esc(q.libelle)} : ${q.masse_vide} ${a.unites.masse} a ${q.bras_vide} ${a.unites.bras}</option>`).join(''); selP.value = state.peseeId || '';
  $('#peseeSource').textContent = a.pesee ? a.pesee.source || '' : '';
  $('#porteBloc').hidden = !(a.porte && a.porte.moment_ouverture);
  if (a.porte && a.porte.moment_ouverture) { $('#inPorte').checked = !!state.porteOuverte; $('#porteLibelle').textContent = a.porte.moment_ouverture.libelle; }
  $('#inNomLocal').value = state.nomLocal || '';
  $('#avionType').textContent = (state.nomLocal ? state.nomLocal + ' · ' : '') + a.libelle;
  $('#uniteMasse').textContent = a.unites.masse; $('#uniteBras').textContent = a.unites.bras; $('#uniteCarb').textContent = a.unites.carburant;
  $('#inMasseVide').value = a.masse_vide; $('#inBrasVide').value = a.bras_vide;
  $('#inPilote').value = state.piloteKg; $('#inCarb').value = state.carburant;
  const fm = C.carburantMasse(a, state.carburant);
  $('#carbInfo').textContent = a.unites.carburant === 'L' ? `${fm.toFixed(0)} kg, bras ${C.carburantBras(a, fm).toFixed(2)} m` : `${(fm * a.kg_par_unite_masse).toFixed(0)} kg, bras ${C.carburantBras(a, fm).toFixed(1)} in`;
  $('#carbCap').textContent = a.carburant.capacite ? `capacite ${a.carburant.capacite} ${a.unites.carburant}` : '';
  const notes = [...(a.a_verifier || []), ...(a.variante && a.variante.a_verifier ? [a.variante.source] : [])];
  $('#avionNotes').hidden = !notes.length;
  if (notes.length) $('#avionNotes').innerHTML = '<b>A verifier avant usage reel :</b><ul>' + notes.map((t) => `<li>${esc(t)}</li>`).join('') + '</ul>';
  $('#optMarge').value = state.options.marge_avant_min; $('#optTol').value = state.options.tolerance_marge;
  $('#optEtapes').value = state.options.etapes; $('#optTemps').value = state.options.temps_max_s;
  $('#optGroupes').checked = !!state.options.groupes_ordonnes; $('#optRapide').checked = !!state.options.rapide;
  $('#optMargeUnit').textContent = a.unites.bras; $('#optTolUnit').textContent = a.unites.bras;
  renderParas(a);
  renderEnveloppe(a);
  renderResultats(a);
  sauver();
}

function renderParas(a) {
  const tb = $('#tblParas tbody'); tb.replaceChildren();
  const placesOpts = ['<option value="">auto</option>', '<option value="libre">position libre</option>', ...a.places.map((p) => `<option value="${esc(p.id)}">${esc(p.id)}</option>`)].join('');
  state.paras.forEach((p, i) => {
    const tr = document.createElement('tr');
    const ou = p.place ? esc(p.place) : (p.pos ? `libre ${fmt(p.pos.x, a)}` : '<span class="muted">-</span>');
    tr.innerHTML = `
      <td><input type="text" data-i="${i}" data-k="nom" value="${esc(p.nom)}"></td>
      <td><input type="number" data-i="${i}" data-k="masseKg" value="${p.masseKg}" min="30" max="200" step="0.5"></td>
      <td><input type="text" data-i="${i}" data-k="groupe" value="${esc(p.groupe || '')}" placeholder="-"></td>
      <td><input type="number" data-i="${i}" data-k="sortie" value="${p.sortie ?? ''}" min="1" max="99" placeholder="-"></td>
      <td><input type="text" data-i="${i}" data-k="tandem" value="${esc(p.tandem || '')}" placeholder="-"></td>
      <td><select data-i="${i}" data-k="role" ${p.tandem ? '' : 'disabled'}><option value="porteur" ${p.role !== 'passager' ? 'selected' : ''}>porteur</option><option value="passager" ${p.role === 'passager' ? 'selected' : ''}>passager</option></select></td>
      <td><input type="checkbox" data-i="${i}" data-k="copi" ${(p.interdit || []).includes('COPI') ? 'checked' : ''} title="place copilote interdite" ${a.places.some((s) => s.copilote) ? '' : 'disabled'}></td>
      <td><select data-i="${i}" data-k="verrou">${placesOpts}</select></td>
      <td class="mono">${ou}</td>
      <td><button class="btn ghost mini" data-i="${i}" data-k="suppr" title="retirer ce para">x</button></td>`;
    const sv = tr.querySelector('select[data-k="verrou"]'); sv.value = p.verrou || ''; if (p.verrou === 'libre' && !p.pos) sv.value = '';
    tb.appendChild(tr);
  });
  $('#nbParas').textContent = state.paras.length;
  $('#totalParas').textContent = `${state.paras.reduce((s, p) => s + (Number(p.masseKg) || 0), 0).toFixed(0)} kg`;
}

function renderEnveloppe(a) {
  const modif = !!state.enveloppes[cleEnv()];
  $('#envModif').hidden = !modif;
  $('#envMtow').value = a.mtow;
  const lignes = (pts, lim) => pts.map((p, i) => `<tr><td>${lim === 'avant' ? 'avant' : 'arriere'}</td><td><input type="number" data-lim="${lim}" data-i="${i}" data-c="0" value="${p[0]}" step="${a.unites.bras === 'm' ? 1 : 10}"></td><td><input type="number" data-lim="${lim}" data-i="${i}" data-c="1" value="${p[1]}" step="${a.unites.bras === 'm' ? 0.001 : 0.01}"></td><td><button class="btn ghost mini" data-lim="${lim}" data-i="${i}" data-suppr="1" title="retirer ce sommet">x</button></td></tr>`).join('');
  $('#tblEnv tbody').innerHTML = lignes(a.enveloppe.avant, 'avant') + lignes(a.enveloppe.arriere, 'arriere');
  $('#envUnites').textContent = `masse en ${a.unites.masse}, bras en ${a.unites.bras}`;
}

function parasPlaces() { return state.paras.map((p) => ({ ...p, sortie: p.sortie === '' ? null : p.sortie })); }

function renderResultats(a) {
  const ps = parasPlaces();
  const mode = state.options.etapes === 'toutes' ? 'toutes' : 'premier_groupe';
  const { etapes, nonPlaces } = C.etapes(a, params(), ps, a.places, mode);
  const b = C.bilan(etapes);
  const u = a.unites.bras, dec = etapes[0], nbPlaces = ps.length - nonPlaces;
  const bar = $('#statut');
  bar.className = 'status-bar ' + (nbPlaces === 0 ? 'status-warn' : b.statut === 'ok' ? 'status-ok' : 'status-danger');
  const libelle = { ok: 'dans l enveloppe a toutes les etapes', avant: 'trop centre AVANT', arriere: 'trop centre ARRIERE', mtow: 'au-dessus de la MTOW' }[b.statut];
  bar.textContent = nbPlaces === 0 ? 'Aucun para place : lance le solveur ou glisse les paras dans la cabine.'
    : `${nbPlaces}/${ps.length} paras places : ${libelle}` + (nonPlaces ? ` (${nonPlaces} sans place, non comptes)` : '') + (state.modifie ? ' · placement modifie a la main' : state.resultat ? ' · placement du solveur' : '');
  const ro = (id, v, cls) => { const e = $(id); e.querySelector('.val').textContent = v; e.className = 'readout' + (cls ? ' ' + cls : ''); };
  ro('#roMasse', `${dec.masse.toFixed(0)}`, dec.masse > a.mtow ? 'danger' : 'ok'); $('#roMasse .unit').textContent = `${a.unites.masse} · ${(dec.masse * a.kg_par_unite_masse).toFixed(0)} kg · MTOW ${a.mtow}`;
  ro('#roCg', u === 'm' ? dec.cg.toFixed(3) : dec.cg.toFixed(2)); $('#roCg .unit').textContent = `${u} · ${dec.mac.toFixed(1)} % MAC`;
  ro('#roAvant', fmtMarge(b.margeAvant, u), b.margeAvant < 0 ? 'danger' : b.margeAvant < state.options.marge_avant_min ? 'warn' : 'ok'); $('#roAvant .unit').textContent = `${u} · minimum sur les etapes (cible ${state.options.marge_avant_min})`;
  ro('#roArriere', fmtMarge(b.margeArriere, u), b.margeArriere < 0 ? 'danger' : b.margeArriere < 0.5 ? 'warn' : 'ok'); $('#roArriere .unit').textContent = `${u} · minimum sur les etapes`;
  const tb = $('#tblEtapes tbody'); tb.replaceChildren();
  for (const e of etapes) {
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${esc(e.etape)}</td><td>${e.restants}</td><td>${e.masse.toFixed(0)}</td><td>${u === 'm' ? e.cg.toFixed(3) : e.cg.toFixed(2)}</td><td>${e.mac.toFixed(1)}</td><td>${fmtMarge(e.margeAvant, u)}</td><td>${fmtMarge(e.margeArriere, u)}</td><td><span class="pill ${e.statut === 'ok' ? 'ok' : 'danger'}">${e.statut}</span></td>`;
    tb.appendChild(tr);
  }
  const r = state.resultat, inf = $('#solveurInfo');
  if (!r) inf.textContent = 'Pas encore de calcul.';
  else if (!r.ok) inf.innerHTML = `<span class="pill danger">aucun placement valide</span> ${esc(r.message || '')}` + (r.marge_avant_max_possible != null ? ` (marge avant max possible ${fmtMarge(r.marge_avant_max_possible, u)} ${u})` : '') + (r.placement_au_mieux ? ' · le meilleur compromis a ete applique sur le plan.' : '');
  else inf.innerHTML = `<span class="pill ok">solveur</span> marge arriere max ${fmtMarge(r.marge_arriere_max, u)} ${u} (phase 1 ${esc(r.phase1 || '')}, phase 2 ${esc(r.phase2 || '')}), realisme ${Number(r.cout_realisme).toFixed(1)}, ${Number(r.temps_s).toFixed(1)} s de calcul` + (r.temps_serveur_ms ? ` (${(r.temps_serveur_ms / 1000).toFixed(1)} s serveur)` : '') + (r.premier_groupe ? ` · premier groupe : ${esc(r.premier_groupe.join(', '))}` : '');
  $('#btnRevenir').disabled = !state.placementSolveur || !state.modifie;
  dessinerCabine($('#svgCabine'), a, ps, { onDeplacer: deplacer, onClic: basculerVerrou, onSurvol: (txt) => { $('#cabInfo').textContent = txt || ''; },
    cg: nbPlaces ? { cg: dec.cg, avant: dec.avant, arriere: dec.arriere, statut: b.statut } : null });
  const fuelM = C.carburantMasse(a, state.carburant);
  const vide = C.etat(a, [{ masse: C.masseNative(a, params().piloteKg), bras: a.pilote.bras }, { masse: fuelM, bras: C.carburantBras(a, fuelM) }]);
  const pts = [...etapes.map((e, i) => ({ label: i === 0 ? 'decollage' : e.rang === Infinity ? 'fin' : `sortie ${e.rang}`, masse: e.masse, cg: e.cg, statut: e.statut })), { label: 'sans paras', masse: vide.masse, cg: vide.cg, statut: vide.statut }];
  dessinerCentrogramme($('#svgCentro'), a, nbPlaces ? pts : [pts[pts.length - 1]], { editable: $('#envEdit').open, onSommet: deplacerSommet });
}

// ---------------------------------------------------------------- actions
function deplacer(nom, cible) {
  const p = state.paras.find((q) => q.nom === nom); if (!p) return;
  if (cible.place) {
    const occ = state.paras.find((q) => q.place === cible.place && q !== p);
    if (occ) { occ.place = p.place; occ.pos = p.pos ? { ...p.pos } : null; if (occ.verrou) occ.verrou = occ.place || (occ.pos ? 'libre' : null); }
    p.place = cible.place; p.pos = null; if (p.verrou) p.verrou = cible.place;
  } else if (cible.pos) {
    p.place = null; p.pos = { ...cible.pos }; if (p.verrou) p.verrou = 'libre';
  }
  state.modifie = true; render();
}
function basculerVerrou(nom) {
  const p = state.paras.find((q) => q.nom === nom); if (!p) return;
  if (p.place) p.verrou = p.verrou ? null : p.place;
  else if (p.pos) p.verrou = p.verrou ? null : 'libre';
  render();
}
function deplacerSommet(limite, i, val) {
  const a = avion();
  const env = JSON.parse(JSON.stringify(a.enveloppe)); env[limite][i] = val;
  const n = C.normaliserEnveloppe(env); if (!n) return;
  state.enveloppes[cleEnv()] = { mtow: a.mtow, enveloppe: n }; render();
}
function appliquerTableEnveloppe() {
  const a = avion();
  const env = { avant: [], arriere: [] };
  $('#tblEnv tbody').querySelectorAll('tr').forEach((tr) => {
    const ins = tr.querySelectorAll('input'); const lim = ins[0].dataset.lim;
    env[lim].push([Number(ins[0].value), Number(ins[1].value)]);
  });
  const n = C.normaliserEnveloppe(env); if (!n) { $('#envStatut').textContent = 'Il faut au moins un point par limite.'; return; }
  const mtow = Number($('#envMtow').value) || a.mtow;
  state.enveloppes[cleEnv()] = { mtow, enveloppe: n }; state.resultat = null; $('#envStatut').textContent = 'Enveloppe modifiee appliquee (memorisee dans ce navigateur).'; render();
}

async function calculer() {
  const a = avion(); const btn = $('#btnCalculer'); const st = $('#calcStatut');
  const noms = new Set(); for (const p of state.paras) { if (!p.nom.trim()) { st.textContent = 'Chaque para doit avoir un nom.'; return; } if (noms.has(p.nom)) { st.textContent = `Nom en double : ${p.nom}`; return; } noms.add(p.nom); }
  if (state.paras.length === 0) { st.textContent = 'Ajoute au moins un para.'; return; }
  if (state.paras.length > a.places.length) { st.textContent = `${state.paras.length} paras pour ${a.places.length} places.`; return; }
  const options = { ...state.options }; delete options.rapide; if (state.options.rapide) options.rapide = true;
  const stick = C.stickPourSolveur(a, params(), state.paras, options);
  btn.disabled = true; st.textContent = 'Calcul en cours (solveur HiGHS)...'; const t0 = performance.now();
  try {
    const rep = await fetch('/api/placement', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(stick) });
    const out = await rep.json().catch(() => ({ ok: false, message: `reponse ${rep.status} illisible` }));
    if (!rep.ok && !out.placement && !out.placement_au_mieux) { st.textContent = `Erreur ${rep.status} : ${out.message || ''} ${out.detail || ''}`; state.resultat = out; render(); return; }
    state.resultat = out; state.derniereEntree = stick;
    const pl = out.placement || out.placement_au_mieux;
    if (pl) {
      state.placementSolveur = {};
      for (const p of state.paras) {
        const q = pl.find((x) => x.nom === p.nom);
        if (!q) { p.place = null; p.pos = null; }
        else if (q.place === `L-${p.nom}`) { p.place = null; /* pos conservee */ }
        else { p.place = q.place; p.pos = null; }
        state.placementSolveur[p.nom] = { place: p.place, pos: p.pos ? { ...p.pos } : null };
      }
      state.modifie = false;
    }
    st.textContent = out.ok ? `Placement calcule en ${((performance.now() - t0) / 1000).toFixed(1)} s.` : `Aucun placement valide : ${out.message || ''}`;
  } catch (e) {
    st.textContent = 'Appel du solveur impossible : ' + (e && e.message ? e.message : e);
  } finally { btn.disabled = false; render(); }
}

function revenirSolveur() {
  if (!state.placementSolveur) return;
  for (const p of state.paras) { const s = state.placementSolveur[p.nom]; p.place = s ? s.place : null; p.pos = s && s.pos ? { ...s.pos } : null; }
  state.modifie = false; render();
}

function telecharger() {
  const a = avion();
  const data = { avion: a.id, variante: state.varianteId, pesee: state.peseeId, masse_vide: a.masse_vide, bras_vide: a.bras_vide, nom_local: state.nomLocal || null, parametres: params(), paras: state.paras, options: state.options,
    enveloppe_utilisee: { mtow: a.mtow, ...a.enveloppe, modifiee: !!state.enveloppes[cleEnv()] },
    entree_solveur: state.derniereEntree || C.stickPourSolveur(a, params(), state.paras, state.options), resultat_solveur: state.resultat,
    placement_actuel: state.paras.map((p) => ({ nom: p.nom, place: p.place, pos: p.pos })),
    etapes_actuelles: C.etapes(a, params(), parasPlaces(), a.places, state.options.etapes === 'toutes' ? 'toutes' : 'premier_groupe').etapes };
  const blob = new Blob([JSON.stringify(data, null, 1)], { type: 'application/json' });
  const url = URL.createObjectURL(blob); const l = document.createElement('a'); l.href = url; l.download = `centrage_${a.id}_${new Date().toISOString().slice(0, 16).replace(/[:T]/g, '-')}.json`; l.click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
}

function changerAvion(id) {
  const a = AVIONS.find((x) => x.id === id); if (!a) return;
  state.avionId = id; state.varianteId = a.variante_defaut; state.peseeId = a.pesees && a.pesees[0] ? a.pesees[0].id : null; state.masseVide = null; state.brasVide = null; state.carburant = a.carburant.defaut; state.piloteKg = a.pilote.masse_kg_defaut; state.porteOuverte = false;
  for (const p of state.paras) { p.place = null; p.pos = null; p.verrou = null; }
  state.resultat = null; state.placementSolveur = null; state.modifie = false; render();
}

// ---------------------------------------------------------------- branchements
function brancher() {
  $('#selAvion').innerHTML = AVIONS.map((a) => `<option value="${esc(a.id)}">${esc(a.libelle)}</option>`).join('');
  $('#selAvion').addEventListener('change', (e) => changerAvion(e.target.value));
  $('#selVariante').addEventListener('change', (e) => { state.varianteId = e.target.value; state.resultat = null; render(); });
  $('#selPesee').addEventListener('change', (e) => { state.peseeId = e.target.value; state.masseVide = null; state.brasVide = null; state.resultat = null; render(); });
  $('#inPorte').addEventListener('change', (e) => { state.porteOuverte = e.target.checked; render(); });
  $('#btnMiseEnPlace').addEventListener('click', () => { state.paras = C.miseEnPlace(avion(), state.paras, 2); state.modifie = true; render(); });
  $('#inNomLocal').addEventListener('change', (e) => { state.nomLocal = e.target.value.trim().slice(0, 40); render(); });
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
    else if (k === 'verrou') {
      const v = t.value || null;
      if (v === 'libre') { if (!p.pos) { const a = avion(); const rg = a.rangees[0]; p.pos = { x: p.place ? a.places.find((s) => s.id === p.place).x : (rg.xmin + rg.xmax) / 2, y: rg.y }; p.place = null; } p.verrou = 'libre'; }
      else if (v) { const occ = state.paras.find((q) => q !== p && q.place === v); if (occ) { occ.place = p.place; occ.pos = p.pos; } p.place = v; p.pos = null; p.verrou = v; state.modifie = true; }
      else p.verrou = null;
    }
    else if (k === 'masseKg' || k === 'sortie') { p[k] = t.value === '' ? '' : Number(t.value); }
    else { p[k] = t.value.trim(); if (k === 'tandem' && !p.tandem) p.role = ''; if (k === 'tandem' && p.tandem && !p.role) p.role = 'porteur'; }
    render();
  });
  $('#tblParas').addEventListener('click', (e) => { const b = e.target.closest('button[data-k="suppr"]'); if (!b) return; state.paras.splice(Number(b.dataset.i), 1); render(); });
  $('#btnAjouter').addEventListener('click', () => { const n = state.paras.length + 1; state.paras.push({ ...genererParas(1, Number($('#genKg').value) || 90)[0], nom: `P${n}` }); render(); });
  $('#btnGenerer').addEventListener('click', () => { state.paras = genererParas(Number($('#genN').value) || 10, Number($('#genKg').value) || 90); state.resultat = null; state.placementSolveur = null; state.modifie = false; render(); });
  $('#btnVider').addEventListener('click', () => { for (const p of state.paras) { p.place = null; p.pos = null; p.verrou = null; } state.modifie = !!state.placementSolveur; render(); });
  $('#btnExemple').addEventListener('click', () => { state = { ...defaut(), enveloppes: state.enveloppes, avionId: EXEMPLE.avionId, varianteId: EXEMPLE.varianteId, peseeId: 'A', piloteKg: EXEMPLE.piloteKg, carburant: EXEMPLE.carburant, paras: EXEMPLE.paras.map((p) => ({ groupe: '', sortie: '', tandem: '', role: '', interdit: [], verrou: null, place: null, pos: null, ...p })) }; render(); });
  $('#btnCalculer').addEventListener('click', calculer);
  $('#btnRevenir').addEventListener('click', revenirSolveur);
  $('#btnJson').addEventListener('click', telecharger);
  $('#btnReset').addEventListener('click', () => { localStorage.removeItem(KEY); state = defaut(); render(); });
  // enveloppe
  $('#envEdit').addEventListener('toggle', () => render());
  $('#btnEnvAppliquer').addEventListener('click', appliquerTableEnveloppe);
  $('#btnEnvReset').addEventListener('click', () => { delete state.enveloppes[cleEnv()]; state.resultat = null; $('#envStatut').textContent = 'Enveloppe du manuel retablie.'; render(); });
  $('#btnEnvAjouter').addEventListener('click', () => { const a = avion(); const env = JSON.parse(JSON.stringify(a.enveloppe)); const last = env.avant[env.avant.length - 1]; env.avant.push([last[0], last[1]]); state.enveloppes[cleEnv()] = { mtow: a.mtow, enveloppe: env }; render(); });
  $('#btnEnvAjouterAr').addEventListener('click', () => { const a = avion(); const env = JSON.parse(JSON.stringify(a.enveloppe)); const last = env.arriere[env.arriere.length - 1]; env.arriere.push([last[0], last[1]]); state.enveloppes[cleEnv()] = { mtow: a.mtow, enveloppe: env }; render(); });
  $('#tblEnv').addEventListener('click', (e) => { const b = e.target.closest('button[data-suppr]'); if (!b) return; const a = avion(); const env = JSON.parse(JSON.stringify(a.enveloppe)); if (env[b.dataset.lim].length <= 1) return; env[b.dataset.lim].splice(Number(b.dataset.i), 1); state.enveloppes[cleEnv()] = { mtow: a.mtow, enveloppe: env }; render(); });
}

brancher();
render();
