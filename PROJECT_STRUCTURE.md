# Project Structure – lab-software

Brief overview of the layout, modules, and responsibilities of the `lab-software` project.

## Directory Tree

```
lab-software/
├── app/
│   ├── analysis/
│   │   └── dna_tools.py      # DNA sequence analysis (reverse complement, transcription, translation)
│   ├── domain/
│   │   └── models.py         # Data models (Sample, FragmentTemplate) incl. validation
│   ├── io/
│   │   ├── storage_json.py    # Persistence: load/save samples as JSON
│   │   ├── template_storage.py # Persistence: load/save fragment templates as JSON
│   │   ├── fasta_import.py   # FASTA parsing and sample ID generation for import
│   │   └── export.py         # Sample export to CSV and Excel
│   ├── scripts/
│   │   ├── cli.py            # Click-based CLI commands
│   │   └── demo.py           # Manual demo/test script
│   ├── services/
│   │   ├── lab_service.py    # Business logic / in-memory sample management
│   │   └── template_service.py # Business logic / in-memory fragment template management
│   └── main.py                # Entry point (calls cli())
├── tests/
│   ├── __init__.py
│   ├── test_models.py        # Tests for Sample validation
│   ├── test_lab_service.py   # Tests for LabService
│   ├── test_template_service.py # Tests for TemplateService
│   ├── test_storage_json.py  # Tests for JSON persistence (samples)
│   ├── test_template_storage.py # Tests for JSON persistence (templates)
│   ├── test_dna_tools.py     # Tests for DNA analysis functions
│   ├── test_fasta_import.py  # Tests for FASTA parsing and ID generation
│   ├── test_cli.py           # Tests for CLI commands (Click CliRunner)
│   └── test_main.py          # Smoke test for the entry point
├── .github/
│   └── workflows/
│       └── tests.yml         # CI: runs pytest with coverage on every push/PR
├── data/
│   ├── lab_state.json         # persisted sample state (gitignored)
│   ├── fragment_templates.json # persisted fragment templates (gitignored)
│   ├── fasta_import/         # drop zone for FASTA files (gitignored)
│   │   └── processed/        # files moved here after import
│   └── exports/               # exported CSV/Excel files (gitignored)
├── pyproject.toml
├── uv.lock
├── README.md
├── .python-version
└── .gitignore
```

## Architecture

4-layer separation:

- **domain** – pure data models, no I/O, no dependency on other app layers
- **analysis** – pure DNA sequence analysis functions, no I/O, no dependency on `services` or `io`
- **services** – business logic, holds the in-memory state (`LabService`)
- **io** – persistence layer, converts domain objects to/from JSON
- **scripts** – application entry points (CLI, demo)

Dependency direction: `scripts → services → domain`, `scripts → io → domain`, and `scripts → analysis → domain`. `services` does not know about `io` or `analysis` directly (persistence and analysis are orchestrated by the CLI, not by the service itself).

## Modules in Detail

### `app/domain/models.py`
- **`Sample`**: a `pydantic.BaseModel` with `sample_id` (exactly 9 characters, digits 1–9 only) and `sample_dna` (IUPAC character set: `ACGTNRYKMSWBDHV-`).
- Validation happens via `field_validator`s (`validate_sample_id`, `validate_sample_dna`); raises `pydantic.ValidationError` on invalid input.
- DNA sequence is automatically normalized to uppercase.
- **Derived analysis fields** (all optional, default `None`): `reverse_complement`, `rna_transcript`, `protein`. Populated and persisted once the corresponding analysis has been performed via `analyze`; reset whenever `sample_dna` changes (see `LabService.update_sample`).
- **`IUPAC_COMPLEMENT`**: dict mapping each IUPAC base/ambiguity code to its complement, shared with `app/analysis/dna_tools.py`.
- **`validate_sample_id_format`** / **`validate_sample_dna_format`**: standalone validation functions used both by `Sample`'s field validators and by the CLI's per-option prompt callbacks (see `app/scripts/cli.py`), so the rules live in one place.
- **`FragmentTemplate`**: a `pydantic.BaseModel` for fragment/mutation-analysis templates, with `name` (non-empty, stripped), `recognition_sequence`, and `wildtype_sequence` (both validated/normalized the same way as `Sample.sample_dna`). Used by `search-fragment` to compare a sample's sequence against a known reference region. `validate_template_name_format` backs the name validator.

