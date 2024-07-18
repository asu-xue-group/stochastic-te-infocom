import itertools

import numpy as np
from networkx import DiGraph
from graphs.srg_graph import Srg


# Return a set of edges that contains all the failed links if failure event q happened
def E_f(q: int, srg: list[Srg]):
    # Convert q to a binary array
    indicators = np.array([int(i) for i in bin(q)[2:]])
    indicators = np.insert(indicators, 0, np.zeros(len(srg) - len(indicators)))
    failed_srg = [srg[i].edges for i in range(len(indicators)) if indicators[i] == 1]
    failed_srg = list(itertools.chain.from_iterable(failed_srg))
    for x in failed_srg[:]:
        failed_srg.append(tuple(reversed(x)))
    return failed_srg


# Calculate the probability of failure event configuration z
def calc_pq(z: int, srg: list[Srg]):
    product = 1
    for i in range(len(z)):
        product *= z[i] * srg[i].prob + (1 - z[i]) * (1 - srg[i].prob)
    return product


# Calculate the edge-path mapping (L in the paper)
def calculate_l(G: DiGraph, paths: list):
    edges = list(G.edges.data())

    # Set up the dictionary that stores the edge-path mapping
    L = dict()
    for edge in edges:
        # Needs to add both forward and backward edges if undirected graph
        L[(edge[0], edge[1])] = set()
        # L[(edge[1], edge[0])] = set()
    for path_grp in paths:
        for path in path_grp:
            for i in range(len(path) - 2 + 1):
                L[tuple(path[i:i + 2])].add(tuple(path))
    return L


# Return an indicator that, if failure event q happened, whether the path r is affected
def y(r: tuple, q: int, srg: list[Srg], l: dict):
    # Convert q to a binary array
    indicators = np.array([int(i) for i in bin(q)[2:]])
    indicators = np.insert(indicators, 0, np.zeros(len(srg) - len(indicators)))
    failed_srg = [srg[i].edges for i in range(len(indicators)) if indicators[i] == 1]
    for f_srg in failed_srg:
        if r in l[f_srg[0]]:
            return 0
    return 1


# Return an indicator to show whether the path r uses the edge e
def L(l: dict, r: tuple, e: tuple):
    if r in l[e]:
        return 1
    else:
        return 0
