import gurobipy as gp
import networkx as nx
from gurobipy import *
from networkx import DiGraph, Graph
import numpy as np
import itertools
from lp_solvers.common import *
from utilities.print_formatting import print_flows


def cvar(commodities: list, srg: list, G: DiGraph, W, beta):
    with gp.Env(empty=True) as env:
        env.setParam('OutputFlag', 0)
        env.setParam('DualReductions', 0)
        env.start()
        m = gp.Model(env=env)
        num_srg = len(srg)

        # These variables are used to index the commodities and SRGs (for Gurobi variables).
        # Actual data is stored in their respective variables
        I = range(len(commodities))
        Q = range(int(math.pow(2, num_srg)))
        E = G.edges()


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

        phi = m.addVars(Q, name='phi')
        alpha = m.addVar(name='alpha')
        R = m.addVars(I, Q, E, name='R')

        m.addConstrs((gp.quicksum(R[i, q, *e1] for e1 in G.in_edges(v)) -
                      gp.quicksum(R[i, q, *e2] for e2 in G.out_edges(v)) == 0
                      for i in I for v in non_terminals[i] for q in Q), name='Eq 35')

        # Eq. 38
        m.addConstrs((R[i, q, *e] <= W[i, *e] for e in E for q in Q for i in I), name='Eq 38')

        # Eq. 41
        m.addConstrs((R[i, q, *e] == 0 for q in Q for e in E_f(q, srg) for i in I), name='Eq 41')

        m.addConstrs((phi[q] >= gp.quicksum(W[i, *e1] for i in I for e1 in G.in_edges(commodities[i][0][1])) -
                      gp.quicksum(W[i, *e2] for i in I for e2 in G.out_edges(commodities[i][0][1])) -
                      gp.quicksum(R[i, q, *e3] for i in I for e3 in G.in_edges(commodities[i][0][1])) +
                      gp.quicksum(R[i, q, *e4] for i in I for e4 in G.out_edges(commodities[i][0][1]))
                      - alpha for q in Q), name='Eq 42')

        m.setObjective(alpha + 1 / (1 - beta) * gp.quicksum(p[q] * phi[q] for q in Q), GRB.MINIMIZE)

        m.optimize()

        return m.ObjVal
