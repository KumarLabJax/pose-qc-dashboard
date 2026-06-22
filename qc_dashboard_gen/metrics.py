"""Metric computations for pose QC."""

from __future__ import annotations

from typing import Any

import numpy as np

from .constants import THRESHOLDS


def round_list(values: np.ndarray, digits: int = 4) -> list[float]:
    arr = np.asarray(values, dtype=float)
    arr = np.where(np.isfinite(arr), arr, 0.0)
    return np.round(arr, digits).tolist()


def safe_nanmean(values: np.ndarray, axis: int | None = None) -> np.ndarray:
    with np.errstate(invalid="ignore"):
        out = np.nanmean(values, axis=axis)
    return np.where(np.isfinite(out), out, 0.0)


def safe_nanmedian(values: np.ndarray, axis: int | None = None) -> np.ndarray:
    with np.errstate(invalid="ignore"):
        out = np.nanmedian(values, axis=axis)
    return np.where(np.isfinite(out), out, 0.0)


def temporal_keypoint_means(confidence: np.ndarray, fps: float, bin_sec: float) -> list[list[float]]:
    frames_per_bin = max(1, int(round(fps * bin_sec)))
    n_frames, n_kps = confidence.shape
    bins: list[list[float]] = []

    for kp_idx in range(n_kps):
        row = []
        for start in range(0, n_frames, frames_per_bin):
            stop = min(start + frames_per_bin, n_frames)
            row.append(float(safe_nanmean(confidence[start:stop, kp_idx])))
        bins.append([round(v, 2) for v in row])

    return bins


def threshold_metrics(confidence: np.ndarray, fps: float, bin_sec: float) -> dict[str, Any]:
    frames_per_bin = max(1, int(round(fps * bin_sec)))
    n_frames, n_kps = confidence.shape
    metrics: dict[str, Any] = {}

    for threshold in THRESHOLDS:
        thr = float(threshold)
        lost = (~np.isfinite(confidence)) | (confidence < thr)
        lost_counts = lost.sum(axis=1)
        dropout_hist = np.bincount(lost_counts, minlength=n_kps + 1)[: n_kps + 1] / n_frames

        temporal_loss = []
        for start in range(0, n_frames, frames_per_bin):
            stop = min(start + frames_per_bin, n_frames)
            temporal_loss.append(float(lost_counts[start:stop].mean()))

        metrics[threshold] = {
            "klf": round_list(lost.mean(axis=0), 4),
            "dh": round_list(dropout_hist, 4),
            "tp": [round(v, 2) for v in temporal_loss],
        }

    return metrics


def pose_confidence_metrics(confidence: np.ndarray, fps: float, bin_sec: float) -> dict[str, Any]:
    n_frames = int(confidence.shape[0])
    return {
        "n_frames": n_frames,
        "duration_min": round(n_frames / fps / 60.0, 2),
        "mean_conf": round(float(safe_nanmean(confidence)), 4),
        "kp_mean": round_list(safe_nanmean(confidence, axis=0), 4),
        "kp_median": round_list(safe_nanmedian(confidence, axis=0), 4),
        "kp_temporal": temporal_keypoint_means(confidence, fps, bin_sec),
        "thr": threshold_metrics(confidence, fps, bin_sec),
    }