### `app/analysis/dna_tools.py`
- `reverse_complement(sequence)`: returns the reverse complement of a DNA sequence, using `IUPAC_COMPLEMENT`.
- `transcribe(sequence)`: returns the RNA transcript (replaces `T` with `U`).
- `translate(sequence)`: finds the first start codon (`ATG`), translates codon by codon (using the standard genetic code, `CODON_TABLE`) until a stop codon (`TAA`/`TAG`/`TGA`) or the end of the sequence. Raises `ValueError("DNA does not contain a gene (no start codon found).")` if no start codon is present.
- Pure functions, no validation — operate on already-validated `Sample.sample_dna` strings.
- Adapted from a standalone reference script in the sister `bioinformatics-tools` project.
- `find_fragment_positions(sequence, pattern)`: returns all 0-based start positions where `pattern` occurs in `sequence`, including overlapping matches. Empty list if not found.
- `extract_region_after(sequence, recognition_sequence, region_length)`: finds the first occurrence of `recognition_sequence`, returns the `region_length` bases immediately following it, or `None` if the recognition sequence isn't found or too few bases remain after it. Used by `search-fragment`'s template mode to extract the region to compare against a `FragmentTemplate.wildtype_sequence`.

### `app/services/lab_service.py`
- **`LabService`**: holds samples in a dict (`sample_id → Sample`).
- Methods: `add_sample`, `list_samples`, `update_sample`, `delete_sample`, `find_sample`, `get_state`, `set_state`.
- `update_sample(sample_id, sample_dna)`: replaces the DNA of an existing sample (ID stays fixed as the primary key); validates the new DNA via the `Sample` constructor. Since it constructs a brand-new `Sample` with only `sample_id`/`sample_dna`, all derived analysis fields (`reverse_complement`, `rna_transcript`, `protein`) reset to `None` automatically.
- Prevents duplicate IDs in `add_sample`.

### `app/services/template_service.py`
- **`TemplateService`**: holds fragment templates in a dict (`name → FragmentTemplate`), mirroring `LabService`'s structure.
- Methods: `add_template`, `list_templates`, `find_template`, `get_state`, `set_state`. Prevents duplicate template names in `add_template`. No update/delete yet — templates are currently create-and-list only (see roadmap).

### `app/io/storage_json.py`
- `save_samples(path, samples_dict)`: writes samples as a JSON list via `Sample.model_dump()`, creates the target directory if needed.
- `load_samples(path)`: reads JSON, builds `Sample` objects via `Sample.model_validate()`, detects duplicate IDs in the file.
- Returns an empty dict if the file doesn't exist.
- Using `model_dump`/`model_validate` (rather than manual field-by-field mapping) means derived analysis fields are persisted and restored automatically without touching this module when `Sample`'s fields change.

### `app/io/template_storage.py`
- `save_templates(path, templates_dict)` / `load_templates(path)`: same pattern as `storage_json.py`, but for `FragmentTemplate`, keyed by `name` and persisted to `data/fragment_templates.json`. Detects duplicate names in the file on load.

