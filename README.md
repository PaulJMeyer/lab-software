# Lab Software

A lightweight command-line application for managing biological lab samples. Supports registering, listing, searching, and deleting samples with persistent JSON storage.

---

## Features

- Register new samples with ID and DNA sequence validation
- List all registered samples with a formatted overview
- Search for a specific sample by ID
- Delete samples by ID
- Persistent storage via JSON file
- Duplicate ID prevention

---

## Usage

```bash
# Add sample
python main.py add --id "123456789" --dna "ACGTNNRRY"

# Add sample (interactive)
python main.py add

# List all samples
python main.py list

# Search sample
python main.py search --id "123456789"

# Delete sample
python main.py delete --id "123456789"
```

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

## Roadmap

- [ ] Unit tests (pytest)
- [ ] Sample update
- [ ] Pydantic-based validation
- [ ] Export (CSV, Excel)
- [ ] DNA analysis tools:
  - [ ] Transcription
  - [ ] Translation
  - [ ] Search for DNA fragments

---

## Dependencies

| Package  | Version  |
|----------|----------|
| click    | ≥ 8.3.1  |
| pandas   | ≥ 3.0.1  |
| pydantic | ≥ 2.12.5 |
