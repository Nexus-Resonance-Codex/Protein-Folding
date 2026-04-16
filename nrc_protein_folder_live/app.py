#  Nexus Resonance Codex - 2025-2026 Breakthrough Series
#  Copyright (c) 2026 James Trageser (@jtrag)
#
#  Licensed under CC-BY-NC-SA-4.0 + NRC-L
"""NRC Protein Folder Live: Institutional Gradio Dashboard."""

import os
import shutil
import tempfile
from pathlib import Path

import gradio as gr
import plotly.graph_objects as go
import pandas as pd

from .folder import NRCFoldBackend, ProteinLibrary, FoldResult

# Institutional CSS
THEME_CSS = """
.gradio-container {
    background-color: #0d0d0d !important;
    color: #ffd700 !important;
    font-family: 'Inter', sans-serif !important;
}
.gr-button-primary {
    background: linear-gradient(135deg, #ffd700 0%, #b8860b 100%) !important;
    color: black !important;
    border: none !important;
    font-weight: bold !important;
}
.gr-input, .gr-textarea, .gr-dropdown {
    background-color: #1a1a1a !important;
    border: 1px solid #ffd700 !important;
    color: #ffd700 !important;
}
h1, h2, h3 {
    color: #ffd700 !important;
    text-shadow: 0 0 10px rgba(255, 215, 0, 0.3);
}
"""


def build_app():
    backend = NRCFoldBackend()
    
    with gr.Blocks(css=THEME_CSS, title="NRC Protein Folder Live") as demo:
        gr.Markdown("# 🧬 NRC Protein Folder Live – Level 5.0")
        gr.Markdown("### Institutional Structural Resonance Dashboard")
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("## 🏗️ Configuration")
                
                # Selection logic
                protein_names = list(ProteinLibrary.DATA.keys())
                selector = gr.Dropdown(
                    choices=protein_names + ["Custom (Raw FASTA)"],
                    value="Insulin (1ZNI)",
                    label="Target Protein"
                )
                
                description_box = gr.Markdown(
                    f"**Description**: {ProteinLibrary.DATA['Insulin (1ZNI)']['description']}"
                )
                
                sequence_input = gr.Textbox(
                    label="Sequence (FASTA)",
                    value=ProteinLibrary.DATA["Insulin (1ZNI)"]["sequence"],
                    lines=4
                )
                
                with gr.Row():
                    dim_slider = gr.Slider(minimum=256, maximum=729, value=729, step=1, label="Manifold Dimension")
                    damping_slider = gr.Slider(minimum=0.1, maximum=1.0, value=0.5, step=0.1, label="QRT Damping Intensity")
                
                fold_btn = gr.Button("🚀 Fold Now", variant="primary")
                
            with gr.Column(scale=2):
                gr.Markdown("## 📈 Folding Resonance Real-Time")
                
                with gr.Row():
                    rmsd_plot = gr.Plot(label="RMSD Convergence (Å)")
                    energy_plot = gr.Plot(label="Energy Landscape (kcal/mol)")
                
                with gr.Row():
                    dssp_table = gr.DataTable(
                        label="DSSP Structural Phasing",
                        headers=["Index", "Residue", "Assignment"],
                        datatype=["number", "str", "str"],
                        interactive=False
                    )
                
                with gr.Row():
                    pdb_output = gr.File(label="Download PDB Structure")
                    zip_output = gr.File(label="Download Full Results (.zip)")
                
                gr.Markdown("---")
                gr.Markdown("🔗 [Open in 256D Visualizer](https://nexus-resonance-codex.github.io/Ai-Enhancements/) | [Lattice Documentation](https://github.com/Nexus-Resonance-Codex/NRC/wiki)")

        # Event Handlers
        def update_sequence(name):
            if name in ProteinLibrary.DATA:
                data = ProteinLibrary.DATA[name]
                return f"**Description**: {data['description']}", data['sequence']
            return "**Description**: Manual sequence input mode.", ""

        selector.change(update_sequence, inputs=[selector], outputs=[description_box, sequence_input])

        def run_folding(seq, dim, damp, progress=gr.Progress()):
            progress(0, desc="Initializing Giza Projection...")
            
            # Update dimension in backend
            backend.dimension = dim
            
            # Simulate steps for progress bar
            result = backend.fold(seq, steps=100, damping=damp)
            
            # Prepare RMSD Plot
            fig_rmsd = go.Figure()
            fig_rmsd.add_trace(go.Scatter(y=result.rmsd_history, mode='lines+markers', name='RMSD', line=dict(color='#ffd700')))
            fig_rmsd.update_layout(title="RMSD Convergence", template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            
            # Prepare Energy Plot
            fig_energy = go.Figure()
            fig_energy.add_trace(go.Bar(y=result.energy_history, name='Energy', marker_color='#b8860b'))
            fig_energy.update_layout(title="Energy Landscape", template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            
            # Prepare DSSP Data
            dssp_data = [[i+1, seq[i], result.dssp_assignment[i]] for i in range(len(seq))]
            df_dssp = pd.DataFrame(dssp_data, columns=["Index", "Residue", "Assignment"])
            
            # Save files to temp
            temp_dir = Path(tempfile.mkdtemp())
            pdb_path = temp_dir / "folded_structure.pdb"
            with open(pdb_path, "w") as f:
                f.write(result.pdb_content)
            
            zip_path = backend.create_package(result, temp_dir)
            
            return fig_rmsd, fig_energy, df_dssp, str(pdb_path), str(zip_path)

        fold_btn.click(
            run_folding,
            inputs=[sequence_input, dim_slider, damping_slider],
            outputs=[rmsd_plot, energy_plot, dssp_table, pdb_output, zip_output]
        )

    return demo


if __name__ == "__main__":
    app = build_app()
    app.launch(server_name="0.0.0.0", server_port=7860)
