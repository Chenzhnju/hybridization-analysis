"""Local row bounds, scalar estimates, and equality identities in D.4-D.6."""
from pathlib import Path
from fractions import Fraction as F
from itertools import product
from copy import deepcopy
import json
import platform
import sys
import time
from dyadic_cover import cover_cells
from verification_io import PUBLICATION_REVISION, expect_rejection, read_certificate, source_hashes
from exact_intervals import I,SCALE,BITS,norm,dot,matvec,transpose
from exact_polynomials import P,equal,vector_equal
from local_rows import (CASES,SIGNS,PRINCIPALS,A_MAX,D_MAX,grid,response,
                        balance_terms, parameters, tilt_terms, tilt, witness, gap_formula,
                        strict_rows, prepared_rows, check_box)

HERE = Path(__file__).resolve().parent
DOMAIN = {'a': ['0', str(A_MAX)], 'D': [str(-D_MAX), str(D_MAX)]}


def check_grid_geometry():
    e, f = (1, 0), (0, 1)
    minus_e, minus_f = (-1, 0), (0, -1)
    table = {'opposite': (e, minus_f), 'parallel_pos': (e, e),
             'parallel_anti': (e, minus_e), 'exchange_plus': (f, e),
             'exchange_minus': (f, minus_e)}
    assert set(CASES) == set(table)
    assert {response(row) for row in PRINCIPALS} == {(e, f), (minus_e, minus_f)}
    records = {}
    for name, case in CASES.items():
        points = grid(name)
        third = SIGNS[case['third']]
        assert response(third) == table[name], (name, third)
        complete = {row for row in points if all(row)}
        assert complete == PRINCIPALS | {third}
        strict = dict(strict_rows(name))
        incomplete = set(points) - complete
        assert all(strict[row] >= F(1, 2500) for row in incomplete)
        if 'epsilon' in case:
            assert set(strict) == incomplete
        else:
            assert set(strict) == incomplete | {third} and strict[third] >= F(1, 100)
        records[name] = dict(grid_rows=len(points), strict_rows=len(strict), principal_equalities=2,
                             third_cell=case['third'], sign_cells=sorted(SIGNS.index(row) for row in complete))
    return records


def check_interval_engine():
    """Independent Fraction endpoint checks of the rounded arithmetic."""
    values=list(map(F,('-3/2','-1/7','0','1/9','2/3','2')))
    ranges=[(x,y) for x in values for y in values if x<=y]
    count=0
    def contains(interval,lo,hi):
        assert F(interval.lo,SCALE)<=lo<=hi<=F(interval.hi,SCALE)
    for lo,hi in ranges:
        x=I(lo,hi);contains(x,lo,hi)
        sqlo=F(0) if lo<=0<=hi else min(lo*lo,hi*hi)
        contains(x.square(),sqlo,max(lo*lo,hi*hi));count+=1
        if lo>=0:
            r=x.sqrt()
            assert F(r.lo,SCALE)**2<=lo and F(r.hi,SCALE)**2>=hi
            count+=1
        for low,high in ranges:
            y=I(low,high)
            contains(x+y,lo+low,hi+high)
            contains(x-y,lo-high,hi-low)
            v=[a*b for a,b in product((lo,hi),(low,high))]
            contains(x*y,min(v),max(v));count+=3
            if low>0 or high<0:
                v=[a/b for a,b in product((lo,hi),(low,high))]
                contains(x/y,min(v),max(v));count+=1
    assert I(0).sqrt().bounds()==['0','0']
    assert I(4).sqrt().bounds()==['2','2']
    return dict(status='PASS',independent_fraction_checks=count)


