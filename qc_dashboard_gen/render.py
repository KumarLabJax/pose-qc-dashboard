"""HTML rendering and JSON artifact writing."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def replace_data_block(template: str, data: dict[str, Any]) -> str:
    marker = "<script>const D="
    start = template.index(marker)
    close = template.index("</script>", start) + len("</script>")
    data_json = json.dumps(data, separators=(",", ":"), allow_nan=False)
    return template[:start] + marker + data_json + ";</script>" + template[close:]


def render_dashboard(template_path: Path, output_path: Path, data: dict[str, Any]) -> None:
    template = template_path.read_text(encoding="utf-8")
    output_path.write_text(replace_data_block(template, data), encoding="utf-8")


def video_summary(video: dict[str, Any]) -> dict[str, Any]:
    return {
        "file": video["file"],
        "source_path": video.get("source_path"),
        "n_frames": video["n_frames"],
        "duration_min": video["duration_min"],
        "mean_conf": video["mean_conf"],
        "available_metrics": video.get("available_metrics", []),
        "h5_datasets": sorted(video.get("h5", {}).get("inventory", {}).get("datasets", {}).keys()),
    }


def write_json_artifacts(data: dict[str, Any], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    videos_dir = output_dir / "videos"
    videos_dir.mkdir(parents=True, exist_ok=True)

    summary = {
        "schema_version": data["schema_version"],
        "generated_at": data["generated_at"],
        "source": data["source"],
        "config": data["config"],
        "keypoints": data["keypoints"],
        "n_kps": data["n_kps"],
        "n_videos": data["n_videos"],
        "videos": [video_summary(video) for video in data["videos"]],
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    for video in data["videos"]:
        name = Path(video["file"]).stem + ".json"
        (videos_dir / name).write_text(json.dumps(video, indent=2), encoding="utf-8")
