import gradio as gr
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from nrc_engine import NRCEngine
from biophysics import BiophysicsSuite
from reporting import ReportingSuite
import os

# ─── Initialization ──────────────────────────────────────────────────────────
engine = NRCEngine()

# ─── Prototypes / Presets ──────────────────────────────────────────────────
PROTEIN_LIBRARY = {
    "Insulin (A+B)": {"seq": "GIVEQCCTSICSLYQLENYCNFVNQHLCGSHLVEALYLVCGERGFFYTPKT"},
    "Ubiquitin": {"seq": "MQIFVKTLTGKTITLEVEPSDTIENVKAKIQDKEGIPPDQQRLIFAGKQLEDGRTLSDYNIQKESTLHLVLRLRGG"},
    "NRC-Alpha (Synthetic)": {"seq": "MLRLLRLLRLLRLLRLLRLLRLLRLLRLLRLLRLLRLLRLLRLLRLLRLLR"}
}

CSS = """
:root {
    --nrc-gold: #D4AF37;
    --nrc-obsidian: #1A1A1B;
}
.main-header { text-align: center; color: var(--nrc-gold); padding: 2rem; }
.expert-card { background: #2D2D2E; border-left: 4px solid var(--nrc-gold); padding: 1rem; border-radius: 4px; }
footer { display: none !important; }
"""

def get_viewer_html(pdb_str, engine_type="3Dmol", pockets=None):
    if engine_type == "3Dmol":
        pockets_js = ""
        if pockets:
            for p in pockets:
                indices = ",".join(map(str, p["residues"]))
                pockets_js += f"viewer.addSurface($3Dmol.SurfaceType.VDW, {{opacity:0.4, color:'cyan'}}, {{resi:[{indices}]}});\n"
        
        return f"""
        <div id="mol-container" style="height: 500px; width: 100%; position: relative;"></div>
        <script>
            (function() {{
                const container = document.getElementById('mol-container');
                const viewer = $3Dmol.createViewer(container, {{backgroundColor: 'black'}});
                viewer.addModel(`{pdb_str}`, "pdb");
                viewer.setStyle({{}}, {{cartoon: {{color: 'spectrum'}}}});
                {pockets_js}
                viewer.zoomTo();
                viewer.render();
            }})();
        </script>
        """
    else: # NGL
        return f"""
        <div id="ngl-container" style="height: 500px; width: 100%;"></div>
        <script>
            (function() {{
                const stage = new NGL.Stage("ngl-container", {{backgroundColor: "black"}});
                const blob = new Blob([`{pdb_str}`], {{type: 'text/plain'}});
                stage.loadFile(blob, {{ext: "pdb"}}).then(function(o) {{
                    o.addRepresentation("cartoon", {{color: "resname"}});
                    o.autoView();
                }});
            }})();
        </script>
        """

# ─── Handlers ────────────────────────────────────────────────────────────────
def run_nrc_folding(seq, viewer_choice):
    try:
        if not seq: return [None]*10
        seq = seq.strip().upper()
        print(f"Folding sequence: {seq[:20]}... (length: {len(seq)})")
        
        # 1. Fold
        frames = list(engine.fold_sequence(seq))
        final = frames[-1]
        coords = final["coords"]
        
        # 2. Analyze
        analysis = BiophysicsSuite.analyze_sequence(seq, coords)
        meta = {
            "hash": ReportingSuite.generate_share_hash(seq),
            "avg_confidence": float(np.mean(final["confidence"])),
            "ttt_stability": float(final["stability"])
        }
        
        # 3. Reports
        pdb_text = ReportingSuite.generate_pdb(seq, coords)
        zip_path = ReportingSuite.create_research_package(f"nrc_{meta['hash']}", seq, coords, analysis, meta)
        
        # 4. 3D Visualization
        viewer_html = get_viewer_html(pdb_text, viewer_choice, pockets=analysis["pockets"][:1])
        
        # 5. Lattice Explorer
        lattice_viz = go.Figure(data=[go.Scatter3d(
            x=coords[:, 0], y=coords[:, 1], z=coords[:, 2],
            mode='lines+markers', line=dict(color='gold', width=4)
        )])
        lattice_viz.update_layout(template="plotly_dark", title="φ-Lattice Projection")
        
        # 6. Analytics Plots
        h_fig = go.Figure(data=go.Heatmap(z=[analysis["hydropathy"]], colorscale='Viridis'))
        h_fig.update_layout(template="plotly_dark", title="Hydrophobicity Profile", height=200)
        
        c_fig = go.Figure(data=go.Heatmap(z=[analysis["charge"]], colorscale='RdBu', zmid=0))
        c_fig.update_layout(template="plotly_dark", title="Charge Profile", height=200)
        
        summary_df = pd.DataFrame([
            ["Length", len(seq)],
            ["pI", analysis["pI"]],
            ["Stability", f"{meta['ttt_stability']:.4f}"]
        ], columns=["Metric", "Value"])
        
        return (
            viewer_html, lattice_viz, h_fig, c_fig, summary_df, 
            zip_path, pdb_text, "".join(analysis["dssp"]), analysis["pI"], meta["hash"]
        )
    except Exception as e:
        print(f"PIPELINE ERROR: {e}")
        import traceback
        traceback.print_exc()
        raise gr.Error(f"Institutional Error: {str(e)}")

