import sys
import types

import core.detector as detector


class _Completed:
    def __init__(self, stdout="", stderr=""):
        self.stdout = stdout
        self.stderr = stderr


def test_get_cuda_version_with_torch(monkeypatch):
    # create a fake torch module
    fake_torch = types.ModuleType("torch")
    class _Ver:
        cuda = "11.8"
    fake_torch.version = _Ver()
    def fake_is_available():
        return True
    fake_torch.cuda = types.SimpleNamespace(is_available=fake_is_available)

    monkeypatch.setitem(sys.modules, "torch", fake_torch)

    res = detector.get_cuda_version()
    assert res["source"] == "torch"
    assert res["version"] == "11.8"


def test_get_cuda_version_nvcc(monkeypatch):
    # ensure torch not present
    monkeypatch.delitem(sys.modules, "torch", raising=False)

    def fake_run(cmd, capture_output=True, text=True, timeout=2.0):
        # emulate nvcc --version being called
        if isinstance(cmd, list) and cmd[0] == "nvcc":
            return _Completed(stdout="Cuda compilation tools, release 11.7, V11.7.64\n")
        return _Completed(stdout="")

    monkeypatch.setattr(detector.subprocess, "run", fake_run)
    res = detector.get_cuda_version()
    assert res["source"] == "nvcc"
    assert res["version"] == "11.7"