def check_basis_connection():
    """Connect the implemented gap to Phi in the original coordinates."""
    d,n,ell,t,a,b,c,z,e,r,s,nu,nv=(P(x) for x in
        ('D','n','ell','t','a','b','c','zeta','sqrt2','r','s','nu','nv'))
    p=dict(m=1-d,q=1+d,n=n,ell=ell,t=t)
    combine = gap_formula(dict(a=a, b=b, c=c, n=n, e=e, r=r, s=s))
    B=[[1,1],[1,-1]];checks=0
    for name in CASES:
        h,k,w=witness(name,p)
        ho=matvec(B,h);ko=matvec(B,k)
        wo=[[sum(B[i][j]*w[j][l]*B[l][k] for j,l in product(range(2),repeat=2))/2
             for k in range(2)] for i in range(2)]
        equal(wo[0][0]+wo[1][1],2)
        for point in grid(name):
            u,v=point[:2],point[2:];U,V=response(point)
            wv, wtu = matvec(wo, v), matvec(transpose(wo), u)
            wV, wtU = matvec(w, V), matvec(transpose(w), U)
            hu, kv, bil = dot(ho, u), dot(ko, v), dot(u, wv)
            terms = dot(h, U), dot(k, V), dot(U, wV)
            equal(hu, 2*terms[0]); equal(kv, 2*terms[1]); equal(bil, 2*terms[2])
            ro = [x+y for x, y in zip(ho, wv)]
            so = [x+y for x, y in zip(ko, wtu)]
            rr = [x+y for x, y in zip(h, wV)]
            ss = [x+y for x, y in zip(k, wtU)]
            equal(dot(ro,ro),2*dot(rr,rr));equal(dot(so,so),2*dot(ss,ss))
            original=(1-c)*hu+(1-b)*kv+a*bil+2*z-c*e*nu-b*e*nv
            baseline=2*z+2*a*n-c*e*r-b*e*s
            equal(original-baseline, combine(*terms, nu, nv))
            checks += 6
    return dict(status='PASS',polynomial_identity_checks=checks)


def check_identities(field_function=witness):
    a,d,b,c,n,ell,t,R,S=(P(x) for x in ('a','D','b','c','n','ell','t','R','S'))
    p=dict(m=1-d,q=1+d,n=n,ell=ell,t=t)
    hb, hc, H = balance_terms(b, c, R, S, n)
    equal(hb, b*S - 2*(1-b)*n)
    equal(hc, c*R - 2*(1-c)*n)
    equal(H, hb + hc)
    kappas = {'opposite': F(1,16), 'parallel_pos': F(9,20)-3*a, 'parallel_anti': F(1,4)}
    identities=0
    for name in CASES:
        h,k,w=field_function(name,p)
        equal(w[0][0]+w[1][1],2)
        if name in kappas:
            left, right, denominator = tilt_terms(name, dict(a=a, hb=hb, hc=hc, H=H))
            equal(denominator, hb+hc)
            equal(left, kappas[name]*hb)
            equal(right, kappas[name]*hc)
            equal(right*hb-left*hc, 0)
        for rho in (-1,1):
            u=[rho,0];v=[0,rho]
            wv, wtu = matvec(w, v), matvec(transpose(w), u)
            equal(dot(u, wv), n)
            if name.startswith('exchange_'):
                vector_equal(h,[0,0]);vector_equal(k,[0,0])
                vector_equal(wv,[rho*n,rho*p['q']])
                vector_equal(wtu,[rho*p['m'],rho*n])
            else:
                sigma=CASES[name]['sigma']
                vector_equal([h[i]+wv[i] for i in range(2)],
                             [(rho+sigma*ell)*n,(rho+sigma*ell)*p['q']])
                vector_equal([k[i]+wtu[i] for i in range(2)],
                             [(rho-sigma*t)*p['m'],(rho-sigma*t)*n])
                # 0 < ell,t < 1 fixes the signs of the two norm factors.
                g=2*(1-c)*dot(h,u)+2*(1-b)*dot(k,v)-sigma*rho*c*ell*R+sigma*rho*b*t*S
                equal(g,sigma*rho*(t*hb-ell*hc))
            identities+=1
        if name.startswith('exchange_'):
            eps=CASES[name]['epsilon'];u=[0,1];v=[eps,0]
            wv, wtu = matvec(w, v), matvec(transpose(w), u)
            equal(dot(u, wv), n)
            vector_equal(wv,[eps*p['m'],n])
            vector_equal(wtu,[eps*n,p['q']])
            equal(dot(wv, wv),p['m']**2+n**2)
            equal(dot(wtu, wtu),p['q']**2+n**2)
            equal(c*(R-S)+b*(S-R),(b-c)*(S-R))
            identities+=1
    w3 = P('w3')
    b, c = (1-a+d)/2, (1-a-d)/2
    equal(2*(c*R+b*S-w3*d*(S-R)), (1-a)*(R+S)+(1-2*w3)*d*(S-R))
    z2=F(1,2)-a-a*a/2
    equal((1-a)**2/2-a*a,z2) # (1-a)F(0)/sqrt(2)-an=Z_a, with positive roots.
    A=P('A')
    equal((1-A)**2*((1+a)**2-d*d)-(1+A)**2*((1-a)**2-d*d),
          4*(A*d*d-(A-a)*(1-a*A)))
    zA2 = F(1,2) - A - A*A/2
    equal(2*(z2-zA2), (A-a)*(2+A+a))
    za, zA = P('Z_a'), P('Z_A')
    equal((1-A*a)*(za+zA) - (1-A)*(2+A+a)*zA,
          (1-A*a)*(za-zA) + (A-a)*(1+A)*zA)
    return dict(status='PASS',principal_and_exchanged_row_identities=identities,
                tilt_balance=True,closing_normalization=True,independence_identity=True,
                tilt_families=len(kappas), averaged_row_identity=True, rationalized_difference=True)


