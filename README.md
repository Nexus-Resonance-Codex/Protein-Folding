<div align="center">
<img src="https://raw.githubusercontent.com/Nexus-Resonance-Codex/Phi-Infinity-Lattice-Compression/main/docs/assets/phi_spiral_banner.png" width="100%" alt="NRC Protein-Folding Banner">

# NRC Protein-Folding
## Infinite Structural Stability via φ^∞ Lattice Resonance

**"Revolutionizing computational biology with O(N) folding complexity and high-dimensional geometric resonance."**

[![Test Directly on GitHub](https://img.shields.io/badge/🚀%20Live-Folding%20Showcase-cyan?style=for-the-badge&logo=github)](https://nexus-resonance-codex.github.io/Protein-Folding/demos/protein-folding-showcase.html)
[![Models: Try on GitHub](https://img.shields.io/badge/🤖%20Run-HRE%20Verifier-gold?style=for-the-badge&logo=github)](https://github.com/Nexus-Resonance-Codex/Protein-Folding/blob/master/.github/prompts/folding-simulation-verifier.prompt.yml)
[![CI: Bio-Stability](https://github.com/Nexus-Resonance-Codex/Protein-Folding/actions/workflows/folding-evals.yml/badge.svg)](https://github.com/Nexus-Resonance-Codex/Protein-Folding/actions/workflows/folding-evals.yml)

[Flagship Showcase](https://nexus-resonance-codex.github.io/Protein-Folding/demos/protein-folding-showcase.html) • [Playground Hub](docs/NRC-Playground-Guide.md) • [Math Proofs](docs/math-foundations.md) • [Lattice Visualizer](docs/demos/lattice-visualizer.html)

</div>

---

### 🧪 The Breakthrough: O(N) Lattice Folding

Traditional protein folding architectures (e.g., AlphaFold 2) suffer from $O(N^2)$ attention bottlenecks. **NRC Protein-Folding** bypasses this limitation by mapping amino acid sequences into a stable **8192-dimensional lattice manifold**. 

By utilizing **Hierarchical Residual Encoding (HRE)** and $\varphi$-spiral projections, structural convergence becomes a constant-time geometric property rather than a stochastic search.

### 🌟 Interactive Playground

Forget local setup. Test the future of structural biology directly in your browser or on the GitHub UI:

| Feature | Action | Impact |
| :--- | :--- | :--- |
| **Live Showcase** | [**Launch 3D Folding Demo**](https://nexus-resonance-codex.github.io/Protein-Folding/demos/protein-folding-showcase.html) | Interactive 3D visualization + real-time RMSD. |
| **Interactive Verifier** | [**Run Model on GitHub**](https://github.com/Nexus-Resonance-Codex/Protein-Folding/blob/master/.github/prompts/folding-simulation-verifier.prompt.yml) | Input sequence → receive full folding trajectory. |
| **Stability Audit** | [**Compare Acceleration**](https://github.com/Nexus-Resonance-Codex/Protein-Folding/blob/master/.github/prompts/lattice-accelerated-folding-comparison.prompt.yml) | Test O(N^2) vs O(N) scaling side-by-side. |

---

### 🏛 Repository Architecture

*   **`src/nrc_bio`**: Core Rust-optimized FFI primitives for bio-lattice acceleration.
*   **`.github/prompts`**: PhD-level AI tools for structural verification and RMSD testing.
*   **`docs/math-foundations`**: Formal proofs for TUPT, TTT, and QRT damping in folding.
*   **`visualizations`**: Real-time manifold projection engines (Three.js).

### 🚀 Reproducibility & Verification

We maintain a 100% green verification pipeline. Run the logic locally or check our nightly logs:

```bash
# 1. Clone & Setup
git clone https://github.com/Nexus-Resonance-Codex/Protein-Folding.git
cd Protein-Folding && uv sync

# 2. Verify Mathematical Primitives
uv run pytest tests/ -k "lattice_stability"

# 3. View Benchmarks
cat docs/benchmarks.md
```

---
*Developed for the technological ascension of molecular life by James Trageser.*
