import numpy as np
from scipy.optimize import minimize
from nrc_chemistry import NRCChemistry
from nrc_atoms import NRCAtoms

class NRCForcefield:
    """
    Institutional All-Atom Resonance Forcefield.
    Implements deterministic TTT-7 stability and Tesla 3-6-9 Exclusion.
    """
    def __init__(self, sequence):
        self.sequence = sequence
        self.N_res = len(sequence)
        self.phi = (1 + np.sqrt(5)) / 2
        
        # Load Chemistry & Atom Manifolds
        self.chem = NRCChemistry()
        self.atom_lib = NRCAtoms()
        
        # Parameters (Calibrated for REFOLD parity)
        self.K_BOND = 10000.0  # Increased for structural rigidity
        self.K_RES = 500.0     # Resonance weight
        self.RG_TARGET = 3.0 * (self.N_res ** 0.33)
        self.MODULAR_SCALE = 3.8017 # TTT-7 Stable Anchor
        
        # Initial CA Seed
        self.ca_x0 = self.spherical_fibonacci_initialization(self.N_res)
        self.x0 = self.ca_x0

    def spherical_fibonacci_initialization(self, N):
        indices = np.arange(1, N + 1)
        z = 1 - (2 * indices - 1) / N
        theta = (2 * np.pi / (self.phi**2)) * indices
        x = np.sqrt(1 - z**2) * np.cos(theta)
        y = np.sqrt(1 - z**2) * np.sin(theta)
        return (np.column_stack((x, y, z)) * self.RG_TARGET).flatten()

    def _get_spatial_neighbors(self, coords, cutoff=10.0):
        """Pure math spatial hashing for O(N) interaction search."""
        n = len(coords)
        grid = {}
        cell_size = cutoff
        for i in range(n):
            cell = tuple((coords[i] // cell_size).astype(int))
            if cell not in grid: grid[cell] = []
            grid[cell].append(i)
        
        neighbors = []
        for cell, indices in grid.items():
            # Check 3x3x3 neighborhood
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    for dz in [-1, 0, 1]:
                        neighbor_cell = (cell[0]+dx, cell[1]+dy, cell[2]+dz)
                        if neighbor_cell in grid:
                            for i in indices:
                                for j in grid[neighbor_cell]:
                                    if i < j: neighbors.append((i, j))
        return neighbors

    def energy_and_gradient(self, coords_flat):
        """
        Refined All-Atom energy with Spatial Hashing and TTT-7 Resonance.
        """
        coords = coords_flat.reshape(-1, 3)
        n_atoms = coords.shape[0]
        grad = np.zeros_like(coords)
        total_e = 0.0

        # 1. Harmonic Backbone Constraints
        diff_bond = coords[1:] - coords[:-1]
        d_bond = np.linalg.norm(diff_bond, axis=1) + 1e-9
        bond_e = self.K_BOND * np.sum((d_bond - 3.8)**2)
        total_e += bond_e
        bond_mag = 2 * self.K_BOND * (d_bond - 3.8) / d_bond
        grad[:-1] += -bond_mag[:, np.newaxis] * diff_bond
        grad[1:] += bond_mag[:, np.newaxis] * diff_bond

        # 2. Non-bonded Resonance Manifold (Spatial Hashing)
        neighbors = self._get_spatial_neighbors(coords, cutoff=12.0)
        if neighbors:
            idx1, idx2 = zip(*neighbors)
            diff = coords[list(idx1)] - coords[list(idx2)]
            d = np.linalg.norm(diff, axis=1) + 1e-9
            
            # 2a. Tesla 3-6-9 Exclusion (Damped Periodic)
            dr = d * self.MODULAR_SCALE
            # Smoothness damping to avoid high-frequency oscillations
            damping = 1.0 / (1.0 + 0.1 * d**2)
            void_penalty = self.K_RES * damping * (1.0 + np.cos(2 * np.pi * dr / 3.0))
            total_e += np.sum(void_penalty)
            
            # Gradient: Product rule for damping * periodic
            p_grad_periodic = -self.K_RES * damping * (2 * np.pi / 3.0) * np.sin(2 * np.pi * dr / 3.0) * self.MODULAR_SCALE
            p_grad_damping = -self.K_RES * (1.0 + np.cos(2 * np.pi * dr / 3.0)) * (0.2 * d) * (damping**2)
            p_grad_total = p_grad_periodic + p_grad_damping
            
            # 2b. TTT-7 Resonance Anchor
            ttt_factor = 2 * np.pi / 9.0
            ttt_e = -50.0 * np.cos(ttt_factor * (dr - 7.0))
            total_e += np.sum(ttt_e)
            ttt_grad_mag = 50.0 * ttt_factor * np.sin(ttt_factor * (dr - 7.0)) * self.MODULAR_SCALE
            
            # Vectorized gradient update
            combined_mag = (p_grad_total + ttt_grad_mag) / d
            for k, (i, j) in enumerate(neighbors):
                g = combined_mag[k] * diff[k]
                grad[i] += g
                grad[j] -= g

        # 3. Radius of Gyration Confinement
        mean_coords = np.mean(coords, axis=0)
        rel_coords = coords - mean_coords
        rg = np.sqrt(np.mean(np.sum(rel_coords**2, axis=1)) + 1e-9)
        conf_e = 100.0 * (rg - self.RG_TARGET)**2
        total_e += conf_e
        grad += (200.0 * (rg - self.RG_TARGET) / (rg * n_atoms + 1e-9)) * rel_coords

        return total_e, grad.flatten()

    def optimize(self, max_iter=500):
        res = minimize(
            self.energy_and_gradient,
            self.x0,
            method='L-BFGS-B',
            jac=True,
            options={'maxiter': max_iter, 'gtol': 1e-5}
        )
        self.x0 = res.x
        return res.x.reshape(-1, 3)

    def generate_all_atom(self, ca_coords):
        """
        Fleshes out the CA skeleton into a full-atom manifold with torsion frames.
        Returns coordinates and metadata.
        """
        ca_coords = ca_coords.reshape(-1, 3)
        all_coords = []
        atom_types = []
        res_indices = []
        res_names = []
        
        for i, aa in enumerate(self.sequence):
            # Calculate local torsion-aware frame
            phi, psi = 0.0, 0.0
            if i > 0 and i < self.N_res - 1:
                v_prev = ca_coords[i] - ca_coords[i-1]
                v_next = ca_coords[i+1] - ca_coords[i]
                # Tangent, Normal, Binormal approximation
                t = (v_prev + v_next) / (np.linalg.norm(v_prev + v_next) + 1e-9)
                n = np.cross(v_prev, v_next)
                n /= (np.linalg.norm(n) + 1e-9)
                b = np.cross(t, n)
                rot = np.column_stack((t, n, b))
                # Pseudo-torsion for side-chain orientation
                phi = np.arctan2(n[1], n[0])
                psi = np.arctan2(b[2], b[1])
            else:
                rot = np.eye(3)
            
            res_dict = self.atom_lib.get_full_residue(aa, ca_coords[i], rotation_matrix=rot, phi=phi, psi=psi)
            for atom_name, coord in res_dict.items():
                all_coords.append(coord)
                atom_types.append(atom_name)
                res_indices.append(i + 1)
                res_names.append(aa)
                
        return {
            "coords": np.array(all_coords),
            "atom_types": atom_types,
            "res_indices": res_indices,
            "res_names": res_names
        }
