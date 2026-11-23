"""The CC protocol and missing-quadrant witness in D.1, and the cutoff in D.2."""
from fractions import Fraction as F
from itertools import product

from grid_witness import mode_coefficients
from verification_io import PUBLICATION_REVISION, expect_rejection

CC_WEIGHTS = (F(3, 8), F(3, 8), F(1, 4))
CC_RESPONSES = ((F(-1, 3), -1), (1, F(1, 3)), (-1, 1))


def check_cc_protocol(weights=CC_WEIGHTS, responses=CC_RESPONSES):
    assert len(responses) == len(weights) == 3 and min(weights) > 0 and sum(weights) == 1
    slopes = [tuple(-F(3, 2)*x for x in u) for u in responses]  # v_j = zeta * slope_j
    for u, slope in zip(responses, slopes):
        assert len(u) == 2 and all(abs(x) <= 1 for x in u)
        assert all(F(2, 3)*abs(x) <= 1 for x in slope)
    for i in range(2):
        assert sum(p*u[i] for p, u in zip(weights, responses)) == 0
        assert sum(p*v[i] for p, v in zip(weights, slopes)) == 0
        for j in range(2):
            second = sum(p*u[i]*u[j] for p, u in zip(weights, responses))
            cross = sum(p*u[i]*v[j] for p, u, v in zip(weights, responses, slopes))
            assert second == F(2, 3)*(i == j), (i, j, second)
            assert cross == -int(i == j), (i, j, cross)
    return dict(status='PASS', visibility=['0', '2/3'], weights=list(map(str, weights)),
                local_means=[0, 0], uu_diagonal='2/3', correlation='-zeta I_2')


def check_mode_cap(w=(-3, -3, -5, -5, 10, 2, 2, 10)):
    vectors = tuple(product((-1, 0, 1), repeat=2))
    grid = [u + v for u in vectors for v in vectors if v != (1, 1)]
    modes = ((0, 1), (0, F(4, 5)), (F(1, 5), F(4, 5)))
    # Scale the witness before rounding to bound the original norms in tenths.
    trace, rows = mode_coefficients([10*x for x in w], grid)
    assert trace > 0
    minimum = min((A + B*b + C*c + F(2, 3)*trace)/10
                  for A, B, C in rows for b, c in modes)
    assert minimum >= F(1, 30), minimum
    return dict(status='PASS', response_vertices=len(grid), mode_vertices=len(modes),
                vertex_checks=len(grid)*len(modes), lower_bound=str(minimum),
                witness=list(w), trace=trace//10, excluded_domain='c >= 4/5; party exchange gives b >= 4/5')


def check_small_cost():
    d = F(1, 64)
    assert F(3, 2)**2 > 2 and F(2, 3) > (F(4, 3) + 2*F(3, 2))*d*d
    # k0 - 9*c*d = (2 - 12*d) - (1 + 18*d)*sqrt(2).
    left, right = 2 - 12*d, 1 + 18*d
    assert left > 0 and right > 0 and left**2 > 2*right**2
    return d*d


def compute():
    cap = check_mode_cap()
    negative = expect_rejection('zero missing-quadrant witness', lambda: check_mode_cap((0,)*8))
    return dict(status='PASS_FINITE_PRELIMINARIES', publication_revision=PUBLICATION_REVISION,
                manuscript_sections=['D.1', 'D.2 (final scalar comparison only)'],
                cc_protocol=check_cc_protocol(), mode_cap=cap,
                small_cost_final_square_comparison=True, small_cost_cutoff=str(check_small_cost()),
                negative_controls_rejected=[negative],
                scope='Eq. (D.3), the missing-quadrant witness, and the scalar cutoff in Eq. (D.6).')


if __name__ == '__main__':
    raise SystemExit('Run python verify.py to check all stages in order.')
