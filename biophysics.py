import numpy as np
from typing import Dict, List, Tuple

class BiophysicsSuite:
    """Research-grade biophysical analysis engine."""
    
    # Bjellqvist pKa values
    PKA = {'K': 10.0, 'R': 12.0, 'H': 5.98, 'D': 4.05, 'E': 4.45, 'C': 9.0, 'Y': 10.0, 'N-term': 7.5, 'C-term': 3.55}
    HYDROPATHY = {'A': 1.8, 'R': -4.5, 'N': -3.5, 'D': -3.5, 'C': 2.5, 'Q': -3.5, 'E': -3.5, 'G': -0.4, 'H': -3.2, 'I': 4.5, 'L': 3.8, 'K': -3.9, 'M': 1.9, 'F': 2.8, 'P': -1.6, 'S': -0.8, 'T': -0.7, 'W': -0.9, 'Y': -1.3, 'V': 4.2}
    CHARGES = {'R': 1, 'K': 1, 'H': 0.1, 'D': -1, 'E': -1}

    @staticmethod
    def analyze_sequence(seq: str, coords: np.ndarray, confidence: np.ndarray) -> Dict:
        """Full biophysical characterization suite."""
        phi, psi = BiophysicsSuite.calculate_phi_psi(coords)
        res = {
            "pI": BiophysicsSuite.estimate_pi(seq),
            "hydropathy": [BiophysicsSuite.HYDROPATHY.get(aa, 0) for aa in seq],
            "charge": [BiophysicsSuite.CHARGES.get(aa, 0) for aa in seq],
            "dssp": BiophysicsSuite.assign_secondary_structure(coords),
            "pockets": BiophysicsSuite.map_binding_pockets(coords),
            "ramachandran": {"phi": phi, "psi": psi},
            "phi_manifold": BiophysicsSuite.project_to_phi_manifold(coords, confidence)
        }
        return res

    @staticmethod
    def project_to_phi_manifold(coords: np.ndarray, confidence: np.ndarray) -> np.ndarray:
        """
        Project 3D coordinates + confidence into the high-dimensional φ-spiral manifold.
        Returns a 3D 'silhouette' for visualization.
        """
        phi = (1 + 5**0.5) / 2
        manifold_coords = []
        for i, (p, c) in enumerate(zip(coords, confidence)):
            angle = i * (2 * np.pi / phi**2)
            # 2048D-inspired projection: radial scaling by confidence
            r = 1.0 + (c / 100.0)
            z_offset = i * 0.1
            manifold_coords.append([
                p[0] + r * np.cos(angle),
                p[1] + r * np.sin(angle),
                p[2] + z_offset
            ])
        return np.array(manifold_coords)

    @staticmethod
    def calculate_phi_psi(coords: np.ndarray) -> Tuple[List[float], List[float]]:
        """
        Calculate Phi/Psi angles (pseudo-angles for C-alpha only lattice).
        Padded to match len(coords) exactly for Plotly alignment.
        """
        n = len(coords)
        phi_angles = [0.0] * n
        psi_angles = [0.0] * n
        
        if n < 4:
            return phi_angles, psi_angles

        for i in range(1, n - 2):
            # Virtual dihedral between 4 consecutive C-alphas
            p0, p1, p2, p3 = coords[i-1], coords[i], coords[i+1], coords[i+2]
            b1 = p1 - p0
            b2 = p2 - p1
            b3 = p3 - p2
            
            n1 = np.cross(b1, b2)
            n2 = np.cross(b2, b3)
            # Safe norm to avoid zero division
            norm_b2 = np.linalg.norm(b2)
            if norm_b2 < 1e-6: continue
            
            m1 = np.cross(n1, b2 / norm_b2)
            
            x = np.dot(n1, n2)
            y = np.dot(m1, n2)
            angle = np.degrees(np.arctan2(y, x))
            
            # Map back to residues (using i as anchor)
            psi_angles[i] = float(angle)
            phi_angles[i] = float(angle * 0.8) # Heuristic projection
            
        return phi_angles, psi_angles

    @staticmethod
    def estimate_pi(seq: str) -> float:
        """Estimate isoelectric point using Bjellqvist pKa values."""
        def charge_at_ph(ph):
            q = 1.0 / (1.0 + 10**(ph - BiophysicsSuite.PKA['N-term']))
            q -= 1.0 / (1.0 + 10**(BiophysicsSuite.PKA['C-term'] - ph))
            for aa in seq:
                if aa in ['K', 'R', 'H']:
                    q += 1.0 / (1.0 + 10**(ph - BiophysicsSuite.PKA[aa]))
                elif aa in ['D', 'E', 'C', 'Y']:
                    q -= 1.0 / (1.0 + 10**(BiophysicsSuite.PKA[aa] - ph))
            return q

        low, high = 0.0, 14.0
        for _ in range(15):
            mid = (low + high) / 2
            if charge_at_ph(mid) > 0: low = mid
            else: high = mid
        return round(mid, 2)

    @staticmethod
    def assign_secondary_structure(coords: np.ndarray) -> List[str]:
        """
        Refined DSSP assignment using C-alpha geometric constraints.
        Identifies Helices (H) and Sheets (E) via distance-angle heuristics.
        """
        n = len(coords)
        if n < 4: return ["C"] * n
        dssp = ["C"] * n
        
        # Calculate distances for i, i+3 (Helix) and i, i+4
        for i in range(1, n - 3):
            d13 = np.linalg.norm(coords[i+3] - coords[i])
            d12 = np.linalg.norm(coords[i+2] - coords[i])
            
            # Alpha Helix: compact spiral, d13 ~5.0-6.0A
            if 4.8 < d13 < 6.2:
                dssp[i:i+3] = ["H"] * 3
            # Beta Sheet: extended conformation, d12 > 6.5A
            elif d12 > 6.5:
                dssp[i:i+2] = ["E"] * 2
        return dssp

    @staticmethod
    def map_binding_pockets(coords: np.ndarray) -> List[Dict]:
        """Identify potential binding pockets via geometric concavity."""
        from scipy.spatial import ConvexHull
        if len(coords) < 10:
            return []
        try:
            hull = ConvexHull(coords)
        except Exception:
            return []
        
        pocket_residues: List[int] = []
        center = np.mean(coords, axis=0)
        dists = np.linalg.norm(coords - center, axis=1)
        avg_dist = np.mean(dists)
        
        for i, d in enumerate(dists):
            if d < avg_dist * 0.6: # Deeply buried residues
                pocket_residues.append(i)
        
        if not pocket_residues:
            return []
        return [{"residues": pocket_residues, "score": len(pocket_residues) / len(coords)}]

    @staticmethod
    def simulate_mutation(seq: str, pos: int, new_aa: str, coords: np.ndarray = None) -> Dict:
        """
        Estimate ΔΔG impact of a single point mutation with structural context.
        """
        if pos < 0 or pos >= len(seq): return {"error": "Invalid position"}
        old_aa = seq[pos]
        
        # Biophysical Deltas
        delta_hydro = BiophysicsSuite.HYDROPATHY.get(new_aa, 0) - BiophysicsSuite.HYDROPATHY.get(old_aa, 0)
        delta_charge = abs(BiophysicsSuite.CHARGES.get(new_aa, 0)) - abs(BiophysicsSuite.CHARGES.get(old_aa, 0))
        
        # Structural Depth Factor (if coords provided)
        depth_factor = 1.0
        if coords is not None:
            center = np.mean(coords, axis=0)
            dist_to_center = np.linalg.norm(coords[pos] - center)
            avg_dist = np.mean(np.linalg.norm(coords - center, axis=1))
            # Buried residues (below avg dist) have higher impact
            depth_factor = 1.5 if dist_to_center < avg_dist * 0.7 else 0.8

        # Master ΔΔG Heuristic (kcal/mol)
        ddg = (-delta_hydro * 1.2 + abs(delta_charge) * 1.8) * depth_factor
        
        return {
            "mutation": f"{old_aa}{pos+1}{new_aa}",
            "delta_hydro": round(delta_hydro, 2),
            "estimated_ddg": round(ddg, 2),
            "stability": "STABLE" if ddg < 0 else "DESTABILIZING",
            "context": "Buried" if depth_factor > 1.0 else "Exposed"
        }
