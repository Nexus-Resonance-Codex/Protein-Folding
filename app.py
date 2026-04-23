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
from datetime import datetime

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

engine = NRCEngine()

from protein_library import PROTEIN_LIBRARY

# --- Aesthetics ───────────────────────────────────────────────────────────────

RESONANCE_THEME = gr.themes.Default(
    primary_hue="amber",
    neutral_hue="zinc",
).set(
    body_background_fill="#0A0A0A",
    block_background_fill="#111111",
    block_border_width="1px",
    button_primary_background_fill="#D4AF37",
    button_primary_text_color="#000000"
)

RESONANCE_CSS = r"""
:root { --nrc-gold: #D4AF37; --nrc-obsidian: #0A0A0A; --nrc-green: #00FF88; }
body { background-color: var(--nrc-obsidian); }
.main-header { background: #000; padding: 2rem; border-bottom: 2px solid var(--nrc-gold); text-align: center; }
.main-header h1 { color: var(--nrc-gold) !important; letter-spacing: 4px; font-weight: 900; }
.premium-card { background: rgba(20,20,20,0.8) !important; border: 1px solid #222 !important; border-radius: 20px !important; padding: 1.5rem !important; margin-bottom: 1rem; }
.log-console { background: #000 !important; color: var(--nrc-green) !important; font-family: 'JetBrains Mono', monospace !important; border: 1px solid #333 !important; }
.stat-box { text-align: center; border-right: 1px solid #333; padding: 10px; }
.stat-box:last-child { border-right: none; }
button.primary { background: linear-gradient(90deg, #B8860B, #D4AF37) !important; color: #000 !important; font-weight: 700 !important; border-radius: 16px !important; border: none !important; }
button.secondary { background: #1a1a1b !important; color: var(--nrc-gold) !important; border: 1px solid var(--nrc-gold) !important; border-radius: 12px !important; }
.nrc-viewer { border-radius: 20px; box-shadow: 0 0 40px rgba(212, 175, 55, 0.1); }
.tabs { background: transparent !important; border: none !important; }
"""

def get_viewer_html(pdb_str, engine_type="3Dmol", pockets=None):
    pdb_safe = pdb_str.replace("`", "\\`").replace("$", "\\$").replace("\n", "\\n")
    pockets_js = ""
    if engine_type == "3Dmol" and pockets:
        for p in pockets:
            indices = ",".join(map(str, [i+1 for i in p["residues"]]))
            pockets_js += f"viewer.addSurface($3Dmol.SurfaceType.VDW, {{opacity:0.6, color:'#D4AF37'}}, {{resi:[{indices}]}});\n"
    
    container_id = f"nrc-manifold-{int(datetime.now().timestamp() * 1000)}"
    line_count = pdb_str.count("\n")
    est_residues = line_count / 10
    
    style_js = "{cartoon: {color: 'spectrum', thickness: 0.8, arrows: true}}"
    if est_residues > 5000:
        style_js = "{line: {color: 'spectrum', linewidth: 2}}"
    if est_residues > 20000:
        style_js = "{trace: {color: 'spectrum', thickness: 1.0}}"

    if engine_type == "NGL":
        return f"""
        <div id="{container_id}" style="height: 600px; width: 100%; border-radius: 20px; background: #000; border: 1px solid #333;"></div>
        <script>
            (function() {{
                const initNGL = () => {{
                    const el = document.getElementById('{container_id}');
                    if (!el) return;
                    if (typeof NGL === 'undefined') {{
                        setTimeout(initNGL, 200);
                        return;
                    }}
                    el.innerHTML = "";
                    const stage = new NGL.Stage('{container_id}', {{backgroundColor: 'black'}});
                    const blob = new Blob([`{pdb_safe}`], {{type: 'text/plain'}});
                    stage.loadFile(blob, {{ext: 'pdb'}}).then(function(o) {{
                        o.addRepresentation("cartoon", {{color: "resname"}});
                        o.autoView();
                    }});
                }};
                initNGL();
            }})();
        </script>
        """

    return f"""
    <div id="{container_id}" class="nrc-viewer" style="height: 600px; width: 100%; border-radius: 20px; background: #000; overflow: hidden; border: 1px solid #333;"></div>
    <script>
        (function() {{
            let retry = 0;
            const render = () => {{
                const el = document.getElementById('{container_id}');
                if (!el) return;
                if (typeof $3Dmol === 'undefined') {{
                    if (retry++ < 50) setTimeout(render, 200);
                    return;
                }}
                el.innerHTML = "";
                const viewer = $3Dmol.createViewer(el, {{backgroundColor: '#000'}});
                viewer.addModel(`{pdb_safe}`, "pdb");
                viewer.setStyle({{}}, {style_js});
                {pockets_js}
                viewer.zoomTo();
                viewer.render();
                // Periodic re-render for HF stability
                setTimeout(() => {{ if(viewer) {{ viewer.zoomTo(); viewer.render(); }} }}, 500);
            }};
            render();
        }})();
    </script>
    """

