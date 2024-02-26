from .utils import (
    currentPower,
    getLearnedMoves,
    getWeakness,
    dominatedCandSet,
    getMoveWeakness,
    hoyerSparseness,
)

from functools import reduce
from .glob_var import moves, pokPreFilter
import numpy as np


def attack_obj_fun(team, pokList):
    return sum(
        list(
            map(
                lambda x: currentPower(
                    pokList[x[0]],
                    getLearnedMoves(pokList, x, [x[1], x[2], x[3], x[4]]),
                ),
                team,
            )
        )
    )


def team_coverage_fun(team, pokList):
    team_vector = reduce(np.multiply, map(lambda x: getWeakness(pokList[x[0]]), team))
    total_score = sum(value**2 for value in team_vector)
    sparsity_penalty = 1 - hoyerSparseness(team_vector)  # Flip the result
    final_score = total_score * sparsity_penalty  # Multiply by the total_score
    return final_score


# (
#         1
#         / np.power(
#             np.ones_like(
#                 reduce(
#                     np.multiply, map(lambda x: getWeakness(pokPreFilter[x[0]]), team)
#                 )
#             )
#             * 2,
#             reduce(np.multiply, map(lambda x: getWeakness(pokPreFilter[x[0]]), team)),
#         ).mean()
#     )


# def team_type_coverage_fun(team):
#     total_weaknesses = 0
#     total_resistances = 0
#     types = []
#     for pokemon in team:
#     # Loop through each unique type
#     for pokemon in team:
#         for type_ in set(pokemon.types):
#             # Find the index of the type in the typeOrder list
#             type_index = typeOrder.index(type_)

#             # Calculate weaknesses and resistances using the typeChart
#             weaknesses = sum(typeChart[type_index] > 1)
#             resistances = sum(typeChart[type_index] < 1)

#             # Update total weaknesses and resistances
#             total_weaknesses += weaknesses
#             total_resistances += resistances

#     # Calculate the overall team type coverage score
#     team_coverage_score = total_resistances - total_weaknesses

#     return team_coverage_score


# TODO This function doesn't work, if used in MOACO the teams are definetly not good
def self_coverage_fun(team):
    return np.mean(
        [
            *map(
                lambda x: 1
                / (
                    np.power(
                        np.ones(18) * 2, getMoveWeakness(x[0], x[1:5]), dtype=np.float64
                    ).mean()
                ),
                team,
            )
        ]
    )
