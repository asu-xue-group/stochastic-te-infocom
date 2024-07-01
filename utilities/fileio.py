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