def check_equality_marginals():
    """Alice's marginal in D.6 at Delta=0 and a=zeta*n."""
    zeta, n, imbalance, w3 = (P(x) for x in ('zeta', 'n', 'p_plus_minus_p_minus', 'w3'))
    u, v = response((1, 1, 1, -1))
    bounds = {}
    for name in ('exchange_plus', 'exchange_minus'):
        case = CASES[name]
        eps = case['epsilon']
        third_u, third_v = response(SIGNS[case['third']])
        h, k, w = witness(name, dict(m=1, q=1, n=n))
        vector_equal(h, [0, 0])
        vector_equal(k, [0, 0])
        for direction in (v, third_v):
            wv = matvec(w, direction)
            equal(dot(wv, wv), 1 + n*n)
        mean_u = [imbalance*x + w3*y for x, y in zip(u, third_u)]
        mean_v = [imbalance*x + w3*y for x, y in zip(v, third_v)]
        # At equality (1-a)/sqrt(2*(1+n²)) = zeta and the disk response is -Wv/||Wv||.
        mx, my = [(1+zeta*n)*x-zeta*y for x, y in zip(mean_u, matvec(w, mean_v))]
        equal(mx, imbalance - eps*zeta*w3)
        equal(my, w3-zeta*imbalance)
        equal(my + zeta*mx, (1-eps*zeta**2)*w3)
        lower = min(F(1), 1-eps*F(1,2))
        assert lower > 0, name
        bounds[name] = str(lower)
    plus, minus = P('p_plus'), P('p_minus')
    total, difference = plus+minus+w3, plus-minus
    equal((total-w3+difference)/2, plus)
    equal((total-w3-difference)/2, minus)
    # At w3=difference=0 both expressions are half the total mass.
    return dict(status='PASS', determinant_lower=bounds, principal_weights=['1/2', '1/2'],
                exceptional_weight='0')


def check_constants():
    a0=A_MAX;d0=D_MAX;z2=F(1,2)-a0-a0*a0/2
    assert 0<a0<1 and 0<d0<1 and z2>0
    assert z2>F(16,25)**2 and a0*a0/z2<F(1,11)**2
    assert (1-a0-d0)/2==F(447,1000) and (1+d0)/2==F(21,40)
    p=parameters(I(0,a0),I(-d0,d0))
    assert p['z'].above(0) and p['n'].lo>=0 and p['n'].below(F(1,11))
    signs={}
    for name in ('opposite','parallel_anti','parallel_pos'):
        q=tilt(name,p)
        signs[name]={'ell':q['ell'].bounds(),'t':q['t'].bounds()}
    # Exact one-dimensional derivative bounds for Eq. (D.8) -> Eq. (D.9).
    first=(1-d0)**2/((1-d0)**2+F(1,11)**2)
    second=F(1,11)**2/(1-d0)**3
    assert first==F(43681,44081)>F(99,100)**2
    assert second==F(8000,829939)<F(1,100)
    coefficient=F(99,200)*(1-2*F(7,19))-F(1,400)
    assert coefficient==F(971,7600)
    assert F(7,5)**2<2 and coefficient*F(7,5)>F(7,40)
    assert F(1,3)<F(7,19)
    # At the upper local endpoint, ((1-A)/(1+A))² already lies below 4/5.
    cost_at_a0 = ((1-a0)/(1+a0))**2
    assert cost_at_a0 < F(4,5)
    assert z2 > F(3,5)**2
    difference_bound = a0/(2*(1-a0)*F(3,5))
    assert difference_bound < F(1,20)
    assert F(7,40)-F(1,20)==F(1,8)
    return dict(status='PASS',domain=DOMAIN,n_upper='1/11',
                positive_denominators={'Z_a':p['z'].bounds(),'H':p['H'].bounds(),
                                       'H_b':p['hb'].bounds(),'H_c':p['hc'].bounds()},
                tilt_signs=signs,first_derivative_squared_lower=str(first),
                second_derivative_upper=str(second),averaged_coefficient=str(coefficient),
                symmetric_cost_at_a_max=str(cost_at_a0),
                rationalized_coefficient_upper=str(difference_bound), final_imbalance_coefficient='1/8')