def query_esmfold(sequence):
    """Queries the ESMFold-v1 API for zero-shot protein structure prediction."""
    token = os.getenv("HF_TOKEN")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    api_url = "https://api-inference.huggingface.co/models/facebook/esmfold-v1"
    
    try:
        response = requests.post(api_url, headers=headers, json={"inputs": sequence}, timeout=60)
        if response.status_code == 200:
            return response.text
        return None
    except Exception:
        return None

def parse_pdb_coords(pdb_str):
    """Extracts C-alpha coordinates and pLDDT from a PDB string."""
    coords = []
    plddt = []
    for line in pdb_str.splitlines():
        if line.startswith("ATOM") and " CA " in line:
            try:
                x = float(line[30:38])
                y = float(line[38:46])
                z = float(line[46:54])
                conf = float(line[60:66])
                coords.append([x, y, z])
                plddt.append(conf)
            except ValueError:
                continue
    return np.array(coords), np.array(plddt)

def run_nrc_pipeline(seq, viewer_type, folding_mode):
    logs = [f"[{datetime.now().strftime('%H:%M:%S')}] INITIALIZING {folding_mode.upper()} PIPELINE..."]
    try:
        seq = seq.strip().upper().replace("\n", "").replace(" ", "")
        if not seq: return [None]*16 + ["[ERROR] EMPTY SEQUENCE"]
        
        coords = None
        confidence = None
        templates = None
        
        if folding_mode in ["ESMFold (AI Only)", "Hybrid (AI + NRC)"]:
            logs = [f"[{datetime.now().strftime('%H:%M:%S')}] QUERYING ESMFOLD API (Hugging Face Manifold)..."]
            esm_pdb = query_esmfold(seq)
            if esm_pdb:
                esm_coords, esm_plddt = parse_pdb_coords(esm_pdb)
                if len(esm_coords) == len(seq):
                    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] ESMFOLD DATA ACQUIRED. Resonance Sync Success.")
                    if folding_mode == "ESMFold (AI Only)":
                        coords = esm_coords
                        confidence = esm_plddt
                    else:
                        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] INTEGRATING AI SEED INTO NRC LATTICE (Hybrid Projection)...")
                        templates = {i: c for i, c in enumerate(esm_coords)}
                else:
                    logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [WARN] ESMFOLD MISMATCH ({len(esm_coords)} vs {len(seq)}). FALLING BACK TO NRC PURE MATH.")
            else:
                logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] [WARN] ESMFOLD API UNAVAILABLE / UNAUTHORIZED. FALLING BACK TO NRC PURE MATH.")

        # Run NRC Math Engine (as primary or refinement)
        if coords is None:
            logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] INITIATING 2048D PHI-LATTICE FOLDING ENGINE...")
            frames = list(engine.fold_sequence(seq, templates=templates))
            final = frames[-1]
            coords = final["coords"]
            confidence = final["confidence"]
        
        # Biophysics Analysis
        analysis = BiophysicsSuite.analyze_sequence(seq, coords, confidence)
        
        # Metadata and Reporting
        meta = {
            "hash": ReportingSuite.generate_share_hash(seq), 
            "avg_confidence": float(np.mean(confidence)), 
            "ttt_stability": float(analysis.get("ttt_stability", 7.0)),
            "folding_mode": folding_mode
        }
        
        pdb_text = ReportingSuite.generate_pdb(seq, coords, confidence)
        viewer_html = get_viewer_html(pdb_text, viewer_type, analysis["pockets"][:1])
        
        # --- Plotly Visualizations (Defensive Alignment) ----------------------
        def align_arrays(x, y):
            x = np.array(x)
            y = np.array(y)
            min_len = min(len(x), len(y))
            return x[:min_len], y[:min_len]

        # Adaptive Sub-sampling for Plotly Performance
        stride = 1
        if len(seq) > 5000: stride = int(len(seq) / 5000) + 1
        
        # Aligned indices for sub-sampling
        indices = np.arange(0, len(seq), stride)

        # 3D Lattice Projection (Sub-sampled)
        l_x, l_conf = align_arrays(coords[indices, 0], confidence[indices])
        l_y, _ = align_arrays(coords[indices, 1], confidence[indices])
        l_z, _ = align_arrays(coords[indices, 2], confidence[indices])
        
        l_fig = go.Figure(data=[go.Scatter3d(
            x=l_x, y=l_y, z=l_z, 
            mode='lines+markers', 
            marker=dict(size=4 if stride == 1 else 2, color=l_conf, colorscale='Viridis', showscale=True, colorbar=dict(title="pLDDT")),
            line=dict(color='#D4AF37', width=3 if stride == 1 else 1)
        )])
        l_fig.update_layout(template="plotly_dark", scene=dict(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False), margin=dict(l=0,r=0,b=0,t=0), title=f"3D Structural Geometry {'(Sub-sampled)' if stride > 1 else ''}")

        # 2048D φ-Manifold Projection (Sub-sampled)
        m_coords = analysis["phi_manifold"]
        m_x, m_conf = align_arrays(m_coords[indices, 0], confidence[indices])
        m_y, _ = align_arrays(m_coords[indices, 1], confidence[indices])
        m_z, _ = align_arrays(m_coords[indices, 2], confidence[indices])
        
        m_fig = go.Figure(data=[go.Scatter3d(
            x=m_x, y=m_y, z=m_z,
            mode='lines+markers',
            marker=dict(size=3 if stride == 1 else 1, color=m_conf, colorscale='Magma', showscale=True, colorbar=dict(title="Resonance")),
            line=dict(color='#00FF88', width=2 if stride == 1 else 0.5, dash='dot')
        )])
        m_fig.update_layout(template="plotly_dark", scene=dict(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False), margin=dict(l=0,r=0,b=0,t=0), title=f"2048D φ-Spiral Projection {'(Sub-sampled)' if stride > 1 else ''}")
        
        # Ramachandran (Aligned)
        phi, psi = align_arrays(analysis["ramachandran"]["phi"], analysis["ramachandran"]["psi"])
        r_fig = px.scatter(x=phi, y=psi, labels={'x': 'Phi', 'y': 'Psi'}, title="Ramachandran Projection")
        r_fig.update_layout(template="plotly_dark", shapes=[dict(type="rect", x0=-180, y0=-180, x1=180, y1=180, line=dict(color="#333"))])
        
        # Confidence (Aligned to Indices)
        conf_x = list(range(1, len(confidence) + 1))
        conf_fig = go.Figure(data=go.Scatter(x=conf_x, y=confidence, mode='lines+markers', line=dict(color='#00FF88'), fill='tozeroy'))
        conf_fig.update_layout(template="plotly_dark", title="Per-Residue Confidence (pLDDT)", xaxis_title="Residue Index", yaxis_title="Score")
        
        # Biophysical Profiles
        h_y = analysis["hydropathy"]
        c_y = analysis["charge"]
        h_fig = go.Figure(data=go.Bar(y=h_y, marker_color='#3498db')).update_layout(template="plotly_dark", title="Hydropathy Profile")
        c_fig = go.Figure(data=go.Bar(y=c_y, marker_color='#e74c3c')).update_layout(template="plotly_dark", title="Charge Distribution")
        
        # Summary Data
        summary_df = pd.DataFrame([
            ["Residues", len(seq)], 
            ["Avg Confidence", f"{meta['avg_confidence']:.2f}%"], 
            ["TTT Stability", f"{meta['ttt_stability']:.4f}"],
            ["Folding Mode", folding_mode],
            ["Lattice Hash", meta["hash"]]
        ], columns=["Metric", "Value"])
        
        # Generate Export Package
        zip_path = ReportingSuite.create_research_package(f"nrc_{meta['hash']}", seq, coords, confidence, analysis, meta)
        
        logs.append(f"[OK] FOLDING COMPLETE. MODE: {folding_mode} | NODES: {len(seq)}")
        return [
            "\n".join(logs), l_fig, m_fig, r_fig, h_fig, c_fig, conf_fig, 
            summary_df, zip_path, pdb_text, "".join(analysis["dssp"]), 
            analysis["pI"], meta["hash"], coords, analysis, meta, 
            gr.update(selected="results_tab") 
        ]
    except Exception as e: 
        import traceback
        logs.append(f"[FATAL] {str(e)}")
        return ["\n".join(logs)] + [None]*12 + [None, None, None, gr.update()]


