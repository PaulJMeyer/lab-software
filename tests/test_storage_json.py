import pytest

from app.domain.models import Sample
from app.io.storage_json import save_samples, load_samples


@pytest.fixture
def samples_dict():
    sample_a = Sample("111111111", "ACGT")
    sample_b = Sample("222222222", "TTTT")
    return {sample_a.sample_id: sample_a, sample_b.sample_id: sample_b}


class TestLoadSamples:

    def test_load_from_missing_file_returns_empty_dict(self, tmp_path):
        path = tmp_path / "does_not_exist.json"
        assert load_samples(path) == {}

    def test_load_raises_on_duplicate_id_in_file(self, tmp_path):
        path = tmp_path / "duplicates.json"
        path.write_text(
            '[{"sample_id": "111111111", "sample_dna": "ACGT"},'
            ' {"sample_id": "111111111", "sample_dna": "TTTT"}]',
            encoding="utf-8",
        )
        with pytest.raises(ValueError):
            load_samples(path)


class TestSaveAndLoadRoundtrip:

    def test_save_creates_parent_directories(self, tmp_path, samples_dict):
        path = tmp_path / "nested" / "dir" / "lab_state.json"
        save_samples(path, samples_dict)
        assert path.exists()

    def test_roundtrip_preserves_sample_data(self, tmp_path, samples_dict):
        path = tmp_path / "lab_state.json"

        save_samples(path, samples_dict)
        loaded = load_samples(path)

        assert loaded.keys() == samples_dict.keys()
        for sample_id, original in samples_dict.items():
            assert loaded[sample_id].sample_dna == original.sample_dna

    def test_save_empty_dict_produces_loadable_empty_result(self, tmp_path):
        path = tmp_path / "lab_state.json"
        save_samples(path, {})
        assert load_samples(path) == {}
