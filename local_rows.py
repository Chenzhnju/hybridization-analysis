"""The five witnesses in Appendix D.4, Table 2, and their row bounds."""
from fractions import Fraction as F
from functools import lru_cache
from exact_intervals import I, SCALE, norm, dot, matvec, transpose
from grid_witness import SIGNS, grid_rows

A_MAX = F(7, 125)
D_MAX = F(1, 20)
CASES = {
    'exchange_plus': dict(third=11, epsilon=1, incomplete_margin=F(1,50)),
    'exchange_minus': dict(third=8, epsilon=-1, incomplete_margin=F(1,50)),
    'opposite': dict(third=13, sigma=1, incomplete_margin=F(1,50)),
    'parallel_anti': dict(third=12, sigma=1, incomplete_margin=F(1,2500)),
    'parallel_pos': dict(third=15, sigma=-1, incomplete_margin=F(1,2500)),
}
PRINCIPALS = {(1,1,1,-1), (-1,-1,-1,1)}


def grid(name):
    return grid_rows((1, 14, CASES[name]['third']))


def response(p):
    x, y, z, t = p
    # Physical responses in the orthonormal (e,f) frame are sqrt(2) U,V.
    return (F(x+y, 2), F(x-y, 2)), (F(z+t, 2), F(z-t, 2))


def balance_terms(b, c, R, S, n):
    hb = b*S - 2*(1-b)*n
    hc = c*R - 2*(1-c)*n
    return hb, hc, hb + hc


def parameters(a, d):
    z2 = F(1, 2) - a - a.square()/2
    assert z2.lo > 0
    z = z2.sqrt()
    n, m, q = a/z, 1-d, 1+d
    b, c = (1-a+d)/2, (1-a-d)/2
    assert min(b.lo, c.lo, m.lo, q.lo) >= 0
    e = I(2).sqrt()
    r, s = norm((q, n)), norm((m, n))
    R, S = e*r, e*s
    hb, hc, H = balance_terms(b, c, R, S, n)
    assert min(hc.lo, hb.lo, H.lo) > 0
    return dict(a=a, d=d, z=z, n=n, m=m, q=q, b=b, c=c, e=e, r=r, s=s,
                R=R, S=S, hc=hc, hb=hb, H=H)


def tilt_terms(name, p):
    """Numerators of ell and t and their common denominator in Table 2."""
    if name == 'opposite':
        kappa = F(1, 16)
    elif name == 'parallel_anti':
        kappa = F(1, 4)
    elif name == 'parallel_pos':
        kappa = F(9, 20) - 3*p['a']
    else:
        raise ValueError(f"No tilt for family {name}")
    return kappa*p['hb'], kappa*p['hc'], p['H']


def tilt(name, p):
    if 'epsilon' in CASES[name]:
        return p
    left, right, denominator = tilt_terms(name, p)
    ell, t = left/denominator, right/denominator
    assert ell.lo > 0 and t.lo > 0 and ell.below(1) and t.below(1)
    return dict(p, ell=ell, t=t)


def witness(name, p):
    """Return h/sqrt(2), k/sqrt(2) and W in the (e, f) basis of Table 2."""
    case = CASES[name]
    m, q, n = p['m'], p['q'], p['n']
    if 'epsilon' in case:
        return [0, 0], [0, 0], [[m, n], [case['epsilon']*n, q]]
    ell, t, sigma = p['ell'], p['t'], case['sigma']
    h = [sigma*ell*n, sigma*ell*q]
    k = [-sigma*t*m, -sigma*t*n]
    lower = 0 if name == 'opposite' else ell*q
    return h, k, [[m, n], [lower, q]]


def gap_formula(p):
    a, b, c = p['a'], p['b'], p['c']
    h_weight, k_weight, bilinear_weight = 2*(1-c), 2*(1-b), 2*a
    def combine(hu, kv, uv, nr, ns):
        return (h_weight*hu + k_weight*kv + bilinear_weight*(uv - p['n'])
                + p['e']*(c*(p['r'] - nr) + b*(p['s'] - ns)))
    return combine


def row_gap(p, fields):
    """Evaluate Phi - L, reusing the single-party terms within this box."""
    h, k, w = fields
    wt = transpose(w)
    combine = gap_formula(p)
    @lru_cache(maxsize=None)
    def alice_terms(u):
        wtu = matvec(wt, u)
        return dot(h, u), norm((k[0] + wtu[0], k[1] + wtu[1]))

    @lru_cache(maxsize=None)
    def bob_terms(v):
        wv = matvec(w, v)
        return dot(k, v), wv, norm((h[0] + wv[0], h[1] + wv[1]))

    def evaluate(u, v):
        hu, ns = alice_terms(u)
        kv, wv, nr = bob_terms(v)
        return combine(hu, kv, dot(u, wv), nr, ns)

    return evaluate


def gap(name, point, p, fields=None):
    fields = witness(name, p) if fields is None else fields
    return row_gap(p, fields)(*response(point))


def strict_rows(name):
    case = CASES[name]
    special = SIGNS[case['third']]
    rows = []
    for point in grid(name):
        if point in PRINCIPALS or (point == special and 'epsilon' in case):
            continue
        if point == special:
            margin = F(1, 100)
        else:
            assert 0 in point
            margin = case['incomplete_margin']
        rows.append((point, margin))
    return rows


def box_parameters(i, j, level):
    den = 1 << level
    a = I(A_MAX*F(i, den), A_MAX*F(i+1, den))
    d = I(D_MAX*(F(2*j, den)-1), D_MAX*(F(2*(j+1), den)-1))
    return parameters(a, d)


@lru_cache(maxsize=len(CASES))
def prepared_rows(name):
    return tuple((point, margin, response(point)) for point, margin in strict_rows(name))


def check_box(name, i, j, level, early=True):
    p = tilt(name, box_parameters(i, j, level))
    evaluate = row_gap(p, witness(name, p))
    worst = None
    failures = []
    for point, margin, (u, v) in prepared_rows(name):
        bound = evaluate(u, v)
        excess = F(bound.lo, SCALE) - margin
        if worst is None or excess < worst:
            worst = excess
        if excess <= 0:
            failures.append((point, str(margin), bound.bounds()))
            if early:
                break
    return not failures, worst, failures
