"""Support orbits, mode localization, and the antialigned cover in D.3."""
from pathlib import Path
from fractions import Fraction as F
from itertools import product, permutations, combinations
from functools import lru_cache
from collections import Counter
from copy import deepcopy
import json
import platform
import sys
import time
from dyadic_cover import cover_cells
from grid_witness import SIGNS, affine_row, grid_rows, mode_coefficients, witness_trace
from verification_io import PUBLICATION_REVISION, expect_rejection, read_certificate, source_hashes

HERE=Path(__file__).resolve().parent
INDEX={s:i for i,s in enumerate(SIGNS)}
ANTI=(3,6,9)
ANTI_SIGNS = [list(SIGNS[cell]) for cell in ANTI]
ZDEN=1<<40


def transformed(support,axes,flip,exchange):
    rows=[]
    for i in support:
        a,b=SIGNS[i][:2],SIGNS[i][2:]
        if exchange:a,b=b,a
        rows.append(INDEX[tuple(flip[k]*a[axes[k]] for k in range(2))+
                          tuple(flip[k]*b[axes[k]] for k in range(2))])
    return tuple(sorted(rows))


def orbit(support):
    return {transformed(support,axes,flip,exchange)
            for axes,flip,exchange in product(permutations((0,1)),
                product((-1,1),repeat=2),(False,True))}


REPS={min(orbit(s)) for s in combinations(range(16),3)}
FIVE={s for s in REPS if any(INDEX[tuple(-x for x in SIGNS[j])] in s and
    SIGNS[j][0]*SIGNS[j][2]+SIGNS[j][1]*SIGNS[j][3]==0 for j in s)}
assert len(REPS)==49 and len(FIVE)==5


def check_classification():
    """Recompute the orbit cover and the bridge to the five local frames."""
    assert ANTI in REPS and ANTI not in FIVE
    # The antialigned cover requires three occupied cells.
    padded=0
    for size in (1,2):
        for support in combinations(range(16),size):
            remaining=set(range(16))-set(support)
            assert any(min(orbit(tuple(sorted(support+extra))))!=ANTI
                       for extra in combinations(sorted(remaining),3-size))
            padded+=1
    frames=[((0,1,14),(0,1),(-1,-1),False,15),
            ((1,2,13),(1,0),(1,-1),True,13),
            ((1,3,14),(0,1),(-1,-1),False,12),
            ((1,4,11),(0,1),(-1,1),False,11),
            ((1,7,8),(1,0),(1,1),True,8)]
    assert {frame[0] for frame in frames} == FIVE
    local_cells = []
    for support, axes, flip, exchange, third in frames:
        image = transformed(support, axes, flip, exchange)
        assert set(image) == {1, 14, third}
        local_cells.append(list(image))
    return dict(status='PASS',three_cell_subsets=560,orbits=len(REPS),
                ordinary_exclusion_orbits=43,retained_orbits=len(FIVE),
                antialigned_orbits=1,smaller_supports_padded=padded,
                local_frame_maps=len(frames),retained_supports=sorted(FIVE),
                local_sign_cells=sorted(local_cells))


def inverse_comparison(k,T,qn,qd):
    # q2(k/T) <= qn/qd. The quantities squared here are nonnegative.
    V=T*T-k*k
    assert V>0 and 0<=qn<=qd and qd>0
    N=2*T*T*qd+(qd-qn)*V
    return N*N<=8*T*T*V*qd*qd


@lru_cache(None)
def zeta_floor(b,c,S):
    qn=b*c;qd=(S-b)*(S-c)
    assert 0<=qn<=qd and qd>0
    if not inverse_comparison(2,3,qn,qd):return 2,3
    lo=2*ZDEN//3;hi=ZDEN-1
    assert inverse_comparison(lo,ZDEN,qn,qd)
    assert not inverse_comparison(hi,ZDEN,qn,qd)
    while hi-lo>1:
        mid=(lo+hi)//2
        if inverse_comparison(mid,ZDEN,qn,qd):lo=mid
        else:hi=mid
    if 3*lo<2*ZDEN:return 2,3
    return lo,ZDEN


