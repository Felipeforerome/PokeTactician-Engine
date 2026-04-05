"""Test utilities for PokeTactician tests."""

from typing import Dict

import numpy as np
from numpy.typing import NDArray

from poketactician.config import MAX_NUMBER_OF_POKEMON, NUMBER_OF_MOVES_SLOTS


def assert_preselected_in_solution(
    solution: NDArray[np.int16],
    pre_selected: Dict[int, list],
    pokemon_in_team: int = MAX_NUMBER_OF_POKEMON,
) -> None:
    """Assert that preselected pokemon and moves are correctly present in a solution.

    Validates that:
    1. Each preselected pokemon appears at the expected position (first N slots)
    2. Each preselected pokemon has all their preselected moves in their moveset

    Args:
        solution: Solution array from optimization (pokemon IDs + moves)
        pre_selected: Dictionary mapping pokemon IDs to lists of move IDs
        pokemon_in_team: Number of pokemon in a team (default: 6)

    Raises:
        AssertionError: If preselected pokemon or moves are missing or misplaced

    Example:
        >>> solution = np.array([1, 2, 3, 5, 7, 9, 10, 11, 12, 13, ...], dtype=np.int16)
        >>> pre_selected = {1: [10, 11], 2: [12, 13]}
        >>> assert_preselected_in_solution(solution, pre_selected)
    """
    # Parse solution into pokemon IDs and moves
    pokemon_ids = solution[:pokemon_in_team]
    moves = solution[pokemon_in_team:].reshape(pokemon_in_team, NUMBER_OF_MOVES_SLOTS)

    # Get preselected pokemon IDs in order
    preselected_pokemon_ids = list(pre_selected.keys())

    # Validate each preselected pokemon is in the first N positions
    for i, expected_pokemon_id in enumerate(preselected_pokemon_ids):
        actual_pokemon_id = pokemon_ids[i]
        assert actual_pokemon_id == expected_pokemon_id, f"Preselected pokemon {expected_pokemon_id} should be at position {i}, but found {actual_pokemon_id}"

        # Validate all preselected moves are present for this pokemon
        pokemon_moves = moves[i]
        expected_moves = pre_selected[expected_pokemon_id]

        for expected_move in expected_moves:
            assert expected_move in pokemon_moves, (
                f"Preselected pokemon {expected_pokemon_id} at position {i} should have move {expected_move}, but has moves {pokemon_moves}"
            )
