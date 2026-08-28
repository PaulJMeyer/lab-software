from app.domain.models import IUPAC_COMPLEMENT

START_CODON = "ATG"
STOP_CODONS = {"TAA", "TAG", "TGA"}

# Standard genetic code (codon -> single-letter amino acid, "*" = stop)
CODON_TABLE = {
    "TTT": "F", "TTC": "F", "TTA": "L", "TTG": "L",
    "CTT": "L", "CTC": "L", "CTA": "L", "CTG": "L",
    "ATT": "I", "ATC": "I", "ATA": "I", "ATG": "M",
    "GTT": "V", "GTC": "V", "GTA": "V", "GTG": "V",
    "TCT": "S", "TCC": "S", "TCA": "S", "TCG": "S",
    "CCT": "P", "CCC": "P", "CCA": "P", "CCG": "P",
    "ACT": "T", "ACC": "T", "ACA": "T", "ACG": "T",
    "GCT": "A", "GCC": "A", "GCA": "A", "GCG": "A",
    "TAT": "Y", "TAC": "Y", "TAA": "*", "TAG": "*",
    "CAT": "H", "CAC": "H", "CAA": "Q", "CAG": "Q",
    "AAT": "N", "AAC": "N", "AAA": "K", "AAG": "K",
    "GAT": "D", "GAC": "D", "GAA": "E", "GAG": "E",
    "TGT": "C", "TGC": "C", "TGA": "*", "TGG": "W",
    "CGT": "R", "CGC": "R", "CGA": "R", "CGG": "R",
    "AGT": "S", "AGC": "S", "AGA": "R", "AGG": "R",
    "GGT": "G", "GGC": "G", "GGA": "G", "GGG": "G",
}


def reverse_complement(sequence: str) -> str:
    """Return the reverse complement of a validated DNA sequence."""
    complement = "".join(IUPAC_COMPLEMENT[base] for base in sequence)
    return complement[::-1]


def transcribe(sequence: str) -> str:
    """Return the RNA transcript of a validated DNA (coding strand) sequence."""
    return sequence.replace("T", "U")


def translate(sequence: str) -> str:
    """
    Translate a DNA (coding strand) sequence into a protein sequence.

    Searches for the first start codon (ATG), then translates codon by
    codon until a stop codon or the end of the sequence is reached.
    Raises ValueError if no start codon is found.
    """
    start_index = sequence.find(START_CODON)
    if start_index == -1:
        raise ValueError("DNA does not contain a gene (no start codon found).")

    protein = ""
    for i in range(start_index, len(sequence) - 2, 3):
        codon = sequence[i:i + 3]
        if codon in STOP_CODONS:
            break
        protein += CODON_TABLE.get(codon, "X")

    return protein


def find_fragment_positions(sequence: str, pattern: str) -> list[int]:
    """
    Return all 0-based start positions where pattern occurs in sequence.
    Finds overlapping matches as well. Returns an empty list if pattern
    is empty or not found.
    """
    if not pattern:
        return []

    positions = []
    start = 0
    while True:
        index = sequence.find(pattern, start)
        if index == -1:
            break
        positions.append(index)
        start = index + 1

    return positions


def extract_region_after(sequence: str, recognition_sequence: str, region_length: int) -> str | None:
    """
    Find the first occurrence of recognition_sequence in sequence and
    return the region_length bases immediately following it.

    Returns None if recognition_sequence is not found, or if fewer than
    region_length bases remain after the match.
    """
    index = sequence.find(recognition_sequence)
    if index == -1:
        return None

    start = index + len(recognition_sequence)
    end = start + region_length

    if end > len(sequence):
        return None

    return sequence[start:end]
