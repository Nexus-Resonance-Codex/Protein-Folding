import math
import mpmath
import torch

# Set maximum precision for golden ratio resonance calculations
mpmath.mp.dps = 100

# Exact constants
PHI_MP = (mpmath.mpf(1) + mpmath.sqrt(5)) / 2
PHI_FLOAT = float(PHI_MP)

PHI_INVERSE_MP = 1 / PHI_MP
PHI_INVERSE_FLOAT = float(PHI_INVERSE_MP)

SQRT_5_FLOAT = math.sqrt(5.0)

def binet_formula(n: int, as_mpmath: bool = False):
    """
    Calculates the exact nth Fibonacci number using Binet's formula:
    F_n = (φ^n - (-φ)^{-n}) / sqrt(5)
    """
    if as_mpmath:
        return (PHI_MP**n - (-PHI_MP)**(-n)) / mpmath.sqrt(5)
    return (PHI_FLOAT**n - (-PHI_FLOAT)**(-n)) / SQRT_5_FLOAT

def phi_power_tensor(n_tensor: torch.Tensor) -> torch.Tensor:
    """
    Computes φ^n over an entire PyTorch tensor efficiently.
    """
    return torch.pow(PHI_FLOAT, n_tensor)

def phi_infinity_fold(x: torch.Tensor, iterations: int = 5) -> torch.Tensor:
    """
    Computes the φ^∞ folding: repeated φ^n fold + 1/sqrt(5) stabilization
    for lossless infinite scaling.
    """
    folded = x.clone()
    for n in range(1, iterations + 1):
        folded = torch.pow(PHI_FLOAT, n) * folded + (1.0 / SQRT_5_FLOAT)
    return folded