def clip_halfplane(poly,A,B,C):
    """Clip a closed polygon to A*x+B*y <= C, keeping boundary points."""
    if not poly:return []
    out=[]
    previous=poly[-1];fp=A*previous[0]+B*previous[1]-C
    for current in poly:
        fc=A*current[0]+B*current[1]-C
        if (fp<=0)!=(fc<=0):
            t=fp/(fp-fc)
            out.append(tuple(previous[j]+t*(current[j]-previous[j]) for j in range(2)))
        if fc<=0:out.append(current)
        previous,fp=current,fc
    return out


def physical_polygon(box,exchange,cap):
    (bl,bh),(cl,ch)=box
    poly=[(bl,cl),(bh,cl),(bh,ch),(bl,ch)]
    poly=clip_halfplane(poly,F(1),F(1),cap)
    if exchange:poly=clip_halfplane(poly,F(1),F(-1),F(0))
    return sorted(set(poly))


def exact_int(q):
    assert q.denominator==1
    return q.numerator


def check_analytic_mode_lemma(data):
    assert data['mode_cap']=='3/4'
    w=data['analytic_mode_witness']
    assert w==[-6,-6,6,6,42,7,7,42]
    grid = grid_rows(ANTI)
    tr,rows=mode_coefficients([4*v for v in w],grid)
    modes=[(F(0),F(1)),(F(1),F(0)),(F(0),F(3,4)),(F(3,4),F(0))]
    low=min(F(A)+B*b+C*c+F(2,3)*tr for A,B,C in rows for b,c in modes)
    assert low>=1
    return dict(status='PASS',fixed_witnesses=1,a_max='1/4',
                verified_lower_margin=str(low/4),vertex_checks=len(rows)*len(modes))


def check_mode_witness(leaf, cell, exchange, coefficients, grid, support):
    """Check the affine lower bound on every response row and polygon vertex."""
    b, c, scale = cell
    trace, rows = coefficients
    box = [(F(b, scale), F(b + 1, scale)), (F(c, scale), F(c + 1, scale))]
    vertices = physical_polygon(box, exchange, F(1))
    location = f"D.3 support={support}, leaf={leaf['path'] or 'root'}, witness={leaf['witness']}"
    assert vertices, f"{location}: empty witness polygon"
    assert len(rows) == len(grid), f"{location}: missing response row"
    denominator = 2 * scale
    points = [(exact_int(x * denominator), exact_int(y * denominator)) for x, y in vertices]
    zp, zd = zeta_floor(b, c, scale)
    weak = leaf['reason'] == 'witness_strict_zeta'
    if weak:
        assert trace > 0 and 3*zp == 2*zd, (
            f"{location}: endpoint strictness requires positive trace and zeta=2/3, "
            f"found trace={trace}, zeta={F(zp, zd)}"
        )
    checks = 0
    for row, (A, B, C) in zip(grid, rows):
        offset = denominator * (zd*A + zp*trace)
        for x, y in points:
            value = offset + zd * (B*x + C*y)
            if value < 0 or (value == 0 and not weak):
                relation = '>=' if weak else '>'
                raise AssertionError(
                    f"{location}, row={row}, b={F(x, denominator)}, c={F(y, denominator)}: "
                    f"lower bound {F(value, denominator*zd)} (expected {relation} 0)"
                )
            checks += 1
    return checks


