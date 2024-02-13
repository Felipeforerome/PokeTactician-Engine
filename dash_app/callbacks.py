from dash import Input, Output, callback, State
import sys

sys.path.append(sys.path[0] + "/..")
from poketactician.MOACO import MOACO
from poketactician.Colony import Colony, ColonyGPT
from poketactician.glob_var import pokPreFilter, alpha, beta, Q, rho
from poketactician.objectives import (
    attack_obj_fun,
    team_coverage_fun,
    self_coverage_fun,
)
import time


@callback(
    Output("team-output", "children"),
    Output("time-to-calc", "children"),
    [Input("suggest-team-btn", "n_clicks"), State("objective-funcs", "value")],
)
def update_output(n, objFuncsParam):
    if n is None:
        return "Click the button to suggest a team.", ""
    else:
        start = time.time()
        objectiveFuncs = []
        attackObjFun = lambda team: attack_obj_fun(team)
        teamCoverageFun = lambda team: team_coverage_fun(team)
        selfCoverageFun = lambda team: self_coverage_fun(team)
        if "1" in objFuncsParam:
            objectiveFuncs.append((attackObjFun, Q, 0.1))
        if "2" in objFuncsParam:
            objectiveFuncs.append((teamCoverageFun, Q, rho))
        if "3" in objFuncsParam:
            objectiveFuncs.append((selfCoverageFun, Q, rho))
        print(objectiveFuncs)
        mCol = MOACO(
            ColonyGPT,
            400,
            objectiveFuncs,
            pokPreFilter,
            alpha,
            beta,
        )
        mCol.optimize(iters=20, time_limit=None)
        team = mCol.getSolnTeamNames()
        return (
            f"Suggested Team: {', '.join(team)}",
            f"Time to compute: {time.time()-start} - Objective Value: {mCol.getObjTeamValue()}",
        )
