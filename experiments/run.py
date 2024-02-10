import sys

sys.path.append("../PokemonOpti")

from poketactician.MOACO import MOACO
import random
import numpy as np
import plotly.graph_objects as go
from poketactician.glob_var import pokPreFilter, alpha, beta, Q, rho
from poketactician.Colony import Colony, ColonyGPT


def test():
    from poketactician.objectives import (
        attack_obj_fun,
        team_coverage_fun,
        self_coverage_fun,
    )

    np.seterr(all="raise")
    random.seed(10)
    np.random.seed(10)
    attackObjFun = lambda team: attack_obj_fun(team)
    teamCoverageFun = lambda team: team_coverage_fun(team)
    selfCoverageFun = lambda team: self_coverage_fun(team)
    objectiveFuncs = [
        (attackObjFun, 1, 1),
        # (teamCoverageFun, 0.0001, 0),
    ]

    fig = go.Figure()
    # Find out why it takes too long with a population of 50, and crashes with 20
    mCol = MOACO(ColonyGPT, 600, objectiveFuncs, pokPreFilter, alpha, beta)
    mCol.optimize(iters=50, time_limit=None)
    # mCol.getSolnTeamNames()
    averages = [
        np.mean(list(map(mCol.jointFun, iteration_points[0])))
        for iteration_points in mCol.candSetsPerIter
    ]
    fig.add_trace(
        go.Scatter(
            x=np.arange(len(averages)),
            y=averages,
            mode="lines",
            name=f"rho: {1}",
        )
    )
    del mCol
    fig.update_layout(
        xaxis_title="Iteration",
        yaxis_title="Objective Function Value",
        title=f"Analizing rho Variation",
    )

    fig.show()


if __name__ == "__main__":
    # TODO Turn project into a library
    test()
