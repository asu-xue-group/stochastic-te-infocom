from typing import List, Any

import matplotlib.pyplot as plt
import networkx as nx
import pickle
import random


def L(edge: tuple, path: list, mapping: dict) -> bool:
    if edge not in mapping:
        return False
    else:
        return tuple(path) in mapping[edge]


def main():
    with open('test.pk', 'rb') as f:
        G: nx.Graph = pickle.load(f)

        nx.draw(G, with_labels=True, font_weight='bold')
        plt.show()

        edges = list(G.edges.data())
        paths = list(nx.all_shortest_paths(G, source=0, target=12))

        # Set up the dictionary that stores the edge-path mapping
        temp = dict()
        for edge in edges:
            # Needs to add both forward and backward edges
            temp[(edge[0], edge[1])] = set()
            temp[(edge[1], edge[0])] = set()
        for path in paths:
            for i in range(len(path) - 2 + 1):
                temp[tuple(path[i:i+2])].add(tuple(path))

        print(edges)
        print(paths)

        print(L((0, 11), [0, 11, 12], temp))
        print(L((0, 11), [0, 11, 15], temp))
        print(L((5, 6), [0, 11, 15], temp))
        print(L((11, 12), [0, 11, 12], temp))

        for edge in G.edges:
            if random.random() < 0.5:
                capacity = 300
            else:
                capacity = 200
            nx.set_edge_attributes(G, {edge: {'cap': capacity}})
        #
        # weights = {
        #     (5, 3): {'cap': 200, 'prob': 0.995},
        #     (13, 4): {'cap': 500, 'prob': 1.00},
        #     (0, 10): {'cap': 150}
        # }
        # nx.set_edge_attributes(G, weights)
        print(G[0][10]['cap'])
        print(G[5][3]['cap'])


if __name__ == '__main__':
    main()
