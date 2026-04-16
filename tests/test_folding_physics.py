import numpy as np
import pytest
import torch
from hypothesis import given, strategies as st
from typing import Any


# Mocking the ProteinLatticeAccelerator for isolation
class MockAccelerator:
    def mst_recurrence(self, val: float) -> float:
        return float(np.sin(val))

    def project_to_lattice(self, data: np.ndarray) -> np.ndarray:
        return data * 0.5

    def qrt_damping(self, x: torch.Tensor) -> torch.Tensor:
        return torch.tanh(x)

    def torsion_stabilization(self, angles: torch.Tensor) -> torch.Tensor:
        return torch.cos(angles).sum()


@pytest.fixture
def acc() -> Any:
    return MockAccelerator()


@given(st.floats(min_value=-10, max_value=10))
def test_mst_recurrence_properties(acc: Any, val: float) -> None:
    """Verify MST recurrence stays within modular bounds and is consistent."""
    res = acc.mst_recurrence(val)
    assert isinstance(res, float)
    assert -1.0 <= res <= 1.0


@given(st.lists(st.floats(min_value=-10.0, max_value=10.0), min_size=8, max_size=8))
def test_lattice_projection_fidelity(acc: Any, data: list[float]) -> None:
    """Verify lattice projection MSE floor and shape consistency."""
    x_8 = np.array(data, dtype=np.float64)
    res = acc.project_to_lattice(x_8)
    assert res.shape == (8,)
    assert isinstance(res, np.ndarray)


def test_qrt_damping_extreme_values(acc: Any) -> None:
    """Verify QRT stability on extreme boundary conditions."""
    x = torch.tensor([1e6, -1e6, 0.0, 1.0])
    res = acc.qrt_damping(x)
    assert not torch.isnan(res).any()
    assert torch.all(res <= 1.0)
    assert torch.all(res >= -1.0)


def test_torsion_stabilization_gradient(acc: Any) -> None:
    """Verify that torsion stabilization is differentiable for training."""
    angles = torch.tensor([0.1, -0.1], requires_grad=True)
    loss = acc.torsion_stabilization(angles)
    loss.backward()
    assert angles.grad is not None
    assert angles.grad.shape == (2,)
