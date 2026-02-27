"""
NRC Math Library — Protein Folding Edition
==========================================
Core mathematical constants and transforms:
  - phi.py:            Golden Ratio (φ) constants and Binet's formula
  - qrt.py:            Quadratic Residue Transform
  - mst.py:            Modular Stability Transform
  - tupt_exclusion.py: Tesla Universal Prime Transform exclusion logic
"""

from .phi import PHI_FLOAT, PHI_INVERSE_FLOAT, binet_formula, phi_power_tensor
from .qrt import qrt_damping
from .mst import mst_step, MST_MODULUS, MST_LAMBDA
from .tupt_exclusion import tupt_base_check, apply_exclusion_gate, TUPT_MOD, TUPT_PATTERN

__all__ = [
    "PHI_FLOAT",
    "PHI_INVERSE_FLOAT",
    "binet_formula",
    "phi_power_tensor",
    "qrt_damping",
    "mst_step",
    "MST_MODULUS",
    "MST_LAMBDA",
    "tupt_base_check",
    "apply_exclusion_gate",
    "TUPT_MOD",
    "TUPT_PATTERN",
]
