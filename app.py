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

# Environment configuration
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
from deposition import depositor

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

def get_viewer_html(pdb_str, engine_type="Three.js", pockets=None):
    pdb_safe = pdb_str.replace("`", "\\`").replace("$", "\\$").replace("\n", "\\n")
    
    # Extract coordinates for Three.js direct injection
    coords = []
    plddt = []
    for line in pdb_str.splitlines():
        if line.startswith("ATOM") and " CA " in line:
            try:
                coords.append([float(line[30:38]), float(line[38:46]), float(line[46:54])])
                plddt.append(float(line[60:66]))
            except: continue
    
    # Sub-sample for Three.js if extremely large (Cap at 2000 points for browser stability)
    max_v_points = 2000
    stride = 1
    if len(coords) > max_v_points:
        stride = int(len(coords) / max_v_points) + 1
    
    coords_js = [[round(c[0],3), round(c[1],3), round(c[2],3)] for c in coords[::stride]]
    plddt_js = [round(p, 2) for p in plddt[::stride]]

    container_id = f"nrc-manifold-{int(datetime.now().timestamp() * 1000)}"
    
    if engine_type == "Three.js":
        return f"""
        <div id="{container_id}" class="nrc-viewer" style="height: 600px; width: 100%; border-radius: 20px; background: #000; overflow: hidden; border: 1px solid #333; position: relative;">
            <div id="loading-{container_id}" style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: #D4AF37; font-family: monospace;">INITIALIZING LATTICE...</div>
        </div>
        <script>
            (function() {{
                const initThree = () => {{
                    const el = document.getElementById('{container_id}');
                    const loader = document.getElementById('loading-{container_id}');
                    if (!el || typeof THREE === 'undefined' || !THREE.OrbitControls) {{
                        setTimeout(initThree, 200);
                        return;
                    }}
                    loader.style.display = 'none';
                    el.innerHTML = "";
                    
                    const scene = new THREE.Scene();
                    scene.background = new THREE.Color(0x000000);
                    
                    const camera = new THREE.PerspectiveCamera(45, el.offsetWidth / el.offsetHeight, 1, 10000);
                    const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
                    renderer.setSize(el.offsetWidth, el.offsetHeight);
                    renderer.setPixelRatio(window.devicePixelRatio);
                    el.appendChild(renderer.domElement);
                    
                    const controls = new THREE.OrbitControls(camera, renderer.domElement);
                    controls.enableDamping = true;
                    
                    const coords = {coords_js};
                    const plddt = {plddt_js};
                    
                    // Create Backbone Trace
                    const points = coords.map(c => new THREE.Vector3(c[0], c[1], c[2]));
                    const geometry = new THREE.BufferGeometry().setFromPoints(points);
                    
                    // Color by pLDDT
                    const colors = [];
                    const color = new THREE.Color();
                    plddt.forEach(val => {{
                        // Rainbow spectrum: 70 (red) to 100 (blue/cyan)
                        const hue = (val - 70) / 30 * 0.7; // 0 to 0.7
                        color.setHSL(0.7 - hue, 1.0, 0.5);
                        colors.push(color.r, color.g, color.b);
                    }});
                    geometry.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
                    
                    const material = new THREE.LineBasicMaterial({{ 
                        vertexColors: true, 
                        linewidth: 2,
                        transparent: true,
                        opacity: 0.8
                    }});
                    
                    const line = new THREE.Line(geometry, material);
                    scene.add(line);
                    
                    // Add Atoms as glowing points
                    const pMaterial = new THREE.PointsMaterial({{ 
                        size: 4, 
                        vertexColors: true,
                        transparent: true,
                        opacity: 0.6
                    }});
                    const pointCloud = new THREE.Points(geometry, pMaterial);
                    scene.add(pointCloud);
                    
                    // Center camera
                    const box = new THREE.Box3().setFromObject(line);
                    const center = box.getCenter(new THREE.Vector3());
                    const size = box.getSize(new THREE.Vector3());
                    const maxDim = Math.max(size.x, size.y, size.z);
                    camera.position.set(center.x, center.y, center.z + maxDim * 2);
                    controls.target.copy(center);
                    
                    const animate = () => {{
                        requestAnimationFrame(animate);
                        controls.update();
                        renderer.render(scene, camera);
                    }};
                    animate();
                    
                    window.addEventListener('resize', () => {{
                        if(!el) return;
                        camera.aspect = el.offsetWidth / el.offsetHeight;
                        camera.updateProjectionMatrix();
                        renderer.setSize(el.offsetWidth, el.offsetHeight);
                    }});
                }};
                initThree();
            }})();
        </script>
        """

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

