import graphs.toy_extended as toy_ext
from graphs.srg_graph import SrgGraph
from lp_solvers import *
from utilities.cycle_check import check_cycle
from utilities.print_formatting import *
import timeit


G = toy_ext.get_graph()
srg = G.srg
k = 0
num_srg = len(srg)
g = G.graph
commodities = G.commodities
Q = range(int(math.pow(2, num_srg)))
I = range(len(commodities))

# Calculate the probability of each failure event
p = np.zeros((len(Q),))
for i, z in enumerate([list(i) for i in itertools.product([0, 1], repeat=num_srg)]):
    p[i] = calc_pq(z, srg)

# Cache the nodes after removing the source and the destination of a commodity
non_terminals = {}
for i in I:
    all_nodes = set(g.nodes)
    all_nodes.remove(commodities[i][0][0])
    all_nodes.remove(commodities[i][0][1])
    non_terminals[i] = all_nodes

# CVaR beta
beta = 0.95

# Solve for the optimal gamma
gamma = solve_p3(G)


def lp():
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

        W_curr, flows, phi, m = solve_p5(G, beta, gamma, curr_lambda, p, non_terminals)
        # the current model is infeasible, we need to increase the lambda to relax the constraints
        if not W_curr:
            lambda_lb = curr_lambda
            logging.debug('Infeasible model, increasing lambda')
        # The current model is feasible; however we need to check for cycles
        else:
            m.update()
            # If it contains a cycle, then we need to increase the lambda
            if check_cycle(g, flows):
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
    alpha = best_m.getVarByName('alpha')

    # print_model(beta, best_phi, best_m.getVarByName('alpha').x, best_lambda, p)
    tmp = {}
    for k, v in best_flows.items():
        tmp[k] = v.x

    # Recover the flow with max throughput
    final_R = {}
    for q in Q:
        _, R, m = solve_p4(G, tmp, q, p, non_terminals)
        m.update()
        for k, v in R.items():
            if v.x > 0:
                final_R[k] = v.x


print(timeit.repeat('solve_p6(G, k, gamma, beta, p)', number=100, globals=globals()))
print(timeit.repeat('solve_p7(G, k, gamma, p)', number=100, globals=globals()))
print(timeit.repeat('lp()', number=100, globals=globals()))
