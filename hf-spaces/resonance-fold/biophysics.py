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
        phi, psi = BiophysicsSuite.calculate_phi_psi(coords)
        res = {
            "pI": BiophysicsSuite.estimate_pi(seq),
            "hydropathy": [BiophysicsSuite.HYDROPATHY.get(aa, 0) for aa in seq],
            "charge": [BiophysicsSuite.CHARGES.get(aa, 0) for aa in seq],
            "dssp": BiophysicsSuite.assign_secondary_structure(coords),
            "pockets": BiophysicsSuite.map_binding_pockets(coords),
            "ramachandran": {"phi": phi, "psi": psi}
        }
        return res

    @staticmethod
    def calculate_phi_psi(coords: np.ndarray) -> Tuple[List[float], List[float]]:
        """
        Calculate Phi/Psi angles (pseudo-angles for C-alpha only lattice).
        In a full PDB these require N, CA, C, O. Here we use C-alpha virtual dihedrals.
        """
        phi_angles = [0.0]
        psi_angles = []
        
        for i in range(1, len(coords) - 2):
            # Virtual dihedral between 4 consecutive C-alphas
            p0, p1, p2, p3 = coords[i-1], coords[i], coords[i+1], coords[i+2]
            b1 = p1 - p0
            b2 = p2 - p1
            b3 = p3 - p2
            
            n1 = np.cross(b1, b2)
            n2 = np.cross(b2, b3)
            m1 = np.cross(n1, b2 / np.linalg.norm(b2))
            
            x = np.dot(n1, n2)
            y = np.dot(m1, n2)
            angle = np.degrees(np.arctan2(y, x))
            psi_angles.append(float(angle))
            phi_angles.append(float(angle * 0.8)) # Approximation for virtual lattice
            
        psi_angles.append(0.0)
        phi_angles.append(0.0)
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
        """Simplified DSSP based on C-alpha distances and angles."""
        if len(coords) < 4: return ["C"] * len(coords)
        dssp = ["C"] * len(coords)
        for i in range(1, len(coords) - 2):
            dist = np.linalg.norm(coords[i+2] - coords[i-1])
            if dist < 6.0: dssp[i] = "H" # Alpha Helix
            elif dist > 9.5: dssp[i] = "E" # Beta Sheet
            else: dssp[i] = "C"
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
    def simulate_mutation(seq: str, pos: int, new_aa: str) -> Dict:
        """Estimate ΔΔG impact of a single point mutation."""
        if pos < 0 or pos >= len(seq): return {"error": "Invalid position"}
        old_aa = seq[pos]
        # Professional-grade ΔΔG heuristic
        # Polar to non-polar in solvent-exposed region vs buried...
        # Here we use hydropathy and charge delta
        delta_hydro = BiophysicsSuite.HYDROPATHY.get(new_aa, 0) - BiophysicsSuite.HYDROPATHY.get(old_aa, 0)
        delta_charge = abs(BiophysicsSuite.CHARGES.get(new_aa, 0)) - abs(BiophysicsSuite.CHARGES.get(old_aa, 0))
        
        ddg = -delta_hydro * 1.5 + abs(delta_charge) * 2.0
        
        return {
            "mutation": f"{old_aa}{pos+1}{new_aa}",
            "delta_hydro": round(delta_hydro, 2),
            "estimated_ddg": round(ddg, 2),
            "stability": "STABLE" if ddg < 0 else "DESTABILIZING"
        }
