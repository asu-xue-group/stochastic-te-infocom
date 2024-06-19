import gurobipy as gp
from gurobipy import *
from networkx import DiGraph
import numpy as np


# import ENV

#
# # Calculate the edge-path mapping (L in the paper)
# def calculate_l(G: DiGraph, paths: list):
#     edges = list(G.edges.data())
#
#     # Set up the dictionary that stores the edge-path mapping
#     L = dict()
#     for edge in edges:
#         # Needs to add both forward and backward edges if undirected graph
#         L[(edge[0], edge[1])] = set()
#         # L[(edge[1], edge[0])] = set()
#     for path_grp in paths:
#         for path in path_grp:
#             for i in range(len(path) - 2 + 1):
#                 L[tuple(path[i:i + 2])].add(tuple(path))
#     return L
#
#
# # Return an indicator that, if failure event q happened, whether the path r is affected
# def y(r: tuple, q: int, srg: list, l: dict):
#     # Convert q to a binary array
#     indicators = np.array([int(i) for i in bin(q)[2:]])
#     indicators = np.insert(indicators, 0, np.zeros(len(srg) - len(indicators)))
#     failed_srg = [srg[i] for i in range(len(indicators)) if indicators[i] == 1]
#     for f_srg in failed_srg:
#         if r in l[f_srg[0]]:
#             return 0
#     return 1
#
#
# # Return an indicator to show whether the path r uses the edge e
# def L(l: dict, r: tuple, e: tuple):
#     if r in l[e]:
#         return 1
#     else:
#         return 0
#

# Calculate the probability of failure event configuration z
def calc_pq(z, srg):
    product = 1
    for i in range(len(z)):
        product *= z[i] * srg[i][1] + (1 - z[i]) * (1 - srg[i][1])
    return product


