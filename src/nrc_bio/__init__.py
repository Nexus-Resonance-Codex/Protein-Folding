"""nrc_bio: Institutional-Grade Protein Folding via φ^∞ Lattice Resonance."""

from .accelerator import NRCFoldAccelerator, fold_sequence

__all__ = ["NRCFoldAccelerator", "fold_sequence"]
