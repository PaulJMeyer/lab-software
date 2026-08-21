import pytest

from app.domain.models import Sample


class TestSampleId:

    def test_valid_id_accepted(self):
        sample = Sample("123456789", "ACGT")
        assert sample.sample_id == "123456789"

    def test_empty_id_raises(self):
        with pytest.raises(ValueError):
            Sample("", "ACGT")

    def test_id_too_short_raises(self):
        with pytest.raises(ValueError):
            Sample("12345678", "ACGT")

    def test_id_too_long_raises(self):
        with pytest.raises(ValueError):
            Sample("1234567890", "ACGT")

    def test_id_with_zero_raises(self):
        with pytest.raises(ValueError):
            Sample("120456789", "ACGT")

    def test_id_with_letters_raises(self):
        with pytest.raises(ValueError):
            Sample("12345678A", "ACGT")


class TestSampleDna:

    def test_valid_dna_accepted(self):
        sample = Sample("123456789", "ACGTNRYKMSWBDHV-")
        assert sample.sample_dna == "ACGTNRYKMSWBDHV-"

    def test_empty_dna_raises(self):
        with pytest.raises(ValueError):
            Sample("123456789", "")

    def test_dna_lowercase_is_normalized_to_uppercase(self):
        sample = Sample("123456789", "acgt")
        assert sample.sample_dna == "ACGT"

    def test_dna_with_invalid_characters_raises(self):
        with pytest.raises(ValueError):
            Sample("123456789", "ACGTX")

    def test_dna_error_message_lists_invalid_characters(self):
        with pytest.raises(ValueError, match="X"):
            Sample("123456789", "ACGTX")


class TestSampleRepr:

    def test_repr_contains_id_and_dna_length(self):
        sample = Sample("123456789", "ACGT")
        assert repr(sample) == str(("123456789", 4))
