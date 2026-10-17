#!/usr/bin/env node
// Reproducibility check for simulate_tem (the TEM-view digital twin).
//
// simulateTem() is the reference implementation of the tool: it runs the twin headlessly and returns the
// detector arrays with their calibration. The check simulates selected-area diffraction of gold, indexes the
// (111), (200) and (220) rings from the background-subtracted radial profile using only the calibration in
// the metadata, and must recover the spacings and the fcc lattice constant of fixtures/sample/input.json.
import { readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';
import { Sim } from 'tem-view/js/sim.js';
import { defaultState } from 'tem-view/js/state.js';
import * as P from 'tem-view/js/physics.js';
import { collectData, toNpz } from 'tem-view/js/export.js';

export function simulateTem({ mode = 'tem', specimen = 'au', kV, defocus_nm, dose, steps = 10, out } = {}) {
  if (!P.SPECIMENS[specimen]) throw new Error(`unknown specimen ${specimen}`);
  const S = defaultState(), sp = P.SPECIMENS[specimen];
  S.spec = specimen; S.fov = sp.fov; [S.cx, S.cy] = sp.center; S.mode = mode;
  if (kV) S.kV = kV;
  if (dose) S.dose = dose;
  S.df = defocus_nm ?? S.dfFam[['tem', 'diff', 'oah', 'ilh'].includes(mode) ? 'tem' : 'probe'];
  const sim = new Sim(S);
  for (let i = 0; i < steps; i++) sim.update(0.05);
  const data = collectData(sim, S);
  if (out) writeFileSync(out, toNpz(data));
  return { ok: true, result: { out: out ?? null, arrays: data.arrays, metadata: data.meta }, diagnostics: { generator: data.meta.generator, simulated: true } };
}

// background-subtracted radial profile → ring radii (px), refined by a parabola
function rings(arr, n) {
  const c = n / 2, prof = new Float64Array(n), cnt = new Float64Array(n);
  for (let y = 0; y < n; y++) for (let x = 0; x < n; x++) { const i = Math.round(Math.hypot(x - c, y - c)); if (i < n) { prof[i] += arr[y * n + x]; cnt[i]++; } }
  for (let r = 0; r < n; r++) prof[r] /= cnt[r] || 1;
  const W = 7, rel = new Float64Array(n), peaks = [];
  for (let r = W; r < c - W; r++) { let s = 0; for (let j = -W; j <= W; j++) s += prof[r + j]; rel[r] = prof[r] / (s / (2 * W + 1)) - 1; }
  for (let r = W + 1; r < c - W - 1; r++) if (rel[r] > 0.02 && rel[r] >= rel[r - 1] && rel[r] > rel[r + 1]) {
    const y0 = rel[r - 1], y1 = rel[r], y2 = rel[r + 1];
    peaks.push({ r: r + 0.5 * (y0 - y2) / (y0 - 2 * y1 + y2 || 1e-9), s: y1 });
  }
  return peaks;
}

function main() {
  const args = process.argv.slice(2), opt = {};
  for (let i = 0; i < args.length; i += 2) opt[args[i].replace(/^--/, '')] = args[i + 1];
  const fixture = JSON.parse(readFileSync(join(opt.fixture ?? 'fixtures/sample', 'input.json'), 'utf8'));
  const { truth, tolerance } = fixture, HKL = { '111': 3, '200': 4, '220': 8 };
  let ok = true;
  for (const run of fixture.runs) {
    const { result } = simulateTem(run);
    const pat = result.arrays.pattern, n = pat.shape[0], k = result.metadata.calibration.k_per_px_invA; // Å⁻¹ per pixel
    const peaks = rings(pat.data, n).map((p) => ({ ...p, d: 1 / (p.r * k) }));
    const found = {}, aEst = [];
    for (const [hkl, dTrue] of Object.entries(truth.d_A)) {
      const best = peaks.filter((p) => Math.abs(p.d / dTrue - 1) < 0.06).sort((a, b) => b.s - a.s)[0];
      const err = best ? best.d / dTrue - 1 : null;
      found[hkl] = best ? `${best.d.toFixed(4)} Å (${(err * 100).toFixed(2)} %)` : 'not found';
      if (!best || Math.abs(err) > tolerance.d_rel) ok = false;
      if (best) aEst.push(best.d * Math.sqrt(HKL[hkl]));
    }
    const a = aEst.reduce((x, y) => x + y, 0) / (aEst.length || 1), aErr = a / truth.a_A - 1;
    if (aEst.length < 3 || Math.abs(aErr) > tolerance.a_rel) ok = false;
    console.log(`${run.kV} kV  d111 ${found['111']}  d200 ${found['200']}  d220 ${found['220']}  a = ${a.toFixed(4)} Å (${(aErr * 100).toFixed(2)} %)`);
  }
  console.log(ok ? 'PASS: the twin recovers the gold lattice from its own calibration' : 'FAIL');
  process.exit(ok ? 0 : 1);
}

if (import.meta.url === `file://${process.argv[1]}`) main();
