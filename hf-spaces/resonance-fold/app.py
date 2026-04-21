import sys
import os

# Add the app directory to sys.path to resolve local modules when running from root
app_dir = os.path.dirname(os.path.abspath(__file__))
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

# --- JINJA2 HASH-ARMOR POLYFILL ---
try:
    import jinja2.utils
    _LRU = jinja2.utils.LRUCache
    def _safe_get(self, key, default=None):
        try: hash(key); return _orig_get(self, key, default)
        except TypeError: return default
    _orig_get = _LRU.get; _LRU.get = _safe_get
    print("NRC: Jinja2 Armor Active.")
except: pass

import gradio as gr
import requests
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from nrc_engine import NRCEngine
from biophysics import BiophysicsSuite
from reporting import ReportingSuite

# ─── Initialization ──────────────────────────────────────────────────────────
engine = NRCEngine()

PROTEIN_LIBRARY = {
    "Insulin (Human)": "GIVEQCCTSICSLYQLENYCNFVNQHLCGSHLVEALYLVCGERGFFYTPKT",
    "Ubiquitin": "MQIFVKTLTGKTITLEVEPSDTIENVKAKIQDKEGIPPDQQRLIFAGKQLEDGRTLSDYNIQKESTLHLVLRLRGG",
    "Myoglobin": "MGLSDGEWQLVLNVWGKVEADIPGHGQEVLIRLFKGHPETLEKFDKFKHLKSEDEMKASEDLKKHGATVLTALGGILKKKGHHEAEIKPLAQSHATKHKIPVKYLEFISECIIQVLQSKHPGDFGADAQGAMNKALELFRKDMASNYKELGFQG",
    "p53 Fragment": "SVPSQKTYQGSYGFRLGFLHSGTAKSVTCTYSPALNKMFCQLAKTCPVQLWVDSTPPPGTRVRAMAIYKQSQHMTEVVRRCPHHERCSDSDGLAPPQHLIRVEGNLRVEYLDDRNTFRHSVVVPYEPPEVGSDCTTIHYNYMCNSSCMGGMNRRPILTIITLEDSSGNLLGRNSFEVRVCACPGRDRRTEEENLRKKGEPHHELPPGSTKRALPNNTSSSPQPKKKPLDGEYFTLQIRGRERFEMFRELNEALELKDAQAGKEPGGSRAHSSHLKSKKGQSTSRHKKLMFKTEGPDSD",
    "SARS-CoV-2 RBD": "NITNLCPFGEVFNATRFASVYAWNRKRISNCVADYSVLYNSASFSTFKCYGVSPTKLNDLCFTNVYADSFVIRGDEVRQIAPGQTGKIADYNYKLPDDFTGCVIAWNSNNLDSKVGGNYNYLYRLFRKSNLKPFERDISTEIYQAGSTPCNGVEGFNCYFPLQSYGFQPTNGVGYQPYRVVVLSFELLHAPATVCGPKKSTNLVKNKCVNF",
}

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=Fira+Code:wght@400;500&display=swap');

:root {
    --nrc-gold: #D4AF37;
    --nrc-obsidian: #0a0a0b;
    --nrc-accent: #1c1c1e;
    --nrc-glass: rgba(255, 255, 255, 0.02);
    --nrc-glow: rgba(212, 175, 55, 0.15);
}

