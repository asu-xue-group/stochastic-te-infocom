import itertools
import logging
import math

import networkx as nx
import numpy as np

from graphs.toy import toy
from lp_solvers.common import calc_pq
from lp_solvers.p3 import solve_p3
from lp_solvers.p4 import solve_p4
from lp_solvers.p5 import solve_p5
from utilities.cycle_check import check_cycle
from utilities.cvar_calc import cvar_2, cvar_3
from utilities.fileio import print_model
from utilities.print_formatting import print_flows


def main(beta=None):
    G = toy()
    G = nx.to_directed(G)
    logging.getLogger().setLevel(logging.DEBUG)

    # Draw the network / sanity check
    # nx.draw(G, with_labels=True, font_weight='bold')
    # plt.show()

    # Commodities
    commodities = [
        ((1, 7), 2),
        ((2, 8), 2)
    ]

    # Shared risk groups
    srg = [(((3, 5),), 0.95), (((4, 6),), 0.05)]
    num_srg = len(srg)
    Q = range(int(math.pow(2, num_srg)))
    I = range(len(commodities))

    # Calculate the probability of each failure event
    p = np.zeros((len(Q),))
    for i, z in enumerate([list(i) for i in itertools.product([0, 1], repeat=num_srg)]):
        p[i] = calc_pq(z, srg)

    # Cache the nodes after removing the source and the destination of a commodity
    non_terminals = {}
    for i in I:
        all_nodes = set(G.nodes)
        all_nodes.remove(commodities[i][0][0])
        all_nodes.remove(commodities[i][0][1])
        non_terminals[i] = all_nodes

    # CVaR beta
    # beta @ 0.945 may be interesting
    # Using simplex, different behavior can be observed at
    # 0.94499999, 0.944999999, 0.9449999999
    beta = 0.944999999
    # Solve for the optimal gamma
    gamma = solve_p3(commodities, G)
    if gamma == -1:
        logging.critical('No flow can be established for the input.')
        exit(-1)
    else:
        logging.info(f'gamma={gamma}')

    # Maximum flow
    W_max = np.sum([gamma * c[1] for c in commodities])
    logging.info(f'W_max={W_max}')

    # Solve for lambda_opt via bisection
    lambda_ub = W_max
    lambda_lb = 0
    # Previously epsilon is at 1e-6
    epsilon = 1e-6
    itr = 1

    best_lambda = -1
    best_m = None
    best_flows = None
    best_phi = None

    while lambda_ub - lambda_lb > epsilon:
        curr_lambda = (lambda_ub + lambda_lb) / 2.0
        logging.info(f'Iteration {itr}, current lambda={curr_lambda} [{lambda_lb}-{lambda_ub}]')

        W_curr, flows, phi, m = solve_p5(commodities, srg, G, beta, gamma, curr_lambda, p, non_terminals)
        # the current model is infeasible, we need to increase the lambda to relax the constraints
        if not W_curr:
            lambda_lb = curr_lambda
            logging.debug('Infeasible model, increasing lambda')
        # The current model is feasible; however we need to check for cycles
        else:
            m.update()
            # If it contains a cycle, then we need to increase the lambda
            if check_cycle(G, flows):
                lambda_lb = curr_lambda
                logging.debug('Cycle detected, increasing lambda')
            # Otherwise, we can try a more aggressive solution to get a better result
            else:
                best_lambda = curr_lambda
                best_flows = flows
                best_m = m
                best_phi = phi

                lambda_ub = curr_lambda
                logging.debug('Acyclic solution found, decreasing lambda')
                # We can stop early if the p4's objective is already equivalent to p2, there's nothing we need to do
                if W_curr == W_max:
                    logging.info('Current flow value is already equal to opt, no need for further optimization')
                    break
        itr += 1
    if best_lambda == -1:
        logging.error('\nFailed to find an acyclic solution from the input')
    else:
        logging.info(f'\nOptimal lambda (CVaR) is {best_lambda:.4f}\n')

    best_m.update()

    # print_model(beta, best_phi, best_m.getVarByName('alpha').x, best_lambda, p)
    tmp = {}
    for k, v in best_flows.items():
        tmp[k] = v.x

    # Recover the flow with max throughput
    final_R = {}
    for q in Q:
        _, R, m = solve_p4(commodities, srg, G, tmp, q, p, non_terminals)
        m.update()
        for k, v in R.items():
            if v.x > 0:
                final_R[k] = v.x

    cvar = cvar_2(commodities, srg, G, tmp, beta, p, non_terminals)

    print_flows(G, tmp, final_R, commodities, srg, p)
    print(f'Final CVaR = {cvar}')


if __name__ == '__main__':
    main()
