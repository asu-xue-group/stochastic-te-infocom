import gurobipy as gp
from gurobipy import *

from lp_solvers.common import *


def solve_p6(commodities: list, paths: list, srg: list, gamma, beta, p: list, budget: list, G: DiGraph):
    with gp.Env(empty=True) as env:
        env.setParam('OutputFlag', 0)
        env.setParam('Method', 0)
        env.start()
        m = gp.Model(env=env)

        num_srg = len(srg)
        # These variables are used to index the commodities, paths, and SRGs (for Gurobi variables).
        # Actual data is stored in their respective variables
        I = range(len(commodities))
        Q = range(int(math.pow(2, num_srg)))
        R = range(len(paths[0]))
        l = calculate_l(G, paths)
        E = G.edges()

        # VARIABLES
        # W^+_i(r)
        W = m.addVars(I, R, name="W")
        # alpha_i
        alpha = m.addVar(name='alpha')
        # phi^q_i
        phi = m.addVars(Q, name='phi')

        # CONSTRAINTS
        # commodities = i -> ((s, t), d)
        # paths = i -> [path1, path2, ...]
        # srg = [((u, v), fail prob), ...]
        # Constraint A1: throughput requirements
        m.addConstrs((gp.quicksum(W[i, r] for r in R) >= gamma * commodities[i][1] for i in I), name='A1')

        # Constraint A2: capacity constraints
        m.addConstrs((gp.quicksum(W[i, r] * L(l, paths[i][r], e) for r in R for i in I) <= G[e[0]][e[1]]['cap']
                      for e in E), name='A2')

        # Constraint A3: cost constraints
        m.addConstrs((gp.quicksum(W[i, r] * L(l, paths[i][r], e) * G[e[0]][e[1]]['cost']
                                  for e in E for r in R) <= budget[i] for i in I), name='A3')

        # Constraint A4: phi auxiliary variable for CVaR
        m.addConstrs(
            (phi[q] >= gp.quicksum(W[i, r] * (1 - y(paths[i][r], q, srg, l)) - alpha for r in R for i in I) for q in Q),
            name='A4')

        m.setObjective(alpha + 1 / (1 - beta) * gp.quicksum(p[q] * phi[q] for q in Q), GRB.MINIMIZE)

        # Optimize model
        m.optimize()

        return W, m
