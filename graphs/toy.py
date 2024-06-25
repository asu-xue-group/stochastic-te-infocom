from networkx import Graph


def toy() -> Graph:
    g = Graph()

    g.add_node(1, name='s1')
    g.add_node(2, name='s2')
    g.add_node(3, name='a')
    g.add_node(4, name='b')
    g.add_node(5, name='c')
    g.add_node(6, name='d')
    g.add_node(7, name='t1')
    g.add_node(8, name='t2')

    g.add_edge(1, 3, cap=2)
    g.add_edge(2, 4, cap=2)
    g.add_edge(3, 4, cap=3.8)
    g.add_edge(3, 5, cap=3.8)
    g.add_edge(4, 6, cap=3.8)
    g.add_edge(5, 6, cap=3.8)
    g.add_edge(5, 7, cap=2)
    g.add_edge(6, 8, cap=2)

    return g
