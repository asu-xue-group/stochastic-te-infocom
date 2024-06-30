import pickle

import networkx as nx


def dist(x, y):
    return sum(abs(a - b) for a, b in zip(x, y))


G = nx.waxman_graph(15, 0.5, 0.6, metric=dist)

with open('test.pk', 'wb') as f:
    pickle.dump(G, f, pickle.HIGHEST_PROTOCOL)
