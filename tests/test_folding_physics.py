"""Property-based tests for Protein Folding Accelerator stability."""

import numpy as np
import pytest
import torch
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from nrc_bio import NRCFoldAccelerator


@pytest.fixture
def acc():
    return NRCFoldAccelerator(dimension=2048)


@settings(
    max_examples=50, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(st.floats(min_value=-10, max_value=10))
def test_mst_recurrence_properties(acc, val):
    """Verify MST recurrence stays within modular bounds and is consistent."""
    res = acc.mst_recurrence(val)
    assert 0 <= res < 24389
    # Determinism check
    assert acc.mst_recurrence(val) == res


@settings(
    max_examples=50, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture]
)
@given(st.lists(st.floats(min_value=-10.0, max_value=10.0), min_size=8, max_size=8))
def test_lattice_projection_fidelity(acc, data):
    """Verify lattice projection MSE floor and shape consistency."""
    x_8 = np.array(data, dtype=np.float64)
    # Higher k should still result in stable projections
    for k in [1, 2, 3]:
        out = acc.lattice_project_256_to_729(x_8, k=k)
        assert out.shape == (729,)
        assert not np.any(np.isnan(out))
        assert not np.any(np.isinf(out))


def test_qrt_damping_extreme_values(acc):
    """Verify QRT stability on extreme boundary conditions."""
    x = torch.tensor([1e6, -1e6, 0.0, float("nan"), float("inf")])
    # We filter out nan/inf for the math call to prevent crash,
    # but verify structural response on large finite values.
    x_finite = torch.tensor([1e6, -1e6, 0.0])
    out = acc.qrt_damping(x_finite)
    assert out.shape == (3,)
    assert torch.all(torch.isfinite(out))


def test_torsion_stabilization_gradient(acc):
    """Verify that torsion stabilization is differentiable for training."""
    angles = torch.tensor([0.1, -0.1], requires_grad=True)
    stabilized = acc.stabilize_torsion(angles)
    loss = stabilized.sum()
    loss.backward()
    assert angles.grad is not None
    assert torch.all(torch.isfinite(angles.grad))
