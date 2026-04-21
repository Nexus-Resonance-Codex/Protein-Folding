import sys
import os

# --- JINJA2 HASH-ARMOR POLYFILL (defense-in-depth) ---
try:
    import jinja2.utils
    _LRU = jinja2.utils.LRUCache

    _orig_get = _LRU.get
    def _safe_get(self, key, default=None):
        try:
            hash(key)
            return _orig_get(self, key, default)
        except TypeError:
            return default
    _LRU.get = _safe_get

    _orig_getitem = _LRU.__getitem__
    def _safe_getitem(self, key):
        try:
            hash(key)
            return _orig_getitem(self, key)
        except TypeError:
            raise KeyError(key)
    _LRU.__getitem__ = _safe_getitem

    _orig_setitem = _LRU.__setitem__
    def _safe_setitem(self, key, value):
        try:
            hash(key)
            return _orig_setitem(self, key, value)
        except TypeError:
            pass
    _LRU.__setitem__ = _safe_setitem

    _orig_contains = _LRU.__contains__
    def _safe_contains(self, key):
        try:
            hash(key)
            return _orig_contains(self, key)
        except TypeError:
            return False
    _LRU.__contains__ = _safe_contains
    print("NRC: Jinja2 Hash-Armor Active (complete).")
except Exception as e:
    print(f"NRC: Jinja2 patch skipped: {e}")

# --- AUDIOOP POLYFILL (for Python 3.13+ if ever used) ---
try:
    import audioop  # noqa: F401 — available on Python <=3.12
except ImportError:
    try:
        import audioop_lts as audioop
        sys.modules["audioop"] = audioop
    except ImportError:
        pass

# --- HF HUB POLYFILL ---
try:
    import huggingface_hub
    if not hasattr(huggingface_hub, "HfFolder"):
        class MockHfFolder:
            @staticmethod
            def get_token(): return os.getenv("HF_TOKEN")
            @staticmethod
            def save_token(token): pass
            @staticmethod
            def delete_token(): pass
        huggingface_hub.HfFolder = MockHfFolder
except ImportError:
    pass

import gradio as gr
import gradio_client.utils

# Gradio Client JSON Type Polyfill
original = gradio_client.utils.json_schema_to_python_type
def safe_json_schema_to_python_type(schema, defs=None):
    try:
        return original(schema, defs)
    except (TypeError, KeyError):
        return "Any"
gradio_client.utils.json_schema_to_python_type = safe_json_schema_to_python_type

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from nrc_engine import NRCEngine
from biophysics import BiophysicsSuite
from reporting import ReportingSuite

# ─── Initialization ──────────────────────────────────────────────────────────
engine = NRCEngine()

