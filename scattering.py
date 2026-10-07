# Rutherford scattering simulation and inverse-problem helpers

import numpy as np

# Physical setup (lengths in femtometers, energies in MeV)

E_ALPHA = 5.0                # alpha particle kinetic energy
Z_ALPHA = 2                  # alpha particle charge number
B_MAX = 576.0                # effective beam radius per nucleus (toy choice)
Z_GRID = np.arange(1, 119)   # every candidate atomic number


def a_of(Z, z_alpha=Z_ALPHA, energy=E_ALPHA):
    """Rutherford length a = k·Z_alpha·Z·e² / (2E) in fm, using k·e² = 1.44 MeV·fm."""
    return 0.72 * z_alpha * Z / energy


def simulate_angles(Z, n, noise_deg, rng, b_max=B_MAX):
    """Rutherford scattering angles for atomic number Z, with Gaussian detector noise."""
    b = b_max * np.sqrt(rng.uniform(0, 1, n)
                        )        # uniform over the beam's area
    theta = 2 * np.arctan(a_of(Z) / b)
    theta = theta + rng.normal(0, np.radians(noise_deg), n)
    return np.clip(theta, 0.001, np.pi - 0.001)


def build_median_curve(noise_deg, rng, n_calibration=200_000, z_grid=Z_GRID):
    """Calibration curve: the median measured angle each candidate Z would produce."""
    return np.array([
        np.median(simulate_angles(Z, n_calibration, noise_deg, rng))
        for Z in z_grid
    ])


def estimate_Z(theta_obs, median_curve, z_grid=Z_GRID):
    """Pick the Z whose predicted median angle is closest to the observed one."""
    return z_grid[np.argmin(np.abs(median_curve - np.median(theta_obs)))]