def check_modes(data):
    assert data['format'] == 'physical-strict-mode-cover-v3'
    assert data['small_cost_floor'] == '1/4096'
    assert data['local_cost_floor'] == '4/5' and data['local_d_max'] == '1/20'
    cases = data['cases']
    assert len(cases) == 48 and {tuple(case['support']) for case in cases} == REPS - {ANTI}
    stats = Counter(cases=len(cases))
    local_supports = set()
    for case in cases:
        support = tuple(case['support'])
        assert len(support) == 3 and all(type(i) is int for i in support)
        assert support == tuple(sorted(set(support)))
        symmetry = case.get('exchange_symmetry')
        if symmetry is not None:
            axes, flip = symmetry['axes'], symmetry['flip']
            assert sorted(axes) == [0, 1] and all(type(i) is int for i in axes)
            assert len(flip) == 2 and all(type(s) is int and s in (-1, 1) for s in flip)
            assert transformed(support, axes, flip, True) == support
            stats['mode_symmetry_cases'] += 1

        leaves = case['leaves']
        cells = cover_cells((leaf['path'] for leaf in leaves), f"D.3 support={support}")
        grid = grid_rows(support)
        bounds = [mode_coefficients(witness, grid) for witness in case['witnesses']]
        used = set()
        for index, b, c, level in cells:
            leaf = leaves[index]
            reason = leaf['reason']
            scale = 1 << level
            stats['leaves'] += 1
            stats[reason + '_leaves'] += 1
            if reason == 'simplex':
                assert b + c > scale
            elif reason == 'small_cost':
                assert 4096*(b+1)*(c+1) <= (scale-b-1)*(scale-c-1)
            elif reason == 'symmetry_mode':
                assert symmetry is not None and b > c + 1
            elif reason == 'local':
                assert support in FIVE
                assert 5*b*c > 4*(scale-b)*(scale-c)
                assert 20*(b+1-c) <= scale and 20*(c+1-b) <= scale
                local_supports.add(support)
            else:
                assert reason in ('witness', 'witness_strict_zeta')
                assert set(leaf) == {'path', 'reason', 'witness'}
                number = leaf['witness']
                assert type(number) is int and 0 <= number < len(bounds)
                stats['row_corner_checks'] += check_mode_witness(
                    leaf, (b, c, scale), symmetry is not None, bounds[number], grid, support
                )
                used.add(number)
        assert used == set(range(len(bounds)))
        stats['witnesses'] += len(bounds)
    assert local_supports == FIVE
    return dict(status='PASS', small_cost_floor=data['small_cost_floor'],
                local_cost_floor=data['local_cost_floor'], local_d_max=data['local_d_max'], **stats)


def clipped_polygon(x,y):
    # Vertices of [x0,x1] x [y0,y1] intersected with x <= y.
    vertices={(a,b) for a,b in product(x,y) if a<=b}
    lo=max(x[0],y[0]);hi=min(x[1],y[1])
    if lo<=hi:vertices.update(((lo,lo),(hi,hi)))
    return sorted(vertices)


def check_anti_witness(w, box, node=None, number=None):
    vertices = physical_polygon(box[:2], True, F(3, 4))
    assert vertices, f"D.3 antialigned node={node}: empty mode polygon"
    Q = max(x.denominator for vertex in vertices for x in vertex)
    P = max(x.denominator for interval in box[2:] for x in interval)
    modes = [(exact_int(b*Q), exact_int(c*Q)) for b, c in vertices]
    trace = witness_trace(w)
    checks = 0
    for label in range(3):
        start = 2 + 4*label
        ub, vb = box[start:start+2], box[start+2:start+4]
        us = clipped_polygon(*ub) if label == 0 else list(product(*ub))
        assert us, f"D.3 antialigned node={node}: empty response polygon for label {label+1}"
        for u, v in product(us, product(*vb)):
            row = tuple(exact_int(r*P) for r in u + v)
            A, B, C = affine_row(w, row, P)
            for b, c in modes:
                value = 3*(Q*A + b*B + c*C) + 2*trace*Q*P*P
                if value <= 0:
                    raise AssertionError(f"D.3 antialigned node={node}, witness={number}, "
                                         f"label={label+1}, u={u}, v={v}, b={F(b,Q)}, c={F(c,Q)}: "
                                         f"lower bound {F(value,3*Q*P*P)} (expected > 0)")
                checks += 1
    return checks


