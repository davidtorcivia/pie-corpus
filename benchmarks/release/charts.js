// Charts for the PIE benchmark release: plain SVG strings drawn to one scale per chart. Colors and type come from
// CSS tokens (var(--…)), so every chart follows the page theme. Hover text lives in data-tip on hit areas.
const SEGS = [
  { k: "inflection", label: "Inflection", w: 20 },
  { k: "paradigm", label: "Paradigms", w: 15 },
  { k: "en_pie", label: "English → PIE", w: 30 },
  { k: "pie_en", label: "PIE → English", w: 20 },
  { k: "dialogue", label: "Dialogue", w: 15 },
];
const FAM = {
  nemotron: { label: "PIE Nemotron 120B", c: "var(--c-nemotron)" },
  opus: { label: "Claude Opus 5.5", c: "var(--c-opus)" },
  sol: { label: "GPT-6.1 Sol", c: "var(--c-sol)" },
  qwen: { label: "PIE Qwen 35B", c: "var(--c-qwen)" },
  sonnet: { label: "Claude Sonnet 5.5", c: "var(--c-sonnet)" },
  terra: { label: "GPT-6.1 Terra", c: "var(--c-terra)" },
  haiku: { label: "Claude Haiku 5.5", c: "var(--c-haiku)" },
};
const BEST = ["ours-nemotron35-e3-bf16", "claude-opus-xhigh", "ours-merge-half", "codex-gpt-6.1-sol-high",
  "claude-sonnet-xhigh", "codex-gpt-6.1-terra-high", "claude-haiku-xhigh"];
const RUN = Object.fromEntries(DATA.runs.map(r => [r.id, r]));
const HERO = "ours-nemotron35-e3-bf16";
const f1 = v => v.toFixed(1);
const esc = s => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/"/g, "&quot;");
const tip = (title, rows) => esc(`<b>${title}</b>` + rows.map(([k, v]) => `<span>${k}</span><em>${v}</em>`).join(""));

// a horizontal bar whose data end (right) is rounded 4px, anchored square on the baseline (left)
function hbar(x0, y, w, h, fill) {
  const r = Math.min(4, w / 2, h / 2);
  if (w <= 0) return "";
  return `<path d="M${x0} ${y}h${w - r}a${r} ${r} 0 0 1 ${r} ${r}v${h - 2 * r}a${r} ${r} 0 0 1 ${-r} ${r}h${-(w - r)}z" fill="${fill}"/>`;
}
const barFill = r => r.id === HERO ? "var(--c-nemotron)" : r.ours ? "var(--c-ours-soft)" : "var(--bar)";

function gridX(x, top, bottom, ticks, fmt = v => v) {
  return ticks.map(t => `<line x1="${x(t)}" x2="${x(t)}" y1="${top}" y2="${bottom}" class="grid"/>` +
    `<text x="${x(t)}" y="${bottom + 18}" class="axis" text-anchor="middle">${fmt(t)}</text>`).join("");
}

// 1. Leaderboard: the pre-registered hero figure, lenient PIE score, best setting per model (or every run)
function leaderboard(W, mode = "best", opts = {}) {
  const rows = mode === "best" ? BEST.map(id => RUN[id]) : DATA.runs;
  const rowH = opts.rowH || (mode === "best" ? 44 : 27), barH = Math.round(rowH * (mode === "best" ? .5 : .56));
  const lw = Math.min(opts.labelW || 250, Math.round(W * .42)), vw = 52, top = 4;
  const x = v => lw + (W - lw - vw) * v / 100;
  const H = top + rows.length * rowH + 30;
  let s = gridX(x, top, top + rows.length * rowH, [0, 25, 50, 75, 100]);
  rows.forEach((r, i) => {
    const y = top + i * rowH, by = y + (rowH - barH) / 2, hero = r.id === HERO;
    s += `<g class="row${hero ? " hero" : ""}">`;
    s += `<text x="${lw - 14}" y="${y + rowH / 2}" dy=".35em" text-anchor="end" class="label${hero ? " strong" : ""}${r.ours ? " ours" : ""}">${esc(r.name)}</text>`;
    s += hbar(x(0), by, x(r.L) - x(0), barH, barFill(r));
    s += `<text x="${x(r.L) + 8}" y="${y + rowH / 2}" dy=".35em" class="val${hero ? " strong" : ""}">${f1(r.L)}</text>`;
    s += `<rect x="0" y="${y}" width="${W}" height="${rowH}" class="hit" data-tip="${tip(r.name, [["Lenient", f1(r.L)], ["Strict", f1(r.S)]].concat(r.prec ? [["Weights", r.prec]] : []))}"/>`;
    s += `</g>`;
  });
  return `<svg viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" role="img" aria-label="PIE score by model, lenient">${s}</svg>`;
}