WEIGHTS={
    'exchange_plus':dict(w=[6,-1,6,1,9,-1,1,10],ordinary=F(-7,5),special=F(12,5),result=F(7,19)),
    'exchange_minus':dict(w=[2,-2,-2,-2,4,0,0,4],ordinary=F(-3,2),special=F(3),result=F(1,3)),
}


def check_weights(weights=None):
    weights = WEIGHTS if weights is None else weights
    caps = {'exchange_plus': F(7,19), 'exchange_minus': F(1,3)}
    assert set(weights) == set(caps)
    corners = []
    for aa, dd in product((F(0), A_MAX), (-D_MAX, D_MAX)):
        corners.append((aa, dd, I(aa), I((1-aa+dd)/2), I((1-aa-dd)/2)))
    results = {}
    for name, spec in weights.items():
        entries = spec['w']
        assert len(entries) == 8 and all(type(x) is int for x in entries)
        h, k = entries[:2], entries[2:4]
        w = [entries[4:6], entries[6:8]]
        wt = transpose(w)
        trace = w[0][0] + w[1][1]
        assert trace > 0
        visibility_term = I(F(2, 3)*trace)
        worst = None
        checks = 0
        for point in grid(name):
            u, v = point[:2], point[2:]
            wv, wtu = matvec(w, v), matvec(wt, u)
            nr = norm((h[0] + wv[0], h[1] + wv[1]))
            ns = norm((k[0] + wtu[0], k[1] + wtu[1]))
            hu, kv, uwv = dot(h, u), dot(k, v), dot(u, wv)
            margin = spec['special'] if point == SIGNS[CASES[name]['third']] else spec['ordinary']
            for aa, dd, a, b, c in corners:
                bound = visibility_term + (1-c)*hu + (1-b)*kv + a*uwv - c*nr - b*ns
                assert bound.above(margin), (name, point, aa, dd, bound.bounds(), margin)
                excess = F(bound.lo, SCALE) - margin
                worst = excess if worst is None else min(worst, excess)
                checks += 1
        assert spec['ordinary'] < 0 < spec['special']
        limit = -spec['ordinary'] / (spec['special'] - spec['ordinary'])
        assert limit == spec['result'] == caps[name]
        results[name] = dict(status='PASS', vertex_checks=checks, strict_excess_lower=str(worst),
                             other_rows_lower=str(spec['ordinary']), special_row_lower=str(spec['special']),
                             strict_weight_upper=str(limit))
    return results


