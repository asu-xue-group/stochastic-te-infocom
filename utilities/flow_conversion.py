from collections import namedtuple

W_flow = namedtuple('W_flow', ['commodity', ''])


def W_to_dict(W, m):
    m.update()
    temp = {}

    for k, v in W.items():
        if v.x > 0:
            temp[(k[0], k[1], k[2])] = v.x

    return temp


def R_to_dict(R, m):
    m.update()
    temp = {}

    for k, v in R.items():
        if v.x > 0:
            temp[(k[0], k[1])] = k[2]

    return temp
