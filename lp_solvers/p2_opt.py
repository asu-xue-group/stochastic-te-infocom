import gurobipy as gp
import networkx as nx
from gurobipy import *
from networkx import DiGraph, Graph
import numpy as np
import itertools
from lp_solvers.common import *
from utilities.print_formatting import print_flows


def solve_p2(commodities: list, srg: list, G: DiGraph, beta, gamma):
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

    print_flows(G, W_plus, R_plus, commodities, m, srg, p)

    return m.objVal
