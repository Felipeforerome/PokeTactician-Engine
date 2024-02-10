import sys

sys.path.append("../PokemonOpti")

import random
from poketactician.MOACO import MOACO
from collections import defaultdict
import pickle
import time
import numpy as np
from poketactician.glob_var import pokPreFilter, alpha, beta, Q, rho
import multiprocessing
from poketactician.Colony import Colony, ColonyGPT
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd


def worker_function(Q_value, rho_value, alpha_value, beta_value, random_seed=None):
    from poketactician.objectives import (
        attack_obj_fun,
        team_coverage_fun,
        self_coverage_fun,
    )

    print(rho_value)
    if random_seed is not None:
        random.seed(random_seed)
        np.random.seed(random_seed)
    attackObjFun = lambda team: attack_obj_fun(team)
    teamCoverageFun = lambda team: team_coverage_fun(team)
    selfCoverageFun = lambda team: self_coverage_fun(team)
    objectiveFuncs = [
        (attackObjFun, Q_value, rho_value),
    ]
    mCol = MOACO(
        ColonyGPT,
        600,
        objectiveFuncs,
        pokPreFilter,
        alpha_value,
        beta_value,
    )
    mCol.optimize(iters=100, time_limit=None)
    return {rho_value: mCol.candSetsPerIter}


if __name__ == "__main__":
    start = time.time()
    np.seterr(all="raise")

    manager = multiprocessing.Manager()
    # Use multiprocessing to parallelize the loop
    with multiprocessing.Pool() as pool:
        rho_values = [round(x, 1) for x in np.repeat(np.arange(0, 0.11, 0.1), 2)]
        results = pool.starmap(
            worker_function,
            [
                (
                    Q,
                    rho_value,
                    alpha,
                    beta,
                )
                for rho_value in rho_values
            ],
        )
    # Initialize a defaultdict to store lists of lists
    result_dict = defaultdict(list)

    # Iterate through each dictionary in the list
    for d in results:
        # Extract the key and value
        key, value = list(d.items())[0]

        # Append the value to the corresponding key in the result dictionary
        result_dict[key].append(value)

    # Convert the defaultdict to a regular dictionary
    averages_dict = dict(result_dict)

    # Snippet for appending results to alreday existing pickle
    # with open("averages_dict_complete.pkl", "rb") as file:
    #     averages_dict_temp = pickle.load(file)
    #     averages_dict_temp[0] = averages_dict[0]
    #     averages_dict = averages_dict_temp

    # Write pickle
    with open("averages_dict_nonGPT.pkl", "wb") as file:
        pickle.dump(dict(averages_dict), file)

    print(time.time() - start)
