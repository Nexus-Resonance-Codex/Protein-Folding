"""
NRC Bio Library
===============
Nexus Resonance Codex tools for biology and protein folding.
Maps biological configurations into 2048D Giza-lattice mathematics.
"""
from .__about__ import __version__

from .sequence.parser import sequence_to_mass_array
from .mapping.lattice_map import map_sequence_to_lattice
from .openfold.wrapper import NRCOpenFoldWrapper
from .distributed.boinc import generate_boinc_workunits

__all__ = [
    "__version__",
    "sequence_to_mass_array",
    "map_sequence_to_lattice",
    "NRCOpenFoldWrapper",
    "generate_boinc_workunits",
]
