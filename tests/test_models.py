import pytest
from pydantic import ValidationError

from app.domain.models import Sample, FragmentTemplate


class TestSampleId:

    def test_valid_id_accepted(self):
        sample = Sample(sample_id="123456789", sample_dna="ACGT")
        assert sample.sample_id == "123456789"

    def test_empty_id_raises(self):
        with pytest.raises(ValidationError):
            Sample(sample_id="", sample_dna="ACGT")

    def test_id_too_short_raises(self):
        with pytest.raises(ValidationError):
            Sample(sample_id="12345678", sample_dna="ACGT")

    def test_id_too_long_raises(self):
        with pytest.raises(ValidationError):
            Sample(sample_id="1234567890", sample_dna="ACGT")

    def test_id_with_zero_raises(self):
        with pytest.raises(ValidationError):
            Sample(sample_id="120456789", sample_dna="ACGT")

    def test_id_with_letters_raises(self):
        with pytest.raises(ValidationError):
            Sample(sample_id="12345678A", sample_dna="ACGT")


class TestSampleDna:

    def test_valid_dna_accepted(self):
        sample = Sample(sample_id="123456789", sample_dna="ACGTNRYKMSWBDHV-")
        assert sample.sample_dna == "ACGTNRYKMSWBDHV-"

    def test_empty_dna_raises(self):
        with pytest.raises(ValidationError):
            Sample(sample_id="123456789", sample_dna="")

    def test_dna_lowercase_is_normalized_to_uppercase(self):
        sample = Sample(sample_id="123456789", sample_dna="acgt")
        assert sample.sample_dna == "ACGT"

    def test_dna_with_invalid_characters_raises(self):
        with pytest.raises(ValidationError):
            Sample(sample_id="123456789", sample_dna="ACGTX")

    def test_dna_error_message_lists_invalid_characters(self):
        with pytest.raises(ValidationError, match="X"):
            Sample(sample_id="123456789", sample_dna="ACGTX")


class TestSampleRepr:

    def test_repr_contains_id_and_dna_length(self):
        sample = Sample(sample_id="123456789", sample_dna="ACGT")
        assert repr(sample) == str(("123456789", 4))


class TestSampleDerivedFields:

    def test_derived_fields_default_to_none(self):
        sample = Sample(sample_id="123456789", sample_dna="ACGT")
        assert sample.reverse_complement is None
        assert sample.rna_transcript is None
        assert sample.protein is None

    def test_derived_fields_can_be_set(self):
        sample = Sample(
            sample_id="123456789",
            sample_dna="ACGT",
            reverse_complement="ACGT",
            rna_transcript="ACGU",
            protein="M",
        )
        assert sample.reverse_complement == "ACGT"
        assert sample.rna_transcript == "ACGU"
        assert sample.protein == "M"


class TestFragmentTemplate:

    def test_valid_template_accepted(self):
        template = FragmentTemplate(name="Gene X", recognition_sequence="ACGT", wildtype_sequence="TTTT")
        assert template.name == "Gene X"
        assert template.recognition_sequence == "ACGT"
        assert template.wildtype_sequence == "TTTT"

    def test_empty_name_raises(self):
        with pytest.raises(ValidationError):
            FragmentTemplate(name="", recognition_sequence="ACGT", wildtype_sequence="TTTT")

    def test_whitespace_only_name_raises(self):
        with pytest.raises(ValidationError):
            FragmentTemplate(name="   ", recognition_sequence="ACGT", wildtype_sequence="TTTT")

    def test_name_is_stripped(self):
        template = FragmentTemplate(name="  Gene X  ", recognition_sequence="ACGT", wildtype_sequence="TTTT")
        assert template.name == "Gene X"

    def test_invalid_recognition_sequence_raises(self):
        with pytest.raises(ValidationError):
            FragmentTemplate(name="Gene X", recognition_sequence="ACGTX", wildtype_sequence="TTTT")

    def test_invalid_wildtype_sequence_raises(self):
        with pytest.raises(ValidationError):
            FragmentTemplate(name="Gene X", recognition_sequence="ACGT", wildtype_sequence="TTTTX")

    def test_recognition_and_wildtype_normalized_to_uppercase(self):
        template = FragmentTemplate(name="Gene X", recognition_sequence="acgt", wildtype_sequence="tttt")
        assert template.recognition_sequence == "ACGT"
        assert template.wildtype_sequence == "TTTT"
