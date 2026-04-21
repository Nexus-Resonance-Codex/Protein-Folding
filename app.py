import sys
try:
    import audioop
except ImportError:
    try:
        from audioop_lts import audioop
        sys.modules["audioop"] = audioop
    except ImportError:
        from unittest.mock import MagicMock
        sys.modules["audioop"] = MagicMock()

import os
import requests
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import gradio as gr
import os

# Hardened environment configuration
os.environ["MPLCONFIGDIR"] = "/tmp/matplotlib_cache"
os.environ["XDG_CACHE_HOME"] = "/tmp"

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

CSS = r"""
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
            pockets_js += f"viewer.addSurface($3Dmol.SurfaceType.VDW, {{opacity:0.6, color:'#D4AF37'}}, {{resi:[{indices}]}});\n"
    
    script_url = 'https://3Dmol.org/build/3Dmol-min.js'
    container_id = "mol-container"
    
    return f"""
    <div id="{container_id}" style="height: 600px; width: 100%; border-radius: 20px; background: #000; overflow: hidden; border: 1px solid #333;"></div>
    <script src="{script_url}"></script>
    <script>
        (function() {{
            const el = document.getElementById('{container_id}');
            if (!el) return;
            const viewer = $3Dmol.createViewer(el, {{backgroundColor: '#000'}});
            viewer.addModel(`{pdb_safe}`, "pdb");
            viewer.setStyle({{}}, {{cartoon: {{color: 'spectrum', thickness: 0.8, arrows: true}}}});
            {pockets_js}
            viewer.zoomTo();
            viewer.render();
            viewer.animate({{loop: "backAndForth", step: 0.2}});
        }})();
    </script>
    """

def run_nrc_pipeline(seq, viewer_type):
    logs = [f"[{pd.Timestamp.now().strftime('%H:%M:%S')}] INITIALIZING NRC PHI-LATTICE..."]
    try:
        seq = seq.strip().upper()
        if not seq: return [None]*12 + ["[ERROR] EMPTY SEQUENCE"]
        
        # Instantiate Engine and fold
        frames = list(engine.fold_sequence(seq))
        final = frames[-1]
        coords = final["coords"]
        confidence = final["confidence"]
        
        # Biophysics Analysis
        analysis = BiophysicsSuite.analyze_sequence(seq, coords)
        
        # Metadata and Reporting
        meta = {
            "hash": ReportingSuite.generate_share_hash(seq), 
            "avg_confidence": float(np.mean(confidence)), 
            "ttt_stability": float(final["stability"])
        }
        
        pdb_text = ReportingSuite.generate_pdb(seq, coords, confidence)
        viewer_html = get_viewer_html(pdb_text, viewer_type, analysis["pockets"][:1])
        
        # --- Plotly Visualizations (Defensive Alignment) ----------------------
        def align_arrays(x, y):
            min_len = min(len(x), len(y))
            return x[:min_len], y[:min_len]

        # 3D Lattice Projection
        l_fig = go.Figure(data=[go.Scatter3d(
            x=coords[:,0], y=coords[:,1], z=coords[:,2], 
            mode='lines+markers', 
            marker=dict(size=5, color=confidence, colorscale='Viridis', showscale=True, colorbar=dict(title="pLDDT")),
            line=dict(color='#D4AF37', width=4)
        )])
        l_fig.update_layout(template="plotly_dark", scene=dict(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False), margin=dict(l=0,r=0,b=0,t=0))
        
        # Ramachandran (Aligned)
        phi, psi = align_arrays(analysis["ramachandran"]["phi"], analysis["ramachandran"]["psi"])
        r_fig = px.scatter(x=phi, y=psi, labels={'x': 'Phi', 'y': 'Psi'}, title="Ramachandran Projection")
        r_fig.update_layout(template="plotly_dark", shapes=[dict(type="rect", x0=-180, y0=-180, x1=180, y1=180, line=dict(color="#333"))])
        
        # Confidence (Aligned to Indices)
        x_indices = list(range(1, len(confidence) + 1))
        conf_fig = go.Figure(data=go.Scatter(x=x_indices, y=confidence, mode='lines+markers', line=dict(color='#00FF88'), fill='tozeroy'))
        conf_fig.update_layout(template="plotly_dark", title="Per-Residue Confidence (pLDDT)", xaxis_title="Residue Index", yaxis_title="Score")
        
        # Biophysical Profiles
        h_fig = go.Figure(data=go.Bar(y=analysis["hydropathy"], marker_color='#3498db')).update_layout(template="plotly_dark", title="Hydropathy Profile")
        c_fig = go.Figure(data=go.Bar(y=analysis["charge"], marker_color='#e74c3c')).update_layout(template="plotly_dark", title="Charge Distribution")
        
        # Summary Data
        summary_df = pd.DataFrame([
            ["Residues", len(seq)], 
            ["Avg Confidence", f"{meta['avg_confidence']:.2f}%"], 
            ["TTT Stability", f"{meta['ttt_stability']:.4f}"],
            ["Isoelectric Point", f"{analysis['pI']:.2f}"], 
            ["Lattice Hash", meta["hash"]]
        ], columns=["Metric", "Value"])
        
        # Generate Export Package
        zip_path = ReportingSuite.create_research_package(f"nrc_{meta['hash']}", seq, coords, confidence, analysis, meta)
        
        logs.append(f"[OK] FOLDING COMPLETE. NODES: {len(seq)} | RESONANCE: {meta['ttt_stability']:.2f}")
        return viewer_html, l_fig, r_fig, h_fig, c_fig, conf_fig, summary_df, zip_path, pdb_text, "".join(analysis["dssp"]), analysis["pI"], meta["hash"], "\n".join(logs)
    except Exception as e: 
        import traceback
        logs.append(f"[FATAL] {str(e)}")
        return [None]*12 + ["\n".join(logs)]

def fetch_pdb_logic(query):
    query = query.strip()
    if not query: return "", "[ERROR] QUERY REQUIRED", gr.update(choices=[])
    
    try:
        # Regex for PDB ID (4 characters)
        import re
        if re.match(r"^[0-9][A-Za-z0-9]{3}$", query):
            pdb_id = query.upper()
            url = f"https://data.rcsb.org/rest/v1/core/polymer_entity/{pdb_id}/1"
            r = requests.get(url)
            if r.status_code == 200:
                data = r.json()
                seq = data.get("entity_poly", {}).get("pdbx_seq_one_letter_code_can", "")
                if seq:
                    return seq, f"[OK] FETCHED {pdb_id} (ENTITY 1)", gr.update(choices=[pdb_id], value=pdb_id)
        
        # Keyword Search API
        search_url = "https://search.rcsb.org/rcsbsearch/v2/query"
        search_query = {
            "query": {
                "type": "terminal",
                "service": "full_text",
                "parameters": {"value": query}
            },
            "return_type": "entry",
            "request_options": {"paginate": {"start": 0, "rows": 10}}
        }
        sr = requests.post(search_url, json=search_query)
        if sr.status_code == 200:
            results = sr.json().get("result_set", [])
            ids = [res["identifier"] for res in results]
            if ids:
                return "", f"[OK] FOUND {len(ids)} MATCHES. PLEASE SELECT FROM DROPDOWN.", gr.update(choices=ids, interactive=True)
        
        return "", f"[ERROR] NO MATCHES FOR '{query}'", gr.update(choices=[])
    except Exception as e: 
        return "", f"[FATAL] SEARCH FRACTURE: {e}", gr.update(choices=[])

def on_select_pdb(pdb_id):
    if not pdb_id: return ""
    try:
        url = f"https://data.rcsb.org/rest/v1/core/polymer_entity/{pdb_id}/1"
        r = requests.get(url)
        if r.status_code == 200:
            return r.json().get("entity_poly", {}).get("pdbx_seq_one_letter_code_can", "")
    except: pass
    return ""

with gr.Blocks(css=CSS, title="Resonance-Fold Pro") as demo:
    with gr.Column(elem_classes="main-header"):
        gr.HTML("""
            <div style="text-align: center; padding: 20px;">
                <h1 style="font-size: 3rem; margin: 0; color: #D4AF37; letter-spacing: 5px;">RESONANCE-FOLD PRO</h1>
                <p style="font-size: 1.2rem; color: #888; text-transform: uppercase;">Institutional 256D φ-Lattice Protein Folding Platform • v2.6.2</p>
            </div>
        """)

    with gr.Row():
        with gr.Column(scale=1):
            with gr.Column(elem_classes="premium-card"):
                gr.Markdown("### 🏛 Sovereign Search & Input")
                with gr.Row():
                    pdb_search = gr.Textbox(label="RCSB Search (ID or Keyword)", placeholder="e.g., Spike, 1AIE, Insulin")
                    pdb_results = gr.Dropdown(label="Search Results", choices=[], interactive=False)
                    pdb_btn = gr.Button("🔍 SEARCH", variant="secondary")
                seq_input = gr.Textbox(label="Primary Amino Acid Sequence", lines=8, placeholder="MTVKV...")
                with gr.Row():
                    lib_select = gr.Dropdown(choices=list(PROTEIN_LIBRARY.keys()), label="Institutional Prototypes")
                    viewer_type = gr.Radio(["3Dmol", "NGL"], label="Visualizer Engine", value="3Dmol")
                fold_btn = gr.Button("EXECUTE PHI-LATTICE FOLDING", variant="primary", scale=2)
            
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
                    viewer_box = gr.HTML("<div style='height: 600px; background:#000; border-radius: 20px;'></div>")
                    log_box = gr.Textbox(label="Lattice Console", lines=4, elem_classes="log-console")
                with gr.Tab("📈 Analytical Resonance"):
                    with gr.Row():
                        summary_table = gr.Dataframe(label="Lattice Summary")
                        rama_plot = gr.Plot(label="Ramachandran")
                    with gr.Row():
                        conf_plot = gr.Plot(label="Confidence Profile (pLDDT)")
                    with gr.Row():
                        h_plot = gr.Plot(label="Hydropathy Profile"); ch_plot = gr.Plot(label="Charge Profile")
                    with gr.Row():
                        dssp_out = gr.Textbox(label="DSSP Analysis"); pi_out = gr.Label(label="pI"); hash_out = gr.Label(label="Manifold Hash")
                with gr.Tab("🌌 Lattice Explorer"): 
                    l_plot = gr.Plot(label="3D Topology")
                with gr.Tab("📥 Research Export"):
                    with gr.Row():
                        export_zip = gr.File(label="Download Research Package (.zip)")
                        pdb_code = gr.Code(label="PDB Source", language="markdown")
                with gr.Tab("📚 Documentation"): 
                    gr.Markdown("""
                    ### 🏛 NRC Research Protocol
                    This platform utilizes the **φ-Infinity Lattice Projection** algorithm to resolve protein tertiary structures with institutional-grade precision.
                    
                    **Core Metrics:**
                    - **pLDDT**: Local distance difference test (Confidence). 90+ is highly accurate.
                    - **TTT-7**: Trageser Tensor Theorem stability metric.
                    - **Lattice Hash**: Unique identifier for the structural manifold resonance.
                    """)

    # --- Events ---
    lib_select.change(lambda x: PROTEIN_LIBRARY.get(x, ""), inputs=lib_select, outputs=seq_input, api_name=False)
    pdb_btn.click(fetch_pdb_logic, inputs=pdb_search, outputs=[seq_input, log_box, pdb_results], api_name=False)
    pdb_results.change(on_select_pdb, inputs=pdb_results, outputs=seq_input, api_name=False)
    mut_btn.click(lambda s, p, a: f"ΔΔG: {BiophysicsSuite.simulate_mutation(s, int(p), a)['estimated_ddg']}", [seq_input, m_pos, m_aa], mut_out, api_name=False)
    fold_btn.click(
        run_nrc_pipeline, 
        inputs=[seq_input, viewer_type], 
        outputs=[viewer_box, l_plot, rama_plot, h_plot, ch_plot, conf_plot, summary_table, export_zip, pdb_code, dssp_out, pi_out, hash_out, log_box],
        api_name=False
    )

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        show_error=True
    )
