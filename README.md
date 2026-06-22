# Pose QC Dashboard

Static quality-control dashboard for animal pose-estimation recordings stored as H5 files.

The current implementation is the phase-1 H5 refactor. It preserves the shareable single-file
dashboard workflow while adding a modular generator and reusable JSON artifacts for future panels.

## Current Support

- Input format: v6 pose-estimation H5 files.
- Required dataset: `poseest/confidence`.
- Expected confidence shape: `(frames, animals, keypoints)` or `(frames, keypoints)`.
- Current dashboard metrics use the first animal track and the 12-keypoint v6 skeleton:
  `Nose`, `Left Ear`, `Right Ear`, `Base Neck`, `Left Front Paw`, `Right Front Paw`,
  `Center Spine`, `Left Rear Paw`, `Right Rear Paw`, `Base Tail`, `Mid Tail`, `Tip Tail`.
- The extractor also inventories other H5 datasets such as `poseest/points`,
  `poseest/seg_data`, `dynamic_objects/fecal_boli/*`, and `static_objects/corners`,
  but phase 1 only visualizes pose confidence/keypoint reliability.

## Quickstart

Generate the dashboard from a directory of v6 H5 pose files:

```bash
python generate_qc_dashboard.py combined_autism_poses -o qc_dashboard.html
```

Open `qc_dashboard.html` directly in a browser. No server is required.

By default this writes:

- `qc_dashboard.html`: self-contained dashboard with embedded data and Chart.js.
- `qc_dashboard_data/summary.json`: dataset-level reusable QC summary.
- `qc_dashboard_data/videos/*.json`: per-video reusable QC records.

To skip JSON artifact output:

```bash
python generate_qc_dashboard.py combined_autism_poses -o qc_dashboard.html --no-json
```

To tune assumptions used by the current metrics:

```bash
python generate_qc_dashboard.py combined_autism_poses -o qc_dashboard.html --fps 30 --bin-sec 20
```

## Dashboard Workflow

- Use the left panel to search, sort, and filter videos.
- The overview page summarizes confidence distributions and the least reliable body parts.
- Click a video to inspect temporal confidence, dropout, and keypoint reliability.
- Use `Include`, `Undecided`, and `Exclude` decisions during review.
- Decisions are stored in browser `localStorage`.
- Export/import buttons support text/CSV decision handoff.

## Project Layout

```text
generate_qc_dashboard.py       CLI entrypoint
qc_dashboard_template.html     Reusable static dashboard shell
qc_dashboard.html              Generated self-contained dashboard
qc_dashboard_gen/
  extractors.py                H5 reading and dataset inventory
  metrics.py                   Pose confidence QC metrics
  schema.py                    Versioned dashboard data object
  render.py                    HTML embedding and JSON artifact writer
  constants.py                 Keypoints, thresholds, schema version
qc_dashboard_data/
  summary.json                 Dataset-level generated artifact
  videos/*.json                Per-video generated artifacts
```

## Phase 1 Status

Phase 1 is complete:

- v6 H5 confidence extraction replaces the older CSV-only workflow.
- The original static dashboard behavior is preserved.
- JSON artifacts are emitted alongside the embedded HTML.
- Detail-page navigation includes a visible overview/home path.
- The decision controls are near the top of the video review page and remain scrollable.
- The H5 inventory is captured for future non-confidence panels.

## Phase 2 Plan

Phase 2 will expand the dashboard from confidence-only QC into a broader v6 H5 QC system.

1. Normalize v6 H5 parsing.
   - Add typed extractors for `poseest/points`, `poseest/confidence`, `poseest/seg_data`,
     identity/track datasets, fecal boli, and arena corners.
   - Keep one canonical internal shape per signal so later panels do not depend on raw H5 layout.

2. Extend the schema without breaking phase 1.
   - Keep `metrics.pose_confidence` stable.
   - Add new optional namespaces such as `metrics.pose_geometry`, `metrics.tracking`,
     `metrics.segmentation`, `metrics.arena`, and `metrics.fecal_boli`.
   - Preserve backward-compatible top-level fields until the frontend is fully migrated.

3. Add pose-point QC.
   - Use `poseest/points` to compute coordinate ranges, impossible jumps, body-length stability,
     keypoint displacement distributions, and out-of-arena rates.
   - Pair confidence drops with movement anomalies so reviewers can distinguish low confidence from
     physically implausible tracking.

4. Add v6 tracking/identity QC.
   - Use available v6 identity and track datasets to flag identity switches, missing instances,
     and track continuity issues.
   - Surface these as per-video review flags and timeline panels.

5. Add arena/object QC.
   - Use `static_objects/corners` to validate arena geometry and coordinate scaling.
   - Use fecal-boli datasets where available for optional experiment-specific QC panels.

6. Migrate the frontend panel-by-panel.
   - Keep the overview and confidence detail views stable.
   - Add tabs or sections for pose geometry, tracking, segmentation, and arena/object checks.
   - Load from the same embedded data first; later we can optionally support external JSON loading.

7. Add stronger tests and validation fixtures.
   - Add small synthetic H5 fixtures for v6 layout variations.
   - Test extractor shape normalization, schema versioning, and frontend-required fields.

## Verification

Useful checks after changes:

```bash
python -m py_compile generate_qc_dashboard.py qc_dashboard_gen/*.py
python generate_qc_dashboard.py combined_autism_poses -o qc_dashboard.html
```

Then open `qc_dashboard.html` in a browser and confirm overview navigation, video detail scrolling,
decision export/import, and confidence plots.
