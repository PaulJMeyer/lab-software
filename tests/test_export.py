import pandas as pd
import pytest

from app.domain.models import Sample
from app.io.export import export_to_csv, export_to_excel


@pytest.fixture
def samples():
    return [
        Sample(sample_id="111111111", sample_dna="ACGT"),
        Sample(sample_id="222222222", sample_dna="TTTT"),
    ]


class TestExportToCsv:

    def test_creates_parent_directories(self, tmp_path, samples):
        path = tmp_path / "nested" / "dir" / "export.csv"
        export_to_csv(samples, path)
        assert path.exists()

    def test_contains_expected_columns_and_rows(self, tmp_path, samples):
        path = tmp_path / "export.csv"
        export_to_csv(samples, path)

        df = pd.read_csv(path)
        assert list(df.columns) == ["sample_id", "sample_dna"]
        assert len(df) == 2
        assert set(df["sample_id"]) == {111111111, 222222222}

    def test_exports_empty_sample_list(self, tmp_path):
        path = tmp_path / "export.csv"
        export_to_csv([], path)

        df = pd.read_csv(path)
        assert list(df.columns) == ["sample_id", "sample_dna"]
        assert len(df) == 0


class TestExportToExcel:

    def test_creates_parent_directories(self, tmp_path, samples):
        path = tmp_path / "nested" / "dir" / "export.xlsx"
        export_to_excel(samples, path)
        assert path.exists()

    def test_contains_expected_columns_and_rows(self, tmp_path, samples):
        path = tmp_path / "export.xlsx"
        export_to_excel(samples, path)

        df = pd.read_excel(path)
        assert list(df.columns) == ["sample_id", "sample_dna"]
        assert len(df) == 2
        assert set(df["sample_id"]) == {111111111, 222222222}

    def test_exports_empty_sample_list(self, tmp_path):
        path = tmp_path / "export.xlsx"
        export_to_excel([], path)

        df = pd.read_excel(path)
        assert list(df.columns) == ["sample_id", "sample_dna"]
        assert len(df) == 0
