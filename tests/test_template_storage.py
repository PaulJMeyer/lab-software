import pytest

from app.domain.models import FragmentTemplate
from app.io.template_storage import save_templates, load_templates


@pytest.fixture
def templates_dict():
    template_a = FragmentTemplate(name="Gene X", recognition_sequence="ACGT", wildtype_sequence="TTTT")
    template_b = FragmentTemplate(name="Gene Y", recognition_sequence="GGGG", wildtype_sequence="CCCC")
    return {template_a.name: template_a, template_b.name: template_b}


class TestLoadTemplates:

    def test_load_from_missing_file_returns_empty_dict(self, tmp_path):
        path = tmp_path / "does_not_exist.json"
        assert load_templates(path) == {}

    def test_load_raises_on_duplicate_name_in_file(self, tmp_path):
        path = tmp_path / "duplicates.json"
        path.write_text(
            '[{"name": "Gene X", "recognition_sequence": "ACGT", "wildtype_sequence": "TTTT"},'
            ' {"name": "Gene X", "recognition_sequence": "GGGG", "wildtype_sequence": "CCCC"}]',
            encoding="utf-8",
        )
        with pytest.raises(ValueError):
            load_templates(path)


class TestSaveAndLoadRoundtrip:

    def test_save_creates_parent_directories(self, tmp_path, templates_dict):
        path = tmp_path / "nested" / "dir" / "templates.json"
        save_templates(path, templates_dict)
        assert path.exists()

    def test_roundtrip_preserves_template_data(self, tmp_path, templates_dict):
        path = tmp_path / "templates.json"

        save_templates(path, templates_dict)
        loaded = load_templates(path)

        assert loaded.keys() == templates_dict.keys()
        for name, original in templates_dict.items():
            assert loaded[name].recognition_sequence == original.recognition_sequence
            assert loaded[name].wildtype_sequence == original.wildtype_sequence

    def test_save_empty_dict_produces_loadable_empty_result(self, tmp_path):
        path = tmp_path / "templates.json"
        save_templates(path, {})
        assert load_templates(path) == {}
