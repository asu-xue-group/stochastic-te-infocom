from networkx import DiGraph


def toy() -> DiGraph:
    g = DiGraph()

    g.add_node(1, name='s1')
    g.add_node(2, name='s2')
    g.add_node(3, name='a')
    g.add_node(4, name='b')
    g.add_node(5, name='t1')
    g.add_node(6, name='t2')

    g.add_edge(1, 3, cap=1.5)
    g.add_edge(1, 4, cap=1.5)
    g.add_edge(2, 3, cap=2)
    g.add_edge(3, 4, cap=2)
    g.add_edge(3, 6, cap=1.5)
    g.add_edge(4, 5, cap=2)
    g.add_edge(4, 6, cap=1.5)

    return g
