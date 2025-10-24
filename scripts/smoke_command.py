# ensure project root is on sys.path so we can import core when run from anywhere
import sys
from pathlib import Path
repo_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo_root))

import core.version_mapper as vm
from core.command_builder import build_install_command

cases = ["11.8", "11.7", None]
for v in cases:
    rec = vm.get_torch_versions(v)
    print(f"INPUT: {v!r}")
    print("RECOMM:", rec)
    if rec:
        cmd = build_install_command(rec.get('torch'), rec.get('torchvision'), rec.get('torchaudio'), rec.get('pip_tag'))
        print("CMD:", cmd)
    else:
        print("CMD: <no recommendation>")
    print('-' * 60)
