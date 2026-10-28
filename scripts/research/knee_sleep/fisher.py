"""One-sided Fisher exact test for a 2x2 table (no scipy in the project env).

Table [[a, b], [c, d]]: rows = group 1 / group 2, columns = with feature / without.
fisher_greater gives P(X >= a) under the hypergeometric null with fixed margins,
i.e. the test that group 1 has the feature more often than group 2.
"""
from math import comb


def fisher_greater(a, b, c, d):
    r1, c1, n = a + b, a + c, a + b + c + d
    denom = comb(n, c1)
    hi = min(r1, c1)
    return sum(comb(r1, x) * comb(n - r1, c1 - x) for x in range(a, hi + 1)) / denom


def odds_ratio(a, b, c, d):
    if b * c == 0:
        return float('inf') if a * d else float('nan')
    return a * d / (b * c)


if __name__ == '__main__':
    # self-check against known values: tea-tasting table [[3,1],[1,3]] -> 0.2429
    assert abs(fisher_greater(3, 1, 1, 3) - 0.24285714) < 1e-6
    assert abs(fisher_greater(0, 5, 0, 5) - 1.0) < 1e-12
    print('ok')
