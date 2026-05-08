import numpy as np
from scipy.optimize import minimize
from scipy.spatial.distance import pdist

class NRCForcefield:
    def __init__(self, N):
        self.N = N
        self.phi = (1 + np.sqrt(5)) / 2
        self.x0 = self.spherical_fibonacci_initialization(N)

    def spherical_fibonacci_initialization(self, N):
        """Generates a 3D spherical distribution of points to avoid 2D collapse."""
        # Note: indices i go from 1 to N
        indices = np.arange(1, N + 1)
        z = 1 - (2 * indices - 1) / N
        # phi_angle = 2 * pi / phi^2
        phi_angle = 2 * np.pi / (self.phi**2)
        theta = phi_angle * indices
        
        x = np.sqrt(1 - z**2) * np.cos(theta)
        y = np.sqrt(1 - z**2) * np.sin(theta)
        # Scale to a reasonable starting radius for a protein (e.g., 10-20A)
        # But for optimization, 1.0 radius is fine as a starting manifold.
        return np.column_stack((x, y, z)).flatten()

    def qrt_damping_vectorized(self, d):
        """Quantum Residue Turbulence (QRT) Damping potential."""
        return np.sin(self.phi * np.sqrt(2) * 51.85 * d) * np.exp(-d**2 / self.phi) + np.cos(np.pi / self.phi * d)

    def ttt_7_penalty_vectorized(self, d):
        """Trageser Tensor Theorem (TTT-7) Modular Stability potential."""
        # Distance pseudo-integer scaling
        d_int = np.floor(np.abs(d) * 1618).astype(int)
        mod_val = d_int % 9
        
        penalty = np.zeros_like(d, dtype=float)
        # Chaotic Voids: 0, 3, 6, 9
        voids = (mod_val == 0) | (mod_val == 3) | (mod_val == 6) | (mod_val == 9)
        penalty[voids] = 1.0 / self.phi
        
        # Optimal Stability: 7
        stable = (mod_val == 7)
        penalty[stable] = -1.0
        
        return penalty

    def lennard_jones_potential_vectorized(self, d_scaled):
        """Standard Steric Clash Prevention (Lennard-Jones 12-6)."""
        # epsilon added to avoid division by zero
        eps = 1e-9
        return 4 * ((d_scaled + eps)**-12 - (d_scaled + eps)**-6)

    def total_energy(self, coords_flat):
        """Objective function for scipy.optimize.minimize."""
        coords = coords_flat.reshape(-1, 3)
        # Compute all pairwise distances efficiently
        dists = pdist(coords)
        
        # 1. Steric Energy (scaled by 3.8A typical C-alpha distance)
        lj_energy = np.sum(self.lennard_jones_potential_vectorized(dists / 3.8))
        
        # 2. QRT Damping Energy
        qrt_energy = np.sum(self.qrt_damping_vectorized(dists))
        
        # 3. TTT-7 Stability Energy
        ttt_energy = np.sum(self.ttt_7_penalty_vectorized(dists))
        
        return lj_energy + qrt_energy + ttt_energy

    def optimize(self, max_iter=500):
        """Relaxes the 3D structure using L-BFGS-B."""
        # No strict bounds needed for free-folding in space
        res = minimize(
            self.total_energy, 
            self.x0, 
            method='L-BFGS-B', 
            options={'maxiter': max_iter, 'disp': False}
        )
        return res.x.reshape(-1, 3)

if __name__ == "__main__":
    # Quick verification test
    n_residues = 20
    ff = NRCForcefield(n_residues)
    final_coords = ff.optimize(max_iter=100)
    print(f"Optimized coordinates shape: {final_coords.shape}")
    print("Optimization Complete.")