def fetch_pdb_logic(query):
    query = query.strip()
    if not query: return "", "[ERROR] QUERY REQUIRED", gr.update(choices=[])
    try:
        import re
        # 1. Direct PDB ID Match
        if re.match(r"^[0-9][A-Za-z0-9]{3}$", query):
            pdb_id = query.upper()
            # Try polymer_entity first
            url = f"https://data.rcsb.org/rest/v1/core/polymer_entity/{pdb_id}/1"
            r = requests.get(url)
            if r.status_code == 200:
                seq = r.json().get("entity_poly", {}).get("pdbx_seq_one_letter_code_can", "")
                if seq:
                    return seq, f"[OK] FETCHED {pdb_id}", gr.update(choices=[pdb_id], value=pdb_id)
            
            # Fallback to entry
            url_entry = f"https://data.rcsb.org/rest/v1/core/entry/{pdb_id}"
            re_entry = requests.get(url_entry)
            if re_entry.status_code == 200:
                return "", f"[OK] FOUND ENTRY {pdb_id}. SELECT ENTITY BELOW.", gr.update(choices=[pdb_id], value=pdb_id)
        
        # 2. Keyword Search API
        search_url = "https://search.rcsb.org/rcsbsearch/v2/query"
        search_query = {
            "query": {
                "type": "group",
                "logical_operator": "and",
                "nodes": [
                    {"type": "terminal", "service": "full_text", "parameters": {"value": query}},
                    {"type": "terminal", "service": "text", "parameters": {"attribute": "rcsb_entry_info.selected_polymer_entity_types", "operator": "exact_match", "value": "Protein (only)"}}
                ]
            },
            "return_type": "entry",
            "request_options": {"paginate": {"start": 0, "rows": 15}}
        }
        sr = requests.post(search_url, json=search_query)
        if sr.status_code == 200:
            results = sr.json().get("result_set", [])
            ids = [res["identifier"] for res in results]
            if ids:
                return "", f"[OK] FOUND {len(ids)} MATCHES. SELECT ONE TO LOAD SEQUENCE.", gr.update(choices=ids, interactive=True)
        return "", f"[ERROR] NO MATCHES FOR '{query}'", gr.update(choices=[])
    except Exception as e: return "", f"[FATAL] SEARCH FRACTURE: {e}", gr.update(choices=[])

