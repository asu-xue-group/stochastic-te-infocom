import gurobipy as gp
from gurobipy import *

from graphs.srg_graph import SrgGraph
from lp_solvers.common import *


def cvar_2(G: SrgGraph, W, beta, p, non_terminals):
    with gp.Env(empty=True) as env:
        srg = G.srg
        commodities = G.commodities
        g = G.graph
        env.setParam('OutputFlag', 0)
        env.setParam('DualReductions', 0)
        env.start()
        m = gp.Model(env=env)
        num_srg = len(srg)

        # These variables are used to index the commodities and SRGs (for Gurobi variables).
        # Actual data is stored in their respective variables
        I = range(len(commodities))
        Q = range(int(math.pow(2, num_srg)))
        E = g.edges()

        phi = m.addVars(Q, name='phi')
        alpha = m.addVar(name='alpha')
        _lambda = m.addVar(name='lambda')
        R = m.addVars(I, Q, E, name='R')

        # Constraint (e): flow conservation for recovery flows
        m.addConstrs((gp.quicksum(R[i, q, e[0], e[1]] for e in g.in_edges(v)) -
                      gp.quicksum(R[i, q, e[0], e[1]] for e in g.out_edges(v)) == 0
                      for i in I for v in non_terminals[i] for q in Q), name='e')

        # Constraint (f): zero flow for broken links
        m.addConstrs((R[i, q, e[0], e[1]] == 0 for q in Q for e in E_f(q, srg) for i in I), name='f')

        # Constraint (g): recovery flow must be smaller than original flow
        m.addConstrs((R[i, q, e[0], e[1]] <= W[i, e[0], e[1]] for e in E for q in Q for i in I), name='g')

        # Constraint (3.12) / (j)
        m.addConstrs((phi[q] >= gp.quicksum(W[i, e[0], e[1]] for i in I for e in g.in_edges(commodities[i].edge.v)) -
                      gp.quicksum(W[i, e[0], e[1]] for i in I for e in g.out_edges(commodities[i].edge.v)) -
                      gp.quicksum(R[i, q, e[0], e[1]] for i in I for e in g.in_edges(commodities[i].edge.v)) +
                      gp.quicksum(R[i, q, e[0], e[1]] for i in I for e in g.out_edges(commodities[i].edge.v))
                      - alpha for q in Q), name='j')

        # Constraint (3.13) / (k)
        m.addConstr((alpha + 1 / (1 - beta) * gp.quicksum(p[q] * phi[q] for q in Q) <= _lambda), name='k')

        m.setObjective(_lambda, GRB.MINIMIZE)

        m.optimize()
        return m.ObjVal


def cvar_3(G: SrgGraph, W, R, beta, p):
    with gp.Env(empty=True) as env:
        srg = G.srg
        commodities = G.commodities
        g = G.graph
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
        m.addConstrs((phi[q] >= gp.quicksum(W[i, e[0], e[1]] for i in I for e in g.in_edges(commodities[i].edge.v)) -
                      gp.quicksum(W[i, e[0], e[1]] for i in I for e in g.out_edges(commodities[i].edge.v)) -
                      gp.quicksum(R[i, q, e[0], e[1]] for i in I for e in g.in_edges(commodities[i].edge.v)) +
                      gp.quicksum(R[i, q, e[0], e[1]] for i in I for e in g.out_edges(commodities[i].edge.v))
                      - alpha for q in Q), name='j')

        # Constraint (3.9) / (k)
        m.addConstr((alpha + 1 / (1 - beta) * gp.quicksum(p[q] * phi[q] for q in Q) <= _lambda), name='k')

        m.setObjective(_lambda, GRB.MINIMIZE)

        m.optimize()
        return m.ObjVal


def cvar_te(G: SrgGraph, paths: list, beta, p: list, W):
    with gp.Env(empty=True) as env:
        srg = G.srg
        commodities = G.commodities
        g = G.graph

        env.setParam('OutputFlag', 0)
        env.setParam('Method', 0)
        env.start()
        m = gp.Model(env=env)

        num_srg = len(srg)
        # These variables are used to index the commodities, paths, and SRGs (for Gurobi variables).
        # Actual data is stored in their respective variables
        I = range(len(commodities))
        Q = range(int(math.pow(2, num_srg)))
        R = get_R(paths)
        l = calculate_l(g, paths)

        # VARIABLES
        # alpha_i
        alpha = m.addVar(name='alpha')
        # phi^q_i
        phi = m.addVars(Q, name='phi')

        # CONSTRAINTS
        # Constraint A4: phi auxiliary variable for CVaR
        m.addConstrs(
            (phi[q] >= gp.quicksum(W[i, r] * (1 - y(tuple(paths[i][r]), q, srg, l)) for i in I for r in R[i]) - alpha
             for q in Q),
            name='A4')

        m.setObjective(alpha + 1 / (1 - beta) * gp.quicksum(p[q] * phi[q] for q in Q), GRB.MINIMIZE)

        # Optimize model
        m.optimize()

        return m.ObjVal, alpha.x
