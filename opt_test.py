import math

import gurobipy as gp
import numpy as np
import itertools
from gurobipy import *


# z = [0, 0, 1]
def calc_pq(z, srg):
    product = 1
    for i in range(len(z)):
        product *= z[i] * srg[i][1] + (1 - z[i]) * (1 - srg[i][1])
    return product

# Data from TE
srg = [(10, 0.4), (2, 0.5), (22, 0.6)]

# Create a new model
m = Model()

# META VARIABLES
# Commodities
num_srg = len(srg)
# format idx -> [s, t, demand]
i = dict
# format idx -> [paths]
r = dict
q = np.arange(math.pow(2, num_srg))

pq = np.zeros((len(q),))

for i, z in enumerate([list(i) for i in itertools.product([0, 1], repeat=3)]):
    pq[i] = calc_pq(z, srg)

# CONSTANTS
beta = 0.95

# VARIABLES
# W^+_i(r)
W_plus = m.addVars(i, r, name="W+")
# R^{+,q}_i(r)
R_plus = m.addVars(i, q, r, name="R+")
delta = m.addVar(name='delta')
# alpha_i
alpha = m.addVars(i, name='alpha')
# phi^q_i
phi = m.addVars(i, q, name='phi')


#
# def in_t(i):
#     pass
#
#
# def R(i):
#     pass
#
#
# def y(r, q):
#     pass
#
#
# def L(r, e):
#     pass
#
#
# def in_g(v):
#     pass
#
#
# def out_g(v):
#     pass
#
#
# CONSTRAINTS
# Eq. 39
for i in range(num_commodity):
    temp = 0
    for q in range(num_state):
        temp += p[q] * phi(q, i)
    m.addConstr(d[i] - alpha(i) + (1 / beta) * temp <= delta)
#
# # Eq. 40
# for i in range(num_commodity):
#     for q in range(num_state):
#         temp = 0
#         for e in range(len(in_t(i))):
#             for r in range(len(R(i))):
#                 temp += r_plus(i, q, r) * y(r, q) * L(r, e)
#         m.addConstr(phi(q, i) >= alpha(i) - temp)
#
# # Eq. 41
# for v in range(num_node - 2):
#     for i in range(num_commodity):
#         m.addConstr(gp.quicksum(w_plus(i, r) * L[r][e] for r in range(R(i)) for e in range(in_g(v)))
#                     - gp.quicksum(w_plus[i][r] * L[r][e] for r in range(R(i)) for e in range(out_g(v))) == 0)
#
# # Eq. 42
# for i in range(num_commodity):
#     m.addConstr(gp.quicksum(w_plus[i][r] * L[r][e] for r in range(R(i)) for e in range(in_t(i))) == d[i])
#
# # Eq. 43
# for v in range(num_node - 2):
#     for i in range(num_commodity):
#         for q in range(num_state):
#             m.addConstr(gp.quicksum(r_plus[q][i][r] * L[r][e] for r in range(R(i)) for e in range(in_g(v)))
#                         - gp.quicksum(r_plus[q][i][r] * L[r][e] for r in range(R(i)) for e in range(out_g(v))) == 0)
#
# # Eq. 44
# for e in range(num_edge):
#     m.addConstr(gp.quicksum(w_plus[i][r] * L[r][e] for r in range(R(i)) for i in range(num_commodity) <= c[e]))
#
# # Eq. 45
# for e in range(num_edge):
#     for q in range(num_state):
#         m.addConstr(gp.quicksum(r_plus[q][i][r] * L[r][e] for r in range(R(i)) for i in range(num_commodity) <= c[e]))
#
# # Optimize model
# m.optimize()
#
# # Print values for decision variables
# for v in m.getVars():
#     print(v.varName, v.x)
#
# # Print maximized profit value
# print('Maximized profit:', m.objVal)
