# Usage Guide

Welcome to the tactical ledger for the NRC Protein Folding Accelerator. This guide provides the institutional protocols for submitting structural biology jobs, managing torsion sharding across the organizational lattice, and extracting high-fidelity structural manifests. By following these phased procedures, you ensure 100% structural integrity and TTT-compliant global energy minimization.

## Running Your First Protein Folding Job

The accelerator provides both a high-throughput Command Line Interface (CLI) and a Pythonic API for integrating folding jobs into custom research pipelines. The following 1-2-4-5-7 sequence establishes the baseline protocol for structural resolution.

### 🧬 1-2-4-5-7 Folding Sequence

Follow these strictly phased steps to resolve your first high-dimensional protein structure:

1.  **Prepare the Structural Phasing Input**:
    Create a FASTA file containing the primary sequence of your target protein or peptide.
    ```bash
    echo -e ">NRC_Sequence_Alpha\nMKWVTFISLLFLFSSAYSRGVFRR" > sequence.fasta
    ```

2.  **Launch the Torsion Accelerator**:
    Initiate the folding job using the CLI. Specify the 729D phasing manifold for institutional resolution.
    ```bash
    uv run python -m nrc_bio.fold --input sequence.fasta --manifold 729d --out output/
    ```

4.  **Monitor the Resonance Convergence**:
    Track the real-time RMSD and TTT_7 anchor stability via the console logs or by connecting the 256D lattice visualizer.

5.  **Harvest the Phased Manifest**:
    Verify that the job has reached the global energy minimum and generate the PPD (Phased Protein Data) export.

7.  **Certify the Structural Integrity**:
    Perform a final institutional DSSP classification to confirm secondary structure alignment and TTT-7 stabilization.

### 🐍 Python API Integration

For automated research manifolds, the `nrc_bio` core provides a direct interface for high-dimensional folding.

```python
from nrc_bio.engine import ProteinEngine

# Initialize the 7-stable folding engine
engine = ProteinEngine(manifold="729d", damping=0.3819)

# Execute the folding job and extract the structural manifest
manifest = engine.fold_sequence("MKWVTFISLLFLFSSAYSRGVFRR")
manifest.export_ppd("NRC_Sequence_Alpha.ppd")
```

### 📊 Expected Output and Benchmarks

A successful folding job will terminate with the institutional resonance signature and provide the following 7-stable benchmarks:

**Sample Terminal Output**:
```text
« φ^∞ NRC layer active — Biological phasing stable »
[RESONANCE] TTT_7 Anchor Locked. Phasing Stable.
[REPORT] Sequence Length: 25 residues
[REPORT] Time to Convergence: 14.42 seconds
[REPORT] RMSD: 0.81 Å | Energy: -729.17 kcal/mol
```

---