// 2. Notation: strict (the project's exact notation) against lenient, per model
function notation(W, opts = {}) {
  const rows = BEST.map(id => RUN[id]);
  const rowH = opts.rowH || 44, lw = Math.min(opts.labelW || 250, Math.round(W * .38)), gw = 74, top = 34;
  const x = v => lw + (W - lw - gw - 16) * v / 100;
  const H = top + rows.length * rowH + 30;
  let s = gridX(x, top, top + rows.length * rowH, [0, 25, 50, 75, 100]);
  s += `<g class="legend-inline"><circle cx="${lw + 6}" cy="12" r="5.5" fill="var(--ink)"/><text x="${lw + 18}" y="12" dy=".35em" class="axis">strict</text>` +
    `<circle cx="${lw + (opts.lgap || 84)}" cy="12" r="5" fill="var(--surface)" stroke="var(--ink)" stroke-width="2"/><text x="${lw + (opts.lgap || 84) + 12}" y="12" dy=".35em" class="axis">lenient</text></g>` +
    `<text x="${W}" y="12" dy=".35em" text-anchor="end" class="axis">gap</text>`;
  rows.forEach((r, i) => {
    const y = top + i * rowH + rowH / 2, hero = r.id === HERO, col = hero ? "var(--c-nemotron)" : "var(--ink)";
    s += `<text x="${lw - 14}" y="${y}" dy=".35em" text-anchor="end" class="label${hero ? " strong" : ""}${r.ours ? " ours" : ""}">${esc(r.name)}</text>`;
    s += `<line x1="${x(r.S)}" x2="${x(r.L)}" y1="${y}" y2="${y}" stroke="${hero ? "var(--c-nemotron)" : "var(--rule-strong)"}" stroke-width="2"/>`;
    s += `<circle cx="${x(r.S)}" cy="${y}" r="6" fill="${col}" stroke="var(--surface)" stroke-width="2"/>`;
    s += `<circle cx="${x(r.L)}" cy="${y}" r="5" fill="var(--surface)" stroke="${col}" stroke-width="2"/>`;
    const gap = r.L - r.S;
    s += `<text x="${W}" y="${y}" dy=".35em" text-anchor="end" class="val${hero ? " strong" : ""}">${gap < 0.05 ? "0.0" : "−" + f1(gap)}</text>`;
    s += `<rect x="0" y="${y - rowH / 2}" width="${W}" height="${rowH}" class="hit" data-tip="${tip(r.name, [["Strict", f1(r.S)], ["Lenient", f1(r.L)], ["Gap", f1(gap)]])}"/>`;
  });
  return `<svg viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" role="img" aria-label="Strict against lenient PIE score">${s}</svg>`;
}

// 3. Segments: small multiples, one panel per skill, four models in a fixed color order
const SEG_RUNS = ["ours-nemotron35-e3-bf16", "claude-opus-xhigh", "codex-gpt-6.1-sol-high", "ours-merge-half"];
function segments(W, measure = "lenient", opts = {}) {
  const cols = opts.cols || (W >= 980 ? 5 : W >= 600 ? 3 : 1), gap = 28;
  const pw = (W - gap * (cols - 1)) / cols, barH = opts.barH || 22, step = barH + 8, head = opts.head || 46;
  const ph = head + SEG_RUNS.length * step + 6, rowsN = Math.ceil(SEGS.length / cols);
  const H = rowsN * ph + (rowsN - 1) * 24;
  const mi = measure === "strict" ? 1 : 0;
  let s = "";
  SEGS.forEach((g, j) => {
    const ox = (j % cols) * (pw + gap), oy = Math.floor(j / cols) * (ph + 24), vw = opts.vw || 40;
    const x = v => ox + (pw - vw) * v / 100;
    s += `<text x="${ox}" y="${oy + head * .3}" class="panel-title">${g.label}</text>`;
    s += `<text x="${ox}" y="${oy + head * .7}" class="axis">weight ${g.w} · ${RUN[HERO].seg[g.k][2]} items</text>`;
    s += `<line x1="${ox}" x2="${ox}" y1="${oy + head - 4}" y2="${oy + ph - 2}" class="baseline"/>`;
    SEG_RUNS.forEach((id, i) => {
      const r = RUN[id], v = r.seg[g.k][mi], y = oy + head + i * step;
      s += hbar(x(0), y, Math.max(0, x(v) - x(0)), barH, FAM[r.family].c);
      s += `<text x="${x(v) + 6}" y="${y + barH / 2}" dy=".35em" class="val small${id === HERO ? " strong" : ""}">${f1(v)}</text>`;
      s += `<rect x="${ox}" y="${y - 4}" width="${pw}" height="${step}" class="hit" data-tip="${tip(r.name, [[g.label + " (" + measure + ")", f1(v)], ["Strict", f1(r.seg[g.k][1])], ["Lenient", f1(r.seg[g.k][0])]])}"/>`;
    });
  });
  return `<svg viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" role="img" aria-label="Score by skill, ${measure}">${s}</svg>`;
}
const legend = ids => ids.map(id => { const r = RUN[id]; return `<span class="key"><i style="background:${FAM[r.family].c}"></i>${esc(r.name)}</span>`; }).join("");

