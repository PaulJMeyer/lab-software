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
  - [ ] Search for DNA fragments
- [ ] FASTA import: drop FASTA files into a designated directory to have them registered and analyzed
- [ ] Perspective: direct download from bioinformatics databases (e.g. NCBI, ENA)
- [ ] Export (CSV, Excel)

---

## Dependencies

| Package  | Version  |
|----------|----------|
| click    | ≥ 8.3.1  |
| pandas   | ≥ 3.0.1  |
| pydantic | ≥ 2.12.5 |

Dev dependencies (testing): `pytest`, `pytest-cov`.
