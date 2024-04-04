import math

from gurobipy import *


# Create a new model
m = Model()


# VARIABLE and VAR-FUNCTION DECLARATIONS
# W^+_i(r)
def w_plus(i, r):
    pass


# R^{+,q}_i(r)
def r_plus(i, q, r):
    pass


def alpha(i):
    pass


def phi(q, i):
    pass


delta = m.addVar(name='delta')
beta = 0.95
p = []
d = []

num_commodity = 10


# CONSTRAINTS
# Eq. 39
for i in range(num_commodity):
    temp = 0
    for q in range(0, int(math.pow(2, 4))):
        temp += p[q] * phi(q, i)
    m.addConstr(d[i] - alpha(i) + (1/beta) * temp <= delta)


# Optimize model
m.optimize()

# Print values for decision variables
for v in m.getVars():
    print(v.varName, v.x)

# Print maximized profit value
print('Maximized profit:', m.objVal)
