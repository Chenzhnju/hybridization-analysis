# Manuscript and verification map

Version 31.2 uses the Release 31 certificates cited in Ref. [24]. SciPost Tables 2 and 3 are PRA Tables II and III. `DOCUMENT_VERSIONS.json` identifies the manuscript files.

| Manuscript location | Verifier entry | Result |
| --- | --- | --- |
| D.1, Eqs. (D.3) and (D.4) | `check_cc_protocol`, `check_mode_cap` in `verify_prerequisites.py` | Admissibility, both local means, the full correlation matrix, and the missing-quadrant witness |
| D.2, Eq. (D.6) | `check_small_cost` in `verify_prerequisites.py` | Scalar comparison at d = 1/64 after the geometric reduction |
| D.3, Lemma D.1, Eq. (D.7) | `verify_global.py`, `check_stage_links` in `verify.py` | Global cover, strict visibility endpoint, and inclusion in the five local families and their parameter rectangle |
| Appendix D.4, Table 2 and Eq. (D.8) | `local_rows.py`, `verify_local.py`, `certificates/local.json` | Principal-row identities and bounds on the other rows of all five families |
| Appendix D.4, Table 3 | `verify_local.py` | Auxiliary witnesses and exceptional-weight bounds for the two exchanged-axis families |
| D.4 and D.5, Eqs. (D.8)–(D.10) | `check_identities`, `check_constants` in `verify_local.py` | Averaged-row identity, derivative bounds, rationalized difference, and the final coefficient 1/8 |
| D.6 | `check_equality_marginals` in `verify_local.py` | The two marginal equations for each exchanged-axis witness and the elimination of the third weight |

## Worked support in Appendix D.3

`verify_global.check_classification()` enumerates the 560 three-cell sets. Their 49 symmetry orbits comprise 43 ordinary exclusions, five families passed to the local proof and the separate representative `[3,6,9]`.

In `certificates/global.json`, select the entry under `mode_cover.cases` with `support` equal to `[0,3,12]`. Its only leaf uses witness 0 at the root. The eight integers `[0,0,0,0,16,-7,-7,16]` encode zero vectors h and k, followed by the two rows of W. The bounds on this support are |uᵀWv| ≤ 18 and squared norms at most 305. With tr(W) = 32 they give Φ ≥ 32ζ − 18 ≥ 10/3 for ζ ≥ 2/3.

## Worked row in Appendix D.4

The Table 2 row with third corner (f,e) is `exchange_plus` in `local_rows.CASES`. The function `local_rows.witness()` returns its matrix. For the principal row u = √2 e and v = √2 f, the bilinear term is 2n and the two norms are R and S. The test `verify_local.check_identities()` checks the underlying vector and polynomial identities for both signs of the principal row. The comparisons with Table 3 use the auxiliary witnesses in `verify_local.py`.

## Equality argument in Appendix D.6

At the interior optimum, D.5 gives Δ = 0 and ζ = Z. D.4 determines which rows can carry weight. For the two exchanged-axis families, `check_equality_marginals()` substitutes the Table 2 matrices into Alice's marginal. Eliminating the difference of the principal weights gives (1 − εζ²)w₃ = 0 for ε = ±1. The verifier checks the positive coefficient and the normalization of the principal weights. The manuscript uses strictness, interpolation, and equality in the disk bound to classify the original protocols.
