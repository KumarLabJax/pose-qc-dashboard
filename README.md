# Pose QC Dashboard

Turn a folder of pose-estimation `.h5` files into a single, self-contained web page for
reviewing tracking quality. The generated page summarizes keypoint confidence and
reliability for every recording and gives you a simple Include / Exclude review workflow.

No server and no internet connection are needed — the result is one standalone HTML file
that you can open on any computer or email to a colleague.

## Requirements

- Python 3.9 or newer
- Two packages, installed once:

```bash
pip install -r requirements.txt
```

## 1. Generate a dashboard

Point the script at any folder containing pose `.h5` files:

```bash
python generate_qc_dashboard.py /path/to/your/h5_folder -o qc_dashboard.html
```

Then open the resulting `qc_dashboard.html` in any web browser (double-click it).

The folder is searched **recursively**, so pose files inside sub-folders are included too.
By default only files named `*_pose_est_v6.h5` (pose version 6) are used. If your files are a
different version, select it with `--pose-version`:

```bash
python generate_qc_dashboard.py /path/to/your/h5_folder -o qc_dashboard.html --pose-version 6
```

Picking a single version is also how you avoid duplicate entries when a folder holds several
pose versions of the same recording (e.g. both `..._pose_est_v4.h5` and `..._pose_est_v6.h5`).
If two files share the same name in different sub-folders, both are kept and labeled by their
sub-folder so they don't clash.

If your videos were **not** recorded at 30 frames per second, pass your frame rate so the
time axes are labeled correctly:

```bash
python generate_qc_dashboard.py /path/to/your/h5_folder -o qc_dashboard.html --fps 30
```

The data is baked into the HTML, so you can move or share that one file freely.

## 2. Review recordings

- **Left panel** — every recording, with a quality dot (good / okay / poor). Search by name,
  sort by confidence or quality, or filter to a single quality level.
- **Overview** (shown before you select a video) — the confidence distribution across the
  whole dataset and which body parts are least reliable.
- **Detail view** (click a recording) — mean confidence, a confidence-over-time heatmap,
  frame-dropout charts, and per-keypoint reliability.
- **Confidence-threshold slider** (top right) — re-scores quality live, so you can see how a
  stricter or more lenient cutoff changes the picture.
- **Your decision** — mark each recording **Include**, **Undecided**, or **Exclude**, and add
  free-text notes.

## 3. Save and export your decisions

**Where your decisions live.** As you review, your Include / Exclude choices and notes are
saved automatically in your **web browser's local storage** (under a key named
`pqc_<number-of-recordings>`). That means they are:

- kept on **that browser, on that computer** — they do **not** travel inside the HTML file;
- **never written into your `.h5` files**, and never saved to disk by the tool;
- lost if you clear your browser data — so **export** anything you want to keep or share.

**Export buttons** (bottom of the page, under **Export**):

| Button | File you get | What's inside |
| --- | --- | --- |
| Export Included | `include_videos.txt` | One filename per line — every recording marked **Include** |
| Export Excluded | `exclude_videos.txt` | One filename per line — every recording marked **Exclude** |
| Export All Decisions | `qc_decisions.csv` | Columns: `file, decision, quality, mean_confidence, notes` |
| Export Full Metrics | `qc_full_metrics.csv` | The columns above plus duration, frame-loss stats, and a `_mean` and `_reliable` column for each keypoint |

The plain-text lists are convenient for scripting (e.g. feeding the "include" list into an
analysis pipeline). The CSV files open directly in Excel, R, or pandas.

**Re-loading decisions (Import).** Click **Import Decisions** and choose a CSV that has at
least a `file` column and a `decision` column (a `notes` column is optional). Decisions are
matched to recordings by filename, so `qc_decisions.csv` round-trips: export it, move it to
another computer, load the same dataset there, and import it back to restore your review.

> **Tip:** if you plan to re-import, avoid commas inside your notes. The importer splits
> columns on commas, so a comma in a note can shift the other fields.

## License

Copyright 2026 Kumar Lab, The Jackson Laboratory.

Licensed under the Apache License, Version 2.0 — see [LICENSE](LICENSE). You may use, modify,
and redistribute this software under the terms of that license.
