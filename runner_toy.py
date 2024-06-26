import matplotlib.pyplot as plt
import networkx as nx
from graphs.toy import toy
from lp_solvers.p2_opt import solve_p2
from lp_solvers.p4_opt import solve_p4


def L(edge: tuple, path: list, mapping: dict) -> bool:
    if edge not in mapping:
        return False
    else:
        return tuple(path) in mapping[edge]


def main():
    G = toy()
    G = nx.to_directed(G)

    # Draw the network / sanity check
    # nx.draw(G, with_labels=True, font_weight='bold')
    # plt.show()

    # Commodities
    commodities = [
        ((1, 7), 2),
        ((2, 8), 2)
    ]

    # Shared risk groups
    srg = [(((3, 5),), 0.95), (((4, 6),), 0.05)]

    # Solve the LP
    opt_val = solve_p2(commodities, srg, G)

    print('********************************************')

    solve_p4(commodities, srg, G, opt_val)


if __name__ == '__main__':
    main()
