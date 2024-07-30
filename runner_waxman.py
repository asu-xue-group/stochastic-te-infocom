import csv
from concurrent.futures import ProcessPoolExecutor

import graphs.toy_extended as toy_ext
import graphs.grid as grid
import graphs.waxman as waxman
from graphs.srg_graph import SrgGraph
from lp_solvers import *
from utilities.cycle_check import check_cycle
from utilities.print_formatting import *
from numpy.random import Generator, PCG64
from utilities.fileio import create_csv_file, append_to_csv
import time
from functools import partial

existing_entry = set()


def run(k: int, gamma: float = None, beta: float = None, n: int = 100, m=3, seed=1, output=False):
    # logging.getLogger().setLevel(logging.INFO)
    print(f'Starting {n=} {seed=}, pid {os.getpid()}')
    time_start = time.perf_counter()

    # Draw the network / sanity check
    # nx.draw(G, with_labels=True, font_weight='bold')
    # plt.show()

    if (n, seed) in existing_entry:
        return

    rand = Generator(PCG64(seed))
    G = waxman.get_graph(n, 0.1, 0.2, seed=seed, rand=rand)

    paths = G.k_paths(k)
    G.generate_srg(paths, m, rand)

    srg = G.srg
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
        all_nodes.remove(commodities[i].s)
        all_nodes.remove(commodities[i].t)
        non_terminals[i] = all_nodes

    # CVaR beta
    # beta @ 0.945 may be interesting
    # Using simplex, different behavior can be observed at
    # 0.94499999, 0.944999999, 0.9449999999
    if beta is None:
        beta = 0.95

    # Solve for the optimal gamma
    if gamma is None:
        gamma = solve_p3(G)
    if gamma == -1:
        logging.critical('No flow can be established for the input.')
        exit(-1)
    else:
        pass
        # print(f'gamma={gamma}')

    # print('Part 1: TeaVar w/ budget constraints (min CVaR)=======================')
    gamma_ub = gamma
    gamma_lb = 0.0
    epsilon = 1e-6
    best_gamma = 0.0
    W_best = None
    m_best = None
    teavar_ext = 0.0
    teavar_cvar = 0.0

    while gamma_ub - gamma_lb > epsilon:
        curr_gamma = (gamma_ub + gamma_lb) / 2.0
        # Solve TeaVaR w/ budget constraints, min CVaR
        W, mod = solve_p6(G, k, curr_gamma, beta, p, paths)

        if mod.Status == GRB.OPTIMAL:
            if best_gamma < curr_gamma:
                best_gamma = curr_gamma
                W_best = W
                m_best = mod
            gamma_lb = curr_gamma
        else:
            gamma_ub = curr_gamma

    if best_gamma > 0.0:
        # print(f'Best gamma for TeaVaR is {best_gamma}')
        # print(f'TeaVaR time: {teavar_e_best - teavar_s_best}')
        m_best.update()
        tmp = {}
        for k, v in W_best.items():
            tmp[k] = v.x
        teavar_ext, teavar_cvar, teavar_alpha = print_flows_te(G, tmp, paths, p, beta, output)
    else:
        print('TeaVaR was unable to find a solution')

    # Solve TeaVaR w/ budget constraints, Max EXT
    # print('Part 2: Max EXT w/ budget constraints=======================')
    # maxext_start = time.perf_counter()
    # W, mod = solve_p7(G, k, gamma, p, paths)
    # maxext_end = time.perf_counter()
    # print(f'MaxFlow time: {maxext_end - maxext_start}')
    #
    # mod.update()
    # tmp = {}
    # for k, v in W.items():
    #     tmp[k] = v.x
    # print_flows_te(G, tmp, paths, p, beta, output)

    # print('Part 3: LP reformulation =====================')
    # Maximum flow
    W_max = np.sum([gamma * c.demand for c in commodities])
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

        W_curr, flows, phi, mod = solve_p5(G, beta, gamma, curr_lambda, p, non_terminals)
        # the current model is infeasible, we need to increase the lambda to relax the constraints
        if not W_curr:
            lambda_lb = curr_lambda
            logging.debug('Infeasible model, increasing lambda')
        # The current model is feasible; however we need to check for cycles
        else:
            mod.update()
            # If it contains a cycle, then we need to increase the lambda
            if check_cycle(g, flows):
                lambda_lb = curr_lambda
                logging.debug('Cycle detected, increasing lambda')
            # Otherwise, we can try a more aggressive solution to get a better result
            else:
                best_lambda = curr_lambda
                best_flows = flows
                best_m = mod
                best_phi = phi

                lambda_ub = curr_lambda
                logging.debug('Acyclic solution found, decreasing lambda')
                # We can stop early if the p4's objective is already equivalent to p2, there's nothing we need to do
                if W_curr == W_max:
                    logging.info('Current flow value is already equal to opt, no need for further optimization')
                    break
        itr += 1
    # print(f'Bisection took {itr} iterations')
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
        _, R, mod = solve_p4(G, tmp, q, p, non_terminals)
        mod.update()
        for k, v in R.items():
            if v.x > 0:
                final_R[k] = v.x

    lp_cvar, _, _ = cvar_2(G, tmp, beta, p, non_terminals)
    lp_ext = print_flows(G, tmp, final_R, p, output)
    # print(f'CVaR({beta})={lp_cvar:.3f}, alpha={alpha.x:.3f}\n')

    time_end = time.perf_counter()
    time_diff = time_end - time_start
    append_to_csv('results.csv', [n, g.number_of_edges(), m, seed, best_gamma, teavar_cvar,
                                  teavar_ext, gamma, lp_cvar, lp_ext, time_diff])
    print(f'{n=}, {seed=} has finished')


def main():
    prun = partial(run, 3, None, None)
    seed = list(range(120, 500))
    n = [160] * 20
    m = [5] * 20
    # targets = sorted(list(itertools.product(n, m)), key=lambda x: x[1])

    if os.path.isfile('results.csv'):
        with open('results.csv') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                existing_entry.add((int(row[0]), int(row[3])))
    else:
        create_csv_file('results.csv', ['n', 'e', 'm', 'seed', 'tvar-gamma', 'tvar-cvar', 'tvar-ext',
                                        'our-gamma', 'our-cvar', 'our-ext', 'time'])

    with ProcessPoolExecutor(max_workers=10) as executor:
        executor.map(prun, n, m, seed)


if __name__ == '__main__':
    main()