// 4. Effort: the frontier models at every reasoning effort, against our model
function effort(W, opts = {}) {
  const levels = ["low", "medium", "high", "xhigh"], fams = ["opus", "sol", "sonnet", "terra", "haiku"];
  const H = opts.H || 380, top = 16, bottom = H - 34, left = 36, right = W - (opts.gutter || 168);
  const x = i => left + 18 + (right - left - 36) * i / 3, y = v => bottom - (bottom - top) * (v - 20) / 80;
  let s = [20, 40, 60, 80, 100].map(t => `<line x1="${left}" x2="${right}" y1="${y(t)}" y2="${y(t)}" class="grid"/><text x="${left - 8}" y="${y(t)}" dy=".35em" text-anchor="end" class="axis">${t}</text>`).join("");
  s += levels.map((l, i) => `<text x="${x(i)}" y="${bottom + 22}" text-anchor="middle" class="axis">${l}</text>`).join("");
  const hero = RUN[HERO];
  s += `<line x1="${left}" x2="${right}" y1="${y(hero.L)}" y2="${y(hero.L)}" stroke="var(--c-nemotron)" stroke-width="2" stroke-dasharray="6 5"/>`;
  s += `<text x="${left + 6}" y="${y(hero.L) - 9}" class="val small strong" fill="var(--c-nemotron)">PIE Nemotron 120B e3 · ${f1(hero.L)}</text>`;
  const ends = [];
  fams.forEach(f => {
    const pts = levels.map((l, i) => RUN[(f === "sol" || f === "terra" ? "codex-gpt-6.1-" : "claude-") + f + "-" + l]).map((r, i) => r && [x(i), y(r.L), r]).filter(Boolean);
    s += `<polyline points="${pts.map(p => p[0] + "," + p[1]).join(" ")}" fill="none" stroke="${FAM[f].c}" stroke-width="2" stroke-linejoin="round"/>`;
    pts.forEach(([px, py, r]) => {
      s += `<circle cx="${px}" cy="${py}" r="5" fill="${FAM[f].c}" stroke="var(--surface)" stroke-width="2"/>`;
      s += `<circle cx="${px}" cy="${py}" r="14" class="hit" data-tip="${tip(r.name, [["Lenient", f1(r.L)], ["Strict", f1(r.S)]])}"/>`;
    });
    const last = pts[pts.length - 1];
    ends.push({ f, x: last[0], y: last[1], v: last[2].L });
  });
  ends.sort((a, b) => a.y - b.y);
  for (let i = 1; i < ends.length; i++) ends[i].ly = Math.max(ends[i].y, (ends[i - 1].ly ?? ends[i - 1].y) + 17);
  ends[0].ly = ends[0].y;
  ends.forEach(e => {
    s += `<line x1="${e.x + 8}" x2="${right + 10}" y1="${e.y}" y2="${e.ly}" stroke="${FAM[e.f].c}" stroke-width="1" stroke-dasharray="2 3"/>`;
    s += `<circle cx="${right + 16}" cy="${e.ly}" r="4" fill="${FAM[e.f].c}"/>`;
    s += `<text x="${right + 26}" y="${e.ly}" dy=".35em" class="label small">${FAM[e.f].label}</text>`;
  });
  return `<svg viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" role="img" aria-label="Frontier models by reasoning effort">${s}</svg>`;
}

