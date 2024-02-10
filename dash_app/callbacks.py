from dash import Input, Output, callback
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


@callback(
    Output("team-output", "children"),
    [Input("suggest-team-btn", "n_clicks")],
)
def update_output(n):
    if n is None:
        return "Click the button to suggest a team."
    else:
        attackObjFun = lambda team: attack_obj_fun(team)
        teamCoverageFun = lambda team: team_coverage_fun(team)
        selfCoverageFun = lambda team: self_coverage_fun(team)
        objectiveFuncs = [
            (attackObjFun, Q, rho),
        ]
        mCol = MOACO(
            ColonyGPT,
            600,
            objectiveFuncs,
            pokPreFilter,
            alpha,
            beta,
        )
        mCol.optimize(iters=50, time_limit=None)
        team = mCol.getSolnTeamNames()
        return f"Suggested Team: {', '.join(team)}"