def solve_lp(commodities: list, paths: list, srg: list, G: DiGraph):
    # with gp.Env(params=ENV.connection_params) as env:
    #     with gp.Model(env=env) as m:
    # META VARIABLES
    m = gp.Model()
    num_srg = len(srg)
    # These variables are used to index the commodities, paths, and SRGs (for Gurobi variables).
    # Actual data is stored in their respective variables
    I = range(len(commodities))
    Q = range(int(math.pow(2, num_srg)))
    # R = range(len(paths[0]))
    # l = calculate_l(G, paths)
    E = G.edges()
    # num_edges = range(G.number_of_edges())

    # Calculate the probability of each failure event
    p = np.zeros((len(Q),))
    for i, z in enumerate([list(i) for i in itertools.product([0, 1], repeat=3)]):
        p[i] = calc_pq(z, srg)

    # Cache the nodes after removing the source and the destination of a commodity
    non_terminals = {}
    for i in I:
        all_nodes = set(G.nodes)
        all_nodes.remove(commodities[i][0][0])
        all_nodes.remove(commodities[i][0][1])
        non_terminals[i] = all_nodes

    # CONSTANTS
    beta = 0.95

    # VARIABLES
    gamma = m.addVar(name='gamma')
    # W^+_i(e)
    W_plus = m.addVars(I, E, name="W")
    # R^{+,q}_i(r)
    # R_plus = m.addVars(I, Q, R, name="R")
    # alpha_i
    # alpha = m.addVars(I, name='alpha')
    # phi^q_i
    # phi = m.addVars(I, Q, name='phi')

    # Auxiliary problem
    # Eq. 5
    m.addConstrs(gp.quicksum(W_plus[i, *e1] for e1 in G.in_edges(v)) -
                 gp.quicksum(W_plus[i, *e2] for e2 in G.out_edges(v)) == 0
                 for i in I for v in non_terminals[i])

    # Eq. 5
    m.addConstrs(gp.quicksum(W_plus[i, *e1] for e1 in G.in_edges(commodities[i][0][1])) -
                 gp.quicksum(W_plus[i, *e2] for e2 in G.out_edges(commodities[i][0][1])) >= gamma * commodities[i][1]
                 for i in I)

    # CONSTRAINTS
    # commodities = i -> ((s, t), d)
    # paths = i -> [path1, path2, ...]
    # srg = [((u, v), fail prob), ...]
    # Eq. 39
    # m.addConstrs(commodities[i][1] - alpha[i] + (1 / beta) * gp.quicksum(p[q] * phi[i, q] for q in Q) <= delta
    #              for i in I)
    #
    # # Eq. 40
    # m.addConstrs(phi[i, q] >= alpha[i] - gp.quicksum(
    #     R_plus[i, q, r] *
    #     L(l, paths[i][r], e) *
    #     y(paths[i][r], q, srg, l)
    #     for r in R for e in G.in_edges(nbunch=commodities[i][0][1]))
    #              for i in I
    #              for q in Q)
    #
    # # Eq. 42
    # m.addConstrs(
    #     gp.quicksum(W_plus[i, r] * L(l, paths[i][r], e) for r in R for e in G.in_edges(nbunch=commodities[i][0][1])) ==
    #     commodities[i][1] for i in I)
    #
    # m.addConstrs(gp.quicksum(
    #     R_plus[i, q, r] * L(l, paths[i][r], e) for r in R for e in G.in_edges(nbunch=commodities[i][0][1])) <=
    #              commodities[i][1] for i in I for q in Q)
    #
    # # Eq. 44
    # m.addConstrs(gp.quicksum(W_plus[i, r] * L(l, paths[i][r], e)
    #                          for r in R for i in I) <= G[e[0]][e[1]]['cap']
    #              for e in E)
    # # Eq. 45
    # m.addConstrs(gp.quicksum(R_plus[i, q, r] * L(l, paths[i][r], e)
    #                          for r in R for i in I) <= G[e[0]][e[1]]['cap']
    #              for q in Q
    #              for e in E)

    m.setObjective(gamma, GRB.MAXIMIZE)
    # m.setObjectiveN(delta, 0, 1)
    # m.setObjectiveN(-gp.quicksum(gp.quicksum(R_plus[i, q, r] * L(l, paths[i][r], e) for r in R for e in G.in_edges(nbunch=commodities[i][0][1])) for i in I for q in Q), 1, 0)
    m.update()
    m.write('test.lp')

    # Optimize model
    m.optimize()

    # Print values for decision variables
    # for v in m.getVars():
    #     print(v.varName, v.x)

    # Print maximized profit value
    print('Minimized result:', m.ObjVal)

    # Results in a more readable format
    print('\n==========================================')
    print('Original Routing')
    for i in I:
        for r in R:
            print(f'Commodity {i}, route {paths[i][r]}: {W_plus[i, r].x}')

    check = all([sum([W_plus[i, r].x * L(l, paths[i][r], e) for r in R for i in I]) <= G[e[0]][e[1]]['cap'] for e in E])
    print(f'Capacity check: {check}')
    for i in I:
        sat = sum([W_plus[i, r].x for r in R])
        print(f'Commodity {i} satisfied: {sat} out of {commodities[i][1]}')

    print('\n==========================================')
    print('Failure Event Routing')
    for q in Q:
        indicators = np.array([int(i) for i in bin(q)[2:]])
        indicators = np.insert(indicators, 0, np.zeros(len(srg) - len(indicators)))
        failed_srg = [srg[i][0] for i in range(len(indicators)) if indicators[i] == 1]
        print(f'Failed SRG {failed_srg}')
        check = all(
            [sum([R_plus[i, q, r].x * L(l, paths[i][r], e) for r in R for i in I]) <= G[e[0]][e[1]]['cap'] for e in E
             for q in Q])
        print(f'Capacity check: {check}')
        for i in I:
            for r in R:
                print(f'Commodity {i}, route {paths[i][r]}: {R_plus[i, q, r].x}')
            sat = sum([R_plus[i, q, r].x for r in R])
            print(f'Commodity {i} satisfied: {sat} out of {commodities[i][1]}\n')

    print('\n==========================================')
    for i in I:
        cvar = alpha[i].x - (1 / beta) * gp.quicksum(p[q] * phi[i, q].x for q in Q)
        print(f'Commodity {i} CVaR: {cvar}')
        print(f'Commodity {i} Eq. 39 LHS = {commodities[i][1] - cvar}')

    print('delta:', delta.x)
