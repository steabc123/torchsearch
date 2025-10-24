"""Load version mapping data and provide recommendation lookup.

This module expects a JSON file `data/versions.json` with a mapping from cuda version -> package versions.
Example format:
{
  "11.8": {"torch":"2.2.0","torchvision":"0.15.2","torchaudio":"2.2.2","pip_tag":"cu118"}
}

If the file is missing, a built-in constant map is used as a fallback.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

from utils.constants import TORCH_VERSION_MAP


DEFAULT_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "versions.json"


def _convert_constants_map() -> Dict[str, Dict]:
    """Convert utils.constants.TORCH_VERSION_MAP (tuple values) into the dict shape used by JSON data."""
    out: Dict[str, Dict] = {}
    for k, v in TORCH_VERSION_MAP.items():
        # v is expected to be a tuple: (torch, torchvision, torchaudio, pip_tag)
        torch_v, tv_v, ta_v, pip_tag = (list(v) + [None] * 4)[:4]
        out[str(k)] = {
            "torch": torch_v,
            "torchvision": tv_v,
            "torchaudio": ta_v,
            "pip_tag": pip_tag,
        }
    return out


def load_versions(path: Optional[str] | None = None) -> Dict[str, Dict]:
    p = Path(path) if path else DEFAULT_DATA_PATH
    if not p.exists():
        # fallback to built-in constants
        return _convert_constants_map()
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def get_recommendations(cuda_version: Optional[str], versions_data: Optional[Dict] = None) -> Dict:
    """Return recommendations for a given cuda_version.

    If exact match not found, tries to match major.minor; if no exact minor exists,
    it will try to find the closest minor within the same major (numerically closest).
    Returns empty dict when no candidates found.
    """
    if versions_data is None:
        versions_data = load_versions()

    if not cuda_version:
        return {}

    # normalize to major.minor
    norm = None
    import re

    m = re.match(r"(\d+\.\d+)", str(cuda_version))
    if m:
        norm = m.group(1)

    if norm and norm in versions_data:
        return versions_data[norm]

    # fallback: try to find candidates with same major (e.g., 11.x)
    if norm:
        major = norm.split(".")[0]
        candidates = {k: v for k, v in versions_data.items() if k.split(".")[0] == major}
        if candidates:
            # pick the closest minor numerically to the requested norm
            try:
                target_minor = float(norm.split(".")[1])
            except Exception:
                # if parsing failed, fallback to the highest available
                best = sorted(candidates.keys(), reverse=True)[0]
                return versions_data[best]

            def minor_of(key: str) -> float:
                parts = key.split(".")
                return float(parts[1]) if len(parts) > 1 else 0.0

            best_key = min(
                candidates.keys(), key=lambda k: (abs(minor_of(k) - target_minor), -minor_of(k))
            )
            return versions_data[best_key]

    return {}