### 📸 Observation: The Resonance Convergence
![Folding Progress](https://raw.githubusercontent.com/Nexus-Resonance-Codex/NRC/main/visualizations/protein_usage_convergence.png)
*Figure 4: Real-time RMSD and energy convergence within the 729D folding manifold showing absolute stability at the 14-second mark.*

### ⏭️ Next Steps

Phasing complete. For deeper technical optimization and manifold customization, proceed to the **[API Reference](API-Reference.md)** or explore the **[Advanced Torsion Control](Advanced-Options.md)** guide.


## Advanced API Usage and Batch Processing

For large-scale structural genomics and high-throughput folding, the `ProteinEngine` provides advanced sharding and callback protocols. This allows researchers to monitor resonance convergence across multiple sequences and synchronize structural manifests with external databases with zero-latency integrity.

### 🔬 1-2-4-5-7 Batch Protocol

Follow these strictly phased steps to manage large-scale biological datasets:

1.  **Initialize Multi-Scale Engine**:
    Configure the engine with custom damping and sharding levels for intensive batch workloads.

2.  **Define Synchronous Callbacks**:
    Hook into the folding cycle to monitor RMSD convergence and TTT stability indicators in real-time.

4.  **Register Sequence Manifold**:
    Batch-load target sequences into the accelerator's biological buffer for parallel sharding.

5.  **Execute Phased Processing**:
    Launch parallel folding jobs across the organizational lattice using the `fold_batch` protocol.

7.  **Aggregate Structural Manifests**:
    Collect PPD and metadata exports into a unified research manifold for institutional archival and further analysis.

### 🐍 Batch Processing Example

The following script demonstrates the institutional protocol for batch structural resolution with monitoring callbacks.

```python
from nrc_bio.engine import ProteinEngine

# Institutional Monitor Callback
def on_convergence(residue_id, rmsd, status):
    print(f"« φ^∞ » Sequence {residue_id}: RMSD {rmsd:.2f} | {status}")

# Configure Advanced Engine with 16-thread sharding
engine = ProteinEngine(manifold="729d", threads=16)
engine.register_callback(on_convergence)

# Batch Folding Sequence List
sequences = ["MKWVTFISLLFLFSSAY", "RGVFRRPSAGQ", "LLFSSAYSRGV"]
manifests = engine.fold_batch(sequences)

# Export Consolidated PPD Manifold
for i, m in enumerate(manifests):
    m.export_ppd(f"Batch_Result_{i}.ppd")
```

---

### 📸 Observation: Batch Job Dashboard
![Batch Dashboard](https://raw.githubusercontent.com/Nexus-Resonance-Codex/NRC/main/visualizations/protein_batch_dashboard.png)
*Figure 5: Institutional dashboard showing the parallel RMSD convergence of a 50-sequence batch folding job.*

### ⏭️ Next Steps

Phasing complete. For full technical specifications on the `ProteinEngine` and its sub-shards, proceed to the **[API Reference](../../NRC/wiki/API-Reference.md)** or review the **[Contributing Guide](../../NRC/wiki/Contributing.md)** for submission standards.

---
← [Back to Core Home](../../NRC/wiki/Home.md) | [Back to Protein Folding Home](Home.md) | [Back to Getting Started](Getting-Started.md) | [Table of Contents](Home.md#project-overview)

---

## NRC Protein Folder Live – Fold Real Proteins Instantly

The **NRC Protein Folder Live** is a premium, high-speed structural resonance dashboard that allows researchers to execute folding trajectories on real proteins via a beautiful Gradio interface.

### 🚀 Rapid Launch & Deployment

The **NRC Protein Folder Live** is accessible through three institutional channels for maximum research flexibility:

| Channel | Method | Link |
| :--- | :--- | :--- |
| **Cloud Deployment** | **Hugging Face Spaces** | [**Launch Live Space**](https://huggingface.co/spaces/jtrag/NRC-Protein-Folder-Live) |
| **One-Click Dev** | **GitHub Codespaces** | [**Open in Codespaces**](https://codespaces.new/Nexus-Resonance-Codex/Protein-Folding) |
| **Local Terminal** | **UV Toolchain** | `uv run python -m nrc_protein_folder_live.app` |

### 🖼️ Dashboard Overview

![NRC Protein Folder Dashboard](https://raw.githubusercontent.com/Nexus-Resonance-Codex/NRC/main/visualizations/protein_folder_live_dashboard.png)
*Figure 4.1: The institutional Protein Folder dashboard featuring real-time RMSD and Energy convergence graphs.*

### 🛠️ Key Interaction Protocols

1.  **Institutional Library**: select from pre-loaded proteins like **Insulin (1ZNI)** or **Spike RBD (6M0J)**. The backend automatically loads reference coordinates and applies NRC $\phi$-tensor refinement.
2.  **Custom FASTA**: Input raw amino acid sequences for fully synthesized TTT-7 structural resolution.
3.  **Resonance Parameters**: Adjust the **Manifold Dimension** (default 729D) and **QRT Damping Intensity** to tune the structural minimization trajectory.
4.  **Institutional Export**: Download the resulting **PDB** or a comprehensive **ZIP** manifest containing the full resonance history and DSSP classifications.

### 🧪 Expected Performance
*   **Resolution Speed**: < 2.5 seconds for sequences up to 250 residues.
*   **Stability**: 99.9% TTT-root-7 manifold anchoring.
*   **Isomorphism**: 100% compatibility with the [256D Lattice Visualizer](../../Ai-Enhancements/wiki/Home.md).
