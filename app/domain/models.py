import re

VALID_DNA_CHARS = set("ACGTNRYKMSWBDHV-")

class Sample:
    def __init__(self, sample_id: str, sample_dna: str):
        self._validate_id(sample_id)
        self.sample_id = sample_id
        self.sample_dna = self._validate_dna(sample_dna)

    def _validate_id(self, sample_id: str):
        if not sample_id:
            raise ValueError("Sample-ID darf nicht leer sein.")
        if len(sample_id) != 9:
            raise ValueError(f"Sample-ID muss genau 9 Zeichen lang sein, war: {len(sample_id)}")
        if not re.fullmatch(r"[1-9]{9}", sample_id):
            raise ValueError("Sample-ID darf nur Ziffern von 1-9 enthalten (keine 0).")

    def _validate_dna(self, sample_dna: str) -> str:
        if not sample_dna:
            raise ValueError("DNA-Sequenz darf nicht leer sein.")
        normalized = sample_dna.upper()
        invalid = set(normalized) - VALID_DNA_CHARS
        if invalid:
            raise ValueError(f"Ungültige Zeichen in DNA-Sequenz: {', '.join(sorted(invalid))}")
        return normalized

    def __repr__(self):
        return str((self.sample_id, len(self.sample_dna)))