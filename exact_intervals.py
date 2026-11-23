"""Outward-rounded dyadic intervals. Every operation uses integer arithmetic."""
from fractions import Fraction
from math import isqrt

BITS = 64
SCALE = 1 << BITS


def ceil_div(n, d):
    assert d > 0
    return -((-n) // d)


class I:
    __slots__ = ('lo', 'hi')

    def __init__(self, lo, hi=None, *, raw=False):
        if raw:
            assert type(lo) is int and type(hi) is int and lo <= hi
            self.lo, self.hi = lo, hi
        else:
            if isinstance(lo, I):
                assert hi is None
                self.lo, self.hi = lo.lo, lo.hi
                return
            assert not isinstance(lo, float) and not isinstance(hi, float)
            lo, hi = Fraction(lo), Fraction(lo if hi is None else hi)
            assert lo <= hi
            self.lo = (lo.numerator * SCALE) // lo.denominator
            self.hi = ceil_div(hi.numerator * SCALE, hi.denominator)

    def __add__(self, other):
        other = I(other)
        return I(self.lo + other.lo, self.hi + other.hi, raw=True)

    __radd__ = __add__

    def __neg__(self):
        return I(-self.hi, -self.lo, raw=True)

    def __sub__(self, other):
        return self + (-I(other))

    def __rsub__(self, other):
        return I(other) + (-self)

    def __mul__(self, other):
        other = I(other)
        xs = (self.lo * other.lo, self.lo * other.hi,
              self.hi * other.lo, self.hi * other.hi)
        return I(min(xs) // SCALE, ceil_div(max(xs), SCALE), raw=True)

    __rmul__ = __mul__

    def __truediv__(self, other):
        other = I(other)
        assert other.lo > 0 or other.hi < 0, 'division by an interval containing zero'
        if other.hi < 0:
            return (-self) / (-other)
        pairs = [(n * SCALE, d) for n in (self.lo, self.hi)
                 for d in (other.lo, other.hi)]
        return I(min(n // d for n, d in pairs),
                 max(ceil_div(n, d) for n, d in pairs), raw=True)

    def __rtruediv__(self, other):
        return I(other) / self

    def square(self):
        low = 0 if self.lo <= 0 <= self.hi else min(self.lo**2, self.hi**2)
        high = max(self.lo**2, self.hi**2)
        return I(low // SCALE, ceil_div(high, SCALE), raw=True)

    def sqrt(self):
        assert self.lo >= 0, 'square root of a negative lower endpoint'
        low, high = isqrt(self.lo * SCALE), isqrt(self.hi * SCALE)
        if high * high < self.hi * SCALE:
            high += 1
        assert low * low <= self.lo * SCALE < (low + 1)**2
        assert high * high >= self.hi * SCALE
        assert high == 0 or (high - 1)**2 < self.hi * SCALE
        return I(low, high, raw=True)

    def above(self, q):
        q = Fraction(q)
        return self.lo * q.denominator > q.numerator * SCALE

    def below(self, q):
        q = Fraction(q)
        return self.hi * q.denominator < q.numerator * SCALE

    def bounds(self):
        return [str(Fraction(self.lo, SCALE)), str(Fraction(self.hi, SCALE))]


def norm(v):
    return sum((I(x).square() for x in v), I(0)).sqrt()


def dot(u, v):
    u, v = tuple(u), tuple(v)
    if len(u) != len(v):
        raise ValueError(f"Dot product has vector lengths {len(u)} and {len(v)}")
    return sum(x * y for x, y in zip(u, v))


def matvec(w, v):
    v = tuple(v)
    return [dot(row, v) for row in w]


def transpose(w):
    rows = [tuple(row) for row in w]
    if rows and any(len(row) != len(rows[0]) for row in rows):
        raise ValueError("Matrix rows have different lengths")
    return list(zip(*rows))
