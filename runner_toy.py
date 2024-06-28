import networkx as nx
from graphs.toy import toy
from lp_solvers.p2_opt import solve_p2
from lp_solvers.p4_opt import solve_p4
from utilities.cycle_check import check_cycle


def main():
    G = toy()
    G = nx.to_directed(G)

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

    # Constants
    gamma = 1.0
    beta = 0.95

    # Solve the LP
    opt_val = solve_p2(commodities, srg, G, beta, gamma)

    print('*****************Cycle Cancellation***************')

    # Determine an upper bound of lambda
    lambda_ub = 10
    lambda_lb = 1
    epsilon = 1e-6
    itr = 1
    best_lambda = -1

    while lambda_ub - lambda_lb > epsilon:
        curr_lambda = (lambda_ub + lambda_lb) / 2.0
        print('----------')
        print(f'Iteration {itr}, current lambda={curr_lambda} [{lambda_lb}-{lambda_ub}]')

        obj_val, flows, m = solve_p4(commodities, srg, G, opt_val, beta, gamma, curr_lambda)
        # the current model is infeasible, we need to increase the lambda to relax the constraints
        if not obj_val:
            lambda_lb = curr_lambda
            print('Infeasible model, increasing lambda')
        # The current model is feasible; however we need to check for cycles
        else:
            m.update()
            # If it contains a cycle, then we need to increase the lambda
            if check_cycle(G, flows):
                lambda_lb = curr_lambda
                print('Cycle detected, increasing lambda')
            # Otherwise, we can try a more aggressive solution to get a better result
            else:
                best_lambda = curr_lambda
                best_flows = flows
                lambda_ub = curr_lambda
                print(f'Current CVaR: {opt_val * curr_lambda:.8f}')
                print('Acyclic solution found, decreasing lambda')
                # We can stop early if the p4's objective is already equivalent to p2, there's nothing we need to do
                if obj_val == opt_val:
                    # Does not work right now,
                    print('Current obj value is already equal to opt, no need for further optimization')
                    break
        itr += 1

    if best_lambda == -1:
        print('\nFailed to find an acyclic solution from the input')
    else:
        print(f'\nOptimal lambda is {best_lambda:.4f}, CVaR({beta})={best_lambda * opt_val:.8f}\n'
              f'corresponding flow:')
        solve_p4(commodities, srg, G, opt_val, beta, gamma, best_lambda, True)


if __name__ == '__main__':
    main()
