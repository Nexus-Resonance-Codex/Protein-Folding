"""
Mapping biology into the 2048D Hyper-Lattice.
=============================================
Takes raw biological sequences and projects them into the math
domain defined by the Core NRC toolkit.
"""
import numpy as np
from typing import List, Union
# Depend on the core NRC math library for the projection coordinates
from nrc.lattice import phi_lattice_project
from nrc.math.phi import PHI_FLOAT

def map_sequence_to_lattice(mass_array: List[float]) -> np.ndarray:
    """
    Projects a polypeptide mass sequence directly into the 2048D
    Golden lattice space using the core NRC projection engine.

    Args:
        mass_array: List of constituent mass weights.

    Returns:
        A NumPy array of shape (N, 2048) representing the folded
        lattice coordinates.
    """
    masses = np.array(mass_array, dtype=np.float64)
    # The coordinate index equation C_{n} = (mass * \phi)
    base_coords = masses * PHI_FLOAT

    # Project utilizing the core library
    return phi_lattice_project(base_coords)
