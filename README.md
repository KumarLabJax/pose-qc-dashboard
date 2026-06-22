# Pose QC Dashboard

Turn a folder of pose-estimation `.h5` files into a single web page for reviewing
tracking quality — keypoint confidence and reliability for every recording. The page
is fully self-contained: no server, no internet, just open it in a browser.

## Install (once)

Requires Python 3.9 or newer.

```bash
pip install -r requirements.txt
```

## Generate a dashboard

Point it at your folder of pose `.h5` files:

```bash
python generate_qc_dashboard.py /path/to/your/h5_folder -o qc_dashboard.html
```

Then open `qc_dashboard.html` in any web browser (double-click it).

If your videos were not recorded at 30 frames per second, pass your frame rate so the
time axis is correct:

```bash
python generate_qc_dashboard.py /path/to/your/h5_folder -o qc_dashboard.html --fps 30
```

## Using the dashboard

- The left panel lists every recording — search, sort, and filter by quality.
- The overview summarizes confidence across the dataset and highlights the least
  reliable body parts.
- Click a recording to see its confidence over time, frame dropout, and per-keypoint
  reliability.
- Mark each recording **Include**, **Undecided**, or **Exclude**, and add notes as you review.
- Use the **Export** / **Import** buttons to save your decisions or move them to another computer.

Your review decisions are stored in your browser and are never written into the `.h5` files.
