# Notation correspondence

| Meaning | Manuscript symbol | Executable variable |
| --- | --- | --- |
| Normalized CC weight | tilde{w} | `a` |
| Normalized CQ weight | tilde{beta} | `b` |
| Normalized QC weight | tilde{gamma} | `c` |
| Mode asymmetry | Delta | `D = b-c` |
| Visibility | zeta | `zeta` |
| Cost | delta | `delta` |

```text
tilde{w} = w/tau, tilde{beta} = beta/tau, tilde{gamma} = gamma/tau,
tau = 1-delta.
```

The state-bias parameter mu in Sec. 6/Appendix F is unrelated to these weights.
No executable variable or physical parameter has been reinterpreted.

## Local certificate aliases

```text
Z = Z_{tilde{w}}; n = tilde{w}/Z;
m = 1-Delta; q = 1+Delta;
R = sqrt(2) F(Delta); S = sqrt(2) F(-Delta);
F(x) = sqrt((1+x)^2+n^2).
L (manuscript) = L_pair (code)
              = 2*zeta + 2*tilde{w}*n - tilde{gamma}*R - tilde{beta}*S.
```

These aliases in Appendix D.4 match the explicit formulas in `local_rows.py`;
they are not independent physical parameters. The exceptional weight w_3 belongs
to an auxiliary grid corner, not a third physical shared-label probability.
Grid expansions preserve the matching moments and relax the original responses
within their closed sign cells.

W_21 denotes the lower-left matrix entry of W; it is distinct from the executable
variable `c`, which means normalized QC weight. See `MANUSCRIPT_MAP.md` for the
section and equation correspondence.
