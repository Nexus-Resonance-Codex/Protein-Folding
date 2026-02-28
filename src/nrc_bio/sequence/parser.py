"""
Amino Acid sequence parsing and mapping.
========================================
Maps standard biological sequences into their underlying
atomic resonance structures.
"""
from typing import List, Dict

# Standard amino acid to rough atomic mass mapping
AMINO_MASS_MAP: Dict[str, float] = {
    'A': 71.04, 'R': 156.19, 'N': 114.10, 'D': 115.09, 'C': 103.14,
    'E': 129.12, 'Q': 128.13, 'G': 57.05,  'H': 137.14, 'I': 113.16,
    'L': 113.16, 'K': 128.17, 'M': 131.19, 'F': 147.18, 'P': 97.12,
    'S': 87.08,  'T': 101.11, 'W': 186.21, 'Y': 163.18, 'V': 99.13
}

def sequence_to_mass_array(sequence: str) -> List[float]:
    """
    Converts a standard 1-letter amino acid string into an array
    of exact atomic masses for lattice projection.

    Args:
        sequence: The FASTA sequence string (e.g., "MKTIIALSY").

    Returns:
        List of atomic masses. Missing acids default to 0.0.
    """
    sequence = sequence.upper()
    return [AMINO_MASS_MAP.get(aa, 0.0) for aa in sequence]
