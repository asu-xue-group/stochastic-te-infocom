from utilities.cvar_calc import *


def print_flows(G: SrgGraph, W, R, p):
    srg = G.srg
    commodities = G.commodities
    g = G.graph
    num_srg = len(srg)
    I = range(len(commodities))
    Q = range(int(math.pow(2, num_srg)))

    # Results in a more readable format
    print('\n==========================================')
    print('Working Flow')
    # check = all([sum([W_plus[i, e[0], e[1]] for i in I]) <= G[e[0]][e[1]]['cap'] for e in E])
    # print(f'Capacity check: {check}')
    for i in I:
        sat = (sum([W[i, e[0], e[1]] for e in g.in_edges(commodities[i].edge.v)])
               - sum([W[i, e[0], e[1]] for e in g.out_edges(commodities[i].edge.v)]))
        print(f'Commodity {i} satisfied: {sat} out of {commodities[i].demand}')

        print(f'Flow for commodity {i}: ', end='')
        for k, v in W.items():
            if k[0] == i and v > 0:
                print(f'({k[1]}, {k[2]}), {v:.3f} | ', end='')
        print('\n')

    if R is not None:
        print('\n==========================================')
        print('Recovery Flow')
        ext = 0
        for q in Q:
            indicators = np.array([int(i) for i in bin(q)[2:]])
            indicators = np.insert(indicators, 0, np.zeros(len(srg) - len(indicators)))
            failed_srg = [srg[i].edges for i in range(len(indicators)) if indicators[i] == 1]
            print(f'{q}-th case')
            print(f'Failed SRG {failed_srg}')
            print(f'Probability: {p[q]:.4f}')
            # check = all(
            #     [sum([R_plus[i, q, e[0], e[1]] for i in I]) <= G[e[0]][e[1]]['cap'] for e in E
            #      for q in Q])
            # print(f'Capacity check: {check}')
            total = 0
            for i in I:
                sat = (sum([R.get((i, q, e[0], e[1]), 0) for e in g.in_edges(commodities[i].edge.v)])
                       - sum([R.get((i, q, e[0], e[1]), 0) for e in g.out_edges(commodities[i].edge.v)]))
                print(f'Commodity {i} satisfied: {sat:.3f} out of {commodities[i].demand}')
                total = total + sat

                print(f'Flow for commodity {i}: ', end='')
                for k, v in R.items():
                    if k[0] == i and k[1] == q and v > 0:
                        print(f'({k[2]}, {k[3]}), {v:.3f} | ', end='')
                print('\n')

            ext += total * p[q]
            print(f'Total throughput = {total:.3f}')
            print(f'----------------------------------------')
        print(f'Expected throughput = {ext:.3f}')


def print_flows_te(G: SrgGraph, W, paths, p, beta):
    srg = G.srg
    commodities = G.commodities
    g = G.graph
    num_srg = len(srg)
    I = range(len(commodities))
    l = calculate_l(g, paths)
    Q = range(int(math.pow(2, num_srg)))
    R = get_R(paths)

    sat = [np.sum([W[i, r] for r in range(len(paths[0]))]) for i in I]
    for i in I:
        print(f'Commodity {i} satisfied: {sat[i]:.3f} out of {commodities[i].demand}')
        for r in R[i]:
            print(f'------ Path {paths[i][r]} has flow {W[i, r]:.3f}')

    ext = np.sum([p[q] * np.sum([W[i, r] * y(tuple(paths[i][r]), q, srg, l) for i in I for r in R[i]]) for q in Q])
    print(f'Expected throughput={ext:.3f}')
    cvar, alpha = cvar_te(G, paths, beta, p, W)
    print(f'CVaR({beta})={cvar:.3f}, alpha={alpha:.3f}')
    print()
