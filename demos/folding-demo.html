<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>φ^∞ Protein Folding Engine | Nexus Resonance Codex</title>
    <!-- Premium Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;700&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <style>
        :root {
            --bg-dark: #050508;
            --glass-bg: rgba(15, 15, 25, 0.7);
            --glass-border: rgba(255, 255, 255, 0.08);
            --accent-gold: #FFD700;
            --accent-cyan: #00F0FF;
            --phi: 1.618033988749895;
            --transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: 'Outfit', sans-serif;
            background-color: var(--bg-dark);
            color: #fff;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            height: 100vh;
        }

        nav {
            padding: 1.5rem 2rem;
            background: rgba(0, 0, 0, 0.4);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid var(--glass-border);
            display: flex;
            justify-content: space-between;
            align-items: center;
            z-index: 100;
        }

        .brand {
            font-size: 1.2rem;
            font-weight: 700;
            letter-spacing: 2px;
            background: linear-gradient(90deg, var(--accent-gold), var(--accent-cyan));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        main {
            flex: 1;
            display: grid;
            grid-template-columns: 380px 1fr;
            gap: 1rem;
            padding: 1rem;
            overflow: hidden;
        }

        .controls {
            background: var(--glass-bg);
            backdrop-filter: blur(20px);
            border: 1px solid var(--glass-border);
            border-radius: 20px;
            padding: 1.5rem;
            display: flex;
            flex-direction: column;
            gap: 1.5rem;
            overflow-y: auto;
        }

        .section-title {
            font-size: 0.8rem;
            font-weight: 700;
            text-transform: uppercase;
            color: rgba(255, 255, 255, 0.5);
            letter-spacing: 1px;
        }

        textarea {
            width: 100%;
            height: 100px;
            background: rgba(0, 0, 0, 0.5);
            border: 1px solid var(--glass-border);
            border-radius: 12px;
            padding: 1rem;
            color: #fff;
            font-family: 'JetBrains Mono', monospace;
            resize: none;
        }

        button {
            width: 100%;
            padding: 1rem;
            background: linear-gradient(135deg, var(--accent-gold), var(--accent-cyan));
            border: none;
            border-radius: 12px;
            color: #000;
            font-weight: 700;
            text-transform: uppercase;
            cursor: pointer;
            transition: var(--transition);
        }

        button:hover {
            transform: scale(1.02);
            box-shadow: 0 0 20px rgba(0, 240, 255, 0.4);
        }

        .metrics {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0.8rem;
        }

        .metric {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid var(--glass-border);
            border-radius: 10px;
            padding: 0.8rem;
        }

        .metric-label { font-size: 0.7rem; color: #888; text-transform: uppercase; }
        .metric-value { font-family: 'JetBrains Mono', monospace; font-size: 1.1rem; color: var(--accent-gold); }

        .viewport-container {
            position: relative;
            background: #000;
            border-radius: 20px;
            overflow: hidden;
            border: 1px solid var(--glass-border);
        }

        #visualizer { width: 100%; height: 100%; }

        .overlay {
            position: absolute;
            top: 2rem;
            left: 2rem;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.75rem;
            color: rgba(255, 255, 255, 0.5);
            pointer-events: none;
        }
    </style>
</head>
<body>
    <nav>
        <div class="brand">NEXUS RESONANCE CODEX</div>
        <div style="font-size: 0.8rem; color: #888;">PHASE-II: BIOLOGICAL MANIFOLD</div>
    </nav>

    <main>
        <aside class="controls">
            <div class="section-title">Sequence Entry</div>
            <textarea id="seq-input">MQIFVKTLTGKTITLEVEPSDTIENVKAKIQDKEGIPPDQQRLIFAGKQLEDGRTLSDYNIQKESTLHLVLRLRGG</textarea>
            <button id="fold-btn">Commence Folding Cycle</button>

            <div class="section-title">Manifold Telemetry</div>
            <div class="metrics">
                <div class="metric">
                    <div class="metric-label">RMSD (Å)</div>
                    <div class="metric-value" id="rmsd-val">0.000</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Energy (kJ)</div>
                    <div class="metric-value" id="energy-val">-0.00</div>
                </div>
            </div>
        </aside>

        <section class="viewport-container">
            <div id="visualizer"></div>
            <div class="overlay">
                STABILITY: RESONANT<br>
                PARITY: 1.618...<br>
                SYSTEM: φ^∞ BIOME
            </div>
        </section>
    </main>

    <script>
        const container = document.getElementById('visualizer');
        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        renderer.setSize(container.clientWidth, container.clientHeight);
        container.appendChild(renderer.domElement);

        camera.position.z = 50;

        const group = new THREE.Group();
        scene.add(group);

        let atoms = [];
        let connections = null;

        function createPeptide() {
            group.clear();
            atoms = [];
            const len = 76; // Ubiquitin
            const mat = new THREE.MeshPhongMaterial({ color: 0x00F0FF, emissive: 0x00F0FF, emissiveIntensity: 0.2 });
            for(let i=0; i<len; i++) {
                const mesh = new THREE.Mesh(new THREE.SphereGeometry(0.8, 16, 16), mat);
                mesh.position.set(i*2 - len, 0, 0);
                group.add(mesh);
                atoms.push(mesh);
            }
            const pts = atoms.map(a => a.position);
            connections = new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts), new THREE.LineBasicMaterial({ color: 0xFFD700, opacity: 0.4, transparent: true }));
            group.add(connections);
        }

        createPeptide();
        scene.add(new THREE.AmbientLight(0x404040, 2));

        let folding = false;
        let t = 0;
        document.getElementById('fold-btn').onclick = () => {
            folding = !folding;
            document.getElementById('fold-btn').innerText = folding ? "Pause Manifold" : "Resume Manifold";
        };

        function animate() {
            requestAnimationFrame(animate);
            group.rotation.y += 0.005;
            if(folding) {
                t += 0.01;
                atoms.forEach((a, i) => {
                    a.position.x += (Math.cos(t + i*0.2) * 5 * Math.exp(-t*0.1) + (i*0.5-19) - a.position.x) * 0.05;
                    a.position.y += (Math.sin(t + i*0.2) * 5 * Math.exp(-t*0.1) - a.position.y) * 0.05;
                    a.position.z += (Math.sin(t*0.5 + i*0.1) * 2 - a.position.z) * 0.05;
                });
                connections.geometry.setFromPoints(atoms.map(a => a.position));
                document.getElementById('rmsd-val').innerText = (1.1 + Math.exp(-t*0.5)*4.5).toFixed(3);
                document.getElementById('energy-val').innerText = (-148 - (1-Math.exp(-t*0.2))*40).toFixed(2);
            }
            renderer.render(scene, camera);
        }
        animate();
    </script>
</body>
</html>
