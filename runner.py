import matplotlib.pyplot as plt
import networkx as nx
import pickle
import random
from graphs.ItalyNet import italy_net

from opt_test import solve_lp


def L(edge: tuple, path: list, mapping: dict) -> bool:
    if edge not in mapping:
        return False
    else:
        return tuple(path) in mapping[edge]


def main():
    with open('test.pk', 'rb') as f:
        # G: nx.Graph = pickle.load(f)
        # G = nx.to_directed(G)
        G = italy_net()

        nx.draw(G, with_labels=True, font_weight='bold')
        plt.show()

        for edge in G.edges:
            if random.random() < 0.5:
                capacity = 300
            else:
                capacity = 200
            nx.set_edge_attributes(G, {edge: {'cap': capacity}})

        # Commodities
        commodities = [
            ((0, 8), 500),
            ((1, 10), 450),
            ((4, 13), 300),
        ]

        # K-shortest paths for the commodities
        paths = []
        k = 3
        for commodity in commodities:
            for counter, path in enumerate(nx.shortest_simple_paths(G, source=commodity[0][0],
                                                                    target=commodity[0][1])):
                if counter == 0:
                    paths.append([tuple(path)])
                else:
                    paths[-1].append(tuple(path))
                if counter == k-1:
                    paths[-1] = tuple(paths[-1])
                    break

        # Shared risk groups
        srg = [((0, 1), 0.4), ((6, 10), 0.5), ((10, 13), 0.6)]

        solve_lp(commodities, paths, srg, G)


if __name__ == '__main__':
    main()
