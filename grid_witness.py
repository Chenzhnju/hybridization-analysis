"""Grid vertices and integer witness bounds for Eq. (D.4)."""
from itertools import product
from math import isqrt

if not __debug__:
    raise SystemExit('Refused: optimized Python disables assertions.')

SIGNS = tuple(product((-1, 1), repeat=4))


def grid_rows(support):
    return sorted({row for cell in support
                   for row in product(*[(0, sign) for sign in SIGNS[cell]])})


def witness_trace(w):
    assert len(w) == 8 and all(type(x) is int for x in w)
    trace = w[4] + w[7]
    assert trace >= 0, f"Negative witness trace {trace}"
    return trace


def ceil_root(n):
    root = isqrt(n)
    return root + (root * root < n)


def affine_row(w, row, scale=1):
    """Coefficients of 1, b, c in a lower bound on scale² (Phi - zeta tr W).

    The two response vectors are row[:2]/scale and row[2:]/scale.
    Rounding each norm upwards gives a lower bound for nonnegative b and c.
    """
    h0, h1, k0, k1, m00, m01, m10, m11 = w
    x, y, z, t = row
    wv = (m00*z + m01*t, m10*z + m11*t)
    wtu = (m00*x + m10*y, m01*x + m11*y)
    hu = scale*(h0*x + h1*y)
    kv = scale*(k0*z + k1*t)
    bilinear = x*wv[0] + y*wv[1]
    nr = scale*ceil_root((scale*h0 + wv[0])**2 + (scale*h1 + wv[1])**2)
    ns = scale*ceil_root((scale*k0 + wtu[0])**2 + (scale*k1 + wtu[1])**2)
    return hu + kv + bilinear, -kv - bilinear - ns, -hu - bilinear - nr


def mode_coefficients(w, grid):
    return witness_trace(w), [affine_row(w, row) for row in grid]
