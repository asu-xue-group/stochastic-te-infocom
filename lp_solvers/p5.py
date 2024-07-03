import gurobipy as gp
from gurobipy import *

from lp_solvers.common import *


def solve_p5(commodities: list, srg: list, G: DiGraph, beta, gamma, _lambda, budget, p, non_terminals):
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
        # W^+_i(r)
        W = m.addVars(I, E, name="W")
        # R^{+,q}_i(r)
        R = m.addVars(I, Q, E, name="R")
        # delta = m.addVar(name='delta')
        # alpha
        alpha = m.addVar(name='alpha')
        # phi^q_i
        phi = m.addVars(Q, name='phi')

        # CONSTRAINTS
        # Constraint (a): flow conservation
        m.addConstrs((gp.quicksum(W[i, e[0], e[1]] for e in G.in_edges(v)) -
                      gp.quicksum(W[i, e[0], e[1]] for e in G.out_edges(v)) == 0
                      for i in I for v in non_terminals[i]), name='a')

        # Constraint (b): bandwidth requirements
        m.addConstrs((gp.quicksum(W[i, e[0], e[1]] for e in G.in_edges(commodities[i][0][1])) -
                      gp.quicksum(W[i, e[0], e[1]] for e in G.out_edges(commodities[i][0][1])) >= gamma *
                      commodities[i][1]
                      for i in I), name='b')

        # Constraint (c): capacity constraint
        # the "if" clause is added to prevent dupes
        m.addConstrs((gp.quicksum(W[i, e[0], e[1]] + W[i, e[1], e[0]] for i in I) <= G[e[0]][e[1]]['cap']
                      for e in E if e[0] < e[1]), name='c')

        # Constraint (e): flow conservation for recovery flows
        m.addConstrs((gp.quicksum(R[i, q, e[0], e[1]] for e in G.in_edges(v)) -
                      gp.quicksum(R[i, q, e[0], e[1]] for e in G.out_edges(v)) == 0
                      for i in I for v in non_terminals[i] for q in Q), name='e')

        # Constraint (f): zero flow for broken links
        m.addConstrs((R[i, q, e[0], e[1]] == 0 for q in Q for e in E_f(q, srg) for i in I), name='f')

        # Constraint (g): recovery flow must be smaller than original flow
        m.addConstrs((R[i, q, e[0], e[1]] <= W[i, e[0], e[1]] for e in E for q in Q for i in I), name='g')

        # Constraint (j): aux variable phi
        m.addConstrs((phi[q] >= gp.quicksum(W[i, e[0], e[1]] for i in I for e in G.in_edges(commodities[i][0][1])) -
                      gp.quicksum(W[i, e[0], e[1]] for i in I for e in G.out_edges(commodities[i][0][1])) -
                      gp.quicksum(R[i, q, e[0], e[1]] for i in I for e in G.in_edges(commodities[i][0][1])) +
                      gp.quicksum(R[i, q, e[0], e[1]] for i in I for e in G.out_edges(commodities[i][0][1]))
                      - alpha for q in Q), name='j')

        # Constraint (k): lower bound of lambda
        m.addConstr((alpha + 1 / (1 - beta) * gp.quicksum(p[q] * phi[q] for q in Q) <= _lambda), name='k')

        # Constraint (extra): budget constraint
        m.addConstrs((gp.quicksum(G[e[0]][e[1]]['cost'] * W[i, e[0], e[1]] for e in E) <= budget[i] for i in I),
                     name='extra')

        m.setObjective(gp.quicksum(W[i, e[0], e[1]] for e in G.edges for i in I), GRB.MINIMIZE)
        # m.write('test.lp')

        m.optimize()
        if m.Status == GRB.OPTIMAL:
            logging.info(f'alpha={alpha.x}')
            return m.ObjVal, W, phi, m
        else:
            return None, None, None, None
