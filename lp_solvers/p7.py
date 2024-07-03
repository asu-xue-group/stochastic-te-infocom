import gurobipy as gp
from gurobipy import *
from networkx import DiGraph
import numpy as np
from lp_solvers.common import *


def solve_p7(commodities: list, paths: list, srg: list, gamma, p: list, budget: list, G: DiGraph):
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

        # CONSTRAINTS
        # commodities = i -> ((s, t), d)
        # paths = i -> [path1, path2, ...]
        # srg = [((u, v), fail prob), ...]
        # Constraint B1: throughput requirements
        m.addConstrs((gp.quicksum(W[i, r] for r in R) >= gamma * commodities[i][1] for i in I), name='B1')

        # Constraint B2: capacity constraints
        m.addConstrs((gp.quicksum(W[i, r] * L(l, paths[i][r], e) for r in R for i in I) <= G[e[0]][e[1]]['cap']
                     for e in E), name='B2')

        # Constraint B3: cost constraints
        m.addConstrs((gp.quicksum(W[i, r] * L(l, paths[i][r], e) * G[e[0]][e[1]]['cost']
                                 for e in E for r in R) <= budget[i] for i in I), name='B3')

        m.setObjective(gp.quicksum(p[q] * gp.quicksum(W[i, r] * y(paths[i][r], q, srg, l) for r in R for i in I) for q in Q), GRB.MAXIMIZE)

        # Optimize model
        m.optimize()

        return W, m
