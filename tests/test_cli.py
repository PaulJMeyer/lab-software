import pytest
from click.testing import CliRunner

from app.scripts.cli import cli


@pytest.fixture
def runner():
    return CliRunner()


class TestAddCommand:

    def test_add_valid_sample_succeeds(self, runner):
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["add", "--id", "123456789", "--dna", "ACGT"])
            assert result.exit_code == 0
            assert "added successfully" in result.output

    def test_add_invalid_dna_via_flag_shows_error(self, runner):
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["add", "--id", "123456789", "--dna", "ACGTX"])
            assert result.exit_code == 2
            assert "Error" in result.output

    def test_add_invalid_id_via_flag_shows_error(self, runner):
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["add", "--id", "12345", "--dna", "ACGT"])
            assert result.exit_code == 2
            assert "Error" in result.output

    def test_add_duplicate_id_shows_error(self, runner):
        with runner.isolated_filesystem():
            runner.invoke(cli, ["add", "--id", "123456789", "--dna", "ACGT"])
            result = runner.invoke(cli, ["add", "--id", "123456789", "--dna", "TTTT"])
            assert "Error" in result.output

    def test_add_reprompts_for_invalid_id_before_asking_dna(self, runner):
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["add"], input="12345\n123456789\nACGT\n")
            assert result.exit_code == 0
            assert "added successfully" in result.output
            output_before_dna_prompt = result.output.split("DNA sequence:")[0]
            assert "Sample ID must be exactly 9 characters long" in output_before_dna_prompt

    def test_add_reprompts_for_invalid_dna(self, runner):
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["add"], input="123456789\nXYZ\nACGT\n")
            assert result.exit_code == 0
            assert "added successfully" in result.output
            assert "Invalid characters in DNA sequence" in result.output


class TestListCommand:

    def test_list_with_no_samples(self, runner):
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["list"])
            assert "No samples available" in result.output

    def test_list_shows_added_sample(self, runner):
        with runner.isolated_filesystem():
            runner.invoke(cli, ["add", "--id", "123456789", "--dna", "ACGT"])
            result = runner.invoke(cli, ["list"])
            assert "123456789" in result.output
            assert "1 sample(s) total" in result.output


class TestUpdateCommand:

    def test_update_existing_sample_succeeds(self, runner):
        with runner.isolated_filesystem():
            runner.invoke(cli, ["add", "--id", "123456789", "--dna", "ACGT"])
            result = runner.invoke(cli, ["update", "--id", "123456789", "--dna", "TTTT"])
            assert "updated successfully" in result.output

    def test_update_unknown_id_shows_error(self, runner):
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["update", "--id", "999999999", "--dna", "TTTT"])
            assert "Error" in result.output

    def test_update_reprompts_for_invalid_dna(self, runner):
        with runner.isolated_filesystem():
            runner.invoke(cli, ["add", "--id", "123456789", "--dna", "ACGT"])
            result = runner.invoke(cli, ["update"], input="123456789\nXYZ\nTTTT\n")
            assert result.exit_code == 0
            assert "updated successfully" in result.output
            assert "Invalid characters in DNA sequence" in result.output


class TestDeleteCommand:

    def test_delete_existing_sample_succeeds(self, runner):
        with runner.isolated_filesystem():
            runner.invoke(cli, ["add", "--id", "123456789", "--dna", "ACGT"])
            result = runner.invoke(cli, ["delete", "--id", "123456789"])
            assert "deleted successfully" in result.output

    def test_delete_unknown_id_shows_error(self, runner):
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["delete", "--id", "999999999"])
            assert "Error" in result.output


class TestSearchCommand:

    def test_search_existing_sample_shows_details(self, runner):
        with runner.isolated_filesystem():
            runner.invoke(cli, ["add", "--id", "123456789", "--dna", "ACGT"])
            result = runner.invoke(cli, ["search", "--id", "123456789"])
            assert "123456789" in result.output
            assert "ACGT" in result.output

    def test_search_unknown_id_shows_error(self, runner):
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["search", "--id", "999999999"])
            assert "No sample found" in result.output


class TestAnalyzeCommand:

    def test_analyze_existing_sample_shows_results(self, runner):
        with runner.isolated_filesystem():
            runner.invoke(cli, ["add", "--id", "123456789", "--dna", "ACGT"])
            result = runner.invoke(cli, ["analyze", "--id", "123456789"])
            assert "Reverse complement: ACGT" in result.output
            assert "RNA transcript:     ACGU" in result.output

    def test_analyze_unknown_id_shows_error(self, runner):
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ["analyze", "--id", "999999999"])
            assert "No sample found" in result.output


class TestPersistenceAcrossInvocations:

    def test_data_persists_between_cli_calls(self, runner):
        with runner.isolated_filesystem():
            runner.invoke(cli, ["add", "--id", "123456789", "--dna", "ACGT"])
            result = runner.invoke(cli, ["search", "--id", "123456789"])
            assert "ACGT" in result.output
