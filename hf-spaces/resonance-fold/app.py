import sys
import os
import requests
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import gradio as gr

# Add the app directory to sys.path
app_dir = os.path.dirname(os.path.abspath(__file__))
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

# --- Initialization ──────────────────────────────────────────────────────────

from nrc_engine import NRCEngine
from biophysics import BiophysicsSuite
from reporting import ReportingSuite

# ─── Initialization ──────────────────────────────────────────────────────────
engine = NRCEngine()

PROTEIN_LIBRARY = {
    "Insulin (Human)": "GIVEQCCTSICSLYQLENYCNFVNQHLCGSHLVEALYLVCGERGFFYTPKT",
    "Ubiquitin": "MQIFVKTLTGKTITLEVEPSDTIENVKAKIQDKEGIPPDQQRLIFAGKQLEDGRTLSDYNIQKESTLHLVLRLRGG",
    "Myoglobin": "MGLSDGEWQLVLNVWGKVEADIPGHGQEVLIRLFKGHPETLEKFDKFKHLKSEDEMKASEDLKKHGATVLTALGGILKKKGHHEAEIKPLAQSHATKHKIPVKYLEFISECIIQVLQSKHPGDFGADAQGAMNKALELFRKDMASNYKELGFQG",
    "SARS-CoV-2 RBD": "NITNLCPFGEVFNATRFASVYAWNRKRISNCVADYSVLYNSASFSTFKCYGVSPTKLNDLCFTNVYADSFVIRGDEVRQIAPGQTGKIADYNYKLPDDFTGCVIAWNSNNLDSKVGGNYNYLYRLFRKSNLKPFERDISTEIYQAGSTPCNGVEGFNCYFPLQSYGFQPTNGVGYQPYRVVVLSFELLHAPATVCGPKKSTNLVKNKCVNF",
    "Tough-Target-13": "ASFPLDVAPRLCLAVTVAKLGSKASCPAWNLVAAKACMLASKRVRRPLTDLNVKALHSATVLS",
    "Tough-Target-14": "STQLRSALKFKLCCVKKNRHAKYLPEDSALQHFGLHLHPSLMYQKCMLQQVPKHEVLGTHPNLCLALQHISCRTCKVKGPAAAGAYVKPVVHLLLKRVSQLVGMAKK",
    "Tough-Target-15": "QCAREQVKHMALTALQLTHQLAKSGTITNAIHLTTKLGGHSVVLQVAVPALQGLLP",
    "Tough-Target-16": "RCVAAAHAPPGKAASKLVKGLVRPGLHQCVVTDVLNLTCMKHKKKLHHPRHHEKLGCQHLQKKYAATTVR",
    "Tough-Target-17": "KNALRKGHALAVAHGKQWVGKNPCVLATKKTLCAVKRVPKANRCTKRTQSPGVLPCESKPPVADYEARKANHQAVIINAYKAVLCCEAK",
    "Tough-Target-18": "LRSPGKAVNMACFQVPCAQTKSLTKPCLCPSLFCCKKSDAYKVALSIHCKACCGMKCPVKITYPTQAASSNTPALLVPCSLGEHNHLGCVLYRLQLKPCHV",
    "Tough-Target-19": "ADAHLAKYPNGHAQTNVPTPELRQGADVQLTNENGCCVKCQHVAQSCQKCFNAHKAEQKAKRSQVMKSVKKTPAAAKCQTRNNGSWNYALHKPICATNAYKIKTLNVAVLQYHVMTQQNLSHPMRGAHRKAMI",
    "Tough-Target-20": "NLALHHKQMPKCENVLLSNTTGKVLHISAVGCNLQKDLA",
    "Tough-Target-21": "CYFKHWTGCQKMNIALVVDKPHVLKAMPKGKVLASVGKQKHWVSCELPRKYHNSKKAAKPLVGATHFAHQACAMRHHCVALHRIQAVQRKNHLLVTQWLSNVLNEEVSGHPCWRRY",
    "Tough-Target-22": "GTCCWAINCGFDLKVVQHLSGQNRALIDYCKDRCKCNVAPTQPKVLKPGTAKDNTKPHTHPLSQVKRFFKAGHRQGAQHGL"
}

