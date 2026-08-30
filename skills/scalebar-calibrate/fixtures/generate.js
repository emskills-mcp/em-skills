#!/usr/bin/env node
// Generate the deterministic fixture for scalebar-calibrate.
//
// Builds a synthetic 1D intensity profile of a certified cross-grating
// standard: evenly spaced peaks at a known pixel pitch (implied by a known
// physical pitch and a known true pixel size), plus a nominal (slightly
// off) instrument-reported pixel size to calibrate against. Seed is fixed
// (a small deterministic PRNG, since Math.random isn't seedable) so
// re-running this script reproduces the committed fixtures/sample/input.json
// exactly.
"use strict";
const fs = require("fs");
const path = require("path");

const SEED = 0;
const CERTIFIED_PITCH_NM = 500.0;
const TRUE_PIXEL_SIZE_NM = 8.0;
const NOMINAL_PIXEL_SIZE_NM = 8.3; // instrument-reported, has drift error
const PROFILE_LEN_PX = 300;
const PHASE_PX = 10.0;
const PEAK_SIGMA_PX = 2.0;
const JITTER_SIGMA_PX = 0.3;
const PEAK_HEIGHT = 100.0;
const NOISE_SIGMA = 5.0;

function mulberry32(seed) {
  let a = seed;
  return function () {
    a |= 0;
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function makeGaussian(rng) {
  return function (mean, sigma) {
    const u1 = Math.max(rng(), 1e-12);
    const u2 = rng();
    const z0 = Math.sqrt(-2.0 * Math.log(u1)) * Math.cos(2.0 * Math.PI * u2);
    return mean + sigma * z0;
  };
}

function main() {
  const rng = mulberry32(SEED);
  const gauss = makeGaussian(rng);

  const truePitchPx = CERTIFIED_PITCH_NM / TRUE_PIXEL_SIZE_NM;
  const peakCenters = [];
  for (let c = PHASE_PX; c < PROFILE_LEN_PX; c += truePitchPx) {
    peakCenters.push(c + gauss(0, JITTER_SIGMA_PX));
  }

  const intensity = [];
  for (let x = 0; x < PROFILE_LEN_PX; x++) {
    let signal = 15.0;
    for (const c of peakCenters) {
      signal += PEAK_HEIGHT * Math.exp(-((x - c) ** 2) / (2 * PEAK_SIGMA_PX ** 2));
    }
    intensity.push(Math.round((signal + gauss(0, NOISE_SIGMA)) * 100) / 100);
  }

  const fixture = {
    intensity,
    certified_pitch_nm: CERTIFIED_PITCH_NM,
    nominal_pixel_size_nm: NOMINAL_PIXEL_SIZE_NM,
    ground_truth: {
      pixel_size_nm: TRUE_PIXEL_SIZE_NM,
      pitch_px: Math.round(truePitchPx * 1000) / 1000,
    },
  };

  const outDir = path.join(__dirname, "sample");
  fs.mkdirSync(outDir, { recursive: true });
  const outPath = path.join(outDir, "input.json");
  fs.writeFileSync(outPath, JSON.stringify(fixture, null, 2) + "\n");
  console.log(`wrote ${outPath}`);
}

main();
