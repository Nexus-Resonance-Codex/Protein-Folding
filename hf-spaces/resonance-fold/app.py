import os
import time
import gradio as gr
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from typing import Dict, List, Tuple

# ─── NRC Institutional Modules ───────────────────────────────────────────────
from nrc_engine import engine
from biophysics import BiophysicsSuite
from reporting import ReportingSuite

# ─── Protein Library ─────────────────────────────────────────────────────────
PROTEIN_LIBRARY = {
    "Titin (Human)": {
        "desc": "The largest known protein — provides muscle elasticity.",
        "seq": "MTTQAPTFTQPLQSVVVLEGSTATFEAHISGFPVPEVSWFRDGQVISTSTLPGVQISFSDGRAKLTIPAVTKANSGRYSLKATNGSGQATSTAELLVKA",
        "organism": "Homo sapiens",
    },
    "Insulin (1ZNI)": {
        "desc": "Metabolic hormone — regulates blood glucose.",
        "seq": "GIVEQCCTSICSLYQLENYCNFVNQHLCGSHLVEALYLVCGERGFFYTPKT",
        "organism": "Homo sapiens",
    },
    "Lysozyme (1LYZ)": {
        "desc": "Antimicrobial enzyme — cleaves bacterial cell walls.",
        "seq": "KVFGRCELAAAMKRHGLDNYRGYSLGNWVCAAKFESNFNTQATNRNTDGSTDYGILQINSRWWCNDGRTPGSRNLCNIPCSALLSSDITASVNCAKKIVSDGNGMNAWVAWRNRCKGTDVQAWIRGCRL",
        "organism": "Gallus gallus",
    },
}

# ─── CSS ──────────────────────────────────────────────────────────────────────
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
:root { --gold: #d4af37; --obsidian: #0b0e14; }
body { font-family: 'Inter', sans-serif; background: var(--obsidian); color: #d1d5db; }
.main-header { text-align: center; padding: 40px; border-bottom: 1px solid rgba(212, 175, 55, 0.3); }
.main-header h1 { color: var(--gold); font-size: 3em; margin: 0; }
.expert-label { color: var(--gold); border: 1px solid var(--gold); padding: 2px 8px; border-radius: 4px; font-size: 0.7em; }
"""

# ─── Visualization Logic ─────────────────────────────────────────────────────
def get_viewer_html(pdb_text, viewer_type="3Dmol", pockets=[]):
    if not pdb_text: return ""
    v_id = f"v_{int(time.time()*1000)}"
    
    if viewer_type == "3Dmol":
        pocket_js = ""
        if pockets:
            pocket_js = f"v.addSphere({{ center: v.getModel().selectedAtoms({{ resi: {pockets} }})[0], radius: 1.0, color: 'red', opacity: 0.6 }});"
        
        return f"""
        <div id="{v_id}" style="height: 520px; width: 100%; background: #0b0e14; border-radius: 8px;"></div>
        <script>
            (function() {{
                const tryInit = () => {{
                    if (typeof $3Dmol === 'undefined') {{
                        setTimeout(tryInit, 200);
                        return;
                    }}
                    const v = $3Dmol.createViewer('{v_id}', {{ backgroundColor: '0x0b0e14' }});
                    v.addModel(`{pdb_text}`, 'pdb');
                    v.setStyle({{}}, {{ cartoon: {{ color: 'spectrum' }} }});
                    {pocket_js}
                    v.zoomTo(); v.render();
                }};
                tryInit();
            }})();
        </script>
        """
    else: # NGL Viewer
        return f"""
        <div id="{v_id}" style="height: 520px; width: 100%; background: #0b0e14; border-radius: 8px;"></div>
        <script>
            (function() {{
                const tryInit = () => {{
                    if (typeof NGL === 'undefined') {{
                        setTimeout(tryInit, 200);
                        return;
                    }}
                    var stage = new NGL.Stage('{v_id}', {{ backgroundColor: '#0b0e14' }});
                    var blob = new Blob([`{pdb_text}`], {{ type: 'text/plain' }});
                    stage.loadFile(blob, {{ ext: 'pdb' }}).then(function(o) {{
                        o.addRepresentation('cartoon', {{ color: 'residueindex' }});
                        o.autoView();
                    }});
                }};
                tryInit();
            }})();
        </script>
        """

# ─── Handlers ────────────────────────────────────────────────────────────────
def run_fold_v2(*args):
    try:
        print(f"DEBUG: run_fold_v2 called with {len(args)} args: {args}")
        if len(args) == 0: return [None]*10
        seq = args[0]
        viewer_choice = "3Dmol"
        steps = 250
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
        
        # 4. 3D Visualization (with pockets)
        viewer_html = get_viewer_html(pdb_text, viewer_choice, pockets=analysis["pockets"][:1])
        
        # 5. Lattice Explorer
        lattice_viz = go.Figure(data=[go.Scatter3d(
            x=coords[:, 0], y=coords[:, 1], z=coords[:, 2],
            mode='lines+markers', line=dict(color='gold', width=4)
        )])
        lattice_viz.update_layout(template="plotly_dark", title="φ-Lattice Projection")
        
        # 6. Heatmaps (Hydrophobicity & Charge)
        h_fig = go.Figure(data=go.Heatmap(z=[analysis["hydropathy"]], colorscale='Viridis'))
        h_fig.update_layout(template="plotly_dark", title="Hydrophobicity Profile", height=200)
        
        c_fig = go.Figure(data=go.Heatmap(z=[analysis["charge"]], colorscale='RdBu', zmid=0))
        c_fig.update_layout(template="plotly_dark", title="Charge Profile", height=200)
        
        summary_df = pd.DataFrame([
            ["Length", len(seq)],
            ["pI", analysis["pI"]],
            ["Stability", f"{meta['ttt_stability']:.4f}"]
        ], columns=["Metric", "Value"])
        
        print("Pipeline complete.")
        return viewer_html, lattice_viz, h_fig, c_fig, summary_df, zip_path, pdb_text, "".join(analysis["dssp"]), analysis["pI"], meta["hash"]
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
                    status_out = gr.Markdown("Ready")
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
            
            - **Engine**: 736D φ-tensor refinement.
            - **Stability**: TTT-7 stabilization audit.
            - **Capacity**: Up to 32,768 AA.
            """)
            with gr.Accordion("FAQ", open=False):
                gr.Markdown("""
                **Q: What is the maximum sequence length?**
                A: Up to 32,768 residues using our vectorized φ-tensor engine.
                
                **Q: How does the lattice refinement work?**
                A: We project a 736-dimensional manifold into 3D using TTT-7 stabilized tensors.
                """)

    
    fold_btn.click(
        fn=run_fold_v2,
        inputs=[seq_input],
        outputs=[viewer_box, lattice_plot, hydro_plot, charge_plot, summary_table, export_file, raw_pdb, dssp_out, pi_out, hash_out]
    )

if __name__ == "__main__":
    demo.launch()