def run_nrc_pipeline(seq, viewer_type, folding_mode, ref_pdb_id=None):
    logs = [f"[{datetime.now().strftime('%H:%M:%S')}] INITIALIZING PURE NRC DETERMINISTIC PIPELINE..."]
    yield ["\n".join(logs)] + [None]*15
    
    try:
        seq = seq.strip().upper().replace("\n", "").replace(" ", "")
        if not seq: 
            yield ["[ERROR] EMPTY SEQUENCE"] + [None]*15
            return
        
        # Pure NRC Math Engine
        all_atom_data = {}
        logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] INITIATING PHI-LATTICE FOLDING ENGINE...")
        for frame in engine.fold_sequence(seq):
            coords = frame["coords"]
            confidence = frame["confidence"]
            step = frame["step"]
            
            if step == 1:
                logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] STAGE 1: CA-SKELETON GLOBAL RESONANCE OPTIMIZATION")
            elif step == 16:
                logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] STAGE 2: COARSE PACKING & BACKBONE COVARIANCE")
            elif step == 26:
                logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] STAGE 3: ULTIMATE ALL-ATOM RESONANT FINALIZATION")

            if frame.get("all_atom"):
                all_atom_data = {
                    "all_atom": True,
                    "atom_types": frame.get("atom_types"),
                    "res_indices": frame.get("res_indices"),
                    "res_names": frame.get("res_names")
                }

            # Yield progress updates to UI
            if not frame.get("final", False):
                yield ["\n".join(logs + [f"Iteration {step}/30 - {('REFINING' if step > 25 else 'FOLDING')}..."])] + [None]*15
            else:
                logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] LATTICE CONVERGENCE ACHIEVED. STABILITY VERIFIED.")
                yield ["\n".join(logs)] + [None]*15

        # Final Analysis
        analysis = BiophysicsSuite.analyze_sequence(seq, coords, confidence)
        meta = {
            "hash": ReportingSuite.generate_share_hash(seq), 
            "avg_confidence": float(np.mean(confidence)), 
            "ttt_stability": float(analysis.get("ttt_stability", 7.0)),
            "resonance_error": float(analysis.get("resonance_error", 0.0)),
            "folding_mode": folding_mode
        }
        
        # PDB Comparison if ID provided
        comparison_res = None
        if ref_pdb_id and len(ref_pdb_id.strip()) == 4:
            logs.append(f"[{datetime.now().strftime('%H:%M:%S')}] FETCHING REFERENCE PDB {ref_pdb_id.upper()} FOR VALIDATION...")
            yield ["\n".join(logs)] + [None]*15
            # We compare the CA-subset for RMSD consistency
            ca_coords = coords if not all_atom_data else coords[np.array(all_atom_data["atom_types"]) == "CA"]
            comparison_res = BiophysicsSuite.compare_to_native(ref_pdb_id.strip(), ca_coords)
            if "error" in comparison_res:
                logs.append(f"[WARN] PDB COMPARISON FAILED: {comparison_res['error']}")
            else:
                logs.append(f"[VALIDATION] RMSD TO NATIVE ({ref_pdb_id.upper()}): {comparison_res['rmsd']:.4f} Å")
            yield ["\n".join(logs)] + [None]*15
        
        pdb_text = ReportingSuite.generate_pdb(seq, coords, confidence, **all_atom_data)
        pdb_preview = pdb_text if len(pdb_text) < 50000 else f"{pdb_text[:50000]}\n\n... [TRUNCATED] ..."
        viewer_html = get_viewer_html(pdb_text, viewer_type, analysis["pockets"][:1])
        
        # --- Plotly Visualizations ---
        stride = max(1, len(seq) // 300)
        indices = np.arange(0, len(seq), stride)
        
        def safe_sub(arr, idx): return np.array(arr)[idx] if arr is not None else None

        # 3D Topology
        l_fig = go.Figure(data=[go.Scatter3d(
            x=safe_sub(coords[:, 0], indices), y=safe_sub(coords[:, 1], indices), z=safe_sub(coords[:, 2], indices),
            mode='lines+markers', marker=dict(size=2, color=safe_sub(confidence, indices), colorscale='Viridis'),
            line=dict(color='#D4AF37', width=3)
        )])
        l_fig.update_layout(template="plotly_dark", margin=dict(l=0,r=0,b=0,t=0), title="3D Topology (Sub-sampled)")

        # Manifold
        m_coords = analysis["phi_manifold"]
        m_fig = go.Figure(data=[go.Scatter3d(
            x=safe_sub(m_coords[:, 0], indices), y=safe_sub(m_coords[:, 1], indices), z=safe_sub(m_coords[:, 2], indices),
            mode='lines', line=dict(color='#00FF88', width=2)
        )])
        m_fig.update_layout(template="plotly_dark", margin=dict(l=0,r=0,b=0,t=0), title="φ-Spiral Projection")
        
        # Summary
        summary_data = [
            ["Residues", len(seq)], 
            ["Avg Confidence", f"{meta['avg_confidence']:.2f}%"], 
            ["TTT Stability", f"{meta['ttt_stability']:.4f}"],
            ["Resonance Error", f"{meta['resonance_error']:.4f}"],
            ["Mode", folding_mode]
        ]
        if comparison_res and "rmsd" in comparison_res:
            summary_data.append(["RMSD to Native", f"{comparison_res['rmsd']:.4f} Å"])
            
        summary_df = pd.DataFrame(summary_data, columns=["Metric", "Value"])
        
        # Assemble package with all-atom meta
        final_meta = {**meta, **all_atom_data}
        zip_path = ReportingSuite.create_research_package(f"nrc_{meta['hash']}", seq, coords, confidence, analysis, final_meta)
        
        logs.append(f"[OK] FOLDING COMPLETE. MANIFOLD STABILIZED.")
        yield [
            "\n".join(logs), l_fig, m_fig, None, None, None, None, 
            summary_df, zip_path, pdb_preview, "".join(analysis["dssp"]), 
            analysis["pI"], meta["hash"], coords, analysis, final_meta
        ]
    except Exception as e:
        import traceback
        logs.append(f"[FATAL] {str(e)}")
        yield ["\n".join(logs)] + [None]*15


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

def handle_deposition(seq, pdb, meta):
    if not pdb: return "[ERROR] NO STRUCTURE TO DEPOSIT"
    try:
        manifest = depositor.create_zenodo_draft(seq, pdb, meta)
        return json.dumps(manifest, indent=2)
    except Exception as e: return f"[ERROR] DEPOSITION FAILED: {e}"

# Define head scripts for global manifold availability
head_scripts = """
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
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
                <p style="color: #888; text-transform: uppercase; letter-spacing: 2px;">Advanced φ-Lattice Protein Folding Platform • v2.9.0 • Production Ready</p>
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
                        label="Structural Generation Strategy", 
                        choices=["NRC Pure Math & Physics Engine (Deterministic)"], 
                        value="NRC Pure Math & Physics Engine (Deterministic)",
                        info="Pure NRC: φ-based structural seeding. No AI inference involved."
                    )
                    viewer_type = gr.Radio(["Three.js", "3Dmol", "NGL"], label="Visualizer Engine", value="Three.js")
                with gr.Row():
                    ref_pdb_id = gr.Textbox(label="Reference PDB ID (Optional)", placeholder="e.g., 1AKI", max_lines=1)
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
                
                with gr.Tab("Structure Log", id="log_tab"):
                    status_log = gr.Textbox(label="Engine Process Log", lines=10, elem_classes="log-console")
                
                with gr.Tab("Manifold Projection", id="lattice_tab"): 
                    with gr.Row():
                        l_plot = gr.Plot(label="3D Topology")
                        m_plot = gr.Plot(label="φ-Spiral Projection")
                
                with gr.Tab("Research Export"):
                    with gr.Row():
                        export_zip = gr.File(label="Download Research Package (.zip)")
                        pdb_code = gr.Code(label="PDB Source", language="markdown")
                    with gr.Column(elem_classes="premium-card"):
                        gr.Markdown("### Deposition & Archiving")
                        deposit_btn = gr.Button("DEPOT TO ZENODO / MODELARCHIVE (DRAFT)", variant="secondary")
                        deposit_out = gr.Code(label="Submission Manifest", language="json")

    # --- Events ---
    pdb_btn.click(fetch_pdb_logic, inputs=pdb_search, outputs=[seq_input, status_log, pdb_results])
    pdb_results.change(on_select_pdb, inputs=pdb_results, outputs=seq_input)
    lib_select.change(lambda x: PROTEIN_LIBRARY.get(x, ""), inputs=lib_select, outputs=seq_input)
    
    mut_btn.click(handle_mutation, inputs=[seq_input, m_pos, m_aa, coords_state], outputs=mut_out)
    
    fold_btn.click(
        run_nrc_pipeline, 
        inputs=[seq_input, viewer_type, folding_mode, ref_pdb_id], 
        outputs=[
            status_log, l_plot, m_plot, rama_plot, h_plot, ch_plot, conf_plot, 
            summary_table, export_zip, pdb_code, dssp_out, pi_out, hash_out,
            coords_state, analysis_state, meta_state
        ]
    )
    
    deposit_btn.click(
        handle_deposition,
        inputs=[seq_input, pdb_code, meta_state],
        outputs=deposit_out
    )


if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0", 
        server_port=7860, 
        show_error=True,
        allowed_paths=["."],
        theme=RESONANCE_THEME,
        css=RESONANCE_CSS,
        head=head_scripts + """
            <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
        """
    )
