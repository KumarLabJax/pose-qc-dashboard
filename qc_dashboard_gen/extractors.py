"""H5 extraction helpers for the QC dashboard."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import h5py
import numpy as np

from .constants import KP_NAMES


@dataclass(frozen=True)
class PoseH5Data:
    path: Path
    confidence: np.ndarray
    inventory: dict[str, Any]
    pose_metadata: dict[str, Any]


def to_jsonable(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    if isinstance(value, dict):
        return {str(k): to_jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_jsonable(v) for v in value]
    return value


def dataset_inventory(h5: h5py.File) -> dict[str, Any]:
    groups: dict[str, Any] = {}
    datasets: dict[str, Any] = {}

    def visit(name: str, obj: h5py.Dataset | h5py.Group) -> None:
        attrs = to_jsonable(dict(obj.attrs))
        if isinstance(obj, h5py.Dataset):
            datasets[name] = {
                "shape": list(obj.shape),
                "dtype": str(obj.dtype),
                "attrs": attrs,
            }
        else:
            groups[name] = {"attrs": attrs}

    h5.visititems(visit)
    return {
        "root_attrs": to_jsonable(dict(h5.attrs)),
        "groups": groups,
        "datasets": datasets,
    }


def read_pose_h5(path: Path) -> PoseH5Data:
    with h5py.File(path, "r") as h5:
        if "poseest/confidence" not in h5:
            raise KeyError(f"{path.name}: missing poseest/confidence")

        confidence = h5["poseest/confidence"][:]
        inventory = dataset_inventory(h5)
        pose_metadata = {
            "poseest_attrs": to_jsonable(dict(h5["poseest"].attrs)) if "poseest" in h5 else {},
            "points_shape": list(h5["poseest/points"].shape) if "poseest/points" in h5 else None,
            "confidence_shape": list(confidence.shape),
        }

    if confidence.ndim == 3:
        confidence = confidence[:, 0, :]
    elif confidence.ndim != 2:
        raise ValueError(f"{path.name}: unexpected confidence shape {confidence.shape}")

    if confidence.shape[1] != len(KP_NAMES):
        raise ValueError(f"{path.name}: expected {len(KP_NAMES)} keypoints, found {confidence.shape[1]}")

    return PoseH5Data(
        path=path,
        confidence=confidence.astype(np.float32, copy=False),
        inventory=inventory,
        pose_metadata=pose_metadata,
    )
