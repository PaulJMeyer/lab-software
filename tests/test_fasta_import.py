from app.io.fasta_import import parse_fasta, generate_sample_id


class TestParseFasta:

    def test_single_record(self):
        text = ">Sample One\nACGT\n"
        assert parse_fasta(text) == [("Sample One", "ACGT")]

    def test_multiline_sequence_is_concatenated(self):
        text = ">Sample One\nACGT\nTTTT\nGGGG\n"
        assert parse_fasta(text) == [("Sample One", "ACGTTTTTGGGG")]

    def test_multiple_records(self):
        text = ">First\nACGT\n>Second\nTTTT\n"
        assert parse_fasta(text) == [("First", "ACGT"), ("Second", "TTTT")]

    def test_header_prefix_is_stripped(self):
        text = ">  Sample with spaces  \nACGT\n"
        assert parse_fasta(text) == [("Sample with spaces", "ACGT")]

    def test_blank_lines_are_ignored(self):
        text = ">Sample One\n\nACGT\n\nTTTT\n\n"
        assert parse_fasta(text) == [("Sample One", "ACGTTTTT")]

    def test_no_header_returns_empty_list(self):
        text = "ACGT\nTTTT\n"
        assert parse_fasta(text) == []

    def test_empty_text_returns_empty_list(self):
        assert parse_fasta("") == []

    def test_record_with_empty_sequence(self):
        text = ">Header only\n>Second\nACGT\n"
        assert parse_fasta(text) == [("Header only", ""), ("Second", "ACGT")]


class TestGenerateSampleId:

    def test_generates_nine_digit_id(self):
        sample_id = generate_sample_id(set())
        assert len(sample_id) == 9

    def test_generated_id_contains_only_digits_1_to_9(self):
        sample_id = generate_sample_id(set())
        assert set(sample_id).issubset(set("123456789"))

    def test_avoids_existing_ids(self):
        # With only one possible "existing" id excluded, a generated id
        # should never collide by construction (checked via loop), but we
        # can at least assert it differs from a given single existing id
        # over several generations (statistically overwhelming, but to keep
        # this deterministic we directly test the exclusion mechanism).
        existing = {"111111111"}
        for _ in range(20):
            assert generate_sample_id(existing) not in existing

    def test_retries_on_collision(self, monkeypatch):
        import app.io.fasta_import as fasta_import_module

        # First 9 random.choice calls spell out an id that already exists,
        # the next 9 spell out a free one — forces the retry loop to run twice.
        sequence = iter("111111111" "222222222")
        monkeypatch.setattr(fasta_import_module.random, "choice", lambda seq: next(sequence))

        result = generate_sample_id({"111111111"})
        assert result == "222222222"
