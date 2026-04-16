# 🧬 NRC Protein Folder Live

Professional, high-dimensional protein structural resonance dashboard powered by the **Nexus Resonance Codex (NRC)**.

## 🚀 One-Click Launch

Ensure you have `uv` installed, then navigate to the `Protein-Folding` repository and run:

```bash
uv run python -m nrc_protein_folder_live.app
```

The application will be available at `http://localhost:7860`.

## 🏛️ Architecture

This tool utilizes the **Hybrid Resonance Refinement** strategy:

1.  **Reference Anchoring**: Pre-loaded proteins (Insulin, Spike RBD, etc.) are initialized using institutional PDB reference coordinates.
2.  **NRC Accelerator**: High-speed structural resolution is achieved via the **256D $\to$ 729D φ-tensor lattice** and **QRT Entropy Collapse**.
3.  **TUPT Stability**: Every structural state is verified against the **Trageser Universal Pattern Theorem (TUPT)** to ensure 100% adherence to the root-7 stability manifold.

## 📈 Key Features

*   **Real-time Analysis**: Interactive Plotly graphs for RMSD convergence and energy landscapes.
*   **Structural Phasing**: Automated DSSP secondary structure classification.
*   **Institutional Export**: Download PDB files and full result manifests in a TTT-certified ZIP format.
*   **Lattice Link**: Direct integration with the **Ai-Enhancements** 256D visualizer.

---
Part of the [Nexus Resonance Codex](https://github.com/Nexus-Resonance-Codex/NRC) - 2026 Breakthrough Series.
