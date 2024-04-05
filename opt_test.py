import math

from gurobipy import *
import gurobipy as gp


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

def in_t(i):
    pass

def R(i):
    pass

def y(r, q):
    pass

def L(r, e):
    pass

def in_g(v):
    pass

def out_g(v):
    pass

delta = m.addVar(name='delta')
beta = 0.95
p = []
d = []
c = []


num_commodity = 10
num_state = int(math.pow(2, 4))
num_node = 15
num_edge = 32

# CONSTRAINTS
# Eq. 39
for i in range(num_commodity):
    temp = 0
    for q in range(num_state):
        temp += p[q] * phi(q, i)
    m.addConstr(d[i] - alpha(i) + (1/beta) * temp <= delta)

# Eq. 40
for i in range(num_commodity):
    for q in range(num_state):
        temp = 0
        for e in range(len(in_t(i))):
            for r in range(len(R(i))):
                temp +=  r_plus(i, q, r) * y(r, q) * L(r, e)
        m.addConstr(phi(q, i) >= alpha(i) - temp)

# Eq. 41
for v in range (num_node - 2):
    for i in range(num_commodity):
        m.addConstr(gp.quicksum(w_plus[i][r] * L[r][e] for r in range(R(i)) for e in range(in_g(v)))
                    - gp.quicksum(w_plus[i][r] * L[r][e] for r in range(R(i)) for e in range(out_g(v))) == 0)

# Eq. 42
for i in range(num_commodity):
    m.addConstr(gp.quicksum(w_plus[i][r] * L[r][e] for r in range(R(i)) for e in range(in_t(i))) == d[i])

# Eq. 43
for v in range (num_node - 2):
    for i in range(num_commodity):
        for q in range(num_state):
            m.addConstr(gp.quicksum(r_plus[q][i][r] * L[r][e] for r in range(R(i)) for e in range(in_g(v)))
                        - gp.quicksum(r_plus[q][i][r] * L[r][e] for r in range(R(i)) for e in range(out_g(v))) == 0)


# Eq. 44
for e in range(num_edge):
    m.addConstr(gp.quicksum(w_plus[i][r] * L[r][e] for r in range(R(i)) for i in range(num_commodity) <= c[e]))

# Eq. 45
for e in range(num_edge):
    for q in range(num_state):
        m.addConstr(gp.quicksum(r_plus[q][i][r] * L[r][e] for r in range(R(i)) for i in range(num_commodity) <= c[e]))


# Optimize model
m.optimize()

# Print values for decision variables
for v in m.getVars():
    print(v.varName, v.x)

# Print maximized profit value
print('Maximized profit:', m.objVal)
