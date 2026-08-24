from app.analysis.dna_tools import reverse_complement, transcribe


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
