# Project Structure – lab-software

Brief overview of the layout, modules, and responsibilities of the `lab-software` project.

## Directory Tree

```
lab-software/
├── app/
│   ├── analysis/
│   │   └── dna_tools.py      # DNA sequence analysis (reverse complement, transcription)
│   ├── domain/
│   │   └── models.py         # Data models (Sample) incl. validation
│   ├── io/
│   │   └── storage_json.py   # Persistence: load/save as JSON
│   ├── scripts/
│   │   ├── cli.py            # Click-based CLI commands
│   │   └── demo.py           # Manual demo/test script
│   ├── services/
│   │   └── lab_service.py    # Business logic / in-memory management
│   └── main.py                # Entry point (calls cli())
├── tests/
│   ├── __init__.py
│   ├── test_models.py        # Tests for Sample validation
│   ├── test_lab_service.py   # Tests for LabService
│   ├── test_storage_json.py  # Tests for JSON persistence
│   ├── test_dna_tools.py     # Tests for DNA analysis functions
│   ├── test_cli.py           # Tests for CLI commands (Click CliRunner)
│   └── test_main.py          # Smoke test for the entry point
├── .github/
│   └── workflows/
│       └── tests.yml         # CI: runs pytest with coverage on every push/PR
├── data/
│   └── lab_state.json        # persisted state (gitignored)
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
- **`IUPAC_COMPLEMENT`**: dict mapping each IUPAC base/ambiguity code to its complement, shared with `app/analysis/dna_tools.py`.

### `app/analysis/dna_tools.py`
- `reverse_complement(sequence)`: returns the reverse complement of a DNA sequence, using `IUPAC_COMPLEMENT`.
- `transcribe(sequence)`: returns the RNA transcript (replaces `T` with `U`).
- Pure functions, no validation — operate on already-validated `Sample.sample_dna` strings.
- First step of the planned DNA analysis toolset (see roadmap); adapted from a standalone reference script in the sister `bioinformatics-tools` project.

### `app/services/lab_service.py`
- **`LabService`**: holds samples in a dict (`sample_id → Sample`).
- Methods: `add_sample`, `list_samples`, `update_sample`, `delete_sample`, `find_sample`, `get_state`, `set_state`.
- `update_sample(sample_id, sample_dna)`: replaces the DNA of an existing sample (ID stays fixed as the primary key); validates the new DNA via the `Sample` constructor.
- Prevents duplicate IDs in `add_sample`.

### `app/io/storage_json.py`
- `save_samples(path, samples_dict)`: writes samples as a JSON list, creates the target directory if needed.
- `load_samples(path)`: reads JSON, builds `Sample` objects, detects duplicate IDs in the file.
- Returns an empty dict if the file doesn't exist.

### `app/scripts/cli.py`
- Click group `cli` with commands: `add`, `list`, `update`, `delete`, `search`, `analyze`.
- `analyze --id <id>`: looks up a sample and prints its reverse complement and RNA transcript via `app/analysis/dna_tools.py`.
- `get_service()` loads the state from `data/lab_state.json` on every call, creates a `LabService`, and returns it (no caching between commands – a new process starts on every CLI invocation).
- After `add`/`update`/`delete`, the state is immediately saved again.
- Catches `(ValidationError, ValueError)` around commands that can fail; error output is colored via `click.style` (green = success, red = error).

### `app/scripts/demo.py`
- Standalone script for manually walking through the workflow (load → add sample → display → save), independent of the CLI.
- Excluded from coverage measurement (`[tool.coverage.run] omit` in `pyproject.toml`), since it's a manual/demo entry point, not a tested code path.

### `app/main.py`
- Sole purpose: imports and starts `cli()` from `app/scripts/cli.py`.

### `tests/`
- Flat structure, a single `__init__.py` at the root (ensures pytest adds the project root to `sys.path` so `app` is importable).
- `test_models.py`: validation rules for `Sample` (ID format, DNA character set, normalization).
- `test_lab_service.py`: `LabService` behavior incl. `update_sample`, duplicate handling.
- `test_storage_json.py`: save/load roundtrip via `tmp_path`, missing file, duplicate IDs on load.
- `test_dna_tools.py`: reverse complement and transcription, incl. ambiguity codes and gap characters.
- `test_cli.py`: all CLI commands via Click's `CliRunner` + `isolated_filesystem()`, success and error paths.
- `test_main.py`: smoke test confirming the entry point imports and exposes `cli`.
- Run with `uv run pytest -v`, or with coverage: `uv run pytest --cov=app --cov-report=term-missing -v`.
- Currently at 100% coverage (excluding `demo.py`).

### `.github/workflows/tests.yml`
- Runs on every push and pull request.
- Installs dependencies via `uv sync --dev`, runs `pytest --cov=app` with terminal and HTML coverage reports.
- Coverage summary is written to the GitHub Actions job summary (visible per run, no third-party service).
- Full HTML coverage report is uploaded as a downloadable artifact.

## Configuration & Tooling

- **`pyproject.toml`**: Python ≥3.13, package management via `uv` (see `uv.lock`). Runtime dependencies: `click`, `pandas`, `pydantic`. Dev dependency group (`[dependency-groups] dev`): `pytest`, `pytest-cov`.
- **`[tool.coverage.run]`** in `pyproject.toml`: excludes `app/scripts/demo.py` from coverage measurement.
- **Packaging**: `setuptools`, finds packages under `app*`.
- **`.gitignore`**: excludes `.venv`, caches, build artifacts, `.env` files, and `data/lab_state.json` (local state).

## Persistence

- State is stored as a flat JSON list under `data/lab_state.json`.
- File is git-ignored → local state, not part of the repo.

## Open Items / Roadmap

- [x] Unit tests (pytest)
- [x] Sample update function
- [x] Pydantic-based validation
- [x] Test coverage tracked in CI (GitHub Actions job summary)
- [x] DNA analysis tools: reverse complement, transcription
- [ ] DNA analysis tools: translation, fragment search
- [ ] FASTA import: drop FASTA files into a designated directory to have them registered as samples and analyzed
- [ ] Perspective: direct download from bioinformatics databases (e.g. NCBI, ENA)
- [ ] Export (CSV, Excel)

## Notes for Further Development

- `LabService` and `storage_json` are cleanly separated, but the CLI currently handles orchestration (load/save on every command) – as complexity grows, a repository pattern or context manager might make sense.
- Since each CLI invocation starts a new process, there's no in-memory state between commands – every operation fully reads/writes the JSON file. This could become relevant with larger datasets (keyword: later migration to SQLite, as planned in the sister project `library-tracker`).
- `app/analysis/` is intentionally separate from `app/services/` — it holds pure, stateless sequence-analysis functions with no dependency on the in-memory sample store, so it can be reused (e.g. for FASTA-file analysis) without going through `LabService`.
