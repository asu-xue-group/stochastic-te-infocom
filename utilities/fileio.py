from networkx import DiGraph


def read_W(G: DiGraph, I, file):
    W = {}
    for edge in G.edges:
        for i in I:
            W[i, edge[0], edge[1]] = 0
    with open(file, 'r') as f:
        for line in f:
            tokens = line.strip().split(',')
            W[int(tokens[0]), int(tokens[1]), int(tokens[2])] = float(tokens[3])

    return W


def read_R(G: DiGraph, I, Q, file):
    R = {}
    for edge in G.edges:
        for i in I:
            for q in Q:
                R[i, q, edge[0], edge[1]] = 0
    with open(file, 'r') as f:
        for line in f:
            tokens = line.strip().split(',')
            R[int(tokens[0]), int(tokens[1]), int(tokens[2]), int(tokens[3])] = float(tokens[4])

    return R


def print_model(beta, phi, alpha, _lambda, p):
    print('----------------------------------')
    print(f'Variables for beta={beta}:')
    print(f'alpha={alpha}')
    print(f'lambda={_lambda}')
    sum = 0
    for i in range(4):
        print(f'phi[{i}]={phi[i].x}')
        sum += phi[i].x * p[i]
    print(f'summation={sum}')
    k1 = alpha + (1 / (1 - beta)) * sum
    k2 = alpha + (1 / (1 - 0.944999999)) * sum
    k3 = alpha + (1 / (1 - 0.9449999999)) * sum
    print(f'(k) LHS={k1}')
    print(f'diff1={k2 - k1}')
    print(f'(k) LHS w/ beta_6x9={k2}')
    print(f'diff2={k3 - k2}')
    print(f'(k) LHS w/ beta_7x9={k3}')
    print()
