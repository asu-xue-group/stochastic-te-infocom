import itertools

import numpy as np


# Return a set of edges that contains all the failed links if failure event q happened
def E_f(q: int, srg: list):
    # Convert q to a binary array
    indicators = np.array([int(i) for i in bin(q)[2:]])
    indicators = np.insert(indicators, 0, np.zeros(len(srg) - len(indicators)))
    failed_srg = [srg[i][0] for i in range(len(indicators)) if indicators[i] == 1]
    failed_srg = list(itertools.chain.from_iterable(failed_srg))
    for x in failed_srg[:]:
        failed_srg.append(tuple(reversed(x)))
    return failed_srg


# Calculate the probability of failure event configuration z
def calc_pq(z, srg):
    product = 1
    for i in range(len(z)):
        product *= z[i] * srg[i][1] + (1 - z[i]) * (1 - srg[i][1])
    return product