# ─── Prototypes / Presets ──────────────────────────────────────────────────
PROTEIN_LIBRARY = {
    "Insulin": {"seq": "GIVEQCCTSICSLYQLENYCNFVNQHLCGSHLVEALYLVCGERGFFYTPKT"},
    "Ubiquitin": {"seq": "MQIFVKTLTGKTITLEVEPSDTIENVKAKIQDKEGIPPDQQRLIFAGKQLEDGRTLSDYNIQKESTLHLVLRLRGG"},
    "Lysozyme": {"seq": "KVFERCELARTLKRLGMDGYRGISLANWMCLAKWESGYNTRATNYNAGDRSTDYGIFQINSRYWCNDGKTPGAVNACHLSCSALLQDNIADAVACAKRVVRDPQGIRAWVAWRNRCQNRDVRQYVQGCGV"},
    "BPTI": {"seq": "RPDFCLEPPYTGPCKARIIRYFYNAKAGLCQTFVYGGCRAKRNNFKSAEDCMRTCGGA"},
    "Myoglobin": {"seq": "MGLSDGEWQLVLNVWGKVEADIPGHGQEVLIRLFKGHPETLEKFDKFKHLKSEDEMKASEDLKKHGATVLTALGGILKKKGHHEAEIKPLAQSHATKHKIPVKYLEFISECIIQVLQSKHPGDFGADAQGAMNKALELFRKDMASNYKELGFQG"},
    "p53 DNA-binding": {"seq": "MEEPQSDPSVEPPLSQETFSDLWKLLPENNVLSPLPSQAMDDLMLSPDDIEQWFTEDPGPDEAPRMPEAAPPVAPAPAAPTPAAPAPAPSWPLSSSVPSQKTYQGSYGFRLGFLHSGTAKSVTCTYSPALNKMFCQLAKTCPVQLWVDSTPPPGTRVRAMAIYKQSQHMTEVVRRCPHHERCSDSDGLAPPQHLIRVEGNLRVEYLDDRNTFRHSVVVPYEPPEVGSDCTTIHYNYMCNSSCMGGMNRRPILTIITLEDSSGNLLGRNSFEVRVCACPGRDRRTEEENLRKKGEPHHELPPGSTKRALPNNTSSSPQPKKKPLDGEYFTLQIRGRERFEMFRELNEALELKDAQAGKEPGGSRAHSSHLKSKKGQSTSRHKKLMFKTEGPDSD"},
    "Rhodopsin (GPCR)": {"seq": "MNGTEGPNFYVPFSNKTGVVRSPFEAPQYYLAEPWQFSMLAAYMFLLIMLGFPINFLTLYVTVQHKKLRTPLNYILLNLAVADLFMVFGGFTTTLYTSLHGYFVFGPTGCNLEGFFATLGGEIALWSLVVLAIERYVVVCKPMSNFRFGENHAIMGVAFTWVMALACAAPPLVGWSRYIPEGMQCSCGIDYYTPHEETNNESFVIYMFVVHFIIPLIVIFFCYGQLVFTVKEAAAQQQESATTQKAEKEVTRMVIIMVIAFLICWLPYAGVAFYIFTHQGSDFGPIFMTIPAFFAKTSAVYNPVIYIMMNKQFRNCMVTTLCCGKNPLGDDEASATASKTETSQVAPA"},
    "Top7 (Designed)": {"seq": "MGDIQVQVNIDDNGKNFDYTYTVTTESELQKVLNELMDYIKKQGAKRVRISITARTKKEAEKFAAILIKVFAELGYNDINVTFDGDTVTVEGQLEGGSLEHHHHHH"},
    "ORF8 (SARS-CoV-2)": {"seq": "MKFLVFLGIITTVAAFHQECSLQSCTQHQPYVVDDPCPIHFYSKWYIRVGARKSAPLIELCVDEAGSKSPIQYIDIGNYTVSCLPFTINCQEPKLGSLVVRCSFYEDFLEYHDVRVVLDFI"},
}

