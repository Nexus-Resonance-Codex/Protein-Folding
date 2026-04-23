---
title: Resonance Fold Pro
emoji: 🧬
colorFrom: indigo
colorTo: purple
sdk: docker
app_file: hf-spaces/resonance-fold/app.py
pinned: false
---

# Nexus Resonance Codex: Protein-Folding

![NRC Protein Folding](https://img.shields.io/badge/NRC-Protein--Folding-indigo?style=for-the-badge&logo=dna)
![Gradio](https://img.shields.io/badge/Deployment-Hugging_Face-indigo?style=for-the-badge&logo=huggingface)
![Stability](https://img.shields.io/badge/TTT--7-Stable-green?style=for-the-badge)

## 🌌 Overview
This repository contains the high-performance protein folding engine and interactive demonstrations for the **Nexus Resonance Codex (NRC)**. Utilizing the **Trageser Tensor Theorem (TTT)** and high-dimensional **φ-spiral manifolds**, our platform achieves near-instantaneous structural prediction for intrinsically disordered proteins (IDPs) and complex globular targets.

### 🧬 Key Features
- **Multi-Modal Folding Locus**: Toggle between **NRC Pure Math**, **ESMFold (AI Only)**, and **Hybrid (AI + NRC)** modes.
- **Reference IDP Library**: Curated set of 100+ high-impact disordered proteins (sourced from DisProt) linked to neurodegeneration and cancer.
- **2048D φ-Manifold Projection**: Real-time visualization of structural resonance in non-Euclidean space.
- **Mutation Analysis Lab**: Simulate single-point mutations and predict ΔΔG resonance shifts.
- **Comprehensive Research Export**: Automated generation of PDB, CSV, and JSON metadata packages.

---

## 🚀 Live Demonstration
The primary interactive portal is hosted on **Hugging Face Spaces**:

👉 **[Resonance-Fold Pro (Live)](https://huggingface.co/spaces/Nexus-Resonance-Codex/Resonance-Fold)**

---

## 🛠 Repository Structure
- `hf-spaces/resonance-fold/`: Core production code for the Hugging Face Space.
- `nrc_engine.py`: The 2048D phi-lattice engine for deterministic folding.
- `biophysics.py`: Research-grade biophysical profile calculation (Hydropathy, Charge, Entropy).
- `protein_library.py`: Modular library of 100+ medically significant IDP sequences.

## 🧬 Mathematical Foundation
The NRC folding backend operates on the principle of **Lattice Resonance**. By projecting amino acid sequences into a 2048D φ-spiral manifold, we can solve structural topology as a harmonic resonance problem rather than a stochastic optimization.

For more details on the math, visit the **[Nexus Resonance Codex Core Repository](https://github.com/Nexus-Resonance-Codex/NRC)**.

---

## 📜 License
This work is released under the **Nexus Resonance Codex License (NRC-L)**.  
Copyright © 2026 Nexus Resonance Codex Team. All Rights Reserved.
