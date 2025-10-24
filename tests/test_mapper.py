import core.mapper as mapper


def test_load_versions_and_get_recommendation(tmp_path):
    data = {
        "11.8": {"torch": "2.2.0", "torchvision": "0.15.2", "torchaudio": "2.2.2", "pip_tag": "cu118"},
        "10.2": {"torch": "1.9.0"}
    }
    p = tmp_path / "versions.json"
    p.write_text(__import__('json').dumps(data))

    loaded = mapper.load_versions(str(p))
    assert "11.8" in loaded

    rec = mapper.get_recommendations("11.8", versions_data=loaded)
    assert rec.get("torch") == "2.2.0"

    # test major fallback
    rec2 = mapper.get_recommendations("11.7", versions_data=loaded)
    assert rec2.get("torch") == "2.2.0" or rec2.get("torch") == "1.9.0"

