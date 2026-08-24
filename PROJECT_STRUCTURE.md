# Project Structure – lab-software

Brief overview of the layout, modules, and responsibilities of the `lab-software` project.

## Directory Tree

```
lab-software/
├── app/
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
│   └── test_storage_json.py  # Tests for JSON persistence
├── data/
│   └── lab_state.json        # persisted state (gitignored)
├── pyproject.toml
├── uv.lock
├── README.md
├── .python-version
└── .gitignore
```

## Architecture

Classic 3-layer separation:

- **domain** – pure data models, no I/O, no dependency on other app layers
- **services** – business logic, holds the in-memory state (`LabService`)
- **io** – persistence layer, converts domain objects to/from JSON
- **scripts** – application entry points (CLI, demo)

Dependency direction: `scripts → services → domain`, as well as `scripts → io → domain`. `services` does not know about `io` directly (persistence is orchestrated by the CLI, not by the service itself).

## Modules in Detail

### `app/domain/models.py`
- **`Sample`**: core entity with `sample_id` (exactly 9 characters, digits 1–9 only) and `sample_dna` (IUPAC character set: `ACGTNRYKMSWBDHV-`).
- Validation happens in the constructor (`_validate_id`, `_validate_dna`); raises `ValueError` on invalid input.
- DNA sequence is automatically normalized to uppercase.

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
- Click group `cli` with commands: `add`, `list`, `update`, `delete`, `search`.
- `get_service()` loads the state from `data/lab_state.json` on every call, creates a `LabService`, and returns it (no caching between commands – a new process starts on every CLI invocation).
- After `add`/`update`/`delete`, the state is immediately saved again.
- Error output is colored via `click.style` (green = success, red = error).

### `app/scripts/demo.py`
- Standalone script for manually walking through the workflow (load → add sample → display → save), independent of the CLI.

### `app/main.py`
- Sole purpose: imports and starts `cli()` from `app/scripts/cli.py`.

### `tests/`
- Flat structure, a single `__init__.py` at the root (ensures pytest adds the project root to `sys.path` so `app` is importable).
- `test_models.py`: validation rules for `Sample` (ID format, DNA character set, normalization).
- `test_lab_service.py`: `LabService` behavior incl. `update_sample`, duplicate handling.
- `test_storage_json.py`: save/load roundtrip via `tmp_path`, missing file, duplicate IDs on load.
- Run with `uv run pytest -v`.

## Configuration & Tooling

- **`pyproject.toml`**: Python ≥3.13, package management via `uv` (see `uv.lock`). Dependencies: `click`, `pandas`, `pydantic` (Pydantic currently unused – likely intended for a planned validation migration, see roadmap in README).
- **Packaging**: `setuptools`, finds packages under `app*`.
- **`.gitignore`**: excludes `.venv`, caches, build artifacts, `.env` files, and `data/lab_state.json` (local state).

## Persistence

- State is stored as a flat JSON list under `data/lab_state.json`.
- File is git-ignored → local state, not part of the repo.

## Open Items / Roadmap (from README)

- [x] Unit tests (pytest)
- [x] Sample update function
- [ ] Pydantic-based validation (dependency already present, but not yet used)
- [ ] Export (CSV, Excel)
- [ ] DNA analysis tools: transcription, translation, fragment search

## Notes for Further Development

- `LabService` and `storage_json` are cleanly separated, but the CLI currently handles orchestration (load/save on every command) – as complexity grows, a repository pattern or context manager might make sense.
- Since each CLI invocation starts a new process, there's no in-memory state between commands – every operation fully reads/writes the JSON file. This could become relevant with larger datasets (keyword: later migration to SQLite, as planned in the sister project `library-tracker`).