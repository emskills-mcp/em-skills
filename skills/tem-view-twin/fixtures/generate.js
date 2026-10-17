#!/usr/bin/env node
// Writes fixtures/sample/input.json: the simulation settings and the ground truth they must reproduce.
// Ground truth is physical, not taken from the simulator: gold is fcc with a = 4.0782 Å (room temperature),
// so d_hkl = a / sqrt(h² + k² + l²).
import { writeFileSync, mkdirSync } from 'node:fs';
const a = 4.0782;
const d = (h, k, l) => +(a / Math.hypot(h, k, l)).toFixed(4);
const input = {
  description: 'Selected-area diffraction of gold nanoparticles on carbon, simulated by the TEM-view twin',
  runs: [200, 300].map((kV) => ({ mode: 'diff', specimen: 'au', kV, steps: 10 })),
  truth: { lattice: 'fcc', a_A: a, d_A: { '111': d(1, 1, 1), '200': d(2, 0, 0), '220': d(2, 2, 0) } },
  tolerance: { d_rel: 0.025, a_rel: 0.01 },
};
mkdirSync(new URL('./sample/', import.meta.url), { recursive: true });
writeFileSync(new URL('./sample/input.json', import.meta.url), JSON.stringify(input, null, 2) + '\n');
console.log('wrote fixtures/sample/input.json');