def verify_cover(data):
    assert data['format'] == 'appendix-d3-local-interval-cover-v1'
    assert type(data['precision_bits']) is int and data['precision_bits'] == BITS
    assert data['domain'] == DOMAIN
    assert set(data['families']) == set(CASES)
    covers = {}
    for name, entry in data['families'].items():
        assert set(entry) == {'paths'} and isinstance(entry['paths'], list)
        covers[name] = cover_cells(entry['paths'], f"D.4 family={name}", max_depth=11)

    records = {}
    for name, cells in covers.items():
        row_count = len(prepared_rows(name))
        assert row_count > 0
        worst = None
        max_depth = 0
        for index, i, j, level in cells:
            ok, excess, failures = check_box(name, i, j, level, early=False)
            if not ok:
                path = data['families'][name]['paths'][index]
                raise AssertionError(f"D.4 family={name}, leaf={path or 'root'}: {failures}")
            worst = excess if worst is None else min(worst, excess)
            max_depth = max(max_depth, level)
        records[name] = dict(
            status='PASS', leaves=len(cells), row_interval_checks=len(cells)*row_count,
            max_depth=max_depth, strict_excess_lower=str(worst),
            incomplete_margin=str(CASES[name]['incomplete_margin']),
            third_complete_margin=None if name.startswith('exchange_') else '1/100',
        )
    return records


def check_negative_controls(data):
    controls=[]
    bad=deepcopy(data);bad['families']['parallel_pos']['paths'].pop()
    controls.append(expect_rejection('missing local leaf',lambda:verify_cover(bad)))
    bad=deepcopy(data);bad['families']['exchange_plus']['paths'].append(bad['families']['exchange_plus']['paths'][0])
    controls.append(expect_rejection('duplicated local leaf',lambda:verify_cover(bad)))
    bad=deepcopy(data);bad['families'].pop('parallel_pos')
    controls.append(expect_rejection('missing local family',lambda:verify_cover(bad)))
    bad=deepcopy(data);bad['domain']['a'][1]='1/10'
    controls.append(expect_rejection('changed local parameter domain',lambda:verify_cover(bad)))
    bad=deepcopy(data);bad['families']['parallel_pos']['paths']=['']
    controls.append(expect_rejection('unverified unsplit local rectangle',lambda:verify_cover(bad)))
    bad=deepcopy(WEIGHTS);bad['exchange_plus']['w']=[0]*8
    controls.append(expect_rejection('zero third-weight witness',lambda:check_weights(bad)))
    def wrong_fields(name,p):
        h,k,w=witness(name,p)
        if name=='parallel_pos':h=[-x for x in h]
        return h,k,w
    controls.append(expect_rejection('wrong tilt sign in a principal identity',lambda:check_identities(wrong_fields)))
    return controls


def compute(*,verbose=False):
    start=time.monotonic()
    data = read_certificate(HERE / 'certificates/local.json')
    arithmetic=check_interval_engine();geometry=check_grid_geometry()
    basis=check_basis_connection();constants=check_constants();identities=check_identities()
    weights=check_weights();cover=verify_cover(data);negative=check_negative_controls(data)
    names=['verify_local.py','local_rows.py','grid_witness.py','dyadic_cover.py','exact_intervals.py','exact_polynomials.py',
           'verification_io.py','certificates/local.json']
    report=dict(status='PASS_LOCAL_CERTIFICATE',scope='D.4 row and weight bounds, D.5 scalar checks, D.6 marginal identities.',
                publication_revision=PUBLICATION_REVISION,manuscript_sections=['D.4', 'Lemma D.2', 'D.5 (scalar checks)', 'D.6 (marginal identities)'],
                domain=DOMAIN,precision_bits=BITS,interval_engine=arithmetic,
                grid_geometry=geometry,basis_connection=basis,identities=identities,
                constants=constants,weight_bounds=weights,cover=cover,equality_marginals=check_equality_marginals(),
                total_leaves=sum(x['leaves'] for x in cover.values()),
                total_row_interval_checks=sum(x['row_interval_checks'] for x in cover.values()),
                negative_controls_rejected=negative,standard_library_only=True,
                floating_point_in_acceptance_tests=False,
                analytic_connections=['closed sign-cell expansion preserves physical moments',
                    'interval inclusion follows from directed arithmetic operations',
                    'one common witness is averaged over all rows',
                    'derivative bounds are integrated on the stated interval',
                    'Appendix D.3 establishes the local domain before these bounds are used'],
                sha256=source_hashes(HERE, names),
                python_version=sys.version.split()[0],python_implementation=platform.python_implementation(),
                seconds=round(time.monotonic()-start,3))
    if verbose:print(json.dumps(report,indent=2))
    return report


if __name__ == '__main__':
    raise SystemExit('Run python verify.py to check all stages in order.')
