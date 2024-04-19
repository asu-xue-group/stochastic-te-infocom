import gurobipy as gp
import numpy as np
from gurobipy import *
from networkx import DiGraph
import ENV


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
                L[tuple(path[i:i + 2])].add(tuple(path))
    return L


def y(r: tuple, q: int, srg: list, l: dict):
    # Convert q to a binary array
    indicators = np.array([int(i) for i in bin(q)[2:]])
    indicators = np.insert(indicators, 0, np.zeros(len(srg) - len(indicators)))
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
    with gp.Env(params=ENV.connection_params) as env:
        with gp.Model(env=env) as m:
            # META VARIABLES
            # m = gp.Model()
            num_srg = len(srg)
            I = range(len(commodities))
            Q = range(int(math.pow(2, num_srg)))
            R = range(len(paths[0]))
            l = calculate_l(G, paths)
            E = G.edges()

            p = np.zeros((len(Q),))
            for i, z in enumerate([list(i) for i in itertools.product([0, 1], repeat=3)]):
                p[i] = calc_pq(z, srg)

            # CONSTANTS
            beta = 0.95

            # VARIABLES
            # W^+_i(r)
            W_plus = m.addVars(I, R, name="W")
            # R^{+,q}_i(r)
            R_plus = m.addVars(I, Q, R, name="R")
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

            # Eq. 42
            m.addConstrs(gp.quicksum(W_plus[i, r] * L(l, paths[i][r], e) for r in R for e in G.in_edges(nbunch=commodities[i][0][1])) == commodities[i][1] for i in I)

            m.addConstrs(gp.quicksum(R_plus[i, q, r] * L(l, paths[i][r], e) for r in R for e in G.in_edges(nbunch=commodities[i][0][1])) <= commodities[i][1] for i in I for q in Q)

            # Eq. 44
            m.addConstrs(gp.quicksum(W_plus[i, r] *
                                     L(l, paths[i][r], e)
                                     for r in R for i in I) <= G[e[0]][e[1]]['cap']
                         for e in E)
            # Eq. 45
            m.addConstrs(gp.quicksum(R_plus[i, q, r] *
                                     L(l, paths[i][r], e)
                                     for r in R for i in I) <= G[e[0]][e[1]]['cap']
                         for q in Q
                         for e in E)

            m.setObjective(delta, GRB.MINIMIZE)
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
            print('Minimized result:', m.objVal)

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
                check = all([sum([R_plus[i, q, r].x * L(l, paths[i][r], e) for r in R for i in I]) <= G[e[0]][e[1]]['cap'] for e in E for q in Q])
                print(f'Capacity check: {check}')
                for i in I:
                    for r in R:
                        print(f'Commodity {i}, route {paths[i][r]}: {R_plus[i, q, r].x}')
                    sat = sum([R_plus[i, q, r].x for r in R])
                    print(f'Commodity {i} satisfied: {sat} out of {commodities[i][1]}\n')

            print('delta:', delta.x)
