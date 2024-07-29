import gurobipy as gp
from gurobipy import *

from lp_solvers.common import *


def cvar_2(g, srg, commodities, W, beta, p, non_terminals):
    with gp.Env(empty=True) as env:
        env.setParam('OutputFlag', 0)
        env.start()
        mod = gp.Model(env=env)
        num_srg = len(srg)

        # These variables are used to index the commodities and SRGs (for Gurobi variables).
        # Actual data is stored in their respective variables
        I = range(len(commodities))
        Q = range(int(math.pow(2, num_srg)))
        E = g.edges()

        phi = mod.addVars(Q, name='phi')
        alpha = mod.addVar(name='alpha')
        _lambda = mod.addVar(name='lambda')
        R = mod.addVars(I, Q, E, name='R')

        # Constraint (e): flow conservation for recovery flows
        mod.addConstrs((gp.quicksum(R[i, q, e[0], e[1]] for e in g.in_edges(v)) -
                      gp.quicksum(R[i, q, e[0], e[1]] for e in g.out_edges(v)) == 0
                      for i in I for v in non_terminals[i] for q in Q), name='e')

        # Constraint (f): zero flow for broken links
        mod.addConstrs((R[i, q, e[0], e[1]] == 0 for q in Q for e in E_f(q, srg) for i in I), name='f')

        # Constraint (g): recovery flow must be smaller than original flow
        mod.addConstrs((R[i, q, e[0], e[1]] <= W[i, e[0], e[1]] for e in E for q in Q for i in I), name='g')

        # Constraint (3.12) / (j)
        mod.addConstrs((phi[q] >= gp.quicksum(W[i, e[0], e[1]] for i in I for e in g.in_edges(commodities[i][0][1])) -
                      gp.quicksum(W[i, e[0], e[1]] for i in I for e in g.out_edges(commodities[i][0][1])) -
                      gp.quicksum(R[i, q, e[0], e[1]] for i in I for e in g.in_edges(commodities[i][0][1])) +
                      gp.quicksum(R[i, q, e[0], e[1]] for i in I for e in g.out_edges(commodities[i][0][1]))
                      - alpha for q in Q), name='j')

        # Constraint (3.13) / (k)
        mod.addConstr((alpha + 1 / (1 - beta) * gp.quicksum(p[q] * phi[q] for q in Q) <= _lambda), name='k')

        mod.setObjective(_lambda, GRB.MINIMIZE)

        mod.optimize()
        return mod.ObjVal, R, mod


def cvar_3(g, srg, commodities, W, R, beta, p):
    with gp.Env(empty=True) as env:
        env.setParam('OutputFlag', 0)
        env.start()
        m = gp.Model(env=env)
        num_srg = len(srg)

        # These variables are used to index the commodities and SRGs (for Gurobi variables).
        # Actual data is stored in their respective variables
        I = range(len(commodities))
        Q = range(int(math.pow(2, num_srg)))

        phi = m.addVars(Q, name='phi')
        alpha = m.addVar(name='alpha')
        _lambda = m.addVar(name='lambda')

        # Constraint (3.8) / (j)
        m.addConstrs((phi[q] >= gp.quicksum(W[i, e[0], e[1]] for i in I for e in g.in_edges(commodities[i][0][1])) -
                      gp.quicksum(W[i, e[0], e[1]] for i in I for e in g.out_edges(commodities[i][0][1])) -
                      gp.quicksum(R[i, q, e[0], e[1]] for i in I for e in g.in_edges(commodities[i][0][1])) +
                      gp.quicksum(R[i, q, e[0], e[1]] for i in I for e in g.out_edges(commodities[i][0][1]))
                      - alpha for q in Q), name='j')

        # Constraint (3.9) / (k)
        m.addConstr((alpha + 1 / (1 - beta) * gp.quicksum(p[q] * phi[q] for q in Q) <= _lambda), name='k')

        m.setObjective(_lambda, GRB.MINIMIZE)

        m.write('test.lp')

        m.optimize()
        return m.ObjVal, m


# def cvar_te(G: SrgGraph, paths: list, beta, p: list, W):
#     with gp.Env(empty=True) as env:
#         srg = G.srg
#         commodities = G.commodities
#         g = G.graph
#
#         env.setParam('OutputFlag', 0)
#         env.setParam('Method', 0)
#         env.start()
#         m = gp.Model(env=env)
#
#         num_srg = len(srg)
#         # These variables are used to index the commodities, paths, and SRGs (for Gurobi variables).
#         # Actual data is stored in their respective variables
#         I = range(len(commodities))
#         Q = range(int(math.pow(2, num_srg)))
#         R = get_R(paths)
#         l = calculate_l(g, paths)
#
#         # VARIABLES
#         # alpha_i
#         alpha = m.addVar(name='alpha')
#         # phi^q_i
#         phi = m.addVars(Q, name='phi')
#
#         # CONSTRAINTS
#         # Constraint A4: phi auxiliary variable for CVaR
#         m.addConstrs(
#             (phi[q] >= gp.quicksum(W[i, r] * (1 - y(tuple(paths[i][r]), q, srg, l)) for i in I for r in R[i]) - alpha
#              for q in Q),
#             name='A4')
#
#         m.setObjective(alpha + 1 / (1 - beta) * gp.quicksum(p[q] * phi[q] for q in Q), GRB.MINIMIZE)
#
#         # Optimize model
#         m.optimize()
#
#         return m.ObjVal, alpha.x
