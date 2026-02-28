"""
OpenFold Structural Wrappers.
=============================
Applies the NRC physics engines (NS Damping, QRT, TUPT) into the
standard predictive modules of OpenFold models.
"""
import torch
import torch.nn as nn
from typing import Optional
from nrc.math.qrt import qrt_damping
from nrc.math.tupt_exclusion import apply_exclusion_gate

class NRCOpenFoldWrapper(nn.Module):
    """
    Wraps any standard OpenFold Structure/Evoformer module inside
    the NRC physics engine. Replaces stochastic dropouts with
    TUPT gates, and bounds exploding gradients with QRT damping.
    """
    def __init__(self, openfold_module: nn.Module):
        super().__init__()
        self.core = openfold_module

    def forward(self, x: torch.Tensor, **kwargs) -> torch.Tensor:
        """
        Executes a physics-bounded forward pass.

        Args:
            x: Input representations (activations or embeddings).
            **kwargs: Extra dictionary arguments required by OpenFold.

        Returns:
            The stabilized forward outputs.
        """
        # Physics Step 1: Mod-9 Exclusion Gating (TUPT)
        # Convert tensor to numpy, apply the gate from the core nrc, back to tensor
        device = x.device
        x_np = x.detach().cpu().numpy()
        gated_np = apply_exclusion_gate(x_np)
        x_gated = torch.from_numpy(gated_np).to(device).float()

        # Step 2: OpenFold processing
        out = self.core(x_gated, **kwargs)

        # Physics Step 3: Navier-Stokes/QRT Gradient Damping stabilization
        if out.requires_grad:
            def qrt_hook(grad: torch.Tensor) -> torch.Tensor:
                grad_np = grad.cpu().numpy()
                damped = qrt_damping(grad_np)
                return torch.from_numpy(damped).to(device)
            out.register_hook(qrt_hook)

        return out