def on_select_pdb(pdb_id):
    if not pdb_id: return ""
    try:
        url = f"https://data.rcsb.org/rest/v1/core/polymer_entity/{pdb_id}/1"
        r = requests.get(url)
        if r.status_code == 200:
            return r.json().get("entity_poly", {}).get("pdbx_seq_one_letter_code_can", "")
    except: pass
    return ""

def handle_mutation(seq, pos, aa, coords):
    if coords is None: return "[ERROR] PLEASE FOLD PROTEIN FIRST"
    try:
        res = BiophysicsSuite.simulate_mutation(seq, int(pos)-1, aa, coords)
        return f"Mutation: {res['mutation']}\nΔΔG Estimate: {res['estimated_ddg']} kcal/mol\nStability: {res['stability']}\nContext: {res['context']}"
    except Exception as e: return f"[ERROR] {e}"

# Define head scripts for global manifold availability
head_scripts = """
<script src="https://cdnjs.cloudflare.com/ajax/libs/3Dmol/2.0.4/3Dmol-min.js"></script>
<script src="https://unpkg.com/ngl@2.0.0-dev.37/dist/ngl.js"></script>
"""

with gr.Blocks(title="Resonance-Fold Pro") as demo:
    # State Manifolds
    coords_state = gr.State()
    analysis_state = gr.State()
    meta_state = gr.State()

    with gr.Column(elem_classes="main-header"):
        gr.HTML("""
            <div style="text-align: center;">
                <h1>RESONANCE-FOLD PRO</h1>
                <p style="color: #888; text-transform: uppercase; letter-spacing: 2px;">Advanced 2048D φ-Lattice Protein Folding Platform • v2.9.0 • 77,777 Residue Ready</p>
            </div>
        """)

    with gr.Row():
        with gr.Column(scale=1):
            with gr.Column(elem_classes="premium-card"):
                gr.Markdown("### Sequence Input & Configuration")
                with gr.Row():
                    pdb_search = gr.Textbox(label="RCSB Search (ID or Keyword)", placeholder="e.g., Spike, 1AIE")
                    pdb_results = gr.Dropdown(label="Search Results", choices=[], interactive=False)
                    pdb_btn = gr.Button("SEARCH", variant="secondary")
                seq_input = gr.Textbox(label="Primary Amino Acid Sequence", lines=5, placeholder="MTVKV...")
                with gr.Row():
                    lib_select = gr.Dropdown(
                        choices=list(PROTEIN_LIBRARY.keys()), 
                        label="Reference IDP Library (DisProt Curated)",
                        info="Select a medically impactful disordered protein to load its sequence."
                    )
                    folding_mode = gr.Dropdown(
                        label="Folding Engine Mode", 
                        choices=["NRC Pure Math", "ESMFold (AI Only)", "Hybrid (AI + NRC)"], 
                        value="Hybrid (AI + NRC)",
                        info="Pure Math: 100% deterministic NRC logic | Hybrid: AI-seeded lattice resonance."
                    )
                    viewer_type = gr.Radio(["3Dmol", "NGL"], label="Visualizer Engine", value="3Dmol")
                fold_btn = gr.Button("Predict Protein Structure", variant="primary", elem_classes="primary")


            with gr.Column(elem_classes="premium-card"):
                gr.Markdown("### Mutation Analysis (ΔΔG)")
                with gr.Row():
                    m_pos = gr.Number(label="Pos", value=1, precision=0)
                    m_aa = gr.Dropdown(choices=list("ACDEFGHIKLMNPQRSTVWY"), label="AA", value="A")
                mut_btn = gr.Button("SIMULATE MUTATION", variant="secondary")
                mut_out = gr.Textbox(label="Mutation Result (ΔΔG)", lines=4, elem_classes="log-console")

        with gr.Column(scale=2):
            with gr.Tabs(elem_classes="tabs") as tabs_manifold:
                # with gr.Tab("3D Structure Viewer", id="viewer_tab"):
                
                with gr.Tab("Structure Log", id="log_tab"):
                    status_log = gr.Textbox(label="Engine Process Log", lines=10, elem_classes="log-console")
                
                with gr.Tab("Manifold Projection", id="lattice_tab"): 
                    with gr.Row():
                        l_plot = gr.Plot(label="3D Topology")
                        m_plot = gr.Plot(label="2048D Projection")
                
                with gr.Tab("Biophysical Analytics", id="results_tab"):
                    with gr.Row():
                        summary_table = gr.Dataframe(label="Lattice Summary")
                        rama_plot = gr.Plot(label="Ramachandran")
                    with gr.Row():
                        conf_plot = gr.Plot(label="Confidence Profile (pLDDT)")
                    with gr.Row():
                        h_plot = gr.Plot(label="Hydropathy Profile")
                        ch_plot = gr.Plot(label="Charge Profile")
                    with gr.Row():
                        dssp_out = gr.Textbox(label="DSSP Analysis")
                        pi_out = gr.Label(label="pI")
                        hash_out = gr.Label(label="Manifold Hash")
                
                with gr.Tab("Research Export"):
                    with gr.Row():
                        export_zip = gr.File(label="Download Research Package (.zip)")
                        pdb_code = gr.Code(label="PDB Source", language="markdown")

    # --- Events ---
    pdb_btn.click(fetch_pdb_logic, inputs=pdb_search, outputs=[seq_input, status_log, pdb_results])
    pdb_results.change(on_select_pdb, inputs=pdb_results, outputs=seq_input)
    lib_select.change(lambda x: PROTEIN_LIBRARY.get(x, ""), inputs=lib_select, outputs=seq_input)
    
    mut_btn.click(handle_mutation, inputs=[seq_input, m_pos, m_aa, coords_state], outputs=mut_out)
    
    fold_btn.click(
        run_nrc_pipeline, 
        inputs=[seq_input, viewer_type, folding_mode], 
        outputs=[
            status_log, l_plot, m_plot, rama_plot, h_plot, ch_plot, conf_plot, 
            summary_table, export_zip, pdb_code, dssp_out, pi_out, hash_out,
            coords_state, analysis_state, meta_state, tabs_manifold
        ]
    )


if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0", 
        server_port=7860, 
        show_error=True,
        allowed_paths=["."],
        theme=RESONANCE_THEME,
        css=RESONANCE_CSS,
        head=head_scripts
    )
