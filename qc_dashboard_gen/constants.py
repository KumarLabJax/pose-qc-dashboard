"""Shared constants for pose QC generation."""

from __future__ import annotations

import numpy as np


KP_NAMES = [
    "Nose",
    "Left Ear",
    "Right Ear",
    "Base Neck",
    "Left Front Paw",
    "Right Front Paw",
    "Center Spine",
    "Left Rear Paw",
    "Right Rear Paw",
    "Base Tail",
    "Mid Tail",
    "Tip Tail",
]

THRESHOLDS = [f"{v:.2f}" for v in np.arange(0.50, 1.00, 0.05)]
DEFAULT_THRESHOLD = "0.80"
SCHEMA_VERSION = 1
