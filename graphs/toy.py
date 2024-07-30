import networkx as nx
from networkx import Graph
from graphs.srg_graph import *


def get_graph(alt=False):
    g = Graph()

    g.add_node(1, name='s1')
    g.add_node(2, name='s2')
    g.add_node(3, name='a')
    g.add_node(4, name='b')
    g.add_node(5, name='c')
    g.add_node(6, name='d')
    g.add_node(7, name='t1')
    g.add_node(8, name='t2')

    if not alt:
        g.add_edge(1, 3, cap=2, cost=1)
        g.add_edge(2, 5, cap=2, cost=1)
        g.add_edge(3, 4, cap=3.8, cost=0.8)
        g.add_edge(3, 5, cap=3.8, cost=2)
        g.add_edge(4, 6, cap=3.8, cost=3)
        g.add_edge(5, 6, cap=3.8, cost=0.5)
        g.add_edge(4, 7, cap=2, cost=1)
        g.add_edge(6, 8, cap=2, cost=1)
    else:
        g.add_edge(1, 3, cap=2, cost=0)
        g.add_edge(2, 5, cap=2, cost=0)
        g.add_edge(3, 4, cap=3.8, cost=0)
        g.add_edge(3, 5, cap=3.8, cost=0)
        g.add_edge(4, 6, cap=3.8, cost=0)
        g.add_edge(5, 6, cap=3.8, cost=0)
        g.add_edge(4, 7, cap=2, cost=0)
        g.add_edge(6, 8, cap=2, cost=0)
        g.add_edge(1, 7, cap=2, cost=0)
        g.add_edge(2, 8, cap=2, cost=0)

    commodities = [
        Commodity(1, 7, 4, 600),
        Commodity(2, 8, 4, 600)
    ]

    srg = [
        Srg(((3, 4), ), 0.90),
        Srg(((5, 6), ), 0.05)
    ]

    g = nx.to_directed(g)
    G = SrgGraph(g, commodities)
    G.srg = srg
    return G