CSS = \"\"\"
:root {
    --nrc-gold: #D4AF37;
    --nrc-obsidian: #1A1A1B;
}
.main-header { text-align: center; color: var(--nrc-gold); padding: 2rem; }
.expert-card { background: #2D2D2E; border-left: 4px solid var(--nrc-gold); padding: 1rem; border-radius: 4px; }
.log-console { font-family: 'Courier New', monospace; font-size: 0.8rem; background: #000; color: #0F0; padding: 10px; border-radius: 4px; height: 300px; overflow-y: scroll; border: 1px solid #333; }
footer { display: none !important; }
\"\"\"

def get_viewer_html(pdb_str, engine_type="3Dmol", pockets=None):
    if engine_type == "3Dmol":
        pockets_js = ""
        if pockets:
            for p in pockets:
                indices = ",".join(map(str, p["residues"]))
                pockets_js += f"viewer.addSurface($3Dmol.SurfaceType.VDW, {{opacity:0.4, color:'cyan'}}, {{resi:[{indices}]}});\n"
        
        return f\"\"\"
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
        \"\"\"
    else: # NGL
        return f\"\"\"
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
        \"\"\"

def run_nrc_folding(seq, viewer_choice):
    log_history = []
    def log(msg):
        log_history.append(f"[{pd.Timestamp.now().strftime('%H:%M:%S')}] {msg}")
        return "\n".join(log_history)

    try:
        if not seq: return [None]*11
        seq = seq.strip().upper()
        current_logs = log(f"INIT: Resonance-Fold Pipeline v2.6. Target: {seq[:10]}...")
        frames = list(engine.fold_sequence(seq))
        final = frames[-1]
        coords = final["coords"]
        current_logs = log(f"CONVERGENCE: TTT-7 stability achieved at {final['stability']:.4f}")
        analysis = BiophysicsSuite.analyze_sequence(seq, coords)
        meta = {
            "hash": ReportingSuite.generate_share_hash(seq),
            "avg_confidence": float(np.mean(final["confidence"])),
            "ttt_stability": float(final["stability"])
        }
        pdb_text = ReportingSuite.generate_pdb(seq, coords)
        zip_path = ReportingSuite.create_research_package(f"nrc_{meta['hash']}", seq, coords, analysis, meta)
        viewer_html = get_viewer_html(pdb_text, viewer_choice, pockets=analysis["pockets"][:1])
        lattice_viz = go.Figure(data=[go.Scatter3d(
            x=coords[:, 0], y=coords[:, 1], z=coords[:, 2],
            mode='lines+markers', line=dict(color='gold', width=4)
        )])
        lattice_viz.update_layout(template="plotly_dark", title="φ-Lattice Projection")
        h_fig = go.Figure(data=go.Heatmap(z=[analysis["hydropathy"]], colorscale='Viridis'))
        h_fig.update_layout(template="plotly_dark", title="Hydrophobicity Profile", height=200)
        c_fig = go.Figure(data=go.Heatmap(z=[analysis["charge"]], colorscale='RdBu', zmid=0))
        c_fig.update_layout(template="plotly_dark", title="Charge Profile", height=200)
        summary_df = pd.DataFrame([
            ["Length", len(seq)],
            ["pI", analysis["pI"]],
            ["Stability", f"{meta['ttt_stability']:.4f}"]
        ], columns=["Metric", "Value"])
        current_logs = log("SUCCESS: Institutional package ready for export.")
        return (
            viewer_html, lattice_viz, h_fig, c_fig, summary_df, 
            zip_path, pdb_text, "".join(analysis["dssp"]), analysis["pI"], meta["hash"], current_logs
        )
    except Exception as e:
        import traceback
        err_msg = log(f"ERROR: {str(e)}")
        print(f"PIPELINE ERROR: {e}")
        traceback.print_exc()
        raise gr.Error(f"Institutional Error: {str(e)}")

with gr.Blocks(css=CSS, title="Resonance-Fold") as demo:
    gr.HTML("<div class='main-header'><h1>RESONANCE-FOLD</h1></div>")
    with gr.Tabs():
        with gr.Tab("🔬 Playground"):
            with gr.Row():
                with gr.Column(scale=1):
                    seq_input = gr.Textbox(label="Sequence", lines=8, placeholder="Paste FASTA or raw amino acid sequence...")
                    viewer_choice = gr.Radio(["3Dmol", "NGL"], label="3D Engine", value="3Dmol")
                    fold_btn = gr.Button("🚀 EXECUTE", variant="primary")
                    with gr.Accordion("Grand Gallery", open=False):
                        target_select = gr.Dropdown(choices=list(PROTEIN_LIBRARY.keys()), label="Select Target", interactive=True)
                        load_target_btn = gr.Button("📥 LOAD TARGET", size="sm")
                        def load_selected_target(name):
                            if name in PROTEIN_LIBRARY: return PROTEIN_LIBRARY[name]["seq"]
                            return ""
                        target_select.change(load_selected_target, target_select, seq_input)
                        load_target_btn.click(load_selected_target, target_select, seq_input)
                with gr.Column(scale=2):
                    viewer_box = gr.HTML("<div style='height: 520px; border: 1px dashed #444; border-radius: 8px; display: flex; align-items: center; justify-content: center;'>Fold a protein to see the 3D structure here.</div>")
                    log_console = gr.Textbox(label="Institutional Log Console", lines=10, elem_classes="log-console", interactive=False)
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
                    pi_out = gr.Number(label="pI", interactive=False)
                    hash_out = gr.Textbox(label="Hash", interactive=False)
        with gr.Tab("📦 Export"):
            export_file = gr.File(label="Download Research Package (.zip)")
            raw_pdb = gr.Code(label="PDB 3.3 Output", language="markdown")
        with gr.Tab("📚 Documentation"):
            gr.Markdown("### Institutional Protocol\nResonance-Fold utilizes the **Nexus Resonance Codex (NRC)** framework.")

    fold_btn.click(
        fn=run_nrc_folding,
        inputs=[seq_input, viewer_choice],
        outputs=[viewer_box, lattice_plot, hydro_plot, charge_plot, summary_table, export_file, raw_pdb, dssp_out, pi_out, hash_out, log_console]
    )

if __name__ == "__main__":
    demo.queue().launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_api=False,
        show_error=True,
        quiet=True
    )
