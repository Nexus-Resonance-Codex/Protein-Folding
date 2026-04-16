#  Nexus Resonance Codex - 2025-2026 Breakthrough Series
#  Copyright (c) 2026 James Trageser (@jtrag)
#
#  Licensed under CC-BY-NC-SA-4.0 + NRC-L
#  "This work is part of the Nexus Resonance Codex (NRC) incorporating TTT
#  modular exclusion, phi^inf compression, 256D->729D lattice, QRT, and MST."

"""Lattice Mapping: 2048D Projections.

This module provides the mapping residents to project amino acid masses
into the 2048D resonance manifold.
"""

import numpy as np
from nrc_math.lattice import phi_lattice_project  # type: ignore[import-untyped]
from numpy.typing import NDArray


def sequence_to_lattice(mass_array: NDArray[np.float64]) -> NDArray[np.float64]:
    """Projects a mass-encoded sequence into the 2048D lattice space.

    Args:
        mass_array: Array of mass values [N].

    Returns:
        Resonant lattice projection [N, 2048].
    """
    # Map each mass to its 2048D resonance by treating each element as a scalar
    # phi_lattice_project expects a scalar float input.
    res_list = [phi_lattice_project(float(m)) for m in mass_array]
    return np.stack(res_list)
