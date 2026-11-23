"""Sparse polynomials over the rationals for the zero-gap identities."""
from fractions import Fraction as F


class P:
    def __init__(self, value=0):
        if isinstance(value, P):
            self.c = value.c.copy()
        elif isinstance(value, str):
            self.c = {(value,): F(1)}
        elif isinstance(value, dict):
            if any(isinstance(coeff, float) for coeff in value.values()):
                raise TypeError("A polynomial coefficient must be exact")
            self.c = {term: F(coeff) for term, coeff in value.items() if coeff}
        else:
            if isinstance(value, float):
                raise TypeError("A polynomial coefficient must be exact")
            self.c = {(): F(value)} if value else {}

    def __add__(self, other):
        other = other if isinstance(other, P) else P(other)
        out = self.c.copy()
        for term, coeff in other.c.items():
            out[term] = out.get(term, 0) + coeff
        return P(out)

    __radd__ = __add__

    def __neg__(self):
        return P({term: -coeff for term, coeff in self.c.items()})

    def __sub__(self, other):
        return self + (-other if isinstance(other, P) else -P(other))

    def __rsub__(self, other):
        return -self + other

    def __mul__(self, other):
        other = other if isinstance(other, P) else P(other)
        out = {}
        for left, a in self.c.items():
            for right, b in other.c.items():
                term = tuple(sorted(left + right))
                out[term] = out.get(term, 0) + a*b
        return P(out)

    __rmul__ = __mul__

    def __truediv__(self, other):
        if isinstance(other, (float, P)):
            raise TypeError("A polynomial divisor must be an exact scalar")
        return self * (F(1) / F(other))

    def __pow__(self, n):
        assert type(n) is int and n >= 0
        out = P(1)
        for _ in range(n):
            out = out*self
        return out

    def __eq__(self, other):
        other = other if isinstance(other, P) else P(other)
        return self.c == other.c

    def __repr__(self):
        return repr(self.c)


def equal(x, y):
    left = x if isinstance(x, P) else P(x)
    assert left == y, (x, y)


def vector_equal(x, y):
    assert len(x) == len(y)
    for a, b in zip(x, y):
        equal(a, b)