def check_anti(data):
    assert data['format'] == 'antialigned-modecap-cover-v2'
    assert data['status'] == 'COMPLETE_EXCLUSION' and data['pending'] == []
    assert data['zeta_lower'] == '2/3' and data['cost_lower'] == '1/4096'
    assert data['sign_cells'] == ANTI_SIGNS
    assert data['fundamental_domain'] == ['b<=c', 'u_1x<=u_1y']
    analytic = check_analytic_mode_lemma(data)
    # Exchange and negate to order b,c; exchange axes to order the first Alice response.
    assert [[-x for x in s[2:]+s[:2]] for s in ANTI_SIGNS] == ANTI_SIGNS
    assert [[s[1],s[0],s[3],s[2]] for s in ANTI_SIGNS] == [ANTI_SIGNS[i] for i in (0,2,1)]
    unit = (F(0), F(1))
    root = [unit, unit] + [(F(-1), F(0)) if sign < 0 else unit for row in ANTI_SIGNS for sign in row]
    tree, witnesses = data['tree'], data['witnesses']
    seen, used = set(), set()
    stats = Counter()

    def visit(i, box, depth):
        assert type(i) is int and 0 <= i < len(tree) and i not in seen, f"Invalid antialigned node {i}"
        seen.add(i)
        stats['nodes'] += 1
        stats['max_depth'] = max(stats['max_depth'], depth)
        node = tree[i]
        if 'children' in node:
            assert set(node) == {'axis', 'children'}
            axis, children = node['axis'], node['children']
            assert type(axis) is int and 0 <= axis < len(box)
            assert len(children) == 2 and children[0] != children[1]
            lo, hi = box[axis]
            mid = (lo+hi)/2
            for child, interval in zip(children, ((lo,mid), (mid,hi))):
                subbox = list(box)
                subbox[axis] = interval
                visit(child, subbox, depth+1)
            return
        reason = node['reason']
        stats['leaves'] += 1
        stats[reason] += 1
        if reason == 'analytic_mode':
            assert box[0][0] + max(box[0][0], box[1][0]) >= F(3,4)
        elif reason == 'simplex':
            assert box[0][0] + box[1][0] > 1
        elif reason == 'cost_lower':
            b, c = box[0][1], box[1][1]
            assert 4095*b*c + b + c - 1 < 0
        elif reason == 'symmetry_mode':
            assert box[0][0] > box[1][1]
        elif reason == 'symmetry_axis':
            assert box[2][0] > box[3][1]
        else:
            assert reason == 'witness' and set(node) == {'reason', 'witness'}
            wi = node['witness']
            assert type(wi) is int and 0 <= wi < len(witnesses)
            used.add(wi)
            stats['row_corner_checks'] += check_anti_witness(witnesses[wi], box, i, wi)
    visit(0, root, 0)
    assert seen == set(range(len(tree))) and used == set(range(len(witnesses)))
    assert data['stats']['visited'] == stats['nodes']
    for key in ('leaves','simplex','cost_lower','witness','symmetry_mode','symmetry_axis','analytic_mode'):
        assert data['stats'].get(key, 0) == stats[key]
    return dict(status='PASS', witnesses=len(witnesses), analytic_mode_lemma=analytic, **stats)


