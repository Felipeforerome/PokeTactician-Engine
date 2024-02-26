from dash import Input, Output, callback, State, no_update
import sys
from components import PokemonTeam

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
    [
        Input("suggest-team-btn", "n_clicks"),
        State("objectives-multi-select", "value"),
        State("type-multi-select", "value"),
        State("mono-type", "checked"),
    ],
)
def update_output(n, objFuncsParam, includedTypes, monoType):
    if n is None:
        return "", ""
    else:
        if len(objFuncsParam) > 0:
            try:
                if len(includedTypes) > 0:
                    pokList = (
                        [
                            pok
                            for pok in pokPreFilter
                            if (pok.type1 in includedTypes and pok.type2 is None)
                        ]
                        if monoType
                        else [
                            pok
                            for pok in pokPreFilter
                            if (
                                pok.type1 in includedTypes or pok.type2 in includedTypes
                            )
                        ]
                    )
                else:
                    pokList = (
                        [pok for pok in pokPreFilter if (pok.type2 is None)]
                        if monoType
                        else pokPreFilter
                    )

                start = time.time()
                objectiveFuncs = []
                attackObjFun = lambda team: attack_obj_fun(team, pokList)
                teamCoverageFun = lambda team: team_coverage_fun(team)
                selfCoverageFun = lambda team: self_coverage_fun(team)
                if 1 in objFuncsParam:
                    objectiveFuncs.append((attackObjFun, Q, 0.1))
                if 2 in objFuncsParam:
                    objectiveFuncs.append((teamCoverageFun, Q, rho))
                if 3 in objFuncsParam:
                    objectiveFuncs.append((selfCoverageFun, Q, rho))
                mCol = MOACO(
                    ColonyGPT,
                    400,
                    objectiveFuncs,
                    pokList,
                    alpha,
                    beta,
                )
                mCol.optimize(iters=20, time_limit=None)
                team = mCol.getSoln()
                return (
                    PokemonTeam(team.serialize()).layout(),
                    f"Time to compute: {time.time()-start} - Objective Value: {mCol.getObjTeamValue()}",
                )
            except Exception as e:
                return (str(e), "")
        else:
            return (no_update, no_update)


@callback(
    Output("objectives-multi-select", "error"),
    Input("objectives-multi-select", "value"),
)
def select_value(value):
    return "Select at least 1." if len(value) < 1 else ""
