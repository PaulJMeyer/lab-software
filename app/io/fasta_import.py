import random

ID_DIGITS = "123456789"
ID_LENGTH = 9


def parse_fasta(text: str) -> list[tuple[str, str]]:
    """
    Parse FASTA-formatted text into a list of (header, sequence) tuples.

    Supports multi-FASTA files (multiple '>header' records in one file).
    Header lines are returned without the leading '>'. Blank lines are
    ignored. Returns an empty list if no '>' header line is found.
    """
    records = []
    header = None
    seq_lines: list[str] = []

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith(">"):
            if header is not None:
                records.append((header, "".join(seq_lines)))
            header = line[1:].strip()
            seq_lines = []
        else:
            seq_lines.append(line)

    if header is not None:
        records.append((header, "".join(seq_lines)))

    return records


def generate_sample_id(existing_ids: set[str]) -> str:
    """Generate a random 9-digit (1-9) sample ID that isn't already in use."""
    while True:
        candidate = "".join(random.choice(ID_DIGITS) for _ in range(ID_LENGTH))
        if candidate not in existing_ids:
            return candidate
