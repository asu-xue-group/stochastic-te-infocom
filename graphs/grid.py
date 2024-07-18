import networkx as nx
from numpy.random import Generator, PCG64
from graphs.srg_graph import *


# 3x3 -> 12
# 4x4 -> 184
# 5x5 -> 8512
# 6x6 -> 1262816


def get_graph(size, seed):
    g = nx.grid_2d_graph(size, size)

    rand = Generator(PCG64(seed))
    for e in g.edges:
        g[e[0]][e[1]]['cap'] = max([0, rand.normal(1, 0.5)])
        g[e[0]][e[1]]['cost'] = max([0, rand.normal(1, 0.1)])

    commodities = [
        Commodity((0, 0), (size - 1, size - 1), 1, size * 10),
        Commodity((size - 1, 0), (0, size - 1), 1, size * 10),
        Commodity(((size - 1) // 2, 0), ((size - 1) // 2, size - 1), 1, size * 10)
    ]

    # Randomly pick SRGs
    fails = rand.choice(list(g.edges), size=size, replace=False)
    srg = []
    for f in fails:
        srg.append(Srg(((tuple(f[0]), tuple(f[1])),), rand.random()))
    g = nx.to_directed(g)

    return SrgGraph(g, commodities, srg)


get_graph(3, 1)