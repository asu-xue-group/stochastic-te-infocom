from networkx import Graph


def italy_net():
    graph = Graph()

    # Nodes
    graph.add_node(0, name='Turim')
    graph.add_node(1, name='Milan')
    graph.add_node(2, name='Trento')
    graph.add_node(3, name='Genoa')
    graph.add_node(4, name='Venice')
    graph.add_node(5, name='Bologne')
    graph.add_node(6, name='Florence')
    graph.add_node(7, name='Pescara')
    graph.add_node(8, name='Roma')
    graph.add_node(9, name='Cagliari')
    graph.add_node(10, name='Naples')
    graph.add_node(11, name='Bari')
    graph.add_node(12, name='Palermo')
    graph.add_node(13, name='Calabria')

    # Edges
    graph.add_edge(0, 1)
    graph.add_edge(0, 3)
    graph.add_edge(0, 5)
    graph.add_edge(1, 2)
    graph.add_edge(1, 3)
    graph.add_edge(1, 4)
    graph.add_edge(1, 5)
    graph.add_edge(1, 6)
    graph.add_edge(1, 8)
    graph.add_edge(1, 10)
    graph.add_edge(2, 4)
    graph.add_edge(3, 6)
    graph.add_edge(3, 9)
    graph.add_edge(4, 5)
    graph.add_edge(5, 6)
    graph.add_edge(5, 10)
    graph.add_edge(6, 7)
    graph.add_edge(6, 8)
    graph.add_edge(6, 10)
    graph.add_edge(7, 10)
    graph.add_edge(7, 11)
    graph.add_edge(8, 10)
    graph.add_edge(9, 8)
    graph.add_edge(9, 10)
    graph.add_edge(10, 11)
    graph.add_edge(10, 12)
    graph.add_edge(10, 13)
    graph.add_edge(11, 13)
    graph.add_edge(13, 12)

    return graph

