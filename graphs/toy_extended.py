import networkx as nx
from networkx import Graph
from graphs.srg_graph import *


def get_graph():
    g = Graph()

    g.add_node(1)
    g.add_node(2)
    g.add_node(3)
    g.add_node(4)
    g.add_node(5)
    g.add_node(6)
    g.add_node(7)
    g.add_node(8)
    g.add_node(9)
    g.add_node(10)
    g.add_node(11)
    g.add_node(12)
    g.add_node(13)
    g.add_node(14)
    g.add_node(15)

    g.add_edge(1, 3, cap=3, cost=1)
    g.add_edge(1, 4, cap=10, cost=0.5)
    g.add_edge(1, 7, cap=3, cost=10)
    g.add_edge(1, 9, cap=3, cost=2)
    g.add_edge(1, 10, cap=3, cost=8)
    g.add_edge(2, 4, cap=2, cost=1)
    g.add_edge(2, 8, cap=2, cost=10)
    g.add_edge(2, 12, cap=2, cost=1)
    g.add_edge(2, 13, cap=2, cost=8)
    g.add_edge(3, 4, cap=3.8, cost=0.8)
    g.add_edge(3, 5, cap=3.7, cost=2)
    g.add_edge(4, 6, cap=3.6, cost=3)
    g.add_edge(5, 6, cap=3.5, cost=0.5)
    g.add_edge(5, 7, cap=3, cost=1)
    g.add_edge(5, 11, cap=3, cost=2)
    g.add_edge(6, 8, cap=2, cost=1)
    g.add_edge(6, 14, cap=2, cost=2)
    g.add_edge(7, 10, cap=3, cost=8)
    g.add_edge(7, 11, cap=3, cost=2)
    g.add_edge(8, 13, cap=2, cost=8)
    g.add_edge(8, 15, cap=2, cost=2)
    g.add_edge(14, 15, cap=2, cost=2)

    # Convert to a directed representation of the graph
    g = nx.to_directed(g)

    commodities = [
        Commodity(Edge(1, 7), 3, 6),
        Commodity(Edge(2, 8), 3, 6),
        Commodity(Edge(9, 11), 3, 8)
    ]

    srg = [
        Srg(((3, 5),), 0.95),
        Srg(((4, 6),), 0.05),
        Srg(((1, 4),), 0.20)
    ]

    return SrgGraph(g, commodities, srg)
