from collections.abc import Callable, Iterable
from enum import Enum
from functools import lru_cache
from typing import Any, Literal

import numpy as np

from .glob_var import Q, rho
from .models.hinting_types import Ant
from .models.Pokemon import Pokemon
from .models.Roles import (
    is_cleric,
    is_hazard_setter,
    is_phazer,
    is_physical_sweeper,
    is_special_sweeper,
    is_spinner,
    is_wall,
)
from .models.Team import Team
from .models.Types import PokemonType, type_chart, type_order


def attack_obj_fun(ant: np.ndarray, pokemon_list: list[Pokemon]) -> float:
    temp_team = Team.ant_to_team(ant, pokemon_list)
    return sum(
        list(
            map(
                lambda pokemon: pokemon.current_power(),
                temp_team.pokemons,
            )
        )
    )


# def compute_weaknesses_and_coverage(team_types, typeChart):
#     num_types = typeChart.shape[0]
#     team_weaknesses = np.ones(num_types)  # Assume all types are covered initially
#     team_resistances = np.zeros(num_types)

#     for types in team_types:
#         pokemon_resistances = np.product(
#             typeChart[:, np.array([typeOrder.index(type_) for type_ in types])], axis=1
#         )
#         team_resistances += (pokemon_resistances < 1).astype(int)
#         team_weaknesses *= (pokemon_resistances > 1).astype(int)

#     C_W = np.sum(
#         team_resistances * (1 - team_weaknesses)
#     )  # Coverage against weaknesses
#     W = np.sum(1 - team_weaknesses)  # Number of unique weaknesses
#     R = np.sum(team_resistances)  # Total resistances
#     U_R = np.sum(team_resistances > 0)  # Unique resistances

#     return W, C_W, R, U_R


@lru_cache(maxsize=324)
def defense(types: tuple[PokemonType]) -> Iterable[float]:
    defense = np.prod(
        type_chart[:, np.array([type_order.index(type_) for type_ in types])], axis=1
    )
    return defense


def bin_weakness(vector: Iterable[float]) -> list[Literal[0] | Literal[1]]:
    return (vector > 1).astype(int)


def bin_resistance(vector: Iterable[float]) -> list[Literal[0] | Literal[1]]:
    return (vector < 1).astype(int)


def flatten_comprehension(matrix: Iterable[Iterable[Any]]) -> list[int]:
    return [item for row in matrix for item in row]


def CW(team_types: Iterable[tuple[PokemonType, ...]]) -> int:
    omega = np.sum([bin_resistance(defense(types)) for types in team_types], axis=0)
    return np.sum(
        [
            bin_weakness(defense(team_type))
            * (omega - bin_resistance(defense(team_type)))
            for team_type in team_types
        ]
    )


def team_coverage_fun(team: Ant, pokemon_list: Iterable[Pokemon]) -> int:
    team_types = [
        tuple(
            pok_type
            for pok_type in [pokemon_list[pok[0]].type1, pokemon_list[pok[0]].type2]
            if pok_type is not None
        )
        for pok in team
    ]
    # W, C_W, R, U_R = compute_weaknesses_and_coverage(team_types, typeChart)

    # Assuming equal weighting for simplicity, adjust alpha and beta as needed
    # alpha = 0.5
    # beta = 0.5

    # # Compute total score (T_S)
    # T_S = alpha * (C_W / W if W else 0) + beta * (R / U_R if U_R else 0)
    # Added the +1 at the end to avoid the result to be zero because to colony.updatePhCon needs a non-zero fitness value
    T_S = CW(team_types) * len(set(flatten_comprehension(team_types))) + 1

    return T_S


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
# def self_coverage_fun(team):
#     return np.mean(
#         [
#             *map(
#                 lambda x: 1
#                 / (
#                     np.power(
#                         np.ones(18) * 2,
#                         get_move_weakness(x[0], x[1:5]),
#                         dtype=np.float64,
#                     ).mean()
#                 ),
#                 team,
#             )
#         ]
#     )


def generalist_team_fun(ant: Ant, pokemon_list: list[Pokemon]) -> float:
    """
    Evaluates the given team based on their roles as a hazard setter, spinner, and cleric.

    Args:
        team (list): A list of Pokemon representing the team.

    Returns:
        dict: A dictionary containing the evaluation results for each role.
    """
    roles = [is_hazard_setter, is_spinner, is_cleric]
    team = Team.ant_to_team(ant, pokemon_list)
    return team.team_roles_fun(roles)


def defensive_team_fun(ant: Ant, pokemon_list: list[Pokemon]) -> float:
    """
    Evaluates the given team based on their roles as a cleric, status_move, and Phazer.

    Args:
        team (list): A list of Pokemon representing the team.

    Returns:
        dict: A dictionary containing the evaluation results for each role.
    """
    # TODO Missing status move evaluator
    roles = [is_wall, is_phazer]
    team = Team.ant_to_team(ant, pokemon_list)
    return team.team_roles_fun(roles)


def offensive_team_fun(ant: Ant, pokemon_list: list[Pokemon]) -> float:
    """
    Evaluates the given team based on their roles as a Special Sweeper, Physical Sweeper, Choice Item, Boosting Move, and Volt-Switch.

    Args:
        team (list): A list of Pokemon representing the team.

    Returns:
        dict: A dictionary containing the evaluation results for each role.
    """
    # TODO Missing status move evaluator
    roles = [is_special_sweeper, is_physical_sweeper]
    team = Team.ant_to_team(ant, pokemon_list)
    return team.team_roles_fun(roles)


class ObjectiveFunctions(Enum):
    """
    Enum class that represents the different objective functions available for team evaluation.
    """

    ATTACK = "attack"
    # DEFENSE = "Defense"
    TEAM_COVERAGE = "team_coverage"
    # SELF_COVERAGE = "Self Coverage"

    def get_function(self, pok_list: list[Pokemon]) -> Callable:
        """
        Returns the corresponding function for the objective function.

        Returns:
            function: The function corresponding to the objective function.
        """
        return {
            ObjectiveFunctions.ATTACK: (
                lambda team: attack_obj_fun(team, pok_list),
                Q,
                rho,
            ),
            # ObjectiveFunctions.DEFENSE: (lambda team:defense_obj_fun, Q, rho),
            ObjectiveFunctions.TEAM_COVERAGE: (
                lambda team: team_coverage_fun(team, pok_list),
                Q,
                rho,
            ),
            # ObjectiveFunctions.SELF_COVERAGE: (lambda team:self_coverage_fun,, Q, rho),
        }[self]


class StrategyFunctions(Enum):
    """
    Enum class that represents the different objective functions available for team evaluation.
    """

    GENERALIST_TEAM = "Generalist"
    DEFENSIVE_TEAM = "Defensive"
    OFFENSIVE_TEAM = "Offensive"

    def get_function(
        self, pok_list: list[Pokemon]
    ) -> tuple[Callable[..., float], int, float]:
        """
        Returns the corresponding function for the objective function.

        Returns:
            function: The function corresponding to the objective function.
        """
        return {
            StrategyFunctions.GENERALIST_TEAM: (
                lambda team: generalist_team_fun(team, pok_list),
                Q,
                rho,
            ),
            StrategyFunctions.DEFENSIVE_TEAM: (
                lambda team: defensive_team_fun(team, pok_list),
                Q,
                rho,
            ),
            StrategyFunctions.OFFENSIVE_TEAM: (
                lambda team: offensive_team_fun(team, pok_list),
                Q,
                0.15,
            ),
        }[self]