# ─── App UI ──────────────────────────────────────────────────────────────────
HEAD_HTML = """
<script src="https://cdnjs.cloudflare.com/ajax/libs/3Dmol/2.4.2/3Dmol-min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/ngl@2.0.0-dev.37/dist/ngl.js"></script>
"""

with gr.Blocks(css=CSS, title="Resonance-Fold", head=HEAD_HTML) as demo:
    gr.HTML("<div class='main-header'><h1>RESONANCE-FOLD</h1></div>")
    
    with gr.Tabs():
        with gr.Tab("🔬 Playground"):
            with gr.Row():
                with gr.Column(scale=1):
                    seq_input = gr.Textbox(label="Sequence", lines=8, placeholder="Paste FASTA or raw amino acid sequence...")
                    viewer_choice = gr.Radio(["3Dmol", "NGL"], label="3D Engine", value="3Dmol")
                    fold_btn = gr.Button("🚀 EXECUTE", variant="primary")
                    
                    with gr.Accordion("Gallery", open=False):
                        for name, data in PROTEIN_LIBRARY.items():
                            btn = gr.Button(f"Load {name}")
                            btn.click(lambda d=data: d["seq"], None, seq_input)
                
                with gr.Column(scale=2):
                    viewer_box = gr.HTML("<div style='height: 520px; border: 1px dashed #444; border-radius: 8px; display: flex; align-items: center; justify-content: center;'>Fold a protein to see the 3D structure here.</div>")
        
        with gr.Tab("📊 Analytics"):
            with gr.Row():
                hydro_plot = gr.Plot(label="Hydrophobicity")
                charge_plot = gr.Plot(label="Charge")
            summary_table = gr.Dataframe(label="Analysis Summary")
            
        with gr.Tab("🧬 Expert Suite"):
            with gr.Row():
                lattice_plot = gr.Plot(label="φ-Lattice Explorer")
                with gr.Column():
                    dssp_out = gr.Textbox(label="DSSP Assignment", interactive=False)
                    pi_out = gr.Number(label="Isoelectric Point (pI)", interactive=False)
                    hash_out = gr.Textbox(label="Provenance Hash", interactive=False)
        
        with gr.Tab("📦 Export"):
            export_file = gr.File(label="Download Research Package (.zip)")
            raw_pdb = gr.Code(label="PDB 3.3 Output", language="markdown")
            
        with gr.Tab("📚 Documentation"):
            gr.Markdown("""
            ### Institutional Protocol
            Resonance-Fold utilizes the **Nexus Resonance Codex (NRC)** framework to simulate protein structural behavior in high-dimensional φ-manifolds.
            """)

    fold_btn.click(
        fn=run_nrc_folding,
        inputs=[seq_input, viewer_choice],
        outputs=[viewer_box, lattice_plot, hydro_plot, charge_plot, summary_table, export_file, raw_pdb, dssp_out, pi_out, hash_out]
    )

if __name__ == "__main__":
    demo.launch()
