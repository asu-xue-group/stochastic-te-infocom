from collections import namedtuple, Counter
from itertools import islice

import networkx as nx
from networkx import DiGraph
import more_itertools as mit

Commodity = namedtuple('Commodity', ['s', 't', 'demand', 'budget'])
Srg = namedtuple('Srg', ['edges', 'prob'])


class SrgGraph:
    def __init__(self, graph: DiGraph, commodities: list[Commodity]):
        self.graph: DiGraph = graph
        self.commodities: list[Commodity] = commodities
        self.srg = None

    # k-shortest paths from the source to destination
    # if k = 0, then return all possible paths
    def k_paths(self, k: int) -> list[list]:
        if k < 0:
            return []
        try:
            if k == 0:
                results = []
                for c in self.commodities:
                    tmp = list(nx.all_simple_paths(self.graph, c.s, c.t))
                    results.append(tmp)
                return results
            else:
                results = []
                for c in self.commodities:
                    tmp = list(islice(nx.shortest_simple_paths(self.graph, c.s, c.t), k))
                    results.append(tmp)
                return results
        except nx.NetworkXNoPath:
            return []

    # Generate m SRGs among the paths specified
    def generate_srg(self, paths, m, rand):
        paths_tuple = []
        for p in paths:
            for pp in p:
                paths_tuple.extend(mit.windowed(pp, n=2, step=1))

        c = Counter(paths_tuple)
        srg_edge = c.most_common(m)

        srg = []
        for e in srg_edge:
            srg.append(Srg((e[0],), rand.random() * 0.5))

        self.srg = srg
