"""Test utilities and fixtures for PokeTactician tests."""

from typing import Any, Dict

import numpy as np
import pytest

# Import objectives to ensure they're registered
import poketactician.objectives  # noqa: F401
from poketactician.config import MAX_NUMBER_OF_POKEMON, NUMBER_OF_MOVES_SLOTS, NUMBER_OF_NATURES, NUMBER_OF_STATS, NUMBER_OF_TYPES, SEED
from poketactician.engine.problem import PokemonProblem
from poketactician.engine.selector import ObjectiveSelector
from poketactician.registry import register_objective_data


@pytest.fixture
def test_data() -> Dict[str, Any]:
    """Create test data for the PokeTactician test cases."""
    n_pokemon = 13
    n_moves = 20
    n_types = NUMBER_OF_TYPES
    n_stats = NUMBER_OF_STATS
    n_natures = NUMBER_OF_NATURES

    # Set a fixed seed for reproducibility
    seed = SEED
    rng = np.random.default_rng(seed)

    # Move Effectiveness matrix
    me = rng.integers(20, 110, size=(2, n_moves), dtype=np.int16, endpoint=True)
    rows = rng.integers(0, 1, size=me.shape[1], endpoint=True)
    me[rows, np.arange(me.shape[1])] = 0

    # Learnable Moves matrix
    lm = rng.integers(0, 2, size=(n_pokemon, n_moves), dtype=bool)

    # Make sure each Pokemon has at least 4 learnable moves
    for i in range(n_pokemon):
        if np.sum(lm[i]) < NUMBER_OF_MOVES_SLOTS:
            # Add random learnable moves until we have at least 4
            indices = np.where(~lm[i])[0]
            to_set = rng.choice(indices, size=NUMBER_OF_MOVES_SLOTS - np.sum(lm[i]), replace=False)
            lm[i, to_set] = True

    # Pokemon Types matrix (each Pokemon has 1-2 types)
    pokemon_types = np.zeros((n_pokemon, n_types), dtype=bool)
    for i in range(n_pokemon):
        num_types = rng.choice([1, 2])
        selected = rng.choice(n_types, size=num_types, replace=False)
        pokemon_types[i, selected] = True

    # Move Types matrix
    move_types = np.zeros((n_moves, n_types), dtype=bool)
    for i in range(n_moves):
        selected = rng.integers(0, n_types, size=1)[0]
        move_types[i, selected] = True

    # Pokemon Stats matrix
    ps = rng.integers(20, 110, size=(n_pokemon, n_stats), dtype=np.int16, endpoint=True)

    # Natures
    natures = rng.integers(-1, 1, size=(n_natures, n_stats), dtype=np.int16, endpoint=True)

    # Register objectives with data
    register_objective_data(
        {"moves_category": me},
        objective_names=["test_objective", "test_objective2", "test_objective3"],
    )

    return {
        "n_pokemon": n_pokemon,
        "n_moves": n_moves,
        "n_types": n_types,
        "n_stats": n_stats,
        "seed": seed,
        "me": me,
        "lm": lm,
        "pt": pokemon_types,
        "mt": move_types,
        "ps": ps,
        "natures": natures,
    }


@pytest.fixture
def problem(test_data: Dict[str, Any]) -> PokemonProblem:
    """Create a PokemonProblem instance for testing."""
    objectives = ObjectiveSelector(objective_names=["test_objective", "test_objective2"])
    return PokemonProblem(
        objectives=objectives,
        lm=test_data["lm"],
        n_pokemon=test_data["n_pokemon"],
        n_moves=test_data["n_moves"],
        pokemon_in_team=MAX_NUMBER_OF_POKEMON,
    )


@pytest.fixture
def pre_selected(test_data: Dict[str, Any]) -> Dict[int, list]:
    """Create a pre_selected dictionary for testing."""
    pre_selected = {1: [], 2: [], 3: []}
    for i in pre_selected.keys():
        learnable = np.where(test_data["lm"][i])[0]
        if len(learnable) >= 2:
            pre_selected[i] = list(learnable[:2])
    return pre_selected
