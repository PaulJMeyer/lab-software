import pytest

from app.analysis.dna_tools import (
    reverse_complement,
    transcribe,
    translate,
    find_fragment_positions,
    extract_region_after,
)


class TestReverseComplement:

    def test_simple_sequence(self):
        assert reverse_complement("ACGT") == "ACGT"

    def test_non_palindromic_sequence(self):
        assert reverse_complement("AACCGGTT") == "AACCGGTT"

    def test_reverses_order(self):
        assert reverse_complement("ATCG") == "CGAT"

    def test_handles_ambiguity_codes(self):
        assert reverse_complement("RYKMSWBDHVN") == "NBDHVWSKMRY"

    def test_handles_gap_character(self):
        assert reverse_complement("A-T") == "A-T"


class TestTranscribe:

    def test_replaces_t_with_u(self):
        assert transcribe("ACGT") == "ACGU"

    def test_sequence_without_t_unchanged(self):
        assert transcribe("ACG") == "ACG"

    def test_multiple_t_replaced(self):
        assert transcribe("TTTT") == "UUUU"


class TestTranslate:

    def test_translates_simple_gene(self):
        # ATG AAA TAA -> Met Lys Stop
        assert translate("ATGAAATAA") == "MK"

    def test_translation_stops_at_stop_codon(self):
        # ATG AAA TAA GGG -> should stop at TAA, ignore trailing GGG
        assert translate("ATGAAATAAGGG") == "MK"

    def test_translation_without_stop_codon_uses_remaining_sequence(self):
        # ATG AAA CCC (no stop codon) -> translate what's there
        assert translate("ATGAAACCC") == "MKP"

    def test_start_codon_not_at_beginning_is_found(self):
        # leading bases before ATG should be skipped
        assert translate("GGGATGAAATAA") == "MK"

    def test_no_start_codon_raises_value_error(self):
        with pytest.raises(ValueError, match="does not contain a gene"):
            translate("CCCCCCCCCC")

    def test_incomplete_trailing_codon_is_ignored(self):
        # ATG AAA followed by a single leftover base
        assert translate("ATGAAAG") == "MK"


class TestFindFragmentPositions:

    def test_single_match(self):
        assert find_fragment_positions("AAACGTAAA", "ACGT") == [2]

    def test_no_match_returns_empty_list(self):
        assert find_fragment_positions("AAAA", "TTTT") == []

    def test_multiple_non_overlapping_matches(self):
        assert find_fragment_positions("ACGTGGACGT", "ACGT") == [0, 6]

    def test_overlapping_matches_are_found(self):
        assert find_fragment_positions("AAAA", "AA") == [0, 1, 2]

    def test_empty_pattern_returns_empty_list(self):
        assert find_fragment_positions("ACGT", "") == []

    def test_pattern_longer_than_sequence_returns_empty_list(self):
        assert find_fragment_positions("AC", "ACGT") == []


class TestExtractRegionAfter:

    def test_extracts_region_directly_after_match(self):
        assert extract_region_after("GGACGTTTTTCC", "ACGT", 4) == "TTTT"

    def test_uses_first_match_when_multiple_present(self):
        assert extract_region_after("ACGTAAAAACGTBBBB", "ACGT", 4) == "AAAA"

    def test_recognition_sequence_not_found_returns_none(self):
        assert extract_region_after("GGGGCCCC", "ACGT", 4) is None

    def test_not_enough_bases_remaining_returns_none(self):
        assert extract_region_after("GGACGTTT", "ACGT", 4) is None

    def test_region_length_zero_returns_empty_string(self):
        assert extract_region_after("GGACGTCC", "ACGT", 0) == ""
