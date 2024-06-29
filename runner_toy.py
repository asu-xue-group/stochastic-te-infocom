import logging
import numpy as np
import networkx as nx
from graphs.toy import toy
from lp_solvers.p1 import solve_p1
from lp_solvers.p2 import solve_p2
from lp_solvers.p4 import solve_p4
from utilities.cycle_check import check_cycle


def main():
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

    # CVaR beta
    # beta 0.945.txt
    beta = 0.945

    # Solve for the optimal gamma
    gamma = solve_p1(commodities, G)
    if gamma == -1:
        logging.critical('No flow can be established for the input.')
    else:
        logging.info(f'gamma={gamma}')
    # Maximum flow
    W_max = np.sum([gamma * c[1] for c in commodities])
    logging.info(f'W_max={W_max}')

    # Solve for lambda_opt via bisection
    lambda_ub = W_max
    lambda_lb = 0
    epsilon = 1e-6
    itr = 1

    best_lambda = -1
    best_W = -1

    while lambda_ub - lambda_lb > epsilon:
        curr_lambda = (lambda_ub + lambda_lb) / 2.0
        logging.info(f'Iteration {itr}, current lambda={curr_lambda} [{lambda_lb}-{lambda_ub}]')

        W_curr, flows, m = solve_p2(commodities, srg, G, beta, gamma, curr_lambda)
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
                best_W = W_curr
                lambda_ub = curr_lambda
                logging.debug('Acyclic solution found, decreasing lambda')
                # We can stop early if the p4's objective is already equivalent to p2, there's nothing we need to do
                if W_curr == W_max:
                    # Does not work right now,
                    logging.info('Current flow value is already equal to opt, no need for further optimization')
                    break
        itr += 1
    if best_lambda == -1:
        logging.error('\nFailed to find an acyclic solution from the input')
    else:
        logging.info(f'\nOptimal lambda (CVaR) is {best_lambda:.4f}\n')

    # Recover the flow with max throughput
    solve_p4(commodities, srg, G, beta, gamma, best_lambda, best_W, True)


if __name__ == '__main__':
    main()
