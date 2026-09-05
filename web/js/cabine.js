// cabine.js : rendu SVG de la cabine (vue de dessus, nez a gauche, cote droit en bas) avec
// glisser-deposer des paras entre les places, et rendu du centrogramme. DOM seulement, pas d'etat.
const NS = 'http://www.w3.org/2000/svg';
export const PALETTE = ['#1f77b4', '#e8a020', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#17becf', '#bcbd22', '#5c6f82'];

function el(tag, attrs = {}, text) {
  const n = document.createElementNS(NS, tag);
  for (const [k, v] of Object.entries(attrs)) if (v != null) n.setAttribute(k, v);
  if (text != null) n.textContent = text;
  return n;
}

export function groupesDe(paras) {
  return [...new Set(paras.map((p) => p.groupe).filter(Boolean))];
}
export function couleurGroupe(groupe, groupes) {
  if (!groupe) return '#52616f';
  return PALETTE[groupes.indexOf(groupe) % PALETTE.length];
}

/**
 * Dessine la cabine dans `svg`.
 *  avion : entree de AVIONS ; paras : [{nom, masseKg, groupe, sortie, place, verrou}]
 *  opts.onDeplacer(nom, placeId) : depot d'un para sur une place ; opts.onClic(nom) : clic sans deplacement.
 */
export function dessinerCabine(svg, avion, paras, opts = {}) {
  svg.replaceChildren();
  const cab = avion.cabine, places = avion.places;
  const W = 960, margeG = 56, margeD = 40;
  const x0 = cab.x0, x1 = cab.x1;
  const demiLarg = Math.max(...cab.zones.map((z) => z.largeur)) / 2;
  const ech = (W - margeG - margeD) / (x1 - x0);                // px par unite de bras
  const echY = Math.min(ech, 175 / demiLarg);                    // la cabine ne depasse pas 350 px de haut
  const hCab = 2 * demiLarg * echY;
  const yMil = 30 + hCab / 2;
  const nonPlaces = paras.filter((p) => !p.place || !places.some((s) => s.id === p.place));
  const hBanc = nonPlaces.length ? 112 : 0;
  const H = 30 + hCab + 48 + hBanc;
  svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
  const px = (x) => margeG + (x - x0) * ech;
  const py = (y) => yMil + y * echY;                             // y > 0 (droite) vers le bas

  const groupes = groupesDe(paras);
  const pas = pitchMin(places);
  const r = Math.max(12, Math.min(22, pas * ech * 0.42));

  // Fuselage : zones (largeur variable) et fleche « avant »
  for (const z of cab.zones) {
    svg.appendChild(el('rect', { x: px(z.x0), y: py(-z.largeur / 2), width: (z.x1 - z.x0) * ech, height: z.largeur * echY,
      fill: 'var(--surface-2)', stroke: 'var(--line-2)', 'stroke-width': 1 }));
    if (cab.zones.length > 1) svg.appendChild(el('text', { x: px(z.x0) + 4, y: py(-z.largeur / 2) + 11, class: 'cab-zone' }, z.nom.replace('ZONE ', 'Z')));
  }
  svg.appendChild(el('text', { x: margeG - 6, y: yMil + 4, class: 'cab-avant', 'text-anchor': 'end' }, 'avant'));
  svg.appendChild(el('text', { x: margeG - 6, y: py(-demiLarg) + 10, class: 'cab-side', 'text-anchor': 'end' }, 'gauche'));
  svg.appendChild(el('text', { x: margeG - 6, y: py(demiLarg) - 2, class: 'cab-side', 'text-anchor': 'end' }, 'droite'));
  // Porte
  if (cab.porte) {
    const yP = cab.porte.cote === 'droite' ? py(demiLarg) + 3 : py(-demiLarg) - 3;
    svg.appendChild(el('line', { x1: px(cab.porte.x0), x2: px(cab.porte.x1), y1: yP, y2: yP, stroke: 'var(--amber)', 'stroke-width': 5, 'stroke-linecap': 'round' }));
    svg.appendChild(el('text', { x: (px(cab.porte.x0) + px(cab.porte.x1)) / 2, y: cab.porte.cote === 'droite' ? yP + 14 : yP - 8, class: 'cab-porte', 'text-anchor': 'middle' }, 'porte'));
  }
  // Graduation des bras
  const step = pasGraduation(x1 - x0);
  for (let x = Math.ceil(x0 / step) * step; x <= x1 + 1e-9; x += step) {
    svg.appendChild(el('line', { x1: px(x), x2: px(x), y1: py(demiLarg) + 18, y2: py(demiLarg) + 23, stroke: 'var(--line-2)' }));
    svg.appendChild(el('text', { x: px(x), y: py(demiLarg) + 34, class: 'cab-grad', 'text-anchor': 'middle' }, fmt(x, avion)));
  }
  // Places
  const gPlaces = el('g');
  for (const s of places) {
    const g = el('g', { class: 'place', 'data-place': s.id });
    g.appendChild(el('circle', { cx: px(s.x), cy: py(s.y), r, fill: 'var(--surface)', stroke: 'var(--line-2)', 'stroke-dasharray': '3 3' }));
    g.appendChild(el('text', { x: px(s.x), y: py(s.y) + 4, class: 'place-id', 'text-anchor': 'middle' }, s.id));
    gPlaces.appendChild(g);
  }
  svg.appendChild(gPlaces);
  // Banc des paras non places
  if (nonPlaces.length) {
    const yB = 30 + hCab + 48 + 56;
    svg.appendChild(el('text', { x: margeG, y: yB - 40, class: 'cab-side' }, 'paras sans place (a glisser sur une place)'));
    nonPlaces.forEach((p, i) => { p._cx = margeG + r + i * (2 * r + 10); p._cy = yB; });
  }
  // Paras
  const gParas = el('g');
  for (const p of paras) {
    const s = places.find((q) => q.id === p.place);
    const cx = s ? px(s.x) : p._cx, cy = s ? py(s.y) : p._cy;
    if (cx == null) continue;
    const g = el('g', { class: 'para' + (p.verrou ? ' verrou' : ''), 'data-nom': p.nom, style: 'cursor:grab' });
    g.appendChild(el('circle', { cx, cy, r: r - 1, fill: couleurGroupe(p.groupe, groupes), stroke: p.verrou ? 'var(--ink)' : '#fff', 'stroke-width': p.verrou ? 3 : 2 }));
    g.appendChild(el('text', { x: cx, y: cy + 4.5, class: 'para-num', 'text-anchor': 'middle' }, p.sortie != null && p.sortie !== '' ? String(p.sortie) : '·'));
    g.appendChild(el('text', { x: cx, y: cy - r - 4, class: 'para-nom', 'text-anchor': 'middle' }, `${p.nom} ${Math.round(p.masseKg)}`));
    if (p.verrou) g.appendChild(el('text', { x: cx + r - 4, y: cy - r + 8, class: 'para-lock' }, '🔒'));
    // Pas de <title> SVG : l'info-bulle native gele le rendu de certains Chrome ; le survol passe par opts.onSurvol.
    g.dataset.info = `${p.nom}, ${p.masseKg} kg${p.groupe ? ', groupe ' + p.groupe : ''}${p.sortie != null && p.sortie !== '' ? ', sortie ' + p.sortie : ''}${s ? ', place ' + s.id + ' (bras ' + fmt(s.x, avion) + ' ' + avion.unites.bras + ')' : ', sans place'}${p.verrou ? ', verrouille' : ''}. Glisser pour deplacer, cliquer pour (de)verrouiller.`;
    gParas.appendChild(g);
  }
  svg.appendChild(gParas);
  delete svg._drag;
  brancherDrag(svg, avion, paras, { px, py, r, places, opts });
}

function pitchMin(places) {
  let m = Infinity;
  for (const a of places) for (const b of places) if (a !== b && Math.abs(a.y - b.y) < 1e-9) m = Math.min(m, Math.abs(a.x - b.x));
  return Number.isFinite(m) && m > 0 ? m : (Math.max(...places.map((p) => p.x)) - Math.min(...places.map((p) => p.x))) / Math.max(1, places.length - 1);
}
function pasGraduation(etendue) {
  const brut = etendue / 10, p = Math.pow(10, Math.floor(Math.log10(brut)));
  return [1, 2, 2.5, 5, 10].map((k) => k * p).find((s) => s >= brut) || 10 * p;
}
export function fmt(x, avion) {
  return avion.unites.bras === 'm' ? x.toFixed(2) : Math.round(x).toString();
}

function brancherDrag(svg, avion, paras, ctx) {
  const { px, py, r, places, opts } = ctx;
  let drag = null;
  const pt = (ev) => { const m = svg.getScreenCTM().inverse(); const p = new DOMPoint(ev.clientX, ev.clientY).matrixTransform(m); return { x: p.x, y: p.y }; };
  svg.onpointerdown = (ev) => {
    const g = ev.target.closest('g.para'); if (!g) return;
    ev.preventDefault();
    const o = pt(ev);
    drag = { nom: g.dataset.nom, g, x0: o.x, y0: o.y, dx: 0, dy: 0, bouge: false, ghost: null };
    svg.setPointerCapture(ev.pointerId);
  };
  svg.onpointermove = (ev) => {
    if (!drag) return;
    const o = pt(ev); drag.dx = o.x - drag.x0; drag.dy = o.y - drag.y0;
    if (!drag.bouge && Math.hypot(drag.dx, drag.dy) > 4) {
      drag.bouge = true;
      drag.ghost = drag.g.cloneNode(true); drag.ghost.setAttribute('opacity', '0.85'); drag.ghost.style.pointerEvents = 'none';
      svg.appendChild(drag.ghost); drag.g.setAttribute('opacity', '0.35');
    }
    if (drag.bouge) {
      drag.ghost.setAttribute('transform', `translate(${drag.dx} ${drag.dy})`);
      const cible = placeSous(o);
      svg.querySelectorAll('g.place circle').forEach((c) => c.setAttribute('stroke', 'var(--line-2)'));
      if (cible) svg.querySelector(`g.place[data-place="${CSS.escape(cible.id)}"] circle`).setAttribute('stroke', 'var(--cyan)');
    }
  };
  const fin = (ev) => {
    if (!drag) return;
    const d = drag; drag = null;
    if (d.ghost) d.ghost.remove();
    d.g.removeAttribute('opacity');
    if (!d.bouge) { opts.onClic && opts.onClic(d.nom); return; }
    const o = pt(ev); const cible = placeSous(o);
    if (cible && opts.onDeplacer) opts.onDeplacer(d.nom, cible.id);
    else svg.querySelectorAll('g.place circle').forEach((c) => c.setAttribute('stroke', 'var(--line-2)'));
  };
  svg.onpointerup = fin; svg.onpointercancel = fin;
  svg.onpointerover = (ev) => { const g = ev.target.closest && ev.target.closest('g.para'); if (g && opts.onSurvol) opts.onSurvol(g.dataset.info); };
  svg.onpointerout = (ev) => { const g = ev.target.closest && ev.target.closest('g.para'); if (g && opts.onSurvol) opts.onSurvol(null); };
  function placeSous(o) {
    let best = null, bd = Infinity;
    for (const s of places) { const d = Math.hypot(px(s.x) - o.x, py(s.y) - o.y); if (d < bd) { bd = d; best = s; } }
    return bd <= r * 1.6 ? best : null;
  }
}

/**
 * Centrogramme : enveloppe (polygone) et points {label, masse, cg, statut} relies dans l'ordre.
 */
export function dessinerCentrogramme(svg, avion, points) {
  svg.replaceChildren();
  const W = 520, H = 360, mL = 62, mR = 56, mT = 34, mB = 44;
  const av = avion.enveloppe.avant, ar = avion.enveloppe.arriere, mtow = avion.mtow;
  const mMin = Math.min(avion.masse_vide, av[0][0]) * 0.97;
  const mMax = mtow * 1.03;
  const cgs = [...av.map((p) => p[1]), ...ar.map((p) => p[1]), ...points.map((p) => p.cg)];
  const cMin = Math.min(...cgs), cMax = Math.max(...cgs), cPad = Math.max((cMax - cMin) * 0.12, 1e-6);
  const cx0 = cMin - cPad, cx1 = cMax + cPad;
  const X = (c) => mL + (c - cx0) / (cx1 - cx0) * (W - mL - mR);
  const Y = (m) => H - mB - (m - mMin) / (mMax - mMin) * (H - mT - mB);
  svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
  // grille + axes
  const pasC = pasGraduation(cx1 - cx0), pasM = pasGraduation(mMax - mMin);
  for (let c = Math.ceil(cx0 / pasC) * pasC; c <= cx1; c += pasC) {
    svg.appendChild(el('line', { x1: X(c), x2: X(c), y1: mT, y2: H - mB, stroke: 'var(--line)' }));
    svg.appendChild(el('text', { x: X(c), y: H - mB + 14, class: 'ax', 'text-anchor': 'middle' }, fmtCg(c, avion)));
    svg.appendChild(el('text', { x: X(c), y: mT - 6, class: 'ax ax-mac', 'text-anchor': 'middle' }, ((c - avion.mac.lemac) / avion.mac.longueur * 100).toFixed(0) + ' %'));
  }
  for (let m = Math.ceil(mMin / pasM) * pasM; m <= mMax; m += pasM) {
    svg.appendChild(el('line', { x1: mL, x2: W - mR, y1: Y(m), y2: Y(m), stroke: 'var(--line)' }));
    svg.appendChild(el('text', { x: mL - 5, y: Y(m) + 3, class: 'ax', 'text-anchor': 'end' }, Math.round(m)));
    svg.appendChild(el('text', { x: W - mR + 5, y: Y(m) + 3, class: 'ax ax-kg' }, Math.round(m * avion.kg_par_unite_masse) + ' kg'));
  }
  svg.appendChild(el('text', { x: (mL + W - mR) / 2, y: H - 6, class: 'ax-t', 'text-anchor': 'middle' }, `CG (${avion.unites.bras})   ·   en haut : % MAC`));
  svg.appendChild(el('text', { x: 12, y: mT - 6, class: 'ax-t' }, `masse (${avion.unites.masse})`));
  // enveloppe
  const avant = [...av]; if (avant[avant.length - 1][0] < mtow) avant.push([mtow, avant[avant.length - 1][1]]);
  const arriere = [...ar]; if (arriere[arriere.length - 1][0] < mtow) arriere.push([mtow, arriere[arriere.length - 1][1]]);
  const poly = [[mMin, avant[0][1]], ...avant.filter((p) => p[0] > mMin), ...arriere.filter((p) => p[0] <= mtow).reverse().map((p) => [Math.min(p[0], mtow), p[1]]), [mMin, arriere[0][1]]];
  const d = poly.map((p, i) => `${i ? 'L' : 'M'}${X(p[1]).toFixed(1)} ${Y(Math.min(p[0], mtow)).toFixed(1)}`).join(' ') + ' Z';
  svg.appendChild(el('path', { d, fill: 'rgba(63,182,214,.12)', stroke: 'var(--cyan-d)', 'stroke-width': 1.6 }));
  svg.appendChild(el('line', { x1: mL, x2: W - mR, y1: Y(mtow), y2: Y(mtow), stroke: 'var(--danger)', 'stroke-dasharray': '5 4' }));
  svg.appendChild(el('text', { x: W - mR - 4, y: Y(mtow) - 4, class: 'ax', 'text-anchor': 'end', fill: 'var(--danger)' }, 'MTOW ' + mtow));
  // points
  if (points.length > 1) svg.appendChild(el('polyline', { points: points.map((p) => `${X(p.cg)},${Y(p.masse)}`).join(' '), fill: 'none', stroke: 'var(--ink-2)', 'stroke-width': 1.4 }));
  points.forEach((p, i) => {
    const col = p.statut === 'ok' ? 'var(--ok)' : 'var(--danger)';
    svg.appendChild(el('circle', { cx: X(p.cg), cy: Y(p.masse), r: i === 0 ? 6 : 4.5, fill: col, stroke: '#fff', 'stroke-width': 1.5 }));
    const aDroite = X(p.cg) > W - mR - 80;
    svg.appendChild(el('text', { x: X(p.cg) + (aDroite ? -8 : 8), y: Y(p.masse) + (i % 2 ? 12 : -6), class: 'pt-lbl', 'text-anchor': aDroite ? 'end' : 'start' }, p.label));
  });
}
function fmtCg(c, avion) { return avion.unites.bras === 'm' ? c.toFixed(2) : c.toFixed(0); }
