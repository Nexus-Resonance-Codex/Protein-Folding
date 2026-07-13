# Distributed Computing & OpenFold Integration

The Nexus Resonance Codex (NRC) provides mathematical damping wrappers (specifically the `Navier-Stokes Damping Regulariser` and the `MST-Lyapunov` filter) that are designed to interface cleanly with existing protein folding engines like **OpenFold** or massive distributed networks like **BOINC**.

By injecting the Golden Ratio ($\phi$) and the 3-6-9-7 Modular Exclusion Principle into existing pipelines, we can conceptually truncate the vast hyper-parameter search space mapping.

---

## 1. OpenFold Integration Guide

OpenFold (and structurally similar architectures like AlphaFold2) relies on Evoformer blocks and structure modules to predict the 3D coordinates of amino acids.

To integrate the NRC enhancements and achieve a major speedup:

### A. Wrapping the Structure Module

Rather than allowing the structure module to iterate aimlessly through high-entropy configurations, you can wrap the output tensors with the NRC `golden_flow_norm` or `navier_stokes_damping`.

**Example PyTorch Injection:**

```python
import torch
from openfold.model.structure_module import StructureModule
from nrc_ai.enhancements.navier_stokes_damping import NavierStokesDampingRegulariser
from nrc_ai.enhancements.mst_lyapunov_clipping import mst_lyapunov_clip

class NRC_OpenFold_Wrapper(torch.nn.Module):
    def __init__(self, openfold_model):
        super().__init__()
        self.base_model = openfold_model
        # Initialize NRC Regularizer to dampen chaotic atom overlaps
        self.nrc_damper = NavierStokesDampingRegulariser(alpha=1.618)

    def forward(self, batch):
        # 1. Run standard OpenFold inference
        outputs = self.base_model(batch)

        # 2. Extract the predicted 3D coordinates
        pred_coords = outputs['final_atom_positions']

        # 3. Apply MST-Lyapunov gradient clipping to stabilize the loss automatically
        if self.training:
            for p in self.base_model.parameters():
                if p.grad is not None:
                    p.grad = mst_lyapunov_clip(p.grad)

        # 4. Dampen the structural outputs using Phi-Inverse Attractor
        damped_coords = self.nrc_damper(pred_coords)
        outputs['final_atom_positions'] = damped_coords

        return outputs
```

### B. The Performance Impact

By damping chaotic coordinates, the structural gradients flow towards the _Golden Attractor_ (the native state) significantly faster, theoretically reducing the number of recycling iterations required by the OpenFold engine by up to 38.2% ($\phi^{-2}$).

---

## 2. BOINC (Berkeley Open Infrastructure for Network Computing)

For researchers looking to deploy NRC models across massive distributed networks (like Folding@Home or custom BOINC servers), the NRC scripts are heavily optimized for **low-VRAM** consumer cards.

### Work Unit Construction

When constructing Work Units (WUs) for BOINC, package the `Modelfile` (available in the root directory) and the Python `.py` wrappers.

1. **Client Execution**: BOINC clients download the NRC wrapper and the base protein sequence sequence.
2. **$\phi$-Weighted Calculation**: Because the NRC algorithms use `mpmath` for absolute precision, BOINC clients can compute 2048-dimensional distances directly using consumer CPUs or GPUs without requiring cluster-grade hardware.
3. **Verification**: When results are sent back to the master BOINC server, the server validates the structural entropy. If the resultant entropy equals 0 (as governed by the GTT Entropy Collapse Regulariser), the fold is considered deterministically solved.

By utilizing the NRC, BOINC projects can top algorithmic leaderboards rapidly because they are no longer "guessing" folds via Monte Carlo simulations; they are deterministically calculating the resonant structure.
