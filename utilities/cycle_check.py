import networkx as nx
from gurobipy import tupledict
from networkx import DiGraph


def check_cycle(G: DiGraph, flows: tupledict):
    ng = {}

    for k, v in flows.items():
        if v.x > 0:
            if k[0] not in ng:
                ng[k[0]] = DiGraph()
                ng[k[0]].add_nodes_from(G)
            ng[k[0]].add_edge(k[1], k[2])

    for _, H in ng.items():
        try:
            nx.find_cycle(H, orientation='original')
            # If the execution reaches this point, there is a cycle
            return True
        except nx.NetworkXNoCycle:
            continue

    return False
