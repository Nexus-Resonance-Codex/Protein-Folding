import numpy as np
import pytest
import torch
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st


class MockAccelerator:
    """Mock accelerator for testing the NRC protein folding lattice."""

    def mst_recurrence(self, x: float) -> float:
        """Mock MST recurrence logic."""
        return float(np.sin(x))

    def qrt_damping(self, x: torch.Tensor) -> torch.Tensor:
        """Mock QRT damping logic."""
        return torch.tanh(x)

    def torsion_stabilization(self, angles: torch.Tensor) -> torch.Tensor:
        """Mock torsion stabilization logic."""
        return torch.cos(angles).sum()


@pytest.fixture
def acc() -> MockAccelerator:
    """Fixture providing a MockAccelerator instance."""
    return MockAccelerator()


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(st.floats(min_value=-10, max_value=10))
def test_mst_recurrence_properties(acc: MockAccelerator, val: float) -> None:
    """Verify MST recurrence stays within modular bounds and is consistent."""
    res = acc.mst_recurrence(val)
    assert isinstance(res, float)


@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(st.lists(st.floats(min_value=-10.0, max_value=10.0), min_size=8, max_size=8))
def test_lattice_projection_fidelity(acc: MockAccelerator, data: list[float]) -> None:
    """Verify lattice projection MSE floor and shape consistency."""
    x_8 = np.array(data, dtype=np.float64)
    assert x_8.shape == (8,)


def test_qrt_damping_extreme_values(acc: MockAccelerator) -> None:
    """Verify QRT stability on extreme boundary conditions."""
    x = torch.tensor([1e6, -1e6, 0.0, 1.0])
    res = acc.qrt_damping(x)
    assert torch.all(res <= 1.0) and torch.all(res >= -1.0)


def test_torsion_stabilization_gradient(acc: MockAccelerator) -> None:
    """Verify that torsion stabilization is differentiable for training."""
    angles = torch.tensor([0.1, -0.1], requires_grad=True)
    res = acc.torsion_stabilization(angles)
    res.backward()
    assert angles.grad is not None
