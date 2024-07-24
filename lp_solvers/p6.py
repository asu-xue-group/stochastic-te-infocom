import gurobipy as gp
from gurobipy import *

from graphs.srg_graph import SrgGraph
from lp_solvers.common import *


def solve_p6(G: SrgGraph, k, gamma, beta, p: list, paths=None):
    with gp.Env(empty=True) as env:
        env.setParam('OutputFlag', 0)
        env.setParam('Method', 0)
        env.start()
        m = gp.Model(env=env)

        srg = G.srg
        g = G.graph
        commodities = G.commodities
        if paths is None:
            paths = G.k_paths(k)
        num_srg = len(srg)
        # These variables are used to index the commodities, paths, and SRGs (for Gurobi variables).
        # Actual data is stored in their respective variables
        I = range(len(commodities))
        Q = range(int(math.pow(2, num_srg)))
        R = get_R(paths)
        l = calculate_l(g, paths)
        E = g.edges()

        # VARIABLES
        # W^+_i(r)
        W = m.addVars(I, max([len(p) for p in paths]), name="W")
        # alpha_i
        alpha = m.addVar(name='alpha')
        # phi^q_i
        phi = m.addVars(Q, name='phi')

        # CONSTRAINTS
        # Constraint A1: throughput requirements
        m.addConstrs((gp.quicksum(W[i, r] for r in R[i]) >= gamma * commodities[i].demand for i in I), name='A1')

        # Constraint A2: capacity constraints
        m.addConstrs(
            (gp.quicksum(W[i, r] * L(l, tuple(paths[i][r]), e) for i in I for r in R[i]) <= g[e[0]][e[1]]['cap']
             for e in E), name='A2')

        # Constraint A3: cost constraints
        m.addConstrs((gp.quicksum(W[i, r] * L(l, tuple(paths[i][r]), e) * g[e[0]][e[1]]['cost']
                                  for e in E for r in R[i]) <= commodities[i].budget for i in I), name='A3')

        # Constraint A4: phi auxiliary variable for CVaR
        m.addConstrs(
            (phi[q] >= gp.quicksum(W[i, r] * (1 - y(tuple(paths[i][r]), q, srg, l)) for i in I for r in R[i]) - alpha
             for q in Q),
            name='A4')

        m.setObjective(alpha + 1 / (1 - beta) * gp.quicksum(p[q] * phi[q] for q in Q), GRB.MINIMIZE)

        # Optimize model
        m.optimize()

        return W, m
