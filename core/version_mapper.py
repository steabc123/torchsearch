"""Version mapping facade.

This module provides a single, stable function `get_torch_versions` which
returns a normalized recommendation dict for a given CUDA version.

It delegates to `core.mapper` which loads mappings from `data/versions.json`.
This makes the core mapping data-driven and easier to update.
"""
from __future__ import annotations

from typing import Optional, Dict, Any

from .mapper import load_versions, get_recommendations


def get_torch_versions(cuda_version: Optional[str], versions_path: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Return a normalized mapping for the given CUDA version.

    Args:
        cuda_version: string like "11.8" or None
        versions_path: optional path to a JSON file (overrides bundled data)

    Returns:
        A dict with keys: torch, torchvision, torchaudio, pip_tag (values may be None)
        or None if no recommendation is available.
    """
    versions_data = load_versions(versions_path) if versions_path else None
    rec = get_recommendations(cuda_version, versions_data=versions_data)
    if not rec:
        return None

    # normalize returned shape for callers
    return {
        "torch": rec.get("torch"),
        "torchvision": rec.get("torchvision"),
        "torchaudio": rec.get("torchaudio"),
        "pip_tag": rec.get("pip_tag") or rec.get("pip_tag", None),
    }
