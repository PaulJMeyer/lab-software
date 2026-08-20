# Project Structure – lab-software

Kurzüberblick über Aufbau, Module und Verantwortlichkeiten des `lab-software`-Projekts (Stand: erste dokumentierte Version).

## Verzeichnisbaum

```
lab-software/
├── app/
│   ├── domain/
│   │   └── models.py         # Datenmodelle (Sample) inkl. Validierung
│   ├── io/
│   │   └── storage_json.py   # Persistenz: Laden/Speichern als JSON
│   ├── scripts/
│   │   ├── cli.py            # Click-basierte CLI-Kommandos
│   │   └── demo.py           # Manuelles Demo-/Testskript
│   ├── services/
│   │   └── lab_service.py    # Business-Logik / In-Memory-Verwaltung
│   └── main.py                # Einstiegspunkt (ruft cli() auf)
├── data/
│   └── lab_state.json        # persistenter Zustand (gitignored)
├── pyproject.toml
├── uv.lock
├── README.md
├── .python-version
└── .gitignore
```

## Architektur

Klassische 3-Schichten-Trennung:

- **domain** – reine Datenmodelle, kein I/O, keine Abhängigkeit zu anderen App-Schichten
- **services** – Geschäftslogik, hält den In-Memory-Zustand (`LabService`)
- **io** – Persistenzschicht, wandelt Domain-Objekte in JSON und zurück
- **scripts** – Anwendungseinstiegspunkte (CLI, Demo)

Abhängigkeitsrichtung: `scripts → services → domain`, sowie `scripts → io → domain`. `services` kennt `io` nicht direkt (Persistenz wird von der CLI orchestriert, nicht vom Service selbst).

## Module im Detail

### `app/domain/models.py`
- **`Sample`**: Kernentität mit `sample_id` (exakt 9 Zeichen, nur Ziffern 1–9) und `sample_dna` (IUPAC-Zeichensatz: `ACGTNRYKMSWBDHV-`).
- Validierung erfolgt im Konstruktor (`_validate_id`, `_validate_dna`); wirft `ValueError` bei ungültigen Eingaben.
- DNA-Sequenz wird automatisch in Großbuchstaben normalisiert.

### `app/services/lab_service.py`
- **`LabService`**: hält Samples in einem Dict (`sample_id → Sample`).
- Methoden: `add_sample`, `list_samples`, `delete_sample`, `find_sample`, `get_state`, `set_state`.
- Verhindert doppelte IDs bei `add_sample`.

### `app/io/storage_json.py`
- `save_samples(path, samples_dict)`: schreibt Samples als JSON-Liste, legt Zielverzeichnis bei Bedarf an.
- `load_samples(path)`: liest JSON, baut `Sample`-Objekte, erkennt doppelte IDs in der Datei.
- Gibt leeres Dict zurück, falls Datei nicht existiert.

### `app/scripts/cli.py`
- Click-Group `cli` mit Kommandos: `add`, `list`, `delete`, `search`.
- `get_service()` lädt bei jedem Aufruf den Zustand aus `data/lab_state.json`, erzeugt einen `LabService` und gibt ihn zurück (kein Caching zwischen Kommandos – Prozess startet pro CLI-Aufruf neu).
- Nach `add`/`delete` wird der Zustand sofort wieder gespeichert.
- Fehlerausgabe farbig via `click.style` (grün = Erfolg, rot = Fehler).

### `app/scripts/demo.py`
- Eigenständiges Skript zum manuellen Durchspielen des Workflows (laden → Sample hinzufügen → anzeigen → speichern), unabhängig von der CLI.

### `app/main.py`
- Einziger Zweck: importiert und startet `cli()` aus `app/scripts/cli.py`.

## Konfiguration & Tooling

- **`pyproject.toml`**: Python ≥3.13, Paketmanagement über `uv` (siehe `uv.lock`). Dependencies: `click`, `pandas`, `pydantic` (Pydantic aktuell noch ungenutzt – vermutlich für geplante Validierungs-Migration, siehe Roadmap in README).
- **Packaging**: `setuptools`, findet Pakete unter `app*`.
- **`.gitignore`**: schließt `.venv`, Caches, Build-Artefakte, `.env`-Dateien und `data/lab_state.json` (lokaler Zustand) aus.

## Persistenz

- Zustand wird als flache JSON-Liste unter `data/lab_state.json` gespeichert.
- Datei ist git-ignored → lokaler State, kein Teil des Repos.

## Offene Punkte / Roadmap (aus README)

- [ ] Unit Tests (pytest)
- [ ] Sample-Update-Funktion
- [ ] Pydantic-basierte Validierung (Dependency ist schon vorhanden, aber noch nicht genutzt)
- [ ] Export (CSV, Excel)
- [ ] DNA-Analyse-Tools: Transkription, Translation, Fragment-Suche

## Anmerkungen für Weiterentwicklung

- `LabService` und `storage_json` sind sauber getrennt, aber die CLI übernimmt aktuell die Orchestrierung (Laden/Speichern bei jedem Kommando) – bei wachsender Komplexität könnte ein Repository-Pattern oder ein Kontextmanager sinnvoll werden.
- Da pro CLI-Aufruf ein neuer Prozess startet, gibt es keinen In-Memory-Zustand zwischen Kommandos – jede Operation liest/schreibt vollständig die JSON-Datei. Bei größeren Datenmengen könnte das relevant werden (Stichwort: spätere Migration auf SQLite, wie im Schwesterprojekt `library-tracker` geplant).
