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
 * Dessine la cabine. paras : [{nom, masseKg, groupe, sortie, place, pos:{x,y}, verrou}]
 *  opts.onDeplacer(nom, cible) : cible = {place: id} ou {pos: {x, y}} (bras et lateral en unites avion)
 *  opts.onClic(nom) ; opts.onSurvol(texte | null)
 */
export function dessinerCabine(svg, avion, paras, opts = {}) {
  svg.replaceChildren();
  const cab = avion.cabine, places = avion.places, rangees = avion.rangees || [];
  const W = 960, margeG = 56, margeD = 40;
  const x0 = cab.x0, x1 = cab.x1;
  const demiLarg = Math.max(...cab.zones.map((z) => z.largeur)) / 2;
  const ech = (W - margeG - margeD) / (x1 - x0);
  const echY = Math.min(ech, 175 / demiLarg);
  const hCab = 2 * demiLarg * echY;
  const yMil = 30 + hCab / 2;
  const px = (x) => margeG + (x - x0) * ech, py = (y) => yMil + y * echY;
  const ax = (X) => x0 + (X - margeG) / ech, ay = (Y) => (Y - yMil) / echY;
  const estPlace = (p) => places.some((s) => s.id === p.place) || (p.pos && Number.isFinite(p.pos.x));
  const nonPlaces = paras.filter((p) => !estPlace(p));
  const hBanc = nonPlaces.length ? 112 : 0;
  const H = 30 + hCab + 48 + hBanc;
  svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
  const groupes = groupesDe(paras);
  const r = Math.max(12, Math.min(22, pitchMin(places) * ech * 0.42));

  for (const z of cab.zones) {
    svg.appendChild(el('rect', { x: px(z.x0), y: py(-z.largeur / 2), width: (z.x1 - z.x0) * ech, height: z.largeur * echY, fill: 'var(--surface-2)', stroke: 'var(--line-2)', 'stroke-width': 1 }));
    if (cab.zones.length > 1) svg.appendChild(el('text', { x: px(z.x0) + 4, y: py(-z.largeur / 2) + 11, class: 'cab-zone' }, z.nom.replace('ZONE ', 'Z')));
  }
  for (const rg of rangees) {
    svg.appendChild(el('line', { x1: px(rg.xmin), x2: px(rg.xmax), y1: py(rg.y), y2: py(rg.y), stroke: 'var(--line-2)', 'stroke-dasharray': '6 5', 'stroke-width': 1 }));
  }
  svg.appendChild(el('text', { x: margeG - 6, y: yMil + 4, class: 'cab-avant', 'text-anchor': 'end' }, 'avant'));
  svg.appendChild(el('text', { x: margeG - 6, y: py(-demiLarg) + 10, class: 'cab-side', 'text-anchor': 'end' }, 'gauche'));
  svg.appendChild(el('text', { x: margeG - 6, y: py(demiLarg) - 2, class: 'cab-side', 'text-anchor': 'end' }, 'droite'));
  if (cab.porte) {
    const yP = cab.porte.cote === 'droite' ? py(demiLarg) + 3 : py(-demiLarg) - 3;
    svg.appendChild(el('line', { x1: px(cab.porte.x0), x2: px(cab.porte.x1), y1: yP, y2: yP, stroke: 'var(--amber)', 'stroke-width': 5, 'stroke-linecap': 'round' }));
    svg.appendChild(el('text', { x: (px(cab.porte.x0) + px(cab.porte.x1)) / 2, y: cab.porte.cote === 'droite' ? yP + 14 : yP - 8, class: 'cab-porte', 'text-anchor': 'middle' }, 'porte'));
  }
  const step = pasGraduation(x1 - x0);
  for (let x = Math.ceil(x0 / step) * step; x <= x1 + 1e-9; x += step) {
    svg.appendChild(el('line', { x1: px(x), x2: px(x), y1: py(demiLarg) + 18, y2: py(demiLarg) + 23, stroke: 'var(--line-2)' }));
    svg.appendChild(el('text', { x: px(x), y: py(demiLarg) + 34, class: 'cab-grad', 'text-anchor': 'middle' }, fmt(x, avion)));
  }
  const gPlaces = el('g');
  for (const s of places) {
    const g = el('g', { class: 'place', 'data-place': s.id });
    g.appendChild(el('circle', { cx: px(s.x), cy: py(s.y), r, fill: 'var(--surface)', stroke: 'var(--line-2)', 'stroke-dasharray': '3 3' }));
    g.appendChild(el('text', { x: px(s.x), y: py(s.y) + 4, class: 'place-id', 'text-anchor': 'middle' }, s.id));
    gPlaces.appendChild(g);
  }
  svg.appendChild(gPlaces);
  if (nonPlaces.length) {
    const yB = 30 + hCab + 48 + 56;
    svg.appendChild(el('text', { x: margeG, y: yB - 40, class: 'cab-side' }, 'paras sans place (a glisser dans la cabine)'));
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
    g.dataset.info = `${p.nom}, ${p.masseKg} kg${p.groupe ? ', groupe ' + p.groupe : ''}${p.sortie != null && p.sortie !== '' ? ', sortie ' + p.sortie : ''}, ${ou}${p.verrou ? ', verrouille' : ''}. Glisser pour deplacer (place ou position libre), cliquer pour (de)verrouiller.`;
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
    return { pos: { x: Math.round(x * 1000) / 1000, y: rg.y }, X: px(x), Y: py(rg.y) };
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
        if (opts.onSurvol) opts.onSurvol(c ? (c.place ? `→ place ${c.place}` : `→ position libre, bras ${fmt(c.pos.x, avion)} ${avion.unites.bras}`) : 'relacher ici : annule');
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
