import gurobipy as gp
import networkx as nx
from gurobipy import *
from networkx import DiGraph, Graph
import numpy as np
from lp_solvers.common import *
from utilities.print_formatting import print_flows


def solve_p4(commodities: list, srg: list, G: DiGraph, l_opt, beta, gamma, _lambda, print_flow=False):
    # META VARIABLES
    with gp.Env(empty=True) as env:
        env.setParam('OutputFlag', 0)
        env.start()
        m = gp.Model(env=env)
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

        # Eq. 33
        m.addConstrs((gp.quicksum(W_plus[i, *e1] for e1 in G.in_edges(v)) -
                     gp.quicksum(W_plus[i, *e2] for e2 in G.out_edges(v)) == 0
                     for i in I for v in non_terminals[i]), name='Eq 33')

        # Eq. 34
        m.addConstrs((gp.quicksum(W_plus[i, *e1] for e1 in G.in_edges(commodities[i][0][1])) -
                     gp.quicksum(W_plus[i, *e2] for e2 in G.out_edges(commodities[i][0][1])) >= gamma * commodities[i][1]
                     for i in I), name='Eq 34')

        # Eq. 35
        m.addConstrs((gp.quicksum(R_plus[i, q, *e1] for e1 in G.in_edges(v)) -
                     gp.quicksum(R_plus[i, q, *e2] for e2 in G.out_edges(v)) == 0
                     for i in I for v in non_terminals[i] for q in Q), name='Eq 35')

        # Eq. 36
        m.addConstrs((gp.quicksum(W_plus[i, e[0], e[1]] + W_plus[i, e[1], e[0]] for i in I) <= G[e[0]][e[1]]['cap']
                     for e in E), name='Eq 36')

        # Eq. 37
        m.addConstrs((gp.quicksum(R_plus[i, q, e[0], e[1]] + R_plus[i, q, e[1], e[0]] for i in I) <= G[e[0]][e[1]]['cap']
                     for e in E for q in Q), name='Eq 37')

        # Eq. 38
        m.addConstrs((R_plus[i, q, *e] <= W_plus[i, *e] for e in E for q in Q for i in I), name='Eq 38')

        # Eq. 41
        m.addConstrs((R_plus[i, q, *e] == 0 for q in Q for e in E_f(q, srg) for i in I), name='Eq 41')

        # Eq. 42
        m.addConstrs((phi[q] >= gp.quicksum(W_plus[i, *e1] for i in I for e1 in G.in_edges(commodities[i][0][1])) -
                     gp.quicksum(W_plus[i, *e2] for i in I for e2 in G.out_edges(commodities[i][0][1])) -
                     gp.quicksum(R_plus[i, q, *e3] for i in I for e3 in G.in_edges(commodities[i][0][1])) +
                     gp.quicksum(R_plus[i, q, *e4] for i in I for e4 in G.out_edges(commodities[i][0][1]))
                     - alpha for q in Q), name='Eq 42')

        # Eq. 44
        m.addConstr((alpha + 1 / (1 - beta) * gp.quicksum(p[q] * phi[q] for q in Q) <= _lambda * l_opt),
                    name='Eq 44')



        m.setObjective(gp.quicksum(gp.quicksum(W_plus[i, e[0], e[1]]
                                               for e in G.edges) for i in I), GRB.MINIMIZE)
        m.update()
        m.write('test.lp')

        m.optimize()

        print(f'alpha={alpha.x}')

        if print_flow:
            print_flows(G, W_plus, R_plus, commodities, m, srg, p)

        if m.Status == GRB.OPTIMAL:
            obj_val = alpha + (1 / (1 - beta)) * gp.quicksum(p[q] * phi[q] for q in Q)
            return obj_val.getValue(), W_plus, m
        else:
            return None, None, None
