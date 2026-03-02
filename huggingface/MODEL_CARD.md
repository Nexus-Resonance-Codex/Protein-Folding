---
language:
  - en
license: other
license_name: nrc-license-2.0
license_link: https://github.com/Nexus-Resonance-Codex/Protein-Folding/blob/main/LICENSE.md
tags:
  - Protein-Folding
  - biology
  - bioinformatics
  - golden-ratio
  - mathematics
  - pytorch
  - openfold
  - boinc
  - resonance
  - nrc
pipeline_tag: feature-extraction
library_name: nrc_bio
model_type: nrc-Protein-Folding
datasets:
  - Nexus-Resonance-Codex/nrc-protein-dataset
---

<div align="center">

# NRC Protein Folding

**2048-Dimensional Golden Ratio Lattice Mapping for Structural Biology**
_A Nexus Resonance Codex framework that maps biological sequences into φ-bounded hyperdimensional geometry_

[![GitHub](https://img.shields.io/badge/GitHub-protein--folding-181717?logo=github)](https://github.com/Nexus-Resonance-Codex/Protein-Folding)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python)](https://python.org)
[![BioPython](https://img.shields.io/badge/BioPython-1.80%2B-green)](https://biopython.org)
[![License](https://img.shields.io/badge/License-NRC--L--2.0-gold)](LICENSE.md)

</div>

---

## Overview

The NRC Protein Folding library maps biological sequences into a **2048-dimensional lattice** governed by the Golden Ratio φ and the Giza Pyramid slope (51.853°). This provides a deterministic geometric embedding of protein structures that complements statistical folding models like AlphaFold and OpenFold.

The key insight: amino acid mass distributions in stable protein structures cluster around **φ-weighted attractor zones** that can be precisely characterized using the same mathematics that govern crystal lattices and cosmological structure formation.

```python
pip install "nrc_bio @ git+https://github.com/Nexus-Resonance-Codex/Protein-Folding.git"
```

---

## The 2048D Phi-Lattice

Every amino acid mass `m` is projected into a 2048-dimensional coordinate:

```
L_i(m) = (m · φ) · φ^{-i/2048} · cos(i · 51.853° in radians)
```

This creates a unique geometric fingerprint for each residue. When the full polypeptide chain is mapped, the resulting 2048D trajectory reveals:

- **Stable folds** → tight helical trajectories in lattice space
- **Disordered regions** → sparse, scattered lattice coordinates
- **Active sites** → TUPT-excluded zones (mod 3-6-9-7 gating)

---

## Quick Start

```python
from nrc_bio import sequence_to_mass_array, map_sequence_to_lattice, NRCOpenFoldWrapper
import numpy as np

# Parse an amino acid sequence
sequence = "MKTIIALSYIFCLVFAQC"
masses = sequence_to_mass_array(sequence)
print(f"Mass array: {masses[:5]} ...")  # [131.19, 128.17, 101.11, ...]

# Project into 2048D phi-lattice
lattice = map_sequence_to_lattice(masses)
print(f"Lattice shape: {lattice.shape}")  # (18, 2048)
print(f"Lattice L2 norm: {np.linalg.norm(lattice):.4f}")

# Wrap an OpenFold module with NRC physics
import torch.nn as nn
my_openfold_module = nn.Linear(256, 256)  # any OpenFold-compatible module
wrapped = NRCOpenFoldWrapper(my_openfold_module)
# Now forward() applies TUPT gating + QRT gradient damping automatically
```

---

## BOINC Distributed Computing Integration

Large protein targets can be automatically sharded for BOINC distributed computing:

```python
from nrc_bio import sequence_to_mass_array, generate_boinc_workunits

masses = sequence_to_mass_array("MKTIIALSYIFCLVFAQC" * 50)  # long chain
work_units = generate_boinc_workunits(masses, shard_count=100)

print(f"Generated {len(work_units)} BOINC work units")
# Each WU is a JSON-serializable dict ready for BOINC job submission
```

---

## Installation

```bash
# Install prerequisites
pip install "nrc @ git+https://github.com/Nexus-Resonance-Codex/NRC.git"
pip install "nrc_bio @ git+https://github.com/Nexus-Resonance-Codex/Protein-Folding.git"

# Or develop locally
git clone https://github.com/Nexus-Resonance-Codex/Protein-Folding.git
cd Protein-Folding
./setup_venv.sh
source .venv/bin/activate
```

---

## Modules

| Module                     | Description                                       |
| :------------------------- | :------------------------------------------------ |
| `sequence_to_mass_array`   | FASTA → atomic mass array                         |
| `map_sequence_to_lattice`  | Mass array → 2048D φ-lattice coordinates          |
| `NRCOpenFoldWrapper`       | Wraps any OpenFold module with TUPT + QRT physics |
| `generate_boinc_workunits` | Shards large sequences into BOINC WUs             |

---

## Citation

```bibtex
@software{nrc_bio_2026,
  author  = {Trageser, James},
  title   = {NRC Protein Folding: 2048D Golden Ratio Lattice Mapping},
  year    = {2026},
  url     = {https://github.com/Nexus-Resonance-Codex/Protein-Folding},
  version = {1.0.0}
}
```
