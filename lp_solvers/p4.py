import gurobipy as gp
from gurobipy import *
from networkx import DiGraph

from lp_solvers.common import *
from utilities.print_formatting import print_flows


def solve_p4(commodities: list, srg: list, G: DiGraph, W_opt, q, p, non_terminals, print_flow=False):
    # META VARIABLES
    with gp.Env(empty=True) as env:
        env.setParam('OutputFlag', 0)
        env.setParam('Method', 0)
        env.start()
        m = gp.Model(env=env)
        num_srg = len(srg)

        # These variables are used to index the commodities and SRGs (for Gurobi variables).
        # Actual data is stored in their respective variables
        I = range(len(commodities))
        Q = range(int(math.pow(2, num_srg)))
        E = G.edges()

        # VARIABLES
        # R^{+,q}_i(r)
        R = m.addVars(I, Q, E, name="R")

        # CONSTRAINTS
        # Constraint (e): flow conservation for recovery flows
        m.addConstrs((gp.quicksum(R[i, q, e[0], e[1]] for e in G.in_edges(v)) -
                      gp.quicksum(R[i, q, e[0], e[1]] for e in G.out_edges(v)) == 0
                      for i in I for v in non_terminals[i] for q in Q), name='e')

        # Constraint (f): zero flow for broken links
        m.addConstrs((R[i, q, e[0], e[1]] == 0 for q in Q for e in E_f(q, srg) for i in I), name='f')

        # Constraint (g): recovery flow must be smaller than original flow
        m.addConstrs((R[i, q, e[0], e[1]] <= W_opt[i, e[0], e[1]] for e in E for q in Q for i in I), name='g')

        m.setObjective(gp.quicksum(R[i, q, e[0], e[1]] for e in E for i in I), GRB.MAXIMIZE)

        # m.write('test.lp')
        m.optimize()

        if print_flow:
            print_flows(G, W_opt, R, commodities, srg, p)

        if m.Status == GRB.OPTIMAL:
            return m.ObjVal, R, m
        else:
            return None, None, None
