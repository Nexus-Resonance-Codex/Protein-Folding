"""
=============================================================================
PROOF 4: Phi Identity Verification Suite
=============================================================================
Proves the core algebraic identities that underpin every NRC enhancement.
These are not approximations — they are exact mathematical laws.

Used by: ALL 30 Enhancements (φ is the fundamental constant)
=============================================================================
"""
import math

PHI = (1 + math.sqrt(5)) / 2
PHI_INV = 1 / PHI


def prove_phi_identities():
    print("=" * 70)
    print("  PROOF 4: GOLDEN RATIO IDENTITY VERIFICATION")
    print("=" * 70)

    # --- Part 1: Exact Algebraic Identities (must match to machine epsilon) ---
    exact_tests = [
        ("φ² = φ + 1",             PHI**2,                PHI + 1),
        ("1/φ = φ - 1",            PHI_INV,               PHI - 1),
        ("φ × (1/φ) = 1",          PHI * PHI_INV,         1.0),
        ("φ³ = 2φ + 1",            PHI**3,                2*PHI + 1),
        ("φ⁴ = 3φ + 2",            PHI**4,                3*PHI + 2),
        ("φ⁵ = 5φ + 3",            PHI**5,                5*PHI + 3),
        ("φ⁶ = 8φ + 5",            PHI**6,                8*PHI + 5),
        ("φ⁻² = 2 - φ",            PHI_INV**2,            2 - PHI),
        ("φ⁻³ = 2φ - 3",           PHI_INV**3,            2*PHI - 3),
        ("φ² - φ - 1 = 0",         PHI**2 - PHI - 1,      0.0),
    ]

    print(f"\n  EXACT ALGEBRAIC IDENTITIES (tolerance < 1e-12):")
    print(f"  {'Identity':<30} | {'LHS':>22} | {'RHS':>22} | {'Status'}")
    print("-" * 95)

    all_exact_passed = True
    for name, lhs, rhs in exact_tests:
        err = abs(lhs - rhs)
        passed = err < 1e-12
        status = "  ✓ EXACT" if passed else f"  ✗ err={err:.2e}"
        if not passed:
            all_exact_passed = False
        print(f"  {name:<30} | {lhs:>22.15f} | {rhs:>22.15f} | {status}")

    assert all_exact_passed, "Exact Phi identities failed!"
    print(f"\n  All 10 exact identities verified  ✓\n")

    # --- Part 2: Fib(n)/Fib(n-1) convergence to φ ---
    print("  FIBONACCI RATIO CONVERGENCE TO φ:")
    print(f"  {'n':>6} | {'Fib(n)':>20} | {'Fib(n)/Fib(n-1)':>22} | {'Error vs φ':>14}")
    print("-" * 75)

    a, b = 1, 1
    for n in range(3, 31):
        a, b = b, a + b
        ratio = b / a
        err = abs(ratio - PHI)
        print(f"  {n:>6} | {b:>20} | {ratio:>22.15f} | {err:>14.2e}")

    final_err = abs(b / a - PHI)
    assert final_err < 1e-10, f"Fibonacci ratio failed to converge: err={final_err}"
    print(f"\n  Fib(30)/Fib(29) converges to φ within {final_err:.2e}  ✓")

    print("\n" + "=" * 70)
    print("  CONCLUSION: All algebraic φ identities hold exactly, and")
    print("  the Fibonacci ratio converges to φ exponentially fast.")
    print("=" * 70)


if __name__ == "__main__":
    prove_phi_identities()