CSS = """
:root { --nrc-gold: #D4AF37; --nrc-obsidian: #0A0A0A; }
.main-header { background: #000; padding: 2rem; border-bottom: 2px solid var(--nrc-gold); text-align: center; }
.main-header h1 { color: var(--nrc-gold) !important; letter-spacing: 4px; }
.status-ring { display: inline-block; width: 12px; height: 12px; background: #00FF88; border-radius: 50%; box-shadow: 0 0 10px #00FF88; margin-right: 8px; }
.premium-card { background: rgba(20,20,20,0.8) !important; border: 1px solid #222 !important; border-radius: 20px !important; padding: 1.5rem !important; }
.log-console { background: #000 !important; color: #00FF88 !important; font-family: monospace !important; }
button.primary { background: linear-gradient(90deg, #B8860B, #D4AF37) !important; color: #000 !important; font-weight: 700 !important; border-radius: 16px !important; }
"""

def get_viewer_html(pdb_str, engine_type="3Dmol", pockets=None):
    pdb_safe = pdb_str.replace("`", "\\`").replace("$", "\\$").replace("\n", "\\n")
    pockets_js = ""
    if engine_type == "3Dmol" and pockets:
        for p in pockets:
            indices = ",".join(map(str, p["residues"]))
            pockets_js += f"viewer.addSurface($3Dmol.SurfaceType.VDW, {{opacity:0.5, color:'gold'}}, {{resi:[{indices}]}});\n"
    
    script_url = 'https://3Dmol.org/build/3Dmol-min.js' if engine_type == "3Dmol" else 'https://unpkg.com/ngl@2.0.0-dev.37/dist/ngl.js'
    container_id = "mol-container" if engine_type == "3Dmol" else "ngl-container"
    
    init_logic = f"""
        const v = $3Dmol.createViewer(el, {{backgroundColor: '#000'}});
        v.addModel(`{pdb_safe}`, "pdb");
        v.setStyle({{}}, {{cartoon: {{color: 'spectrum', thickness: 0.6}}}});
        {pockets_js}
        v.zoomTo(); v.render(); v.animate({{loop: "backAndForth", step: 0.5}});
    """ if engine_type == "3Dmol" else f"""
        const s = new NGL.Stage("{container_id}", {{backgroundColor: "black"}});
        const b = new Blob([`{pdb_safe}`], {{type: 'text/plain'}});
        s.loadFile(b, {{ext: "pdb"}}).then(o => {{ o.addRepresentation("cartoon", {{color: "resname"}}); o.autoView(); }});
    """

    return f"""
    <div id="{container_id}" style="height: 600px; width: 100%; border-radius: 20px; background: #000;"></div>
    <script>
        (function() {{
            const el = document.getElementById('{container_id}');
            if (!el) return;
            const lib = "{'3Dmol' if engine_type == '3Dmol' else 'NGL'}";
            if (!window[lib]) {{
                const s = document.createElement('script');
                s.src = '{script_url}';
                s.onload = () => {{ /* trigger re-init */ }};
                document.head.appendChild(s);
            }}
            setTimeout(() => {{ {init_logic} }}, 500);
        }})();
    </script>
    """

def run_nrc_pipeline(seq, viewer_type):
    logs = [f"[{pd.Timestamp.now().strftime('%H:%M:%S')}] INITIALIZING..."]
    try:
        seq = seq.strip().upper()
        if not seq: return [None]*11 + ["[ERROR] EMPTY SEQUENCE"]
        frames = list(engine.fold_sequence(seq))
        final = frames[-1]
        coords = final["coords"]
        analysis = BiophysicsSuite.analyze_sequence(seq, coords)
        meta = {"hash": ReportingSuite.generate_share_hash(seq), "avg_confidence": float(np.mean(final["confidence"])), "ttt_stability": float(final["stability"])}
        pdb_text = ReportingSuite.generate_pdb(seq, coords)
        viewer_html = get_viewer_html(pdb_text, viewer_type, analysis["pockets"][:1])
        l_fig = go.Figure(data=[go.Scatter3d(x=coords[:,0], y=coords[:,1], z=coords[:,2], mode='lines+markers', marker=dict(size=4, color=final["confidence"], colorscale='Viridis'))])
        l_fig.update_layout(template="plotly_dark", margin=dict(l=0,r=0,b=0,t=0))
        r_fig = px.scatter(x=analysis["ramachandran"]["phi"], y=analysis["ramachandran"]["psi"], title="Ramachandran Projection").update_layout(template="plotly_dark")
        h_fig = go.Figure(data=go.Bar(y=analysis["hydropathy"])).update_layout(template="plotly_dark", title="Hydropathy")
        c_fig = go.Figure(data=go.Bar(y=analysis["charge"])).update_layout(template="plotly_dark", title="Charge")
        summary_df = pd.DataFrame([["Residues", len(seq)], ["Confidence", f"{meta['avg_confidence']:.2f}%"], ["pI", analysis['pI']], ["Hash", meta["hash"]]], columns=["Metric", "Value"])
        zip_path = ReportingSuite.create_research_package(f"nrc_{meta['hash']}", seq, coords, analysis, meta)
        logs.append(f"[OK] FOLDING COMPLETE. STABILITY: {meta['ttt_stability']:.4f}")
        return viewer_html, l_fig, r_fig, h_fig, c_fig, summary_df, zip_path, pdb_text, "".join(analysis["dssp"]), analysis["pI"], meta["hash"], "\n".join(logs)
    except Exception as e: return [None]*11 + [f"[ERROR] {str(e)}"]

