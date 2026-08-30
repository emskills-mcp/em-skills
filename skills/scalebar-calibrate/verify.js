#!/usr/bin/env node
// Reproducibility check for calibrate_scale.
//
// Finds cross-grating peaks in the intensity profile from
// fixtures/sample/input.json (local maxima above a background-relative
// threshold, deduplicated by minimum separation), averages the peak-to-peak
// pixel pitch, derives a calibrated pixel size from the certified physical
// pitch, and checks it against the fixture's ground truth.
"use strict";
const fs = require("fs");
const path = require("path");

const MIN_PEAK_SEPARATION_PX = 4;
const THRESHOLD_ABOVE_BASELINE = 25.0;
const RELATIVE_TOLERANCE = 0.05;

function parseArgs(argv) {
  const args = { fixture: "fixtures/sample", seed: 0 };
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === "--fixture") args.fixture = argv[++i];
    else if (argv[i] === "--seed") args.seed = parseInt(argv[++i], 10);
  }
  return args; // --seed accepted for CLI symmetry; unused (fully deterministic)
}

function findPeaks(intensity, threshold, minSeparation) {
  const sorted = [...intensity].sort((a, b) => a - b);
  const baseline = sorted[Math.floor(sorted.length / 4)];
  const candidates = [];
  for (let i = 1; i < intensity.length - 1; i++) {
    if (
      intensity[i] > baseline + threshold &&
      intensity[i] >= intensity[i - 1] &&
      intensity[i] >= intensity[i + 1]
    ) {
      candidates.push(i);
    }
  }
  const peaks = [];
  for (const i of candidates) {
    if (peaks.length && i - peaks[peaks.length - 1] < minSeparation) {
      if (intensity[i] > intensity[peaks[peaks.length - 1]]) {
        peaks[peaks.length - 1] = i;
      }
    } else {
      peaks.push(i);
    }
  }
  return peaks;
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  const inputPath = path.join(args.fixture, "input.json");
  const data = JSON.parse(fs.readFileSync(inputPath, "utf8"));

  const { intensity, certified_pitch_nm: certifiedPitchNm, nominal_pixel_size_nm: nominalPixelSizeNm } = data;
  const truth = data.ground_truth;

  const peaks = findPeaks(intensity, THRESHOLD_ABOVE_BASELINE, MIN_PEAK_SEPARATION_PX);
  const spacings = [];
  for (let i = 1; i < peaks.length; i++) spacings.push(peaks[i] - peaks[i - 1]);
  const meanSpacingPx = spacings.reduce((a, b) => a + b, 0) / spacings.length;

  const calibratedPixelSizeNm = certifiedPitchNm / meanSpacingPx;
  const correctionFactor = calibratedPixelSizeNm / nominalPixelSizeNm;

  const relError = Math.abs(calibratedPixelSizeNm - truth.pixel_size_nm) / truth.pixel_size_nm;
  const ok = relError <= RELATIVE_TOLERANCE;

  const output = {
    ok,
    result: {
      pixel_size_nm: Math.round(calibratedPixelSizeNm * 1000) / 1000,
      pitch_px: Math.round(meanSpacingPx * 1000) / 1000,
      correction_factor: Math.round(correctionFactor * 10000) / 10000,
    },
    diagnostics: { relative_error_vs_fixture: Math.round(relError * 100000) / 100000 },
  };
  console.log(JSON.stringify(output, null, 2));
  process.exit(ok ? 0 : 1);
}

main();
