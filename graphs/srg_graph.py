from networkx import Graph, DiGraph
from itertools import islice
from collections import namedtuple
import networkx as nx

Edge = namedtuple('Edge', ['u', 'v'])
Commodity = namedtuple('Commodity', ['edge', 'demand', 'budget'])
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
                    tmp = list(nx.all_simple_paths(self.graph, c.edge.u, c.edge.v))
                    results.append(tmp)
                return results
            else:
                results = []
                for c in self.commodities:
                    tmp = list(islice(nx.shortest_simple_paths(self.graph, c.edge.u, c.edge.v), k))
                    results.append(tmp)
                return results
        except nx.NetworkXNoPath:
            return []
