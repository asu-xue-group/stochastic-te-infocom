import networkx as nx
import numpy as np
from numpy.random import Generator, PCG64
from graphs.srg_graph import *


def get_graph(n, alpha=None, beta=None, seed=None):
    if alpha is None:
        alpha = 0.4
    if beta is None:
        beta = 0.1

    g = nx.waxman_graph(n, beta, alpha, seed=seed)

    rand = Generator(PCG64(seed))
    for e in g.edges:
        g[e[0]][e[1]]['cap'] = max([0, rand.normal(1, 0.5)])
        g[e[0]][e[1]]['cost'] = max([0, rand.normal(1, 0.1)])

    # Randomly pick s and t
    commodities = []
    while len(commodities) < 3:
        s = rand.integers(0, n)
        t = rand.integers(0, n)
        if nx.has_path(g, s, t):
            commodities.append(Commodity(s, t, 1, n * 10))

    # Randomly pick SRGs
    # The number of SRG is given by log(n)
    fails = rand.choice(list(g.edges), size=int(np.ceil(np.log10(n))), replace=False)
    srg = []
    for f in fails:
        srg.append(Srg(((f[0], f[1]),), rand.random()))
    g = nx.to_directed(g)

    return SrgGraph(g, commodities, srg)