def compute(*,verbose=False):
    start = time.monotonic()
    path = HERE / 'certificates/global.json'
    data = read_certificate(path)
    assert data['format']=='appendix-d2-reduced-v2'
    classification=check_classification()
    if verbose:print('PASS: exhaustive support cover and local frame maps.',flush=True)
    mode=check_modes(data['mode_cover'])
    if verbose:print('PASS: ordinary mode covers.',flush=True)
    anti=check_anti(data['antialigned'])
    analytic = anti.pop('analytic_mode_lemma')
    if verbose:print('PASS: antialigned canonical-domain cover.',flush=True)
    bad=deepcopy(data['mode_cover']);bad['cases'][0]['leaves'].pop()
    negative=[expect_rejection('missing mode leaf',lambda:check_modes(bad))]
    bad=deepcopy(data['mode_cover']);bad['cases'][0]['witnesses'][0]=[0]*8
    negative.append(expect_rejection('zero mode witness',lambda:check_modes(bad)))
    bad=deepcopy(data['mode_cover']);bad['cases'][0]['exchange_symmetry']={'axes':[0,0],'flip':[1,1]}
    negative.append(expect_rejection('invalid support symmetry',lambda:check_modes(bad)))
    bad=deepcopy(data['mode_cover']);bad['local_d_max']='1/10'
    negative.append(expect_rejection('enlarged local domain',lambda:check_modes(bad)))
    bad=deepcopy(data['antialigned']);bad['tree'][0]['children'][1]=bad['tree'][0]['children'][0]
    negative.append(expect_rejection('duplicated anti subtree',lambda:check_anti(bad)))
    bad=deepcopy(data['antialigned']);bad['witnesses'][0]=[0]*8
    negative.append(expect_rejection('zero anti witness',lambda:check_anti(bad)))
    bad=deepcopy(data['antialigned']);bad['analytic_mode_witness']=[0]*8
    negative.append(expect_rejection('zero analytic mode witness',lambda:check_anti(bad)))
    bad=deepcopy(data['antialigned']);bad['mode_cap']='5/6'
    negative.append(expect_rejection('changed analytic mode cap',lambda:check_anti(bad)))
    bad=deepcopy(data['mode_cover'])
    case=next(c for c in bad['cases'] if any(r['reason']=='witness_strict_zeta' for r in c['leaves']))
    leaf=next(r for r in case['leaves'] if r['reason']=='witness_strict_zeta')
    case['witnesses'][leaf['witness']]=[0]*8
    negative.append(expect_rejection('zero trace for strict-visibility witness',lambda:check_modes(bad)))
    bad=deepcopy(data['mode_cover'])
    case=next(c for c in bad['cases'] if tuple(c['support']) in FIVE)
    case['leaves']=[{'path':'','reason':'local'}]
    negative.append(expect_rejection('uncertified whole-domain localization',lambda:check_modes(bad)))
    report=dict(status='PASS_GLOBAL_CERTIFICATE',scope='global support exclusion and localization only',
        publication_revision=PUBLICATION_REVISION,certificate_data_revision=2,
        manuscript_sections=['D.3', 'Lemma D.1'],
        computer_assisted=True,classification=classification,
        analytic_premises=['normalized moment and disk witness inequalities',
            'independent small-cost floor delta > 1/4096',
            'attainable benchmark and its piecewise inverse',
            'sign-cell concavity and target-preserving symmetries',
            'written a <= 1/4 antialigned lemma (also checked here)'],
        downstream_written_proofs=['D.4 averaging and integration','D.5 optimal-cost comparison'],
        certified_local_domain={'cost':'delta > 4/5','imbalance':'|b-c| <= 1/20'},
        analytic_mode_lemma=analytic,mode_cover=mode,antialigned=anti,negative_controls_rejected=negative,
        data_witnesses=mode['witnesses']+anti['witnesses'],fixed_analytic_witnesses=1,
        total_witnesses_including_analytic=mode['witnesses']+anti['witnesses']+1,
        total_leaves=mode['leaves']+anti['leaves'],
        certificate_bytes=path.stat().st_size,standard_library_only=True,
        floating_point_in_acceptance_tests=False,
        python_version=sys.version.split()[0],python_implementation=platform.python_implementation(),
        sha256=source_hashes(HERE, ['certificates/global.json', 'verify_global.py',
                                    'grid_witness.py', 'dyadic_cover.py', 'verification_io.py']),
        seconds=round(time.monotonic()-start,3))
    if verbose:print(json.dumps(report,indent=2))
    return report


if __name__ == '__main__':
    raise SystemExit('Run python verify.py to check all stages in order.')
