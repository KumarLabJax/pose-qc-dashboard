"""Versioned dashboard schema assembly."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from .constants import DEFAULT_THRESHOLD, KP_NAMES, SCHEMA_VERSION, THRESHOLDS
from .extractors import read_pose_h5
from .metrics import pose_confidence_metrics


def metric_names_for_inventory(inventory: dict[str, Any]) -> list[str]:
    datasets = inventory.get("datasets", {})
    names = ["pose_confidence"]
    if "poseest/points" in datasets:
        names.append("pose_points")
    if "poseest/seg_data" in datasets:
        names.append("pose_segmentation")
    if "dynamic_objects/fecal_boli/counts" in datasets:
        names.append("fecal_boli")
    if "static_objects/corners" in datasets:
        names.append("arena_corners")
    return names


def build_video_record(path: Path, file_id: str, fps: float, bin_sec: float) -> dict[str, Any]:
    h5_data = read_pose_h5(path)
    pose_metrics = pose_confidence_metrics(h5_data.confidence, fps=fps, bin_sec=bin_sec)

    record = {
        "file": file_id,
        "source_path": str(path),
        "available_metrics": metric_names_for_inventory(h5_data.inventory),
        "h5": {
            "pose_metadata": h5_data.pose_metadata,
            "inventory": h5_data.inventory,
        },
        "metrics": {
            "pose_confidence": pose_metrics,
        },
    }

    # Backward-compatible fields consumed by the current dashboard UI.
    record.update(pose_metrics)
    return record


def build_dashboard_data(
    input_dir: Path, fps: float, bin_sec: float, pose_version: int = 6
) -> dict[str, Any]:
    # Recurse into sub-directories and keep only the requested pose version,
    # matched as the "_pose_est_v<N>.h5" filename suffix. This avoids picking up
    # other versions of the same recording (which would duplicate the dashboard).
    pattern = f"*_pose_est_v{pose_version}.h5"
    files = sorted(input_dir.rglob(pattern))
    if not files:
        raise FileNotFoundError(
            f"no {pattern} files found under {input_dir} (searched recursively). "
            f"Pass --pose-version to select a different version."
        )

    generated_at = datetime.now().replace(microsecond=0).isoformat()
    videos = []
    for idx, path in enumerate(files, start=1):
        file_id = path.relative_to(input_dir).as_posix()
        print(f"[{idx}/{len(files)}] {file_id}")
        videos.append(build_video_record(path, file_id, fps=fps, bin_sec=bin_sec))

    return {
        "schema_version": SCHEMA_VERSION,
        "generated_at": generated_at,
        "ts": generated_at,
        "source": {
            "input_dir": str(input_dir),
            "n_files": len(files),
            "file_type": "h5",
            "pose_version": pose_version,
            "recursive": True,
        },
        "config": {
            "fps": fps,
            "bin_sec": bin_sec,
            "thresholds": THRESHOLDS,
            "default_thr": DEFAULT_THRESHOLD,
        },
        "keypoints": [{"index": i, "name": name} for i, name in enumerate(KP_NAMES)],
        "fps": fps,
        "bin_sec": bin_sec,
        "thresholds": THRESHOLDS,
        "default_thr": DEFAULT_THRESHOLD,
        "kp_names": KP_NAMES,
        "n_kps": len(KP_NAMES),
        "n_videos": len(videos),
        "videos": videos,
    }
