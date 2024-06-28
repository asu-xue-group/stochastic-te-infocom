import math

import numpy as np


def print_flows(G, W_plus, R_plus, commodities, m, srg, p):
    num_srg = len(srg)
    I = range(len(commodities))
    Q = range(int(math.pow(2, num_srg)))
    E = G.edges()

    # Print maximized profit value
    print('Optimized result:', m.objVal)
    #
    # Results in a more readable format
    print('\n==========================================')
    print('Working Flow')
    # for i in I:
    #     for r in R:
    #         print(f'Commodity {i}, route {paths[i][r]}: {W_plus[i, r].x}')

    check = all([sum([W_plus[i, *e].x for i in I]) <= G[e[0]][e[1]]['cap'] for e in E])
    print(f'Capacity check: {check}')
    for i in I:
        sat = (sum([W_plus[i, *e1].x for e1 in G.in_edges(commodities[i][0][1])])
               - sum([W_plus[i, *e2].x for e2 in G.out_edges(commodities[i][0][1])]))
        print(f'Commodity {i} satisfied: {sat} out of {commodities[i][1]}')

        print(f'Flow for commodity {i}: ', end='')
        for k, v in W_plus.items():
            if k[0] == i and v.x > 0:
                print(f'({k[1]}, {k[2]}), {v.x:.3f} | ', end='')
        print('\n')

    print('\n==========================================')
    print('Recovery Flow')
    for q in Q:
        indicators = np.array([int(i) for i in bin(q)[2:]])
        indicators = np.insert(indicators, 0, np.zeros(len(srg) - len(indicators)))
        failed_srg = [srg[i][0] for i in range(len(indicators)) if indicators[i] == 1]
        print(f'{q}-th case')
        print(f'Failed SRG {failed_srg}')
        print(f'Probability: {p[q]:.4f}')
        check = all(
            [sum([R_plus[i, q, *e].x for i in I]) <= G[e[0]][e[1]]['cap'] for e in E
             for q in Q])
        print(f'Capacity check: {check}')
        total = 0
        for i in I:
            # for r in R:
            #     print(f'Commodity {i}, route {paths[i][r]}: {R_plus[i, q, r].x}')
            sat = (sum([R_plus[i, q, *e3].x for e3 in G.in_edges(commodities[i][0][1])])
                   - sum([R_plus[i, q, *e4].x for e4 in G.out_edges(commodities[i][0][1])]))
            print(f'Commodity {i} satisfied: {sat:.3f} out of {commodities[i][1]}')
            total = total + sat

            print(f'Flow for commodity {i}: ', end='')
            for k, v in R_plus.items():
                if k[0] == i and k[1] == q and v.x > 0:
                    print(f'({k[2]}, {k[3]}), {v.x:.3f} | ', end='')
            print('\n')

        print(f'Total throughput: {total:.3f}')
        print(f'----------------------------------------')
