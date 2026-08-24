from pydantic import BaseModel, field_validator

VALID_DNA_CHARS = set("ACGTNRYKMSWBDHV-")


class Sample(BaseModel):
    sample_id: str
    sample_dna: str

    @field_validator("sample_id")
    @classmethod
    def validate_sample_id(cls, value: str) -> str:
        if not value:
            raise ValueError("Sample ID must not be empty.")
        if len(value) != 9:
            raise ValueError(f"Sample ID must be exactly 9 characters long, was: {len(value)}")
        if not value.isdigit() or "0" in value:
            raise ValueError("Sample ID must only contain digits 1-9 (no 0).")
        return value

    @field_validator("sample_dna")
    @classmethod
    def validate_sample_dna(cls, value: str) -> str:
        if not value:
            raise ValueError("DNA sequence must not be empty.")
        normalized = value.upper()
        invalid = set(normalized) - VALID_DNA_CHARS
        if invalid:
            raise ValueError(f"Invalid characters in DNA sequence: {', '.join(sorted(invalid))}")
        return normalized

    def __repr__(self):
        return str((self.sample_id, len(self.sample_dna)))