// 5. Progress: our models in the order they were trained, against the best frontier run
const STEPS = [
  ["ours-e3", "SFT"], ["ours-rl1-step500", "RL 1"], ["ours-rl3-step275", "RL 3"], ["ours-merge-half", "RL merge"],
  ["ours-nemotron35-e1-bf16", "Epoch 1"], ["ours-nemotron35-e2", "Epoch 2"], ["ours-nemotron35-e3-bf16", "Epoch 3"]];
function progress(W, opts = {}) {
  const H = opts.H || 340, top = 30, bottom = H - 64, left = 36, right = W - 12;
  const n = STEPS.length, x = i => left + 30 + (right - left - 60) * i / (n - 1), y = v => bottom - (bottom - top) * (v - 76) / 16;
  let s = [76, 80, 84, 88, 92].map(t => `<line x1="${left}" x2="${right}" y1="${y(t)}" y2="${y(t)}" class="grid"/><text x="${left - 8}" y="${y(t)}" dy=".35em" text-anchor="end" class="axis">${t}</text>`).join("");
  const op = RUN["claude-opus-xhigh"];
  s += `<line x1="${left}" x2="${right}" y1="${y(op.L)}" y2="${y(op.L)}" stroke="var(--c-opus)" stroke-width="2" stroke-dasharray="6 5"/>`;
  s += `<text x="${right - 4}" y="${y(op.L) + 22}" text-anchor="end" class="val small">Best frontier run · Claude Opus 5.5 xhigh · ${f1(op.L)}</text>`;
  const pts = STEPS.map(([id, l], i) => [x(i), y(RUN[id].L), RUN[id], l]);
  s += `<polyline points="${pts.map(p => p[0] + "," + p[1]).join(" ")}" fill="none" stroke="var(--rule-strong)" stroke-width="2"/>`;
  pts.forEach(([px, py, r, l], i) => {
    const hero = r.id === HERO;
    s += `<circle cx="${px}" cy="${py}" r="${hero ? 7 : 5.5}" fill="${FAM[r.family].c}" stroke="var(--surface)" stroke-width="2"/>`;
    s += `<text x="${px}" y="${py - 14}" text-anchor="middle" class="val small${hero ? " strong" : ""}">${f1(r.L)}</text>`;
    s += `<text x="${px}" y="${bottom + 22}" text-anchor="middle" class="axis">${l}</text>`;
    s += `<circle cx="${px}" cy="${py}" r="18" class="hit" data-tip="${tip(r.name, [["Lenient", f1(r.L)], ["Strict", f1(r.S)], ["Weights", r.prec]])}"/>`;
  });
  const g = (a, b, label, c) => `<line x1="${x(a) - 14}" x2="${x(b) + 14}" y1="${bottom + 36}" y2="${bottom + 36}" stroke="${c}" stroke-width="2"/>` +
    `<text x="${(x(a) + x(b)) / 2}" y="${bottom + 54}" text-anchor="middle" class="label small">${label}</text>`;
  s += g(0, 3, W < 560 ? "Qwen 35B" : "Qwen 3.6 35B-A3B", "var(--c-qwen)") + g(4, 6, W < 560 ? "Nemotron 120B" : "Nemotron 3.5 Super 120B-A12B", "var(--c-nemotron)");
  return `<svg viewBox="0 0 ${W} ${H}" width="${W}" height="${H}" role="img" aria-label="Our models in training order">${s}</svg>`;
}

// shared hover layer
function attachTips(root, tipEl) {
  const show = (e, t) => {
    tipEl.innerHTML = t.getAttribute("data-tip");   // the attribute is already unescaped once parsed
    tipEl.hidden = false;
    const b = tipEl.getBoundingClientRect(), vw = document.documentElement.clientWidth;
    let lx = e.clientX + 14, ly = e.clientY + 14;
    if (lx + b.width > vw - 8) lx = e.clientX - b.width - 14;
    if (ly + b.height > window.innerHeight - 8) ly = e.clientY - b.height - 14;
    tipEl.style.transform = `translate(${Math.max(8, lx)}px, ${Math.max(8, ly)}px)`;
  };
  root.addEventListener("pointermove", e => { const t = e.target.closest("[data-tip]"); t ? show(e, t) : (tipEl.hidden = true); });
  root.addEventListener("pointerleave", () => tipEl.hidden = true);
}
