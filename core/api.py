"""High-level core API that composes detection, mapping and install command generation.

This provides a stable entrypoint for UI or CLI code to request a recommendation
based on detected or provided CUDA version.
"""
from __future__ import annotations

from typing import Optional, Dict, Any

from .detector import get_cuda_version
from .version_mapper import get_torch_versions
from .installer import generate_pip_command


def detect_and_prepare(cuda_override: Optional[str] = None, versions_path: Optional[str] = None, extras: Optional[list] = None) -> Dict[str, Any]:
    """Detect CUDA (or use override), get recommendation, and build install command.

    Args:
        cuda_override: if provided, skip detection and use this CUDA version string.
        versions_path: optional path to versions.json
        extras: optional list of extra pip install tokens to append

    Returns:
        dict with keys:
          - source: where the version came from ("override"|"torch"|"nvcc"|...)
          - detected_version: normalized version string or None
          - recommendation: normalized recommendation dict or None
          - install_command: generated pip command string or None
    """
    if cuda_override:
        source = "override"
        detected_version = cuda_override
    else:
        det = get_cuda_version()
        source = det.get("source")
        detected_version = det.get("version")

    rec = get_torch_versions(detected_version, versions_path=versions_path)

    install_cmd = None
    if rec:
        install_cmd = generate_pip_command(rec, extras=extras)

    return {
        "source": source,
        "detected_version": detected_version,
        "recommendation": rec,
        "install_command": install_cmd,
    }

