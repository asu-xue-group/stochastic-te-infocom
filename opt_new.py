import gurobipy as gp
import networkx as nx
from gurobipy import *
from networkx import DiGraph, Graph
import numpy as np
import itertools


# import ENV


# Return a set of edges that contains all the failed links if failure event q happened
def E_f(q: int, srg: list):
    # Convert q to a binary array
    indicators = np.array([int(i) for i in bin(q)[2:]])
    indicators = np.insert(indicators, 0, np.zeros(len(srg) - len(indicators)))
    failed_srg = [srg[i][0] for i in range(len(indicators)) if indicators[i] == 1]
    failed_srg = list(itertools.chain.from_iterable(failed_srg))
    for x in failed_srg[:]:
        failed_srg.append(tuple(reversed(x)))
    return failed_srg


# Calculate the probability of failure event configuration z
def calc_pq(z, srg):
    product = 1
    for i in range(len(z)):
        product *= z[i] * srg[i][1] + (1 - z[i]) * (1 - srg[i][1])
    return product


def solve_lp(commodities: list, srg: list, G: Graph):
    # with gp.Env(params=ENV.connection_params) as env:
    #     with gp.Model(env=env) as m:
    # META VARIABLES
    m = gp.Model()
    num_srg = len(srg)
    # These variables are used to index the commodities and SRGs (for Gurobi variables).
    # Actual data is stored in their respective variables
    I = range(len(commodities))
    Q = range(int(math.pow(2, num_srg)))
    E = G.edges()

    # Calculate the probability of each failure event
    p = np.zeros((len(Q),))
    for i, z in enumerate([list(i) for i in itertools.product([0, 1], repeat=num_srg)]):
        p[i] = calc_pq(z, srg)

    # Cache the nodes after removing the source and the destination of a commodity
    non_terminals = {}
    for i in I:
        all_nodes = set(G.nodes)
        all_nodes.remove(commodities[i][0][0])
        all_nodes.remove(commodities[i][0][1])
        non_terminals[i] = all_nodes

    # CONSTANTS
    beta = 0.1
    gamma = 1.0

    # VARIABLES
    # W^+_i(r)
    W_plus = m.addVars(I, E, name="W")
    # R^{+,q}_i(r)
    R_plus = m.addVars(I, Q, E, name="R")
    # delta = m.addVar(name='delta')
    # alpha
    alpha = m.addVar(name='alpha')
    # phi^q_i
    phi = m.addVars(Q, name='phi')

    # CONSTRAINTS
    # auxiliary one, Eq. 22
    m.addConstrs(phi[q] >= gp.quicksum(W_plus[i, *e1] for i in I for e1 in G.in_edges(commodities[i][0][1])) -
                 gp.quicksum(W_plus[i, *e2] for i in I for e2 in G.out_edges(commodities[i][0][1])) -
                 gp.quicksum(R_plus[i, q, *e3] for i in I for e3 in G.in_edges(commodities[i][0][1])) +
                 gp.quicksum(R_plus[i, q, *e4] for i in I for e4 in G.out_edges(commodities[i][0][1]))
                 - alpha for q in Q)

    # Eq. 23
    m.addConstrs(gp.quicksum(W_plus[i, *e1] for e1 in G.in_edges(v)) -
                 gp.quicksum(W_plus[i, *e2] for e2 in G.out_edges(v)) == 0
                 for i in I for v in non_terminals[i])

    # Eq. 24
    m.addConstrs(gp.quicksum(W_plus[i, *e1] for e1 in G.in_edges(commodities[i][0][1])) -
                 gp.quicksum(W_plus[i, *e2] for e2 in G.out_edges(commodities[i][0][1])) >= gamma * commodities[i][1]
                 for i in I)

    # Eq. 25
    m.addConstrs(gp.quicksum(R_plus[i, q, *e1] for e1 in G.in_edges(v)) -
                 gp.quicksum(R_plus[i, q, *e2] for e2 in G.out_edges(v)) == 0
                 for i in I for v in non_terminals[i] for q in Q)

    # Eq. 26
    m.addConstrs(gp.quicksum(W_plus[i, e[0], e[1]] + W_plus[i, e[1], e[0]] for i in I) <= G[e[0]][e[1]]['cap']
                 for e in E)

    # Eq. 27
    m.addConstrs(gp.quicksum(R_plus[i, q, e[0], e[1]] + R_plus[i, q, e[1], e[0]] for i in I) <= G[e[0]][e[1]]['cap']
                 for e in E for q in Q)

    # Eq. 28
    m.addConstrs(R_plus[i, q, *e] <= W_plus[i, *e] for e in E for q in Q for i in I)

    # Eq. 31
    m.addConstrs(R_plus[i, q, *e] == 0 for q in Q for e in E_f(q, srg) for i in I)

    m.setObjective(alpha + (1 / (1 - beta)) * gp.quicksum(p[q] * phi[q] for q in Q), GRB.MINIMIZE)
    m.update()
    # m.write('test.lp')

    # Optimize model
    m.optimize()

    # Print maximized profit value
    print('Minimized result:', m.objVal)
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
                print(f'({k[1]}, {k[2]}), {v.x:.3f} ', end='')
        print('\n')

    print('\n==========================================')
    print('Recovery Flow')
    for q in Q:
        indicators = np.array([int(i) for i in bin(q)[2:]])
        indicators = np.insert(indicators, 0, np.zeros(len(srg) - len(indicators)))
        failed_srg = [srg[i][0] for i in range(len(indicators)) if indicators[i] == 1]
        print(f'Failed SRG {failed_srg}')
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
                    print(f'({k[2]}, {k[3]}), {v.x:.3f} ', end='')
            print('\n')

        print(f'Total throughput: {total:.3f}')
        print(f'----------------------------------------')
    #
    # print('\n==========================================')
    # for i in I:
    #     cvar = alpha[i].x - (1 / beta) * gp.quicksum(p[q] * phi[i, q].x for q in Q)
    #     print(f'Commodity {i} CVaR: {cvar}')
    #     print(f'Commodity {i} Eq. 39 LHS = {commodities[i][1] - cvar}')
    #
    # print('delta:', delta.x)
