from dash import Input, Output, callback, State, no_update, clientside_callback
import sys
from components import PokemonTeam

sys.path.append(sys.path[0] + "/..")
from poketactician.MOACO import MOACO
from poketactician.Colony import Colony, Colony
from poketactician.glob_var import pokPreFilter, alpha, beta, Q, rho
from poketactician.objectives import (
    attack_obj_fun,
    team_coverage_fun,
    self_coverage_fun,
)
import time


@callback(
    Output("time-to-calc", "children"),
    Output("team-output", "children"),
    Output("memory-output", "data"),
    [
        Input("suggest-team-btn", "n_clicks"),
        State("objectives-multi-select", "value"),
        State("type-multi-select", "value"),
        State("mono-type", "checked"),
    ],
)
def update_output(n, objFuncsParam, includedTypes, monoType):
    if n is None:
        return "", "", ""
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
                teamCoverageFun = lambda team: team_coverage_fun(team, pokList)
                selfCoverageFun = lambda team: self_coverage_fun(team, pokList)
                if 1 in objFuncsParam:
                    objectiveFuncs.append((attackObjFun, Q, 0.1))
                if 2 in objFuncsParam:
                    objectiveFuncs.append((teamCoverageFun, Q, 0.1))
                if 3 in objFuncsParam:
                    objectiveFuncs.append((selfCoverageFun, Q, rho))
                mCol = MOACO(
                    Colony,
                    400,
                    objectiveFuncs,
                    pokList,
                    alpha,
                    beta,
                )
                mCol.optimize(iters=25, time_limit=None)
                # mCol.optimize(iters=30, time_limit=None)
                team = mCol.getSoln()
                return (
                    "",
                    PokemonTeam(team.serialize()).layout(),
                    [time.time() - start, mCol.getObjTeamValue()],
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


clientside_callback(
    """
    function(data){
        console.log(`Time to compute: ${data[0]} - Objective Value: ${data[1]}`);
        return ''
    }
    """,
    Output("placeholder", "children"),
    Input("memory-output", "data"),
)
