# Exact finite checks in Appendix D

## D.1 and D.2

For Eq. (D.3), the verifier writes each Bob response as ζ times a fixed vector. It checks the two local means, every entry of the second-moment matrix of u, and the coefficient of ζ in each of the four correlations. The largest allowed visibility, 2/3, gives the componentwise bound on the responses throughout the interval.

The missing-quadrant witness has 72 response pairs and three mode vertices. Scaling the witness by ten rounds the norm upper bounds to tenths in its original units. The smallest lower bound is 1/30. D.2 supplies the triangle and conditioning argument. The verifier checks positivity of the radius estimate at d = 1/64 and the sign of (2 − 12d) − (1 + 18d)√2, giving the cutoff δ > 1/4096.

## D.3

A support is a subset of the 16 joint sign cells. Simultaneous signed coordinate permutations and exchange of parties give 49 orbits among the 560 three-cell supports. Each one- or two-cell support extends to a three-cell support in an ordinary orbit. Five ordinary representatives have local images; 43 are excluded. The remaining representative is {3,6,9}.

For normalized CQ and QC weights b and c, the witness bound is

    Φ = (1−c) h·u + (1−b) k·v + (1−b−c) uᵀWv + ζ tr(W)
        − c ‖h+Wv‖ − b ‖k+Wᵀu‖.

`grid_witness.affine_row` rounds both norms upwards by integer square roots. For coordinates with denominator P it returns the coefficients of 1, b, c in a lower bound on P²(Φ − ζ tr(W)). Every row of a given parameter region uses the same witness.

For ordinary supports, the mode square is subdivided into four closed children at each split. Every witness is tested on all response rows and the vertices of the clipped mode polygon. The lower corner determines the visibility floor by inversion of Eq. (24). At a floor of 2/3 and positive trace, a zero lower bound suffices because the candidate has ζ > 2/3. All other witness exclusions require a strictly positive bound.

For {3,6,9} the fixed witness excludes the part with normalized CC weight at most 1/4 in 160 vertex checks. The remaining cover bisects a mode or response coordinate. Its two mode and twelve response coordinates are clipped to b+c ≤ 3/4, b ≤ c, and u₁ₓ ≤ u₁ᵧ. The tree traversal reconstructs the bounds of both children from their parent.

| D.3 cover | Leaves | Stored witnesses | Row/vertex comparisons |
| --- | ---: | ---: | ---: |
| Ordinary | 2,616 | 432 | 304,141 |
| Antialigned | 128 | 93 | 18,040 |

The retained cells obey δ > 4/5 and |Δ| ≤ 1/20. The verifier matches their five symmetry images to the actual D.4 grids. At A = 7/125, the symmetric cost ((1−A)/(1+A))² is 3481/4356 < 4/5. Since the cost decreases with A and (A−a)(1−aA) = AΔ², the retained CC weight satisfies a ≤ A < 7/125.

## D.4

Write a for the normalized CC weight, b = (1−a+Δ)/2, and c = (1−a−Δ)/2. On the local rectangle, the verifier checks H_b,H_c > 0. For the first three witnesses it checks the numerators and common denominator of the implemented tilt fractions, including t H_b = ℓ H_c. The witness and both physical response vectors are expressed in the (e,f) frame, with the factors of √2 restored for comparison with Eq. (D.4).

The two principal rows have Φ = L. For the two exchanged-axis families the third complete row has Φ − L = Δ(S−R). The other complete and incomplete rows use the following strict lower bounds on Φ − L.

| Third pair | Third complete row | Incomplete rows | Boxes | Strict row checks |
| --- | --- | ---: | ---: | ---: |
| (e,−f) | > 1/100 | > 1/50 | 88 | 3,344 |
| (e,e) | > 1/100 | > 1/2500 | 337 | 12,132 |
| (e,−e) | > 1/100 | > 1/2500 | 34 | 1,224 |
| (f,e) | Δ(S−R) | > 1/50 | 4 | 148 |
| (f,−e) | Δ(S−R) | > 1/50 | 4 | 148 |

The local certificate stores only subdivision paths. Each family covers the closed rectangle [0,7/125] × [−1/20,1/20]. The interval endpoints are integers in units of 2⁻⁶⁴. Products, quotients and square roots are rounded outwards. Division requires a denominator interval excluding zero. Within each box, rows with the same u or v reuse that response's norm.

For the two auxiliary witnesses in Table III (SciPost Table 3), Φ is affine in a and Δ at fixed response. The 320 comparisons cover all grid rows and the four rectangle corners at ζ = 2/3. The positive traces extend the strict bounds to larger ζ. The resulting limits on the exceptional weight are 7/19 and 1/3.

## D.5 and D.6

The verifier expands the averaged inequality in Eq. (D.8) and checks the derivative constants used in Eq. (D.9). For Eq. (D.10) it checks the polynomial factorization of the rationalized difference and bounds A/[2(1−A)Z_A] by 35/708 < 1/20. Subtracting 1/20 from 7/40 leaves 1/8. The integration and the optimal-cost comparison are in the manuscript.

In D.6 put s = p₊ − p₋. At the interior optimum Δ = 0 and a = ζn. Using the matrices for the two exchanged-axis families, the verifier derives s = εζw₃ and w₃ = ζs from Alice's marginal. The coefficient 1 − εζ² is positive for either sign. The D.4 principal-row identities, the resulting weights, and the disk equality conditions enter the manuscript's classification of protocols.
