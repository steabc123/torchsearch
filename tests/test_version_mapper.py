import json
import core.version_mapper as vm


def test_get_torch_versions_and_fallback(tmp_path):
    data = {
        "11.8": {"torch": "2.2.0", "torchvision": "0.15.2", "torchaudio": "2.2.2", "pip_tag": "cu118"},
        "10.2": {"torch": "1.9.0"}
    }
    p = tmp_path / "versions.json"
    p.write_text(json.dumps(data))

    res = vm.get_torch_versions("11.8", versions_path=str(p))
    assert res is not None
    assert res["torch"] == "2.2.0"
    assert res["pip_tag"] == "cu118"

    # request 11.7 should fallback to the closest 11.x entry (11.8)
    res2 = vm.get_torch_versions("11.7", versions_path=str(p))
    assert res2 is not None
    assert res2["torch"] == "2.2.0"

