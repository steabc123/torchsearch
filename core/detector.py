"""CUDA detection utilities.

Provides get_cuda_version() which tries multiple strategies:
 - import torch and read torch.version.cuda
 - run nvcc --version
 - run nvidia-smi as a hint

Returns a dict like:
 {"source":"torch"|"nvcc"|None, "version":"11.8", "raw": "..."}
"""
from __future__ import annotations

import re
import subprocess
from typing import Optional


def _run_cmd(cmd, timeout: float = 2.0) -> str:
    try:
        completed = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout
        )
        return (completed.stdout or "") + (completed.stderr or "")
    except Exception:
        return ""


def _parse_nvcc_output(output: str) -> Optional[str]:
    # matches: "release 11.8, V11.8.89" or "Cuda compilation tools, release 11.8"
    m = re.search(r"release\s+(\d+\.\d+)", output, re.IGNORECASE)
    if m:
        return m.group(1)
    return None


def get_cuda_version(timeout: float = 2.0) -> dict:
    """Attempt to detect CUDA version.

    Priority:
      1. import torch -> torch.version.cuda
      2. nvcc --version
      3. nvidia-smi driver hint + nvcc fallback

    Returns dict:
      {"source": "torch"|"nvcc"|None, "version": "11.8"|None, "raw": "...", "error": "..."}
    """
    # 1) Try torch if installed
    try:
        import torch

        ver = getattr(torch.version, "cuda", None)
        if ver:
            # sometimes torch.version.cuda can include micro version; normalize to major.minor
            m = re.match(r"(\d+\.\d+)", str(ver))
            if m:
                return {"source": "torch", "version": m.group(1), "raw": str(ver)}
            return {"source": "torch", "version": str(ver), "raw": str(ver)}
        # if torch exists but cuda not set, we can still check torch.cuda.is_available
        try:
            if getattr(torch.cuda, "is_available", lambda: False)():
                # couldn't get version string but cuda available
                return {"source": "torch", "version": None, "raw": None}
        except Exception:
            pass
    except Exception:
        # torch not installed or import failed
        pass

    # 2) Try nvcc
    nvcc_out = _run_cmd(["nvcc", "--version"], timeout=timeout)
    parsed = _parse_nvcc_output(nvcc_out)
    if parsed:
        return {"source": "nvcc", "version": parsed, "raw": nvcc_out}

    # 3) Try nvidia-smi as hint (driver version); still attempt nvcc via 'where' on windows or just return driver info
    nvs_out = _run_cmd(["nvidia-smi", "--query-gpu=driver_version --format=csv,noheader"], timeout=timeout)
    if nvs_out.strip():
        # we have a driver but not nvcc; return driver note
        return {"source": "nvidia-smi", "version": None, "raw": nvs_out.strip()}

    return {"source": None, "version": None, "raw": "", "error": "Unable to detect CUDA version"}


def get_gpu_status(timeout: float = 2.0) -> str:
    """Return a short human-readable GPU status string using nvidia-smi.

    Example output (multi-line):
      GPU0: NVIDIA GeForce RTX 3080, mem 10240MiB used 1234MiB, util 12%

    If nvidia-smi not available or no GPUs, returns an informative message.
    """
    out = _run_cmd(["nvidia-smi", "--query-gpu=name,memory.total,memory.used,utilization.gpu", "--format=csv,noheader,nounits"], timeout=timeout)
    if not out.strip():
        return "无法获取 GPU 信息 (nvidia-smi 不可用或没有 NVIDIA GPU)"
    lines = [l.strip() for l in out.strip().splitlines() if l.strip()]
    parsed = []
    for idx, line in enumerate(lines):
        # each line: name, total, used, util
        parts = [p.strip() for p in line.split(',')]
        if len(parts) >= 4:
            name, total, used, util = parts[0:4]
            parsed.append(f"GPU{idx}: {name}, mem {total} MiB used {used} MiB, util {util} %")
        else:
            parsed.append(f"GPU{idx}: {line}")
    return "\n".join(parsed)
