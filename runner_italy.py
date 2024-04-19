import matplotlib.pyplot as plt
import networkx as nx
import pickle
import random
from numpy.random import Generator, PCG64
from graphs.ItalyNet import italy_net

from opt_test import solve_lp


def L(edge: tuple, path: list, mapping: dict) -> bool:
    if edge not in mapping:
        return False
    else:
        return tuple(path) in mapping[edge]


def main():
    with open('test.pk', 'rb') as f:
        # Open a network from file
        # G: nx.Graph = pickle.load(f)
        # G = nx.to_directed(G)
        # Open a predefined network from classical papers
        G = italy_net()

        # Draw the network / sanity check
        nx.draw(G, with_labels=True, font_weight='bold')
        plt.show()

        # Assign random capacities to the edges
        seed = 0
        rng = Generator(PCG64(seed))
        for edge in G.edges:
            # capacity = rng.normal(400, 50)
            capacity = 400
            nx.set_edge_attributes(G, {edge: {'cap': capacity}})

        # Commodities
        commodities = [
            ((0, 8), 450),
            ((1, 10), 400),
            ((0, 13), 300),
            ((7, 12), 500),
            ((6, 11), 500)
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
        srg = [((0, 1), 0.6), ((6, 10), 0.8), ((10, 13), 0.9)]
        # srg = [((0, 10), 0.4), ((9, 5), 0.5), ((2, 1), 0.6)]

        # Solve the LP
        solve_lp(commodities, paths, srg, G)


if __name__ == '__main__':
    main()
