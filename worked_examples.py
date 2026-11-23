"""Reproduce the two worked witness calculations in Appendices D.3 and D.4."""
from fractions import Fraction
from pathlib import Path

from exact_intervals import dot, matvec, transpose
from exact_polynomials import P, equal, vector_equal
from grid_witness import grid_rows
from local_rows import response, witness
from verification_io import read_certificate


def global_example():
    path = Path(__file__).resolve().parent / "certificates" / "global.json"
    data = read_certificate(path)
    case, = [entry for entry in data["mode_cover"]["cases"] if entry["support"] == [0, 3, 12]]
    leaf, = case["leaves"]
    assert leaf["path"] == "" and leaf["reason"] == "witness"
    fields = case["witnesses"][leaf["witness"]]
    assert fields == [0, 0, 0, 0, 16, -7, -7, 16]
    matrix = [fields[4:6], fields[6:8]]

    largest_bilinear = 0
    largest_squared_norm = 0
    wt = transpose(matrix)
    for row in grid_rows(case["support"]):
        u, v = row[:2], row[2:]
        wv, wtu = matvec(matrix, v), matvec(wt, u)
        largest_bilinear = max(largest_bilinear, abs(dot(u, wv)))
        largest_squared_norm = max(largest_squared_norm, dot(wv, wv), dot(wtu, wtu))

    assert largest_bilinear == 18 and largest_squared_norm == 305
    assert largest_squared_norm < largest_bilinear ** 2
    trace = matrix[0][0] + matrix[1][1]
    lower_bound = trace * Fraction(2, 3) - largest_bilinear
    assert trace == 32 and lower_bound == Fraction(10, 3)
    print(f"Appendix D.3: max |u^T Wv| = {largest_bilinear}, max squared norm = "
          f"{largest_squared_norm}, lower bound at zeta=2/3 = {lower_bound}.")


def local_example():
    delta, n = P("Delta"), P("n")
    m, q = 1 - delta, 1 + delta
    h, k, matrix = witness("exchange_plus", {"m": m, "q": q, "n": n})
    vector_equal(h, [0, 0])
    vector_equal(k, [0, 0])
    # The physical vectors in the (e,f) basis are sqrt(2) times these coordinates.
    u, v = response((1, 1, 1, -1))
    wv, wtu = matvec(matrix, v), matvec(transpose(matrix), u)
    equal(2 * dot(u, wv), 2 * n)
    equal(2 * dot(wv, wv), 2 * (q ** 2 + n ** 2))
    equal(2 * dot(wtu, wtu), 2 * (m ** 2 + n ** 2))
    print("Appendix D.4, Table 2 (f,e): u^T Wv = 2n, ||Wv||^2 = R^2, ||W^T u||^2 = S^2.")


if __name__ == "__main__":
    global_example()
    local_example()
    print("PASS_WORKED_EXAMPLES")