### `app/io/fasta_import.py`
- `parse_fasta(text)`: parses FASTA-formatted text into a list of `(header, sequence)` tuples. Supports multi-FASTA files (several `>header` records per file); multi-line sequences under one header are concatenated; blank lines are ignored; returns an empty list if no `>` header is found.
- `generate_sample_id(existing_ids)`: generates a random 9-digit sample ID (digits 1-9 only, matching `Sample`'s ID format), retrying until it doesn't collide with `existing_ids`.
- No validation of sequence content here — invalid DNA is caught later by `Sample`'s own validation when the CLI constructs the sample.

### `app/io/export.py`
- `export_to_csv(samples, path)` / `export_to_excel(samples, path)`: build a `pandas.DataFrame` from a list of `Sample` objects (columns: `sample_id`, `sample_dna` only — `EXPORT_COLUMNS`) and write it to CSV or `.xlsx`, creating parent directories if needed. Both accept an empty sample list (writes a header-only file).
- Only base sample data is exported for now; derived analysis fields and fragment-search/mutation-match results are explicitly left out (see roadmap) — `EXPORT_COLUMNS` is the single place to extend this later.
- Requires `openpyxl` (added as a dependency) for `.xlsx` writing via pandas.

### `app/scripts/cli.py`
- Click group `cli` with commands: `add`, `list`, `update`, `delete`, `search`, `analyze`, `import-fasta`, `add-template`, `list-templates`, `search-fragment`, `export`.
- **Per-field validation callbacks** (`validate_id_option`, `validate_dna_option`): attached to the `--id`/`--dna` options of `add` and `update`. They call `validate_sample_id_format`/`validate_sample_dna_format` from `models.py` and raise `click.BadParameter` on failure. Combined with `prompt=True`, this makes Click reprompt for that specific field immediately — e.g. an invalid ID is caught and re-asked before the DNA sequence is even requested, rather than only surfacing after both fields have been entered. When a value is passed non-interactively via the flag (not the prompt) and fails validation, Click reports a standard usage error and exits with code 2, instead of falling through to the command's own try/except.
- **`ANALYSES`**: a registry list of `(field_name, label, function)` tuples — `reverse_complement`, `rna_transcript` (via `transcribe`), and `protein` (via `translate`) — driving the `analyze` menu.
- `analyze --id <id>`: interactive loop. Computes which analyses haven't been performed yet (`getattr(sample, field_name) is None`), shows them as a numbered menu (`click.IntRange` reprompts on out-of-range/non-numeric input), runs the chosen one, stores the result on the `Sample` instance, saves state immediately, then asks "Do you want to perform further analysis?" (`click.confirm`). Repeats until the user declines or no analyses remain; reports completion once nothing is left. A translation attempt without a start codon shows the error but doesn't store a result, so it remains offered on the next run.
- `search --id <id>`: shows sample details plus any derived fields that are not `None` (reverse complement, RNA transcript, protein). `list` intentionally does **not** show these — it stays a compact overview.
- `import-fasta`: scans `data/fasta_import/` for `.fasta`/`.fa` files, parses each with `parse_fasta`, and registers one `Sample` per record with a randomly generated ID (via `generate_sample_id`). Invalid records (e.g. bad DNA characters) are skipped with an error message; the rest of the file and any other files still get processed. A file with no parsable FASTA records is reported and left in place (not moved). Successfully processed files are moved into `data/fasta_import/processed/`, prefixed with a timestamp to avoid name collisions on repeated imports. Prints a final summary of imported/failed record counts. Does not automatically run any analyses — those remain a separate step via `analyze`.
- `add-template --name <name> --recognition <seq> --wildtype <seq>`: creates a `FragmentTemplate`, independent of any sample (its own top-level command, not nested under `analyze` or `search-fragment`). Uses the same `validate_dna_option` callback for reprompting on invalid recognition/wildtype sequences; `name` uniqueness is enforced by `TemplateService.add_template`.
- `list-templates`: shows all saved templates (name, recognition sequence, wildtype sequence) in a compact table, or a hint to run `add-template` if none exist.
- `search-fragment --id <id>`: interactive, two modes selected via a numbered prompt (`click.IntRange` reprompts on invalid input):
  1. **Enter a sequence** — free-text DNA sequence (validated/reprompted via `_dna_value_proc` with `click.prompt`'s `value_proc`), searched in the sample with `find_fragment_positions`. Reports all match positions (1-based for readability) or "not found". No wildtype/mutant comparison in this mode — purely a presence/position check.
  2. **Use a saved template** — lists templates from `TemplateService`, lets the user pick one, then uses `extract_region_after` to pull the region directly following the template's `recognition_sequence` (region length = length of `wildtype_sequence`). Compares that region to `wildtype_sequence`: exact match → "Wildtype", any difference → "Mutant" (shown in yellow, as a value worth noting rather than an error). If the recognition sequence isn't found in the sample, or too little sequence remains after it, reports that instead.
  - Fragment search results are **not** persisted to the sample (unlike `analyze`'s three fixed analyses) — the number of templates is open-ended, so there's no fixed set of fields to store them in. It's a live query each time; see roadmap/notes for potential future persistence.
- `export --format {csv,xlsx,both}` (default `both`): exports all samples' base data (ID, DNA) to `data/exports/lab_samples_<timestamp>.csv`/`.xlsx` via `app/io/export.py`. Skips with a message if there are no samples. Reports each file written.
- `get_service()` loads the state from `data/lab_state.json` on every call, creates a `LabService`, and returns it (no caching between commands – a new process starts on every CLI invocation).
- After `add`/`update`/`delete`/a successful `analyze` step, the state is immediately saved again.
- Catches `(ValidationError, ValueError)` around commands that can fail; error output is colored via `click.style` (green = success, red = error).

### `app/scripts/demo.py`
- Standalone script for manually walking through the workflow (load → add sample → display → save), independent of the CLI.
- Excluded from coverage measurement (`[tool.coverage.run] omit` in `pyproject.toml`), since it's a manual/demo entry point, not a tested code path.

### `app/main.py`
- Sole purpose: imports and starts `cli()` from `app/scripts/cli.py`.

### `tests/`
- Flat structure, a single `__init__.py` at the root (ensures pytest adds the project root to `sys.path` so `app` is importable).
- `test_models.py`: validation rules for `Sample` (ID format, DNA character set, normalization), derived-field defaults/assignment, and `FragmentTemplate` validation (name stripping/non-empty, recognition/wildtype sequence validation and normalization).
- `test_lab_service.py`: `LabService` behavior incl. `update_sample`, duplicate handling, and the reset of derived analysis fields on update.
- `test_template_service.py`: `TemplateService` behavior — add/list/find, duplicate name handling, state get/set.
- `test_storage_json.py`: save/load roundtrip via `tmp_path`, missing file, duplicate IDs on load, roundtrip of derived analysis fields (set and unset).
- `test_template_storage.py`: save/load roundtrip for templates via `tmp_path`, missing file, duplicate names on load.
- `test_dna_tools.py`: reverse complement and transcription incl. ambiguity codes and gap characters; translation incl. stop-codon handling, start codons not at position 0, missing start codon, and incomplete trailing codons; `find_fragment_positions` incl. overlapping matches; `extract_region_after` incl. not-found and not-enough-bases-remaining cases.
- `test_fasta_import.py`: FASTA parsing (single/multi-record, multi-line sequences, blank lines, missing header), and sample ID generation incl. the collision-retry path (via `monkeypatch` on `random.choice`).
- `test_export.py`: CSV/Excel export — expected columns, empty-sample-list handling, parent directory creation, roundtrip via `pandas.read_csv`/`read_excel`.
- `test_cli.py`: all CLI commands via Click's `CliRunner` + `isolated_filesystem()`, success and error paths, including the interactive `analyze` menu (selection, reprompt on invalid input, shrinking menu, completion message, translation-without-gene error), `search`'s conditional display of derived fields, `import-fasta` (single/multi-record files, partial failures, non-FASTA files ignored, malformed files left in place, successful files moved to `processed/`), `add-template`/`list-templates`, `search-fragment` (both modes, reprompt on invalid sequence, wildtype vs. mutant detection, recognition-sequence-not-found, no-templates-available), and `export` (both formats, single-format, no-samples message, invalid `--format` rejection).
- `test_main.py`: smoke test confirming the entry point imports and exposes `cli`.
- Run with `uv run pytest -v`, or with coverage: `uv run pytest --cov=app --cov-report=term-missing -v`.
- Currently at 100% coverage (excluding `demo.py`), 153 tests.

### `.github/workflows/tests.yml`
- Runs on every push and pull request.
- Installs dependencies via `uv sync --dev`, runs `pytest --cov=app` with terminal and HTML coverage reports.
- Coverage summary is written to the GitHub Actions job summary (visible per run, no third-party service).
- Full HTML coverage report is uploaded as a downloadable artifact.

## Configuration & Tooling

- **`pyproject.toml`**: Python ≥3.13, package management via `uv` (see `uv.lock`). Runtime dependencies: `click`, `pandas`, `pydantic`, `openpyxl` (Excel export support for pandas). Dev dependency group (`[dependency-groups] dev`): `pytest`, `pytest-cov`.
- **`[tool.coverage.run]`** in `pyproject.toml`: excludes `app/scripts/demo.py` from coverage measurement.
- **Packaging**: `setuptools`, finds packages under `app*`.
- **`.gitignore`**: excludes `.venv`, caches, coverage artifacts, build artifacts, `.env` files, `data/lab_state.json`, `data/fragment_templates.json` (local state), `data/fasta_import/` (local drop zone and processed files), and `data/exports/` (local export output).

## Persistence

- Sample state is stored as a flat JSON list under `data/lab_state.json`.
- Fragment templates are stored as a flat JSON list under `data/fragment_templates.json`.
- Both files are git-ignored → local state, not part of the repo.
- FASTA files dropped into `data/fasta_import/` are local input data; both the drop zone and its `processed/` subfolder are git-ignored.
- Exported CSV/Excel files land in `data/exports/`, also git-ignored — these are generated output, not application state.

## Open Items / Roadmap

- [x] Unit tests (pytest)
- [x] Sample update function
- [x] Pydantic-based validation
- [x] Test coverage tracked in CI (GitHub Actions job summary)
- [x] DNA analysis tools: reverse complement, transcription, translation (start/stop codon detection)
- [x] Analysis results stored on the sample and persisted (shown in `search`, not in `list`)
- [x] FASTA import: drop FASTA files into `data/fasta_import/` to have them registered as samples (processed files moved to `data/fasta_import/processed/`)
- [x] DNA fragment search: free-sequence position search, plus reusable named templates (recognition sequence + wildtype reference) comparing a sample's region against wildtype to flag mutants — intended as groundwork for future mutation analysis workflows
- [ ] Template management: update/delete templates (currently create-and-list only)
- [ ] Consider persisting `search-fragment` results on the sample, similar to `analyze`'s fixed analyses
- [x] Export (CSV, Excel): base sample data (ID, DNA) via `export --format {csv,xlsx,both}`, written to `data/exports/`
- [ ] Export: include derived analysis fields and/or fragment-search/mutation-match results as additional columns
- [ ] Perspective: direct download from bioinformatics databases (e.g. NCBI, ENA)

## Notes for Further Development

- `LabService` and `storage_json` are cleanly separated, but the CLI currently handles orchestration (load/save on every command) – as complexity grows, a repository pattern or context manager might make sense.
- Since each CLI invocation starts a new process, there's no in-memory state between commands – every operation fully reads/writes the JSON file. This could become relevant with larger datasets (keyword: later migration to SQLite, as planned in the sister project `library-tracker`).
- `app/analysis/` is intentionally separate from `app/services/` — it holds pure, stateless sequence-analysis functions with no dependency on the in-memory sample store, so it can be reused (e.g. for FASTA-file analysis) without going through `LabService`.
- Derived analysis fields on `Sample` are mutated in place by the CLI (`setattr` on the object returned by `find_sample`, which is the same instance held in `LabService`'s internal dict) rather than via `LabService`. If analysis logic needs to move behind a service method later (e.g. once FASTA import reuses it), consider adding something like `LabService.record_analysis_result(sample_id, field_name, value)` to keep all sample mutation behind the service boundary.
- FASTA-imported samples get a randomly generated ID rather than one derived from the FASTA header, since headers are free-form text and don't match the required 9-digit format. The original header text is only shown in the import output, not stored on the `Sample` — if traceability back to the source header becomes important, `Sample` would need an additional field for it.
- `import-fasta` does not automatically run any analyses on imported samples; that's a deliberate, separate step via `analyze`, though this may change later (see roadmap).
- `search-fragment`'s "Wildtype vs. Mutant" comparison is an exact string match between the extracted region and `FragmentTemplate.wildtype_sequence` — any difference (including a single base substitution, insertion, or deletion that shifts the frame) is reported as "Mutant" with no further characterization of what changed. If more detail becomes useful later (e.g. highlighting the specific differing positions, or classifying substitution vs. indel), that logic would extend `extract_region_after`'s result rather than the exact-match check itself.
- `TemplateService`/`FragmentTemplate` intentionally mirror `LabService`/`Sample`'s structure (dict keyed by a unique field, same CRUD-ish method names) for consistency, even though templates currently only support add/list/find — no update or delete yet, since the request was specifically for template creation via an independent command.
- `export` deliberately exports only `sample_id`/`sample_dna` (`EXPORT_COLUMNS` in `export.py`), not the derived analysis fields or any fragment-search/mutation-match results — the request was scoped to base data first, with richer export (e.g. mutation match columns) explicitly flagged as a later step. Each export run creates a new timestamped file rather than overwriting a fixed filename, so `data/exports/` accumulates one file per run until manually cleaned up.
