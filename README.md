# Lab Software

A lightweight command-line application for managing biological lab samples. Supports registering, listing, updating, searching, deleting, and analyzing samples with persistent JSON storage.

---

## Features

- Register new samples with ID and DNA sequence validation (via Pydantic)
- List all registered samples with a formatted overview
- Update the DNA sequence of an existing sample (clears any previously stored analysis results)
- Search for a specific sample by ID, including any stored analysis results
- Delete samples by ID
- Analyze a sample interactively: reverse complement, RNA transcription, and protein translation
- Analysis results are stored on the sample and persisted to JSON
- Import samples from FASTA files (single or multi-record) dropped into a designated directory
- Search a sample for a DNA fragment: enter a sequence directly, or use a saved recognition/wildtype template to detect wildtype vs. mutant
- Create reusable fragment templates independently of any sample
- Export all samples (ID and DNA) to CSV and/or Excel
- Persistent storage via JSON file
- Duplicate ID prevention

---

## Usage

```bash
# Add sample
python -m app.main add --id "123456789" --dna "ACGTNNRRY"

# Add sample (interactive)
python -m app.main add

# List all samples
python -m app.main list

# Update a sample's DNA sequence
python -m app.main update --id "123456789" --dna "ACGTNNRRY"

# Search sample (also shows any stored analysis results)
python -m app.main search --id "123456789"

# Delete sample
python -m app.main delete --id "123456789"

# Analyze sample interactively
python -m app.main analyze --id "123456789"

# Import samples from FASTA files
python -m app.main import-fasta

# Create a fragment analysis template
python -m app.main add-template --name "Gene X" --recognition "ACGTACGT" --wildtype "TTTT"

# List fragment templates
python -m app.main list-templates

# Search a sample for a DNA fragment (sequence or template)
python -m app.main search-fragment --id "123456789"

# Export all samples to CSV and Excel (default: both)
python -m app.main export

# Export to a specific format only
python -m app.main export --format csv
python -m app.main export --format xlsx
```

### Interactive analysis

`analyze` presents a numbered menu of analyses that haven't been performed yet for the given sample:

```
Available analyses:
1. Reverse complement
2. Transcription (DNA to RNA)
3. Translation (RNA to protein)
Select an analysis to perform: 1
✓ Reverse complement: TAGCAAGATGCATGACGACTGACTGACTGACTGCAGCAGT
Do you want to perform further analysis? [y/N]:
```

Each result is saved immediately and shown afterwards in `search`. Once all analyses have been performed, `analyze` reports that nothing is left to do. Updating a sample's DNA sequence clears all previously stored results, since they no longer apply to the new sequence.

Translation looks for the first start codon (`ATG`) and translates codon by codon until a stop codon or the end of the sequence. If no start codon is found, it reports that the DNA does not contain a gene rather than storing a result.

### FASTA import

Drop one or more `.fasta`/`.fa` files into `data/fasta_import/` (created automatically on first run), then:

```bash
python -m app.main import-fasta
```

Each `>header` record in each file becomes a new sample with a randomly generated, unique 9-digit ID (FASTA headers are free-form text and don't match the sample ID format, so they aren't used as the ID directly). Files can contain multiple records (multi-FASTA); multi-line sequences under one header are concatenated automatically.

```
✓ Imported 'gene_1 description text' as sample '384719562'.
✓ Imported 'gene_2' as sample '927154836'.

Import complete: 2 sample(s) imported, 0 failed.
```

Records with invalid DNA characters are skipped and reported, without stopping the rest of the import. Successfully processed files are moved into `data/fasta_import/processed/` (timestamped) so they aren't imported again; a file with no valid FASTA records is left in place and reported. Analyses are **not** run automatically on imported samples — use `analyze` afterwards.

### Fragment search & templates

`search-fragment --id <id>` searches a sample's DNA in one of two modes:

1. **Enter a sequence** — type a DNA sequence to search for; every match position in the sample is reported (or "not found"). This is a plain presence/position check, with no wildtype comparison.
2. **Use a saved template** — pick from your saved templates. The tool locates the template's recognition sequence in the sample, takes the region immediately following it (same length as the template's wildtype sequence), and compares it exactly: a match reports **Wildtype**, any difference reports **Mutant**.

Templates are created independently with their own command, ahead of any specific sample:

```bash
python -m app.main add-template --name "Gene X" --recognition "ACGTACGT" --wildtype "TTTT"
```

- **Name** — a free-text label (e.g. a gene name)
- **Recognition sequence** — the DNA sequence to search for in a sample
- **Wildtype sequence** — the expected sequence of the region directly following the recognition sequence; also defines how many bases are compared

```
Available templates:
1. Gene X
Select a template: 1

Template:             Gene X
Recognition sequence: ACGTACGT
Region found:         GGGG
Wildtype reference:   TTTT
Result:               Mutant
```

This is intended as groundwork for future mutation-analysis workflows. Fragment search results are shown live and are **not** currently stored on the sample (unlike `analyze`'s reverse complement/transcription/translation, which are persisted).

### Export

```bash
python -m app.main export
```

Writes all samples' ID and DNA sequence to timestamped files in `data/exports/` — `lab_samples_<timestamp>.csv` and `.xlsx` by default, or only one via `--format csv` / `--format xlsx`. Each run creates new files rather than overwriting previous exports. Currently exports base sample data only; derived analysis results and fragment-search/mutation-match data are not included yet (see roadmap).

---

## Validation Rules

**Sample ID**
- Must be exactly 9 characters long
- Only digits 1–9 (no 0)
- Must be unique

**DNA Sequence**
- Must not be empty
- Allowed characters (IUPAC notation): `A C G T N R Y K M S W B D H V -`

---

## Testing

Tests are written with `pytest` and cover validation, business logic, persistence, DNA analysis, and all CLI commands.

```bash
# Run tests
uv run pytest -v

# Run tests with coverage
uv run pytest --cov=app --cov-report=term-missing -v
```

Tests run automatically on every push and pull request via GitHub Actions; the coverage summary is shown in the workflow run's job summary.

---

## Roadmap

- [x] Unit tests (pytest)
- [x] Sample update
- [x] Pydantic-based validation
- [x] Test coverage tracked in CI
- [x] DNA analysis tools:
  - [x] Reverse complement
  - [x] Transcription
  - [x] Translation (with start/stop codon detection)
  - [x] Search for DNA fragments (free sequence + reusable templates for wildtype/mutant comparison)
- [x] FASTA import: drop FASTA files into a designated directory to have them registered
- [ ] Template management: update/delete templates
- [x] Export (CSV, Excel): base sample data
  - [ ] Include derived analysis fields / mutation-match results in export
- [ ] Perspective: direct download from bioinformatics databases (e.g. NCBI, ENA)

---

## Dependencies

| Package  | Version  |
|----------|----------|
| click    | ≥ 8.3.1  |
| pandas   | ≥ 3.0.1  |
| pydantic | ≥ 2.12.5 |
| openpyxl | ≥ 3.1.0  |

Dev dependencies (testing): `pytest`, `pytest-cov`.
