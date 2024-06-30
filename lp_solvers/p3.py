import gurobipy as gp
from gurobipy import *
from networkx import DiGraph


# Solve the multi-commodities max-flow for the
def solve_p3(commodities: list, G: DiGraph):
    with gp.Env(empty=True) as env:
        env.setParam('OutputFlag', 0)
        env.start()
        m = gp.Model(env=env)

        I = range(len(commodities))
        E = G.edges
        non_terminals = {}
        for i in I:
            all_nodes = set(G.nodes)
            all_nodes.remove(commodities[i][0][0])
            all_nodes.remove(commodities[i][0][1])
            non_terminals[i] = all_nodes

        # VARIABLES
        W = m.addVars(I, E, name='W')
        # Optimization objective
        gamma = m.addVar(name='gamma')

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

        m.setObjective(gamma, GRB.MAXIMIZE)

        m.optimize()

        if m.Status == GRB.OPTIMAL:
            return m.ObjVal
        else:
            return -1
