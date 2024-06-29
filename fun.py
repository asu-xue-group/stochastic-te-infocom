from graphs.toy import toy
from utilities.cvar_calc import cvar
from utilities.fileio import read_W
import networkx as nx

if __name__ == '__main__':

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
    I = range(len(commodities))
    W = read_W(G, I, '0.94.txt')

    beta = 0
    res = cvar(commodities, srg, G, W, beta)

    print(f'CVaR({beta}) = {res}')
