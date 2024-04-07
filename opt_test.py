import math

import gurobipy as gp
import numpy as np
import itertools
from gurobipy import *
from networkx import DiGraph


def calculate_l(G: DiGraph, paths: list):
    edges = list(G.edges.data())

    # Set up the dictionary that stores the edge-path mapping
    L = dict()
    for edge in edges:
        # Needs to add both forward and backward edges
        L[(edge[0], edge[1])] = set()
        # L[(edge[1], edge[0])] = set()
    for path_grp in paths:
        for path in path_grp:
            for i in range(len(path) - 2 + 1):
                L[tuple(path[i:i+2])].add(tuple(path))
    return L


def y(r: tuple, q: int, srg: list, l: dict):
    # Convert q to a binary array
    indicators = np.array([int(i) for i in bin(q)[2:]])
    failed_srg = [srg[i] for i in range(len(indicators)) if indicators[i] == 1]
    for f_srg in failed_srg:
        if r in l[f_srg[0]]:
            return 0
    return 1


def L(l: dict, r: tuple, e: tuple):
    if r in l[e]:
        return 1
    else:
        return 0


def calc_pq(z, srg):
    product = 1
    for i in range(len(z)):
        product *= z[i] * srg[i][1] + (1 - z[i]) * (1 - srg[i][1])
    return product


def solve_lp(commodities: list, paths: list, srg: list, G: DiGraph):
    # Create a new model
    m = Model()

    # META VARIABLES
    num_srg = len(srg)
    I = range(len(commodities))
    Q = range(int(math.pow(2, num_srg)))
    R = range(len(paths[0]))
    l = calculate_l(G, paths)

    # q = np.arange(math.pow(2, num_srg))

    p = np.zeros((len(Q),))

    for i, z in enumerate([list(i) for i in itertools.product([0, 1], repeat=3)]):
        p[i] = calc_pq(z, srg)

    # CONSTANTS
    beta = 0.95

    # VARIABLES
    # W^+_i(r)
    W_plus = m.addVars(I, R, name="W+")
    # R^{+,q}_i(r)
    R_plus = m.addVars(I, Q, R, name="R+")
    delta = m.addVar(name='delta')
    # alpha_i
    alpha = m.addVars(I, name='alpha')
    # phi^q_i
    phi = m.addVars(I, Q, name='phi')

    # CONSTRAINTS
    # commodities = i -> ((s, t), d)
    # paths = i -> [path1, path2, ...]
    # srg = [((u, v), fail prob), ...]
    # Eq. 39
    m.addConstrs(commodities[i][1] - alpha[i] + (1 / beta) * gp.quicksum(p[q] * phi[i, q] for q in Q) <= delta
                 for i in I)

    # Eq. 40
    m.addConstrs(phi[i, q] >= alpha[i] - gp.quicksum(
                            R_plus[i, q, r] *
                            L(l, paths[i][r], e) *
                            y(paths[i][r], q, srg, l)
                            for r in R for e in G.in_edges(nbunch=commodities[i][0][1]))
                 for i in I
                 for q in Q)

    v = 6
    lhs = ''
    rhs = ''
    for i in I:
        for r in R:
            for e in G.in_edges(nbunch=v):
                if L(l, paths[i][r], e) == 1:
                    lhs += f'W+[{i},{r}] + '
            for e in G.out_edges(nbunch=v):
                if L(l, paths[i][r], e) == 1:
                    rhs += f'W+[{i},{r}] + '
    print(f'({lhs[:-3]}) - ({rhs[:-3]}) = 0')
    # Eq. 41
    for i in I:
        for v in set(G.nodes):
            if v not in commodities[i][0]:
                m.addConstr(
                    gp.quicksum(W_plus[i, r] * L(l, paths[i][r], e) for e in G.in_edges(nbunch=v) for r in R) - gp.quicksum(W_plus[i, r] * L(l, paths[i][r], e) for e in G.out_edges(nbunch=v) for r in R ) == 0)
    # m.addConstrs((gp.quicksum(W_plus[i, r] * L(l, paths[i][r], e) for e in G.in_edges(nbunch=v) for r in R)
    #              - gp.quicksum(W_plus[i, r] * L(l, paths[i][r], e) for e in G.out_edges(nbunch=v) for r in R ) == 0
    #             for v in set(G.nodes)
    #             for i in I
    #             if v not in commodities[i][0]), name='flow_conservation')

    m.setObjective(delta, GRB.MINIMIZE)

    m.update()

    m.write('test.lp')
#
# # Eq. 40
# for i in range(num_commodity):
#     for q in range(num_state):
#         temp = 0
#         for e in range(len(in_t(i))):
#             for r in range(len(R(i))):
#                 temp += r_plus(i, q, r) * y(r, q) * L(r, e)
#         m.addConstr(phi(q, i) >= alpha(i) - temp)
#
# # Eq. 41
# for v in range(num_node - 2):
#     for i in range(num_commodity):
#         m.addConstr(gp.quicksum(w_plus(i, r) * L[r][e] for r in range(R(i)) for e in range(in_g(v)))
#                     - gp.quicksum(w_plus[i][r] * L[r][e] for r in range(R(i)) for e in range(out_g(v))) == 0)
#
# # Eq. 42
# for i in range(num_commodity):
#     m.addConstr(gp.quicksum(w_plus[i][r] * L[r][e] for r in range(R(i)) for e in range(in_t(i))) == d[i])
#
# # Eq. 43
# for v in range(num_node - 2):
#     for i in range(num_commodity):
#         for q in range(num_state):
#             m.addConstr(gp.quicksum(r_plus[q][i][r] * L[r][e] for r in range(R(i)) for e in range(in_g(v)))
#                         - gp.quicksum(r_plus[q][i][r] * L[r][e] for r in range(R(i)) for e in range(out_g(v))) == 0)
#
# # Eq. 44
# for e in range(num_edge):
#     m.addConstr(gp.quicksum(w_plus[i][r] * L[r][e] for r in range(R(i)) for i in range(num_commodity) <= c[e]))
#
# # Eq. 45
# for e in range(num_edge):
#     for q in range(num_state):
#         m.addConstr(gp.quicksum(r_plus[q][i][r] * L[r][e] for r in range(R(i)) for i in range(num_commodity) <= c[e]))
#
# # Optimize model
# m.optimize()
#
# # Print values for decision variables
# for v in m.getVars():
#     print(v.varName, v.x)
#
# # Print maximized profit value
# print('Maximized profit:', m.objVal)
