from collections import namedtuple
from itertools import islice

import networkx as nx
from networkx import DiGraph

Commodity = namedtuple('Commodity', ['s', 't', 'demand', 'budget'])
Srg = namedtuple('Srg', ['edges', 'prob'])


class SrgGraph:
    def __init__(self, graph: DiGraph, commodities: list[Commodity], srg: list[Srg]):
        self.graph: DiGraph = graph
        self.commodities: list[Commodity] = commodities
        self.srg: list[Srg] = srg

    # k-shortest paths from the source to destination
    # if k = 0, then return all possible paths
    def all_paths(self, k: int) -> list[list]:
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
