"""Tests for NRCFoldAccelerator."""

import numpy as np
import torch

from nrc_bio import NRCFoldAccelerator, fold_sequence


def test_qrt_damping() -> None:
    """Verify QRT damping output shape and values."""
    acc = NRCFoldAccelerator()
    x = np.linspace(-1, 1, 10)
    out = acc.qrt_damping(x)
    assert len(out) == 10
    assert isinstance(out, np.ndarray)


def test_mst_recurrence() -> None:
    """Verify MST recurrence is deterministic and within range."""
    acc = NRCFoldAccelerator()
    val = acc.mst_recurrence(1.0)
    assert isinstance(val, int)
    assert 0 <= val < 24389

    # Check determinism
    assert acc.mst_recurrence(1.0) == val


def test_lattice_project() -> None:
    """Verify lattice projection output shape."""
    acc = NRCFoldAccelerator()
    x_8 = np.random.rand(8)
    out = acc.lattice_project_256_to_729(x_8)
    assert len(out) == 729


def test_stabilize_torsion() -> None:
    """Verify torsion stabilization with torch tensors."""
    acc = NRCFoldAccelerator()
    angles = torch.tensor([0.1, 0.2, 0.3])
    stabilized = acc.stabilize_torsion(angles)
    assert stabilized.shape == (3,)
    assert isinstance(stabilized, torch.Tensor)


def test_fold_sequence() -> None:
    """Verify high-level folding interface."""
    res = fold_sequence("ACDEFGHIK")
    assert res["status"] == "TTT STABILIZED"
    assert res["residues"] == 9
    assert "lattice_resonance" in res


def test_metadata() -> None:
    """Verify package metadata."""
    from nrc_bio import __about__

    assert __about__.__version__ == "1.0.0"
    assert __about__.__author__ == "James Trageser"
