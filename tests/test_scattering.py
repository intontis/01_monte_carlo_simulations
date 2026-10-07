import numpy as np
import pytest

from scattering import B_MAX, a_of, build_median_curve, estimate_Z, simulate_angles

# 5 MeV alpha on gold


def test_a_of_scales_correctly():
    assert a_of(79) == pytest.approx(22.752)
    assert a_of(2 * 40) == pytest.approx(2 * a_of(40)
                                         )           # proportional to Z
    assert a_of(79, energy=10.0) == pytest.approx(
        a_of(79) / 2)  # inversely proportional to E


def test_angles_stay_in_physical_range():
    rng = np.random.default_rng(0)
    theta = simulate_angles(79, 50_000, noise_deg=10.0, rng=rng)
    assert theta.min() > 0
    assert theta.max() < np.pi


def test_same_seed_gives_same_angles():
    first = simulate_angles(47, 1_000, 5.0, np.random.default_rng(123))
    second = simulate_angles(47, 1_000, 5.0, np.random.default_rng(123))
    np.testing.assert_array_equal(first, second)

# without noise, a particle scatters beyond 90° exactly when b < a


def test_fraction_beyond_90_degrees_matches_theory():
    n = 200_000
    theta = simulate_angles(79, n, noise_deg=0.0, rng=np.random.default_rng(0))
    p = (a_of(79) / B_MAX) ** 2
    expected = p * n
    sigma = np.sqrt(n * p * (1 - p))
    observed = np.sum(theta > np.pi / 2)
    # 4 std: fails by chance ~1 in 16,000
    assert abs(observed - expected) < 4 * sigma

# built once and shared by the tests below (it is the slow part)


@pytest.fixture(scope="module")
def curve_1deg():
    return build_median_curve(1.0, np.random.default_rng(1))


@pytest.mark.parametrize("Z_true", [30, 47, 79, 100])
def test_estimate_Z_recovers_Z_at_low_noise(Z_true, curve_1deg):
    theta = simulate_angles(Z_true, 10_000, 1.0, np.random.default_rng(2))
    assert abs(estimate_Z(theta, curve_1deg) - Z_true) <= 2
