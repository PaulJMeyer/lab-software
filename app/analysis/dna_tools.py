from app.domain.models import IUPAC_COMPLEMENT


def reverse_complement(sequence: str) -> str:
    """Return the reverse complement of a validated DNA sequence."""
    complement = "".join(IUPAC_COMPLEMENT[base] for base in sequence)
    return complement[::-1]


def transcribe(sequence: str) -> str:
    """Return the RNA transcript of a validated DNA (coding strand) sequence."""
    return sequence.replace("T", "U")