def fetch_pdb_logic(pdb_id):
    pdb_id = pdb_id.strip().upper()
    if len(pdb_id) != 4: return "", "[ERROR] INVALID ID"
    try:
        r = requests.get(f"https://www.rcsb.org/fasta/entry/{pdb_id}", timeout=5)
        if r.status_code == 200:
            seq = "".join(l.strip() for l in r.text.splitlines() if not l.startswith(">"))
            return seq, f"[OK] FETCHED {pdb_id}"
        return "", "[ERROR] NOT FOUND"
    except Exception as e: return "", f"[ERROR] {e}"

with gr.Blocks(css=CSS, title="Resonance-Fold Pro") as demo:
    with gr.Column(elem_classes="main-header"):
        gr.HTML("<h1>RESONANCE-FOLD PRO</h1>")
        gr.Markdown("Institutional 256D φ-Lattice Protein Folding Platform • v2.6.2")

    with gr.Row():
        with gr.Column(scale=1):
            with gr.Column(elem_classes="premium-card"):
                gr.Markdown("### 🛠 Structural Input")
                with gr.Row():
                    pdb_search = gr.Textbox(label="RCSB PDB ID", placeholder="1AIE")
                    pdb_btn = gr.Button("🔍 FETCH", size="sm")
                seq_input = gr.Textbox(label="Sequence", lines=6)
                with gr.Row():
                    lib_select = gr.Dropdown(choices=list(PROTEIN_LIBRARY.keys()), label="Prototypes")
                    viewer_type = gr.Radio(["3Dmol", "NGL"], label="Visualizer", value="3Dmol")
                fold_btn = gr.Button("EXECUTE QUANTUM FOLDING", variant="primary")
            
            with gr.Column(elem_classes="premium-card"):
                gr.Markdown("### 🧬 Mutation Lab")
                with gr.Row():
                    m_pos = gr.Number(label="Pos", value=1)
                    m_aa = gr.Dropdown(choices=list("ACDEFGHIKLMNPQRSTVWY"), label="AA", value="A")
                mut_btn = gr.Button("SIMULATE MUTATION")
                mut_out = gr.Textbox(label="ΔΔG Report")

        with gr.Column(scale=2):
            with gr.Tabs():
                with gr.Tab("🔭 3D Structural Manifold"):
                    viewer_box = gr.HTML("<div style='height: 600px; background:#000;'></div>")
                    log_box = gr.Textbox(label="Lattice Console", lines=4, elem_classes="log-console")
                with gr.Tab("📈 Analytical Resonance"):
                    with gr.Row():
                        summary_table = gr.Dataframe()
                        rama_plot = gr.Plot()
                    with gr.Row():
                        h_plot = gr.Plot(); ch_plot = gr.Plot()
                    dssp_out = gr.Textbox(label="DSSP"); pi_out = gr.Label(label="pI"); hash_out = gr.Label(label="Hash")
                with gr.Tab("🌌 Lattice Explorer"): l_plot = gr.Plot()
                with gr.Tab("📥 Research Export"):
                    export_zip = gr.File(); pdb_code = gr.Code(language="markdown")
                with gr.Tab("📚 Documentation"): gr.Markdown("### NRC Protocol\nInstitutional-grade folding manifold.")

    # --- Events ---
    lib_select.change(lambda x: PROTEIN_LIBRARY.get(x, ""), inputs=lib_select, outputs=seq_input)
    pdb_btn.click(fetch_pdb_logic, inputs=pdb_search, outputs=[seq_input, log_box], api_name=False)
    mut_btn.click(lambda s, p, a: f"ΔΔG: {BiophysicsSuite.simulate_mutation(s, int(p), a)['estimated_ddg']}", [seq_input, m_pos, m_aa], mut_out)
    fold_btn.click(run_nrc_pipeline, [seq_input, viewer_type], [viewer_box, l_plot, rama_plot, h_plot, ch_plot, summary_table, export_zip, pdb_code, dssp_out, pi_out, hash_out, log_box])

if __name__ == "__main__":
    demo.launch()
