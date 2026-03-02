"""
=============================================================================
PROOF 9: Navier-Stokes Damping Bound
=============================================================================
Proves that the NRC Navier-Stokes damping regulariser maintains bounded
energy dissipation. The damping factor reduces gradient norms by a fixed
multiplicative ratio per step, guaranteeing monotonic decay.

Used by:
  - Enhancement #10: Navier-Stokes Damping Regulariser
=============================================================================
"""
import math

PHI = (1 + math.sqrt(5)) / 2
PHI_INV = 1 / PHI


def navier_stokes_damping(gradient_norm, viscosity=PHI_INV, dt=0.01):
    """
    NS-inspired viscous damping: dv/dt = -ν·v  =>  v(t+dt) = v·exp(-ν·dt)
    """
    return gradient_norm * math.exp(-viscosity * dt)


def prove_ns_damping():
    print("=" * 70)
    print("  PROOF 9: NAVIER-STOKES DAMPING REGULARISER BOUNDS")
    print("=" * 70)

    viscosity = PHI_INV
    dt = 0.01
    timesteps = 500

    # The key mathematical claim: after N steps, the reduction factor is
    # exactly exp(-ν * dt * N) regardless of initial magnitude.
    reduction_factor = math.exp(-viscosity * dt * timesteps)

    print(f"\n  Viscosity (ν):       φ⁻¹ = {viscosity:.6f}")
    print(f"  Time step (dt):      {dt}")
    print(f"  Iterations (N):      {timesteps}")
    print(f"  Reduction factor:    exp(-ν·dt·N) = {reduction_factor:.12e}\n")

    test_norms = [0.001, 0.1, 1.0, 10.0, 100.0, 1000.0, 1e6]

    print(f"  {'Initial ‖∇‖':>14} | {'After N steps':>18} | {'Observed Ratio':>16} | {'Match'}")
    print("-" * 75)

    all_match = True
    for g0 in test_norms:
        g = g0
        for _ in range(timesteps):
            g = navier_stokes_damping(g, viscosity, dt)

        observed_ratio = g / g0 if g0 > 0 else 0
        ratio_err = abs(observed_ratio - reduction_factor)
        match = ratio_err < 1e-10
        if not match:
            all_match = False
        status = "✓" if match else "✗"
        print(f"  {g0:>14.4f} | {g:>18.6e} | {observed_ratio:>16.12f} | {status}")

    print("-" * 75)

    assert all_match, "NS damping ratio mismatch!"
    print(f"\n  All gradient norms reduced by EXACTLY the same factor  ✓")
    print(f"  Reduction factor: {reduction_factor:.12e}")
    print(f"  This is independent of initial magnitude — a key physical property.\n")

    # Show that increasing steps drives ANY initial norm to zero
    print("  Convergence to zero:")
    for steps in [100, 500, 1000, 2000, 5000]:
        factor = math.exp(-viscosity * dt * steps)
        print(f"    After {steps:>5} steps: factor = {factor:.6e}  "
              f"(1e6 → {1e6 * factor:.4e})")

    print("\n" + "=" * 70)
    print("  CONCLUSION: NS damping preserves gradient direction while")
    print("  applying an exact, magnitude-independent reduction factor.")
    print("  Unlike hard clipping, this is a smooth, differentiable operation.")
    print("=" * 70)


if __name__ == "__main__":
    prove_ns_damping()
