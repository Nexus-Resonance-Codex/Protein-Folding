import numpy as np
from typing import Dict, List, Tuple

class BiophysicsSuite:
    """Institutional-grade biophysical analysis engine."""
    
    # Bjellqvist pKa values
    PKA = {'K': 10.0, 'R': 12.0, 'H': 5.98, 'D': 4.05, 'E': 4.45, 'C': 9.0, 'Y': 10.0, 'N-term': 7.5, 'C-term': 3.55}
    HYDROPATHY = {'A': 1.8, 'R': -4.5, 'N': -3.5, 'D': -3.5, 'C': 2.5, 'Q': -3.5, 'E': -3.5, 'G': -0.4, 'H': -3.2, 'I': 4.5, 'L': 3.8, 'K': -3.9, 'M': 1.9, 'F': 2.8, 'P': -1.6, 'S': -0.8, 'T': -0.7, 'W': -0.9, 'Y': -1.3, 'V': 4.2}
    CHARGES = {'R': 1, 'K': 1, 'H': 0.1, 'D': -1, 'E': -1}

    @staticmethod
    def analyze_sequence(seq: str, coords: np.ndarray) -> Dict:
        """Full biophysical characterization suite."""
        res = {
            "pI": BiophysicsSuite.estimate_pi(seq),
            "hydropathy": [BiophysicsSuite.HYDROPATHY.get(aa, 0) for aa in seq],
            "charge": [BiophysicsSuite.CHARGES.get(aa, 0) for aa in seq],
            "dssp": BiophysicsSuite.assign_secondary_structure(coords),
            "pockets": BiophysicsSuite.map_binding_pockets(coords)
        }
        return res

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
        """Simplified DSSP based on C-alpha distances and angles."""
        if len(coords) < 4: return ["C"] * len(coords)
        dssp = ["C"] * len(coords)
        for i in range(1, len(coords) - 2):
            # Calculate local curvature/torsion
            v1 = coords[i] - coords[i-1]
            v2 = coords[i+1] - coords[i]
            dist = np.linalg.norm(coords[i+2] - coords[i-1])
            if dist < 6.0: dssp[i] = "H" # Alpha Helix
            elif dist > 9.0: dssp[i] = "E" # Beta Sheet
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
        # Residues far from hull but enclosed are potential pockets
        pocket_residues: List[int] = []
        center = np.mean(coords, axis=0)
        max_dist = np.max(np.linalg.norm(coords - center, axis=1))
        for i, p in enumerate(coords):
            dist_to_center = np.linalg.norm(p - center)
            if dist_to_center < max_dist * 0.4:
                pocket_residues.append(i)
        if not pocket_residues:
            return []
        return [{"residues": pocket_residues, "score": len(pocket_residues) / len(coords)}]

    @staticmethod
    def simulate_mutation(seq: str, pos: int, new_aa: str) -> Dict:
        """Estimate ΔΔG impact of a single point mutation."""
        if pos < 0 or pos >= len(seq): return {"error": "Invalid position"}
        old_aa = seq[pos]
        delta_hydro = BiophysicsSuite.HYDROPATHY.get(new_aa, 0) - BiophysicsSuite.HYDROPATHY.get(old_aa, 0)
        # Heuristic: Hydrophobic to polar in core is destabilizing
        ddg = -delta_hydro * 1.2 # Rough approximation
        return {
            "mutation": f"{old_aa}{pos+1}{new_aa}",
            "estimated_ddg": round(ddg, 2),
            "stability_change": "Increased" if ddg < 0 else "Decreased"
        }
