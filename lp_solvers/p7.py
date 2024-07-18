import gurobipy as gp
from gurobipy import *

from graphs.srg_graph import SrgGraph
from lp_solvers.common import *


def solve_p7(G: SrgGraph, k, gamma, p: list, paths=None):
    with gp.Env(empty=True) as env:
        env.setParam('OutputFlag', 0)
        env.setParam('Method', 0)
        env.start()
        m = gp.Model(env=env)

        srg = G.srg
        commodities = G.commodities
        g = G.graph
        if not paths:
            paths = G.all_paths(k)

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

        # CONSTRAINTS
        # commodities = i -> ((s, t), d)
        # paths = i -> [path1, path2, ...]
        # srg = [((u, v), fail prob), ...]
        # Constraint B1: throughput requirements
        m.addConstrs((gp.quicksum(W[i, r] for r in R[i]) >= gamma * commodities[i].demand for i in I), name='B1')

        # Constraint B2: capacity constraints
        m.addConstrs(
            (gp.quicksum(W[i, r] * L(l, tuple(paths[i][r]), e) for i in I for r in R[i]) <= g[e[0]][e[1]]['cap']
             for e in E), name='B2')

        # Constraint B3: cost constraints
        m.addConstrs((gp.quicksum(W[i, r] * L(l, tuple(paths[i][r]), e) * g[e[0]][e[1]]['cost']
                                  for e in E for r in R[i]) <= commodities[i].budget for i in I), name='B3')

        m.setObjective(
            gp.quicksum(
                p[q] * gp.quicksum(W[i, r] * y(tuple(paths[i][r]), q, srg, l) for i in I for r in R[i]) for q in Q),
            GRB.MAXIMIZE)

        # Optimize model
        m.optimize()

        return W, m
