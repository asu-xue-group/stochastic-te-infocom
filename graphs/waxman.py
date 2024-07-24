import networkx as nx
import numpy as np
from numpy.random import Generator, PCG64
import more_itertools as mit
from graphs.srg_graph import *


def get_graph(n, alpha=None, beta=None, seed=None, rand=None):
    if alpha is None:
        alpha = 0.4
    if beta is None:
        beta = 0.1

    g = nx.waxman_graph(n, beta, alpha, seed=seed)

    if not rand:
        rand = Generator(PCG64(seed))

    for e in g.edges:
        g[e[0]][e[1]]['cap'] = max([0, rand.normal(1, 0.5)])
        g[e[0]][e[1]]['cost'] = max([0, rand.normal(1, 0.1)])

    # Randomly pick s and t
    commodities = []
    while len(commodities) < 3:
        s = int(rand.integers(0, n))
        t = int(rand.integers(0, n))
        if nx.has_path(g, s, t):
            commodities.append(Commodity(s, t, 2, n*1.5))

    g = nx.to_directed(g)
    return SrgGraph(g, commodities)

