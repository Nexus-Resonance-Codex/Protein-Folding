import math

import torch
import torch.nn as nn
import torch.nn.functional as F


class NRCGeometricTransformerLayer(nn.Module):
    """NRC-Enhanced Geometric Transformer Layer for Protein Folding.

    This layer replaces standard scaled dot-product attention with phi-tensor
    contractions in a 2048D Giza-Lattice space. It applies the TTT 3-6-9-7
    filter and QRT damping to entropy collapse the attention mechanism.
    """

    def __init__(self, d_model: int = 256, nhead: int = 8, d_lattice: int = 2048):
        super().__init__()
        self.d_model = d_model
        self.nhead = nhead
        self.d_lattice = d_lattice
        self.d_k = d_lattice // nhead

        # NRC Constants
        self.phi = (1.0 + math.sqrt(5.0)) / 2.0
        self.phi_inv = 1.0 / self.phi
        self.phi_int = 1618

        # 3D to 2048D Giza-Lattice Projectors
        self.q_proj = nn.Linear(d_model, d_lattice)
        self.k_proj = nn.Linear(d_model, d_lattice)
        self.v_proj = nn.Linear(d_model, d_lattice)
        self.out_proj = nn.Linear(d_lattice, d_model)

    def qrt_damping(self, x: torch.Tensor) -> torch.Tensor:
        """Quantum Residue Turbulence (QRT) Entropy Collapse damping.

        ψ(x) = sin(φ √2 · 51.85 x) · exp(-x² / φ) + cos(π / φ · x).
        """
        phi_sqrt2_5185 = self.phi * math.sqrt(2.0) * 51.85
        pi_over_phi = math.pi / self.phi

        term1 = torch.sin(phi_sqrt2_5185 * x) * torch.exp(-(x**2) / self.phi)
        term2 = torch.cos(pi_over_phi * x)
        return term1 + term2

    def ttt_filter(self, scores: torch.Tensor) -> torch.Tensor:
        """Applies the Trageser Tensor Transformer (TTT) modulo 9 reduction.

        Penalizes chaotic voids (3, 6, 9) by decaying their attention weights.
        """
        # Pseudo-integer reduction for modular stability check
        int_scores = (torch.abs(scores) * self.phi_int).long()
        mod_9 = int_scores % 9

        # Determine penalty mask for chaotic nodes (0, 3, 6, 9 mod 9)
        chaos_mask = (mod_9 == 0) | (mod_9 == 3) | (mod_9 == 6) | (mod_9 == 9)

        # Apply phi_inv shrinkage to chaotic nodes (entropy collapse)
        penalty = torch.ones_like(scores)
        penalty[chaos_mask] = self.phi_inv

        return scores * penalty

    def forward(self, x: torch.Tensor, mask: torch.Tensor = None) -> torch.Tensor:
        batch_size, seq_len, _ = x.size()

        # Project tokens into the 2048D Giza-Lattice projector space
        q = self.q_proj(x).view(batch_size, seq_len, self.nhead, self.d_k).transpose(1, 2)
        k = self.k_proj(x).view(batch_size, seq_len, self.nhead, self.d_k).transpose(1, 2)
        v = self.v_proj(x).view(batch_size, seq_len, self.nhead, self.d_k).transpose(1, 2)

        # Compute pre-attention Golden scalar scores
        scores = torch.matmul(q, k.transpose(-2, -1)) / math.sqrt(self.d_k)

        # 1. Apply TTT 3-6-9-7 Chaos Masking
        scores = self.ttt_filter(scores)

        if mask is not None:
            scores = scores.masked_fill(mask == 0, -1e9)

        # 2. Extract standard probability distribution
        attn_weights = F.softmax(scores, dim=-1)

        # 3. Apply QRT Damping function as the attention bias envelope
        qrt_bias = self.qrt_damping(attn_weights)
        attn_weights = attn_weights * qrt_bias

        # Collapse into values
        context = torch.matmul(attn_weights, v)
        context = context.transpose(1, 2).contiguous().view(batch_size, seq_len, self.d_lattice)

        # Project back to original dimension
        return self.out_proj(context)


if __name__ == "__main__":
    print("Initializing NRC Geometric Transformer Layer (2048D Lattice)...")
    layer = NRCGeometricTransformerLayer(d_model=256, nhead=8, d_lattice=2048)
    dummy_input = torch.randn(2, 50, 256)  # Batch size 2, Seq len 50, d_model 256
    output = layer(dummy_input)
    print(f"Successfully processed batch. Output shape: {output.shape}")
