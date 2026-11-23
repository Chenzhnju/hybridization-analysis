"""Subdivision geometry, strict inequalities, and the local witness formula."""
from fractions import Fraction
from math import floor, isqrt
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from dyadic_cover import cover_cells
from exact_intervals import I, SCALE, dot, matvec, norm, transpose
from exact_polynomials import P
from grid_witness import affine_row
from local_rows import CASES, box_parameters, prepared_rows, row_gap, tilt, tilt_terms, witness
from verification_io import read_certificate
from verify import check_stage_links
from verify_global import (ZDEN, check_anti_witness, check_classification, check_mode_witness,
                           clipped_polygon, physical_polygon, zeta_floor)
from verify_local import check_equality_marginals, check_grid_geometry, check_identities
from verify_prerequisites import CC_RESPONSES, check_cc_protocol


class BoundTests(unittest.TestCase):
    def test_cc_weights_and_second_moments(self):
        self.assertEqual(check_cc_protocol()['correlation'], '-zeta I_2')
        for weights, rows in [((Fraction(1, 3),)*3, CC_RESPONSES),
                              ((Fraction(1, 3),)*3, ((0, 0),)*3)]:
            with self.subTest(rows=rows), self.assertRaises(AssertionError):
                check_cc_protocol(weights, rows)

    def test_scaled_integer_witness_against_eq_d4(self):
        def rounded_length(vector, denominator):
            square = dot(vector, vector)
            scaled = square*denominator**2
            root = isqrt(scaled.numerator // scaled.denominator)
            return Fraction(root + (root*root < scaled), denominator)

        fields = [2, -3, 4, 1, 5, -7, 2, 6]
        h, k, w = fields[:2], fields[2:4], [fields[4:6], fields[6:8]]
        for scale, row in [(1, (1,-1,0,1)), (4, (-3,1,2,-1)), (8, (0,4,-2,5))]:
            u, v = [Fraction(t,scale) for t in row[:2]], [Fraction(t,scale) for t in row[2:]]
            wv, wtu = matvec(w,v), matvec(transpose(w),u)
            nr = rounded_length([x+y for x,y in zip(h,wv)], scale)
            ns = rounded_length([x+y for x,y in zip(k,wtu)], scale)
            A, B, C = affine_row(fields,row,scale)
            for b,c in [(0,0),(1,0),(0,1),(Fraction(2,7),Fraction(1,3))]:
                direct = ((1-c)*dot(h,u)+(1-b)*dot(k,v)+(1-b-c)*dot(u,wv)-c*nr-b*ns)
                self.assertEqual(Fraction(A+b*B+c*C,scale**2), direct)

    def test_visibility_floor_at_all_witness_lower_corners(self):
        data = read_certificate(ROOT/'certificates/global.json')['mode_cover']
        corners = {(0,0,1),(1,1,2)}
        for case in data['cases']:
            leaves = case['leaves']
            for idx, b, c, depth in cover_cells((r['path'] for r in leaves), 'D.3'):
                if leaves[idx]['reason'].startswith('witness'):
                    corners.add((b,c,1<<depth))
        def below_inverse(z, delta):
            # Square 2*sqrt(delta)*(1-z²) >= 2-(1+delta)*(1-z²).
            v = 1-z*z
            rhs = 2-(1+delta)*v
            self.assertGreaterEqual(rhs, 0)
            return 4*delta*v*v >= rhs*rhs
        for b,c,scale in corners:
            delta = Fraction(b*c, (scale-b)*(scale-c))
            lower = Fraction(*zeta_floor(b,c,scale))
            self.assertGreaterEqual(lower, Fraction(2,3))
            if lower > Fraction(2,3):
                self.assertTrue(below_inverse(lower,delta))
            following = Fraction(floor(lower*ZDEN)+1, ZDEN)
            self.assertFalse(below_inverse(following,delta))

    def test_antialigned_witness_requires_strict_positivity(self):
        box = [(Fraction(0),Fraction(1))]*2 + [(Fraction(0),Fraction(0))]*12
        with self.assertRaisesRegex(AssertionError, 'node=7, witness=2.*expected > 0'):
            check_anti_witness([0]*8, box, 7, 2)

    def test_clipped_polygons_include_shared_boundaries(self):
        quarter, half = Fraction(1, 4), Fraction(1, 2)
        box = [(quarter, half)]*2
        self.assertEqual(set(physical_polygon(box, True, Fraction(3,4))),
                         {(quarter,quarter), (quarter,half), (Fraction(3,8),Fraction(3,8))})
        self.assertEqual(physical_polygon([(half,1), (0,half)], True, Fraction(1)), [(half,half)])
        self.assertEqual(clipped_polygon((half,1),(0,half)), [(half,half)])

    def test_frame_handoff_and_table_orientations(self):
        images = check_classification()['local_sign_cells']
        preliminary = {'small_cost_cutoff': '1/4096'}
        global_proof = dict(mode_cover=dict(small_cost_floor='1/4096', local_cost_floor='4/5', local_d_max='1/20'),
                            classification=dict(local_sign_cells=images),
                            certified_local_domain=dict(cost='delta > 4/5', imbalance='|b-c| <= 1/20'))
        local = dict(grid_geometry=check_grid_geometry(), domain=dict(a=['0','7/125'], D=['-1/20','1/20']),
                     constants=dict(symmetric_cost_at_a_max='3481/4356', final_imbalance_coefficient='1/8'))
        check_stage_links(preliminary, global_proof, local)
        images[0] = images[1]
        with self.assertRaisesRegex(AssertionError, 'different sign cells'):
            check_stage_links(preliminary, global_proof, local)
        with patch.dict(CASES, parallel_pos=dict(CASES['parallel_pos'], third=12)), self.assertRaises(AssertionError):
            check_grid_geometry()

    def test_unbalanced_tilt_is_rejected(self):
        def swapped(name, p):
            left,right,den = tilt_terms(name,p)
            return right,left,den
        with patch('verify_local.tilt_terms', swapped), self.assertRaises(AssertionError):
            check_identities()

    def test_tilt_ratios_for_distinct_balance_terms(self):
        a, hb, hc = Fraction(1,32), Fraction(1,4), Fraction(1,2)
        p = dict(a=I(a), hb=I(hb), hc=I(hc), H=I(hb+hc))
        for name, kappa in [('opposite',Fraction(1,16)), ('parallel_anti',Fraction(1,4)),
                            ('parallel_pos',Fraction(9,20)-3*a)]:
            result = tilt(name, p)
            for key, weight in [('ell',hb), ('t',hc)]:
                target = kappa*weight/(hb+hc)
                self.assertLessEqual(Fraction(result[key].lo,SCALE), target)
                self.assertGreaterEqual(Fraction(result[key].hi,SCALE), target)

    def test_wrong_exchange_sign_in_equality_equations(self):
        def wrong_matrix(name, p):
            h,k,w = witness(name,p)
            if name == 'exchange_minus':
                w[1][0] = -w[1][0]
            return h,k,w
        self.assertEqual(check_equality_marginals()['determinant_lower'],
                         {'exchange_plus':'1/2','exchange_minus':'1'})
        with patch('verify_local.witness', wrong_matrix), self.assertRaises(AssertionError):
            check_equality_marginals()

    def test_polynomial_coefficients_and_cancellation(self):
        x, y = P('x'), P('y')
        self.assertEqual((x+y)**2 - (x-y)**2, 4*x*y)
        self.assertEqual((x + Fraction(1, 3)) - x, Fraction(1, 3))
        self.assertEqual((x-x).c, {})
        self.assertEqual(x.c, {('x',): Fraction(1)})
        for value in (0.125, {('x',): 0.125}):
            with self.assertRaises(TypeError):
                P(value)

    def test_subdivision_coordinates(self):
        paths = ['3', '1', '02', '2', '01', '00', '03']
        cells = {paths[k]: (i, j, level) for k, i, j, level in cover_cells(paths, 'test')}
        self.assertEqual(cells, {
            '00': (0, 0, 2), '01': (0, 1, 2), '02': (1, 0, 2), '03': (1, 1, 2),
            '1': (0, 1, 1), '2': (1, 0, 1), '3': (1, 1, 1),
        })
        self.assertEqual(cover_cells([''], 'test'), [(0, 0, 0, 0)])

    def test_invalid_subdivisions(self):
        for paths in ([], ['0', '1', '2'], ['0', '0'], ['', '0'], ['0', ''], ['4'], [None]):
            with self.subTest(paths=paths), self.assertRaises(ValueError):
                cover_cells(paths, 'test')
        with self.assertRaises(ValueError):
            cover_cells(['00'], 'test', max_depth=1)

    def test_strictness_at_visibility_endpoint(self):
        # At zeta=2/3 the affine term -2 plus the trace term (2/3)*3 is zero.
        fields = (3, [(-2, 0, 0)])
        row = [(0, 0, 0, 0)]
        leaf = dict(reason='witness_strict_zeta', path='', witness=0)
        count = check_mode_witness(leaf, (0, 0, 1), False, fields, row, (0, 3, 12))
        self.assertEqual(count, 3)
        leaf['reason'] = 'witness'
        with self.assertRaisesRegex(AssertionError, 'lower bound 0'):
            check_mode_witness(leaf, (0, 0, 1), False, fields, row, (0, 3, 12))

    def test_local_bounds_against_direct_formula(self):
        families = read_certificate(ROOT/'certificates/local.json')['families']
        for name, family in families.items():
            cells = cover_cells(family['paths'], name)
            for _, i, j, level in (cells[0], cells[-1]):
                p = tilt(name, box_parameters(i, j, level))
                h, k, w = witness(name, p)
                evaluate = row_gap(p, (h, k, w))
                a, b, c = p['a'], p['b'], p['c']
                for point, _, (u, v) in prepared_rows(name):
                    with self.subTest(name=name, box=(i, j, level), point=point):
                        wv, wtu = matvec(w, v), matvec(transpose(w), u)
                        nr = norm([h[t] + wv[t] for t in (0, 1)])
                        ns = norm([k[t] + wtu[t] for t in (0, 1)])
                        direct = (2*(1-c)*dot(h, u) + 2*(1-b)*dot(k, v)
                                  + 2*a*(dot(u, wv) - p['n'])
                                  + p['e']*(c*(p['r'] - nr) + b*(p['s'] - ns)))
                        bound = evaluate(u, v)
                        self.assertEqual((bound.lo, bound.hi), (direct.lo, direct.hi))


if __name__ == '__main__':
    unittest.main()
