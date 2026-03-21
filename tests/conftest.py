"""Test utilities and fixtures for PokeTactician tests."""

from typing import Any, Dict

import numpy as np
import pytest

from poketactician.engine.problem import PokemonProblem
from poketactician.engine.selector import ObjectiveSelector

# Import objectives to ensure they're registered
from poketactician.objectives.dummy_objectives import (  # noqa: F401
    test_objective,
    test_objective2,
    test_objective3,
)
from poketactician.registry import register_objective_data


@pytest.fixture
def test_data() -> Dict[str, Any]:
    """Create test data for the PokeTactician test cases."""
    n_pokemon = 13
    n_moves = 20
    n_types = 18
    n_stats = 6
    n_natures = 25

    # Set a fixed seed for reproducibility
    seed = 42
    rng = np.random.default_rng(seed)

    # Move Effectiveness matrix
    me = rng.integers(20, 110, size=(2, n_moves), dtype=np.int16, endpoint=True)
    rows = rng.integers(0, 1, size=me.shape[1], endpoint=True)
    me[rows, np.arange(me.shape[1])] = 0

    # Learnable Moves matrix
    lm = rng.integers(0, 2, size=(n_pokemon, n_moves), dtype=bool)

    # Make sure each Pokemon has at least 4 learnable moves
    for i in range(n_pokemon):
        if np.sum(lm[i]) < 4:
            # Add random learnable moves until we have at least 4
            indices = np.where(~lm[i])[0]
            to_set = rng.choice(indices, size=4 - np.sum(lm[i]), replace=False)
            lm[i, to_set] = True

    # Pokemon Types matrix
    pt = rng.integers(0, 2, size=(n_pokemon, n_types), dtype=bool)

    # Move Types matrix
    mt = rng.integers(0, 2, size=(n_moves, n_types), dtype=bool)

    # Pokemon Stats matrix
    ps = rng.integers(20, 110, size=(n_pokemon, n_stats), dtype=np.int16, endpoint=True)

    # Natures
    natures = rng.integers(-1, 1, size=(n_natures, n_stats), dtype=np.int16, endpoint=True)

    # Register objectives with data
    register_objective_data(
        {
            "test_objective": {"me": me},
            "test_objective2": {"me": me},
            "test_objective3": {"me": me},
        }
    )

    return {
        "n_pokemon": n_pokemon,
        "n_moves": n_moves,
        "n_types": n_types,
        "n_stats": n_stats,
        "seed": seed,
        "me": me,
        "lm": lm,
        "pt": pt,
        "mt": mt,
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
        pokemon_in_team=6,
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
