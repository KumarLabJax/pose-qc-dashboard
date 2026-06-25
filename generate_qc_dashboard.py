#!/usr/bin/env python3
"""Generate the static pose QC dashboard from pose-estimation H5 files."""

from __future__ import annotations

import argparse
from pathlib import Path

from qc_dashboard_gen.render import render_dashboard, write_json_artifacts
from qc_dashboard_gen.schema import build_dashboard_data

DEFAULT_TEMPLATE = Path(__file__).with_name("qc_dashboard_template.html")


def default_data_dir(output: Path) -> Path:
    if output.name == "qc_dashboard.html":
        return output.with_name("qc_dashboard_data")
    return output.with_name(f"{output.stem}_data")


def resolve_template_path(output: Path, requested: Path | None) -> Path:
    if requested is not None:
        return requested
    if output.exists():
        return output
    if DEFAULT_TEMPLATE.exists():
        return DEFAULT_TEMPLATE
    legacy_template = Path(__file__).with_name("qc_dashboard.html")
    if legacy_template.exists():
        return legacy_template
    raise FileNotFoundError(
        "No dashboard template found. Re-run in a directory containing qc_dashboard_template.html "
        "or pass --template PATH."
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_dir", type=Path, help="Directory containing pose-estimation .h5 files")
    parser.add_argument("-o", "--output", type=Path, default=Path("qc_dashboard.html"))
    parser.add_argument("--template", type=Path, default=None, help="Existing dashboard HTML to reuse")
    parser.add_argument("--data-dir", type=Path, default=None, help="Directory for reusable JSON artifacts")
    parser.add_argument("--no-json", action="store_true", help="Skip writing JSON artifacts")
    parser.add_argument("--fps", type=float, default=30.0)
    parser.add_argument("--bin-sec", type=float, default=20.0)
    parser.add_argument(
        "--pose-version",
        type=int,
        default=6,
        help="Pose file version to include, matched as the _pose_est_v<N>.h5 filename suffix (default: 6)",
    )
    args = parser.parse_args()

    template_path = resolve_template_path(args.output, args.template)
    data_dir = args.data_dir or default_data_dir(args.output)

    data = build_dashboard_data(
        args.input_dir, fps=args.fps, bin_sec=args.bin_sec, pose_version=args.pose_version
    )
    render_dashboard(template_path=template_path, output_path=args.output, data=data)
    if not args.no_json:
        write_json_artifacts(data, data_dir)
        print(f"Wrote JSON artifacts to {data_dir}")
    print(f"Wrote {args.output} with {data['n_videos']} videos")


if __name__ == "__main__":
    main()
