"""Generate installation command strings from recommendations."""
from __future__ import annotations

from typing import Dict, List, Optional


def generate_pip_command(recommendation: Dict, extras: Optional[List[str]] = None) -> str:
    """Generate a pip install command string for the given recommendation.

    recommendation example:
      {"torch":"2.2.0","torchvision":"0.15.2","torchaudio":"2.2.2","pip_tag":"cu118"}
    """
    extras = extras or []
    parts = []
    torch_ver = recommendation.get("torch")
    torchvision_ver = recommendation.get("torchvision")
    torchaudio_ver = recommendation.get("torchaudio")
    pip_tag = recommendation.get("pip_tag")

    if torch_ver:
        if pip_tag:
            parts.append(f"torch=={torch_ver}+{pip_tag}")
        else:
            parts.append(f"torch=={torch_ver}")
    if torchvision_ver:
        if pip_tag:
            parts.append(f"torchvision=={torchvision_ver}+{pip_tag}")
        else:
            parts.append(f"torchvision=={torchvision_ver}")
    if torchaudio_ver:
        if pip_tag:
            parts.append(f"torchaudio=={torchaudio_ver}+{pip_tag}")
        else:
            parts.append(f"torchaudio=={torchaudio_ver}")

    for e in extras:
        parts.append(e)

    # base command
    if pip_tag:
        index_url = f"https://download.pytorch.org/whl/{pip_tag}"
        # Use --extra-index-url which matches common PyTorch instructions and avoids -f ambiguity
        cmd = f"pip install {' '.join(parts)} --extra-index-url {index_url}"
    else:
        cmd = f"pip install {' '.join(parts)}"
    return cmd
