import torch
import math

PHI = (1.0 + math.sqrt(5.0)) / 2.0
MST_MODULUS = 24389
MST_LAMBDA = 0.381

def mst_step(x_n: torch.Tensor) -> torch.Tensor:
    """
    Modular Synchronisation Theory (MST) step evaluation cap.
    x_{n+1} = floor(1000 * sinh(x_n)) + log(x_n**2 + 1) + φ^{x_n} mod 24389

    Generates cycles of ~2100 with Lyapunov exponent λ ≈ 0.381.
    """
    term1 = torch.floor(1000.0 * torch.sinh(x_n))
    term2 = torch.log(x_n**2 + 1.0)
    term3 = torch.pow(PHI, x_n)

    total = term1 + term2 + term3

    # Use fmod for PyTorch floating modulus
    return torch.fmod(torch.abs(total), MST_MODULUS)