body, .gradio-container {
    background: radial-gradient(circle at top, #141416 0%, var(--nrc-obsidian) 100%) !important;
    color: #f0f0f0 !important;
    font-family: 'Outfit', sans-serif;
}

.main-header {
    text-align: center;
    padding: 4rem 1rem;
    background: linear-gradient(180deg, rgba(20,20,22,1) 0%, rgba(10,10,11,0) 100%);
}

.main-header h1 {
    font-size: 5rem;
    font-weight: 800;
    letter-spacing: -2px;
    background: linear-gradient(135deg, #fff 0%, var(--nrc-gold) 50%, #fff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
}

.premium-card {
    background: var(--nrc-glass) !important;
    border: 1px solid rgba(212, 175, 55, 0.2) !important;
    border-radius: 24px !important;
    padding: 2rem !important;
    box-shadow: 0 20px 40px rgba(0,0,0,0.6) !important;
    backdrop-filter: blur(20px);
}

.spaced-card {
    margin-top: 20px !important;
}

.log-console {
    font-family: 'Fira Code', monospace !important;
    background: #000 !important;
    color: var(--nrc-gold) !important;
    border: 1px solid #222 !important;
    border-radius: 12px !important;
}

.status-ring {
    width: 12px; height: 12px;
    background: #00FF88;
    border-radius: 50%;
    display: inline-block;
    margin-right: 8px;
    box-shadow: 0 0 10px #00FF88;
}

button.primary {
    background: linear-gradient(135deg, var(--nrc-gold) 0%, #8A6D3B 100%) !important;
    color: #000 !important;
    font-weight: 800 !important;
    text-transform: uppercase;
    letter-spacing: 1px;
    border-radius: 16px !important;
    height: 60px !important;
    border: none !important;
}

button.secondary {
    background: rgba(255,255,255,0.05) !important;
    color: #fff !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
}

/* Customizing Gradio Components */
.tabs { border: none !important; }
.tab-nav { background: transparent !important; border-bottom: 1px solid #222 !important; }
.tab-nav button { color: #888 !important; }
.tab-nav button.selected { color: var(--nrc-gold) !important; border-bottom: 2px solid var(--nrc-gold) !important; }

footer { display: none !important; }
"""

def get_viewer_html(pdb_str, engine_type="3Dmol", pockets=None):
    pdb_safe = pdb_str.replace("`", "\\`").replace("$", "\\$").replace("\n", "\\n")
    if engine_type == "3Dmol":
        pockets_js = ""
        if pockets:
            for p in pockets:
                indices = ",".join(map(str, p["residues"]))
                pockets_js += f"viewer.addSurface($3Dmol.SurfaceType.VDW, {{opacity:0.5, color:'gold'}}, {{resi:[{indices}]}});\n"
        
        return f"""
        <div id="mol-container" style="height: 600px; width: 100%; border-radius: 20px; overflow: hidden; background: #000; border: 1px solid #222;"></div>
        <script>
            (function() {{
                const init = () => {{
                    const el = document.getElementById('mol-container');
                    if (!el) return;
                    if (!window.$3Dmol) {{
                        console.log("NRC: 3Dmol not found, loading...");
                        const script = document.createElement('script');
                        script.src = 'https://3Dmol.org/build/3Dmol-min.js';
                        script.onload = () => init();
                        document.head.appendChild(script);
                        return;
                    }}
                    const v = $3Dmol.createViewer(el, {{backgroundColor: '#000'}});
                    v.addModel(`{pdb_safe}`, "pdb");
                    v.setStyle({{}}, {{cartoon: {{color: 'spectrum', thickness: 0.6}}}});
                    {pockets_js}
                    v.zoomTo();
                    v.render();
                    v.animate({{loop: "backAndForth", step: 0.5}});
                    console.log("NRC: 3Dmol Visualizer Resonant.");
                }};
                init();
            }})();
        </script>
        """
    else:
        return f"""
        <div id="ngl-container" style="height: 600px; width: 100%; border-radius: 20px; overflow: hidden; background: #000; border: 1px solid #222;"></div>
        <script>
            (function() {{
                const init = () => {{
                    const el = document.getElementById('ngl-container');
                    if (!el) return;
                    if (!window.NGL) {{
                        console.log("NRC: NGL not found, loading...");
                        const script = document.createElement('script');
                        script.src = 'https://unpkg.com/ngl@2.0.0-dev.37/dist/ngl.js';
                        script.onload = () => init();
                        document.head.appendChild(script);
                        return;
                    }}
                    const s = new NGL.Stage("ngl-container", {{backgroundColor: "black"}});
                    const b = new Blob([`{pdb_safe}`], {{type: 'text/plain'}});
                    s.loadFile(b, {{ext: "pdb"}}).then(o => {{
                        o.addRepresentation("cartoon", {{color: "resname"}});
                        o.autoView();
                        console.log("NRC: NGL Visualizer Resonant.");
                    }});
                }};
                init();
            }})();
        </script>
        """

def run_nrc_pipeline(seq, viewer_type):
    logs = [f"[{pd.Timestamp.now().strftime('%H:%M:%S')}] INITIALIZING RESONANCE-FOLD ENGINE..."]
    try:
        seq = seq.strip().upper()
        if not seq: return [None]*15
        
        # 1. Folding
        frames = list(engine.fold_sequence(seq))
        final = frames[-1]
        coords = final["coords"]
        logs.append(f"[OK] LATTICE CONVERGENCE AT {final['stability']:.4f}")
        
        # 2. Analysis
        analysis = BiophysicsSuite.analyze_sequence(seq, coords)
        meta = {
            "hash": ReportingSuite.generate_share_hash(seq),
            "avg_confidence": float(np.mean(final["confidence"])),
            "ttt_stability": float(final["stability"])
        }
        logs.append(f"[OK] ANALYSIS COMPLETE. CONFIDENCE: {meta['avg_confidence']:.2f}%")
        
        # 3. Visuals
        pdb_text = ReportingSuite.generate_pdb(seq, coords)
        viewer_html = get_viewer_html(pdb_text, viewer_type, analysis["pockets"][:1])
        
        # Lattice Plot
        l_fig = go.Figure(data=[go.Scatter3d(
            x=coords[:,0], y=coords[:,1], z=coords[:,2],
            mode='lines+markers', marker=dict(size=4, color=final["confidence"], colorscale='Viridis', colorbar=dict(title="pLDDT")),
            line=dict(color='rgba(212,175,55,0.3)', width=5)
        )])
        l_fig.update_layout(template="plotly_dark", margin=dict(l=0,r=0,b=0,t=0))
        
        # Ramachandran Plot
        r_fig = px.scatter(x=analysis["ramachandran"]["phi"], y=analysis["ramachandran"]["psi"], 
                           labels={"x":"Phi", "y":"Psi"}, title="Virtual Ramachandran Projection")
        r_fig.add_shape(type="rect", x0=-180, y0=-180, x1=180, y1=180, line=dict(color="rgba(255,255,255,0.1)"))
        r_fig.update_layout(template="plotly_dark", height=400)
        
        # Hydro/Charge Plots
        h_fig = go.Figure(data=go.Bar(y=analysis["hydropathy"], marker_color='cyan'))
        h_fig.update_layout(template="plotly_dark", title="Residue Hydropathy", height=250)
        
        c_fig = go.Figure(data=go.Bar(y=analysis["charge"], marker_color='red'))
        c_fig.update_layout(template="plotly_dark", title="Electrostatic Profile", height=250)
        
        # Summary
        summary_df = pd.DataFrame([
            ["Residues", len(seq)],
            ["Confidence (pLDDT)", f"{meta['avg_confidence']:.2f}%"],
            ["TTT Stability", f"{meta['ttt_stability']:.4f}"],
            ["Isoelectric Point", f"{analysis['pI']}"],
            ["Provenance Hash", meta["hash"]]
        ], columns=["Metric", "Value"])
        
        zip_path = ReportingSuite.create_research_package(f"nrc_{meta['hash']}", seq, coords, analysis, meta)
        
        return (
            viewer_html, l_fig, r_fig, h_fig, c_fig, summary_df,
            zip_path, pdb_text, "".join(analysis["dssp"]), analysis["pI"], meta["hash"], "\n".join(logs)
        )
    except Exception as e:
        return [None]*11 + [f"[ERROR] {str(e)}"]

def run_mutation(seq, pos, new_aa):
    try:
        res = BiophysicsSuite.simulate_mutation(seq, int(pos)-1, new_aa)
        return f"Mutation: {res['mutation']}\nΔΔG Estimate: {res['estimated_ddg']} kcal/mol\nStability: {res['stability']}"
    except Exception as e:
        return f"Error: {e}"

with gr.Blocks(css=CSS, title="Resonance-Fold Pro", head="""
    <script src="https://3Dmol.org/build/3Dmol-min.js"></script>
    <script src="https://unpkg.com/ngl"></script>
""") as demo:
    with gr.Column(elem_classes="main-header"):
        gr.HTML("<h1>RESONANCE-FOLD PRO</h1>")
        gr.Markdown("<div style='text-align:center; color:#888;'>Institutional 256D φ-Lattice Protein Folding Platform • v2.6.2 Stable</div>")
        gr.HTML("<div style='text-align:center; margin-top:10px;'><span class='status-ring'></span><span style='color:#00FF88; font-size:0.8rem; font-weight:600;'>SYSTEMS RESONANT</span></div>")

    with gr.Row():
        with gr.Column(scale=1):
            with gr.Column(elem_classes="premium-card"):
                seq_input = gr.Textbox(label="Protein Sequence", lines=8, placeholder="Enter amino acids (A, R, N, D...)")
                with gr.Row():
                    lib_select = gr.Dropdown(choices=list(PROTEIN_LIBRARY.keys()), label="Prototypes")
                    viewer_type = gr.Radio(["3Dmol", "NGL"], label="Visualizer", value="3Dmol")
                fold_btn = gr.Button("EXECUTE QUANTUM FOLDING", variant="primary")
                lib_select.change(lambda x: PROTEIN_LIBRARY.get(x, ""), lib_select, seq_input)
            
            with gr.Column(elem_classes=["premium-card", "spaced-card"]):
                gr.Markdown("### 🧬 Mutation Lab")
                with gr.Row():
                    m_pos = gr.Number(label="Pos", value=1, precision=0)
                    m_aa = gr.Dropdown(choices=list("ACDEFGHIKLMNPQRSTVWY"), label="New AA", value="A")
                mut_btn = gr.Button("SIMULATE MUTATION", size="sm")
                mut_out = gr.Textbox(label="ΔΔG Resonance Report", interactive=False)
                mut_btn.click(run_mutation, [seq_input, m_pos, m_aa], mut_out)

        with gr.Column(scale=2):
            with gr.Tabs():
                with gr.Tab("🔭 3D Structural Manifold"):
                    viewer_box = gr.HTML("<div style='height: 600px; border: 2px dashed #222; border-radius: 20px; display:flex; align-items:center; justify-content:center; background:#000; color:#444;'>AWAITING RESONANCE TRIGGER</div>")
                    log_box = gr.Textbox(label="Lattice Console", lines=5, elem_classes="log-console")
                
                with gr.Tab("📈 Analytical Resonance"):
                    with gr.Row():
                        summary_table = gr.Dataframe(interactive=False)
                        ramachandran_plot = gr.Plot(label="Ramachandran Projection")
                    with gr.Row():
                        hydro_plot = gr.Plot()
                        charge_plot = gr.Plot()
                    with gr.Row():
                        dssp_out = gr.Textbox(label="Secondary Structure (DSSP)", interactive=False)
                        with gr.Column():
                            pi_out = gr.Label(label="Isoelectric Point")
                            hash_out = gr.Label(label="Provenance Hash")
                
                with gr.Tab("🌌 Lattice Explorer"):
                    lattice_plot = gr.Plot(label="High-Dimensional Projection")
                
                with gr.Tab("📥 Research Export"):
                    with gr.Row():
                        export_zip = gr.File(label="Institutional Package (.zip)")
                        pdb_code = gr.Code(label="PDB Source", language="markdown")

    fold_btn.click(
        fn=run_nrc_pipeline,
        inputs=[seq_input, viewer_type],
        outputs=[
            viewer_box, lattice_plot, ramachandran_plot, hydro_plot, charge_plot, 
            summary_table, export_zip, pdb_code, dssp_out, pi_out, hash_out, log_box
        ]
    )

if __name__ == "__main__":
    demo.queue().launch(server_name="0.0.0.0", server_port=7860, share=False)
