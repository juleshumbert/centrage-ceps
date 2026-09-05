// cabine.js : rendu SVG de la cabine (vue de dessus, nez a gauche, cote droit en bas) avec
// glisser-deposer des paras (sur une place fixe ou en position libre le long d'une rangee),
// et rendu du centrogramme avec sommets d'enveloppe deplacables. DOM seulement, pas d'etat.
const NS = 'http://www.w3.org/2000/svg';
export const PALETTE = ['#1f77b4', '#e8a020', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#17becf', '#bcbd22', '#5c6f82'];

function el(tag, attrs = {}, text) {
  const n = document.createElementNS(NS, tag);
  for (const [k, v] of Object.entries(attrs)) if (v != null) n.setAttribute(k, v);
  if (text != null) n.textContent = text;
  return n;
}
const pointeur = (svg, ev) => { const m = svg.getScreenCTM().inverse(); const p = new DOMPoint(ev.clientX, ev.clientY).matrixTransform(m); return { x: p.x, y: p.y }; };

export function groupesDe(paras) { return [...new Set(paras.map((p) => p.groupe).filter(Boolean))]; }
export function couleurGroupe(groupe, groupes) { return groupe ? PALETTE[groupes.indexOf(groupe) % PALETTE.length] : '#52616f'; }
export function fmt(x, avion) { return avion.unites.bras === 'm' ? x.toFixed(2) : Math.round(x).toString(); }

function pasGraduation(etendue) {
  const brut = etendue / 10, p = Math.pow(10, Math.floor(Math.log10(brut)));
  return [1, 2, 2.5, 5, 10].map((k) => k * p).find((s) => s >= brut) || 10 * p;
}
function pitchMin(places) {
  let m = Infinity;
  for (const a of places) for (const b of places) if (a !== b && Math.abs(a.y - b.y) < 1e-9) m = Math.min(m, Math.abs(a.x - b.x));
  return Number.isFinite(m) && m > 0 ? m : 1;
}

/**
 * Dessine la maquette : fuselage complet (schema `avion.dessin`, nez a gauche, cote droit en bas),
 * aile, empennage, porte, rangees (dont la rangee exterieure cote porte), places, paras, fleche du CG
 * et limites de centrage a la masse courante.
 *  paras : [{nom, masseKg, groupe, sortie, place, pos:{x,y}, verrou}]
 *  opts.onDeplacer(nom, cible) : cible = {place: id} ou {pos: {x, y}} ; opts.onClic(nom) ; opts.onSurvol(texte | null)
 *  opts.cg : {cg, avant, arriere, statut} (etat au decollage) pour la fleche et les limites
 */
export function dessinerCabine(svg, avion, paras, opts = {}) {
  svg.replaceChildren();
  const cab = avion.cabine, places = avion.places, rangees = avion.rangees || [];
  const dess = avion.dessin || { fuselage: [[cab.x0, Math.max(...cab.zones.map((z) => z.largeur)) / 2], [cab.x1, Math.max(...cab.zones.map((z) => z.largeur)) / 2]], blocs: [], graduations: [] };
  const W = 960, margeG = 56, margeD = 24;
  const x0 = Math.min(cab.x0, dess.fuselage[0][0]), x1 = Math.max(cab.x1, dess.fuselage[dess.fuselage.length - 1][0]);
  const demiLarg = Math.max(...dess.fuselage.map((p) => p[1]), ...cab.zones.map((z) => z.largeur / 2));
  const yExt = Math.max(...rangees.map((r) => Math.abs(r.y)), demiLarg);
  const demiTotal = Math.max(yExt + demiLarg * 0.5, (dess.empennage ? dess.empennage.demi_envergure : 0) * 0.42, demiLarg * 1.4);
  const ech = (W - margeG - margeD) / (x1 - x0);
  const echY = Math.min(ech * 2.4, 300 / demiTotal);   // etirement lateral admis : c'est un schema
  const hCab = 2 * demiTotal * echY;
  const yMil = 34 + hCab / 2;
  const px = (x) => margeG + (x - x0) * ech, py = (y) => yMil + y * echY;
  const ax = (X) => x0 + (X - margeG) / ech;
  const estPlace = (p) => places.some((s) => s.id === p.place) || (p.pos && Number.isFinite(p.pos.x));
  const nonPlaces = paras.filter((p) => !estPlace(p));
  const hBanc = nonPlaces.length ? 112 : 0;
  const H = 34 + hCab + 58 + hBanc;
  svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
  const groupes = groupesDe(paras);
  const r = Math.max(11, Math.min(20, pitchMin(places) * ech * 0.42));
  const demiA = (x) => { const f = dess.fuselage; if (x <= f[0][0]) return f[0][1]; for (let i = 1; i < f.length; i++) if (x <= f[i][0]) { const [xa, ya] = f[i - 1], [xb, yb] = f[i]; return ya + (yb - ya) * (x - xa) / (xb - xa); } return f[f.length - 1][1]; };

  // aile et empennage (sous le fuselage)
  if (dess.aile) {
    const env = Math.max(demiTotal, demiLarg * 1.3);
    for (const sg of [-1, 1]) svg.appendChild(el('polygon', { points: `${px(dess.aile.x0)},${py(sg * demiA(dess.aile.x0))} ${px(dess.aile.x0 + (dess.aile.x1 - dess.aile.x0) * 0.15)},${py(sg * env)} ${px(dess.aile.x1)},${py(sg * env)} ${px(dess.aile.x1)},${py(sg * demiA(dess.aile.x1))}`, fill: '#c8d6e8', stroke: 'var(--line-2)', 'stroke-width': 1 }));
  }
  if (dess.empennage) {
    const e = dess.empennage, env = Math.min(demiTotal, e.demi_envergure * 0.42);
    for (const sg of [-1, 1]) svg.appendChild(el('polygon', { points: `${px(e.x0)},${py(sg * demiA(e.x0))} ${px(e.x0 + (e.x1 - e.x0) * 0.4)},${py(sg * env)} ${px(e.x1)},${py(sg * env)} ${px(e.x1)},${py(sg * demiA(e.x1))}`, fill: '#c8d6e8', stroke: 'var(--line-2)', 'stroke-width': 1 }));
  }
  // fuselage : profil en plan, symetrique
  const f = dess.fuselage;
  const contour = [...f.map(([x, d]) => `${px(x)},${py(-d)}`), ...f.slice().reverse().map(([x, d]) => `${px(x)},${py(d)}`)].join(' ');
  svg.appendChild(el('polygon', { points: contour, fill: 'var(--surface-2)', stroke: 'var(--ink-2)', 'stroke-width': 1.6 }));
  // zones cabine (trapezes) et blocs
  for (const z of cab.zones) {
    if (cab.zones.length > 1) {
      svg.appendChild(el('line', { x1: px(z.x0), x2: px(z.x0), y1: py(-demiA(z.x0)), y2: py(demiA(z.x0)), stroke: 'var(--line-2)', 'stroke-width': 1 }));
      svg.appendChild(el('text', { x: (px(z.x0) + px(z.x1)) / 2, y: py(-demiA((z.x0 + z.x1) / 2)) + 10, class: 'cab-zone', 'text-anchor': 'middle' }, z.nom));
    }
  }
  svg.appendChild(el('line', { x1: px(cab.x1), x2: px(cab.x1), y1: py(-demiA(cab.x1)), y2: py(demiA(cab.x1)), stroke: 'var(--line-2)', 'stroke-width': 1 }));
  for (const b of dess.blocs || []) {
    if (b.y0 != null) svg.appendChild(el('rect', { x: px(b.x0), y: py(Math.min(b.y0, b.y1)), width: (b.x1 - b.x0) * ech, height: Math.abs(b.y1 - b.y0) * echY, fill: '#2d6a9f', opacity: 0.18 }));
  }
  for (const rg of rangees) {
    svg.appendChild(el('line', { x1: px(rg.xmin), x2: px(rg.xmax), y1: py(rg.y), y2: py(rg.y), stroke: rg.exterieur ? 'var(--amber)' : 'var(--line-2)', 'stroke-dasharray': '6 5', 'stroke-width': rg.exterieur ? 1.5 : 1 }));
    svg.appendChild(el('text', { x: px(rg.xmin) - 4, y: py(rg.y) + 4, class: 'cab-side', 'text-anchor': 'end' }, rg.libelle));
  }
  svg.appendChild(el('text', { x: px(x0) + 4, y: yMil - 6, class: 'cab-avant' }, 'avant'));
  if (cab.porte) {
    const cote = cab.porte.cote === 'droite' ? 1 : -1;
    const yP = (x) => py(cote * (demiA(x) + 1.5 * (demiLarg / 30)));
    svg.appendChild(el('line', { x1: px(cab.porte.x0), x2: px(cab.porte.x1), y1: yP(cab.porte.x0), y2: yP(cab.porte.x1), stroke: 'var(--amber)', 'stroke-width': 5, 'stroke-linecap': 'round' }));
    svg.appendChild(el('text', { x: (px(cab.porte.x0) + px(cab.porte.x1)) / 2, y: yP((cab.porte.x0 + cab.porte.x1) / 2) + (cote > 0 ? 15 : -8), class: 'cab-porte', 'text-anchor': 'middle' }, 'porte'));
  }
  // graduations des bras
  const grads = dess.graduations && dess.graduations.length ? dess.graduations : (() => { const st = pasGraduation(x1 - x0), out = []; for (let x = Math.ceil(x0 / st) * st; x <= x1 + 1e-9; x += st) out.push(x); return out; })();
  const yG = 34 + hCab;
  for (const x of grads) {
    svg.appendChild(el('line', { x1: px(x), x2: px(x), y1: yG + 4, y2: yG + 9, stroke: 'var(--line-2)' }));
    svg.appendChild(el('text', { x: px(x), y: yG + 20, class: 'cab-grad', 'text-anchor': 'middle' }, fmt(x, avion)));
  }
  // reperes : bord d'attaque de la MAC, limites avant et arriere a la masse courante, fleche du CG
  if (avion.mac) {
    svg.appendChild(el('line', { x1: px(avion.mac.lemac), x2: px(avion.mac.lemac), y1: 14, y2: yG, stroke: 'var(--muted)', 'stroke-dasharray': '2 3', opacity: 0.7 }));
    svg.appendChild(el('text', { x: px(avion.mac.lemac), y: yG + 32, class: 'cab-grad', 'text-anchor': 'middle' }, 'BA MAC'));
  }
  if (opts.cg) {
    const c = opts.cg;
    for (const [x, lab, anc, dx] of [[c.avant, 'LIM AV', 'end', -3], [c.arriere, 'LIM AR', 'start', 3]]) {
      svg.appendChild(el('line', { x1: px(x), x2: px(x), y1: 14, y2: yG, stroke: 'var(--danger)', 'stroke-dasharray': '4 3', opacity: 0.8 }));
      svg.appendChild(el('text', { x: px(x) + dx, y: 11, class: 'cab-grad', 'text-anchor': anc, fill: 'var(--danger)' }, `${lab} ${fmt(x, avion)}`));
    }
    const gx = px(c.cg), col = c.statut === 'ok' ? 'var(--ok)' : 'var(--danger)';
    svg.appendChild(el('line', { x1: gx, x2: gx, y1: 22, y2: yG, stroke: 'var(--amber)', 'stroke-width': 2.5, 'stroke-dasharray': '5 3' }));
    svg.appendChild(el('polygon', { points: `${gx},${yG} ${gx - 5},${yG - 10} ${gx + 5},${yG - 10}`, fill: 'var(--amber)' }));
    svg.appendChild(el('rect', { x: gx - 44, y: 16, width: 88, height: 15, rx: 4, fill: col }));
    svg.appendChild(el('text', { x: gx, y: 27, class: 'cg-lbl', 'text-anchor': 'middle' }, `CG ${avion.unites.bras === 'm' ? c.cg.toFixed(3) : c.cg.toFixed(1)} ${avion.unites.bras}`));
  }
  // places
  const gPlaces = el('g');
  for (const s of places) {
    const g = el('g', { class: 'place', 'data-place': s.id });
    g.appendChild(el('circle', { cx: px(s.x), cy: py(s.y), r, fill: 'var(--surface)', stroke: 'var(--line-2)', 'stroke-dasharray': '3 3' }));
    g.appendChild(el('text', { x: px(s.x), y: py(s.y) + 4, class: 'place-id', 'text-anchor': 'middle' }, s.id));
    gPlaces.appendChild(g);
  }
  svg.appendChild(gPlaces);
  if (nonPlaces.length) {
    const yB = yG + 58 + 34;
    svg.appendChild(el('text', { x: margeG, y: yB - 38, class: 'cab-side' }, 'paras sans place (a glisser dans la cabine ou sur la ligne exterieure)'));
    nonPlaces.forEach((p, i) => { p._cx = margeG + r + i * (2 * r + 10); p._cy = yB; });
  }
  const gParas = el('g');
  for (const p of paras) {
    const s = places.find((q) => q.id === p.place);
    const libre = !s && p.pos && Number.isFinite(p.pos.x);
    const cx = s ? px(s.x) : libre ? px(p.pos.x) : p._cx, cy = s ? py(s.y) : libre ? py(p.pos.y || 0) : p._cy;
    if (cx == null) continue;
    const g = el('g', { class: 'para' + (p.verrou ? ' verrou' : '') + (libre ? ' libre' : ''), 'data-nom': p.nom, style: 'cursor:grab' });
    g.appendChild(el('circle', { cx, cy, r: r - 1, fill: couleurGroupe(p.groupe, groupes), stroke: p.verrou ? 'var(--ink)' : '#fff', 'stroke-width': p.verrou ? 3 : 2, 'stroke-dasharray': libre ? '4 2' : null }));
    g.appendChild(el('text', { x: cx, y: cy + 4.5, class: 'para-num', 'text-anchor': 'middle' }, p.sortie != null && p.sortie !== '' ? String(p.sortie) : '·'));
    g.appendChild(el('text', { x: cx, y: cy - r - 4, class: 'para-nom', 'text-anchor': 'middle' }, `${p.nom} ${Math.round(p.masseKg)}`));
    if (p.verrou) g.appendChild(el('text', { x: cx + r - 4, y: cy - r + 8, class: 'para-lock' }, '🔒'));
    const ou = s ? `place ${s.id} (bras ${fmt(s.x, avion)} ${avion.unites.bras})` : libre ? `position libre, bras ${fmt(p.pos.x, avion)} ${avion.unites.bras}` : 'sans place';
    g.dataset.info = `${p.nom}, ${p.masseKg} kg${p.groupe ? ', groupe ' + p.groupe : ''}${p.sortie != null && p.sortie !== '' ? ', sortie ' + p.sortie : ''}, ${ou}${p.verrou ? ', verrouille' : ''}. Glisser pour deplacer (place, rangee ou ligne exterieure), cliquer pour (de)verrouiller.`;
    gParas.appendChild(g);
  }
  svg.appendChild(gParas);

  // ---- glisser-deposer
  let drag = null;
  const placeSous = (o) => { let best = null, bd = Infinity; for (const s of places) { const d = Math.hypot(px(s.x) - o.x, py(s.y) - o.y); if (d < bd) { bd = d; best = s; } } return bd <= r * 1.15 ? best : null; };
  const rangeeSous = (o) => { let best = null, bd = Infinity; for (const rg of rangees) { const d = Math.abs(py(rg.y) - o.y); if (d < bd) { bd = d; best = rg; } } return bd <= Math.max(r * 2.2, 26) ? best : null; };
  const cibleSous = (o) => {
    const s = placeSous(o); if (s) return { place: s.id, X: px(s.x), Y: py(s.y) };
    const rg = rangeeSous(o); if (!rg) return null;
    const x = Math.min(rg.xmax, Math.max(rg.xmin, ax(o.x)));
    return { pos: { x: Math.round(x * 1000) / 1000, y: rg.y }, X: px(x), Y: py(rg.y), rangee: rg };
  };
  const survolPlaces = (id) => svg.querySelectorAll('g.place circle').forEach((c) => c.setAttribute('stroke', c.parentNode.dataset.place === id ? 'var(--cyan)' : 'var(--line-2)'));
  svg.onpointerdown = (ev) => {
    const g = ev.target.closest('g.para'); if (!g) return;
    ev.preventDefault();
    const o = pointeur(svg, ev);
    drag = { nom: g.dataset.nom, g, x0: o.x, y0: o.y, bouge: false, ghost: null, marque: null };
    svg.setPointerCapture(ev.pointerId);
  };
  svg.onpointermove = (ev) => {
    if (drag) {
      const o = pointeur(svg, ev); const dx = o.x - drag.x0, dy = o.y - drag.y0;
      if (!drag.bouge && Math.hypot(dx, dy) > 4) {
        drag.bouge = true;
        drag.ghost = drag.g.cloneNode(true); drag.ghost.setAttribute('opacity', '0.85'); drag.ghost.style.pointerEvents = 'none'; svg.appendChild(drag.ghost);
        drag.marque = el('circle', { r: r + 3, fill: 'none', stroke: 'var(--cyan)', 'stroke-width': 2, 'pointer-events': 'none' }); svg.appendChild(drag.marque);
        drag.g.setAttribute('opacity', '0.35');
      }
      if (drag.bouge) {
        drag.ghost.setAttribute('transform', `translate(${dx} ${dy})`);
        const c = cibleSous(o);
        survolPlaces(c && c.place);
        if (c) { drag.marque.setAttribute('cx', c.X); drag.marque.setAttribute('cy', c.Y); drag.marque.removeAttribute('visibility'); }
        else drag.marque.setAttribute('visibility', 'hidden');
        if (opts.onSurvol) opts.onSurvol(c ? (c.place ? `→ place ${c.place}` : `→ ${c.rangee.libelle}, bras ${fmt(c.pos.x, avion)} ${avion.unites.bras}`) : 'relacher ici : annule');
      }
      return;
    }
    const g = ev.target.closest && ev.target.closest('g.para');
    if (opts.onSurvol) opts.onSurvol(g ? g.dataset.info : null);
  };
  const fin = (ev) => {
    if (!drag) return;
    const d = drag; drag = null;
    if (d.ghost) d.ghost.remove(); if (d.marque) d.marque.remove();
    d.g.removeAttribute('opacity'); survolPlaces(null);
    if (!d.bouge) { opts.onClic && opts.onClic(d.nom); return; }
    const c = cibleSous(pointeur(svg, ev));
    if (c && opts.onDeplacer) opts.onDeplacer(d.nom, c.place ? { place: c.place } : { pos: c.pos });
    else if (opts.onSurvol) opts.onSurvol(null);
  };
  svg.onpointerup = fin; svg.onpointercancel = fin;
  svg.onpointerleave = () => { if (!drag && opts.onSurvol) opts.onSurvol(null); };
}

/**
 * Centrogramme : enveloppe (polygone) et points {label, masse, cg, statut} relies dans l'ordre.
 * opts.editable : les sommets de l'enveloppe sont deplacables ; opts.onSommet(limite, index, [masse, bras])
 * est appele au relacher ('avant' | 'arriere'). opts.mtowEditable : la ligne MTOW aussi (onMtow(valeur)).
 */
export function dessinerCentrogramme(svg, avion, points, opts = {}) {
  svg.replaceChildren();
  const W = 520, H = 360, mL = 62, mR = 56, mT = 34, mB = 44;
  const av = avion.enveloppe.avant, ar = avion.enveloppe.arriere, mtow = avion.mtow;
  const mMin = Math.min(avion.masse_vide, av[0][0]) * 0.97;
  const mMax = Math.max(mtow, ...av.map((p) => p[0]), ...ar.map((p) => p[0]), ...points.map((p) => p.masse)) * 1.04;
  const cgs = [...av.map((p) => p[1]), ...ar.map((p) => p[1]), ...points.map((p) => p.cg)];
  const cMin = Math.min(...cgs), cMax = Math.max(...cgs), cPad = Math.max((cMax - cMin) * 0.14, 1e-6);
  const cx0 = cMin - cPad, cx1 = cMax + cPad;
  const X = (c) => mL + (c - cx0) / (cx1 - cx0) * (W - mL - mR);
  const Y = (m) => H - mB - (m - mMin) / (mMax - mMin) * (H - mT - mB);
  const Xinv = (px) => cx0 + (px - mL) / (W - mL - mR) * (cx1 - cx0);
  const Yinv = (py) => mMin + (H - mB - py) / (H - mT - mB) * (mMax - mMin);
  svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
  const pasC = pasGraduation(cx1 - cx0), pasM = pasGraduation(mMax - mMin);
  for (let c = Math.ceil(cx0 / pasC) * pasC; c <= cx1; c += pasC) {
    svg.appendChild(el('line', { x1: X(c), x2: X(c), y1: mT, y2: H - mB, stroke: 'var(--line)' }));
    svg.appendChild(el('text', { x: X(c), y: H - mB + 14, class: 'ax', 'text-anchor': 'middle' }, avion.unites.bras === 'm' ? c.toFixed(2) : c.toFixed(0)));
    svg.appendChild(el('text', { x: X(c), y: mT - 6, class: 'ax ax-mac', 'text-anchor': 'middle' }, ((c - avion.mac.lemac) / avion.mac.longueur * 100).toFixed(0) + ' %'));
  }
  for (let m = Math.ceil(mMin / pasM) * pasM; m <= mMax; m += pasM) {
    svg.appendChild(el('line', { x1: mL, x2: W - mR, y1: Y(m), y2: Y(m), stroke: 'var(--line)' }));
    svg.appendChild(el('text', { x: mL - 5, y: Y(m) + 3, class: 'ax', 'text-anchor': 'end' }, Math.round(m)));
    svg.appendChild(el('text', { x: W - mR + 5, y: Y(m) + 3, class: 'ax ax-kg' }, Math.round(m * avion.kg_par_unite_masse) + ' kg'));
  }
  svg.appendChild(el('text', { x: (mL + W - mR) / 2, y: H - 6, class: 'ax-t', 'text-anchor': 'middle' }, `CG (${avion.unites.bras})   ·   en haut : % MAC`));
  svg.appendChild(el('text', { x: 12, y: mT - 6, class: 'ax-t' }, `masse (${avion.unites.masse})`));
  // enveloppe : limite avant de bas en haut, limite arriere de haut en bas, bornee a la MTOW
  const clipM = (pts) => { const out = pts.filter((p) => p[0] <= mtow); const last = pts[pts.length - 1]; if (!out.length || out[out.length - 1][0] < mtow) out.push([mtow, interpLoc(pts, mtow)]); return out; };
  const avant = clipM(av), arriere = clipM(ar);
  const poly = [[mMin, avant[0][1]], ...avant.filter((p) => p[0] > mMin), ...arriere.slice().reverse(), [mMin, arriere[0][1]]];
  svg.appendChild(el('path', { d: poly.map((p, i) => `${i ? 'L' : 'M'}${X(p[1]).toFixed(1)} ${Y(p[0]).toFixed(1)}`).join(' ') + ' Z', fill: 'rgba(63,182,214,.12)', stroke: 'var(--cyan-d)', 'stroke-width': 1.6 }));
  svg.appendChild(el('line', { x1: mL, x2: W - mR, y1: Y(mtow), y2: Y(mtow), stroke: 'var(--danger)', 'stroke-dasharray': '5 4', class: opts.editable ? 'mtow-line' : null }));
  svg.appendChild(el('text', { x: W - mR - 4, y: Y(mtow) - 4, class: 'ax', 'text-anchor': 'end', fill: 'var(--danger)' }, 'MTOW ' + mtow));
  if (points.length > 1) svg.appendChild(el('polyline', { points: points.map((p) => `${X(p.cg)},${Y(p.masse)}`).join(' '), fill: 'none', stroke: 'var(--ink-2)', 'stroke-width': 1.4 }));
  points.forEach((p, i) => {
    const col = p.statut === 'ok' ? 'var(--ok)' : 'var(--danger)';
    svg.appendChild(el('circle', { cx: X(p.cg), cy: Y(p.masse), r: i === 0 ? 6 : 4.5, fill: col, stroke: '#fff', 'stroke-width': 1.5 }));
    const aDroite = X(p.cg) > W - mR - 80;
    svg.appendChild(el('text', { x: X(p.cg) + (aDroite ? -8 : 8), y: Y(p.masse) + (i % 2 ? 12 : -6), class: 'pt-lbl', 'text-anchor': aDroite ? 'end' : 'start' }, p.label));
  });
  if (!opts.editable) return;
  // sommets deplacables
  const gS = el('g', { class: 'sommets' });
  const poignee = (limite, i, p) => {
    const h = el('g', { class: 'sommet', 'data-limite': limite, 'data-i': i, style: 'cursor:move' });
    h.appendChild(el('rect', { x: X(p[1]) - 6, y: Y(p[0]) - 6, width: 12, height: 12, rx: 2, fill: '#fff', stroke: 'var(--cyan-d)', 'stroke-width': 1.5 }));
    h.appendChild(el('text', { x: X(p[1]) + 9, y: Y(p[0]) + 4, class: 'ax', fill: 'var(--cyan-d)' }, `${Math.round(p[0])} · ${avion.unites.bras === 'm' ? p[1].toFixed(3) : p[1].toFixed(2)}`));
    gS.appendChild(h);
  };
  av.forEach((p, i) => poignee('avant', i, p)); ar.forEach((p, i) => poignee('arriere', i, p));
  svg.appendChild(gS);
  let drag = null;
  svg.onpointerdown = (ev) => {
    const h = ev.target.closest('g.sommet'); if (!h) return;
    ev.preventDefault(); drag = { h, limite: h.dataset.limite, i: Number(h.dataset.i) }; svg.setPointerCapture(ev.pointerId);
  };
  svg.onpointermove = (ev) => {
    if (!drag) return;
    const o = pointeur(svg, ev);
    const rect = drag.h.querySelector('rect'); rect.setAttribute('x', o.x - 6); rect.setAttribute('y', o.y - 6);
    const t = drag.h.querySelector('text'); t.setAttribute('x', o.x + 9); t.setAttribute('y', o.y + 4);
    const m = Yinv(o.y), c = Xinv(o.x); t.textContent = `${Math.round(m)} · ${avion.unites.bras === 'm' ? c.toFixed(3) : c.toFixed(2)}`;
  };
  const fin = (ev) => {
    if (!drag) return; const d = drag; drag = null;
    const o = pointeur(svg, ev);
    const m = Math.round(Yinv(o.y)), c = avion.unites.bras === 'm' ? Math.round(Xinv(o.x) * 1000) / 1000 : Math.round(Xinv(o.x) * 100) / 100;
    if (opts.onSommet) opts.onSommet(d.limite, d.i, [m, c]);
  };
  svg.onpointerup = fin; svg.onpointercancel = fin;
}
function interpLoc(points, w) {
  if (w <= points[0][0]) return points[0][1];
  const n = points.length; if (w >= points[n - 1][0]) return points[n - 1][1];
  for (let i = 1; i < n; i++) { const [w0, v0] = points[i - 1], [w1, v1] = points[i]; if (w <= w1) return w1 === w0 ? v1 : v0 + (v1 - v0) * (w - w0) / (w1 - w0); }
  return points[n - 1][1];
}
