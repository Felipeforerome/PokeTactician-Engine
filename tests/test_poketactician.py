"""Tests for the PokeTactician class."""

from typing import Any, Dict

import numpy as np
import pytest
from matplotlib import pyplot as plt

from poketactician.engine.mutation import PokemonMutation
from poketactician.engine.sampling import PokemonTeamSampling
from poketactician.poketactician import PokeTactician


class TestPokeTacticianDecorators:
    """Tests for PokeTactician decorators."""

    def test_has_been_optimized_decorator(self, test_data: Dict[str, Any]) -> None:
        """Test that @has_been_optimized decorator works correctly."""
        # Create a PokeTactician instance
        poke_tactician = PokeTactician(
            objectives=["test_objective", "test_objective2"],
            seed=test_data["seed"],
            learnable_moves=test_data["lm"],
            moves_category=test_data["me"],
            pokemon_types=test_data["pt"],
            move_types=test_data["mt"],
            pokemon_stats=test_data["ps"],
            natures=test_data["natures"],
        )

        # Test @has_been_optimized decorator before optimization
        with pytest.raises(ValueError) as exc_info:
            poke_tactician.convergence_plot()
            assert str(exc_info.value) == "No results available. Run optimize() first."

        # Run optimization
        poke_tactician.optimize(pop_size=10, n_gen=2, verbose=False)

        # Now it should work
        try:
            import matplotlib.pyplot as plt

            with plt.rc_context({"backend": "Agg"}):
                poke_tactician.solutions_plot()
            plt.close("all")  # Close any created figures
        except ValueError:
            assert False, "Should not have raised ValueError"

    def test_with_history_decorator(self, test_data: Dict[str, Any]) -> None:
        """Test that @with_history decorator works correctly."""
        # Create a PokeTactician instance
        poke_tactician = PokeTactician(
            objectives=["test_objective", "test_objective2"],
            seed=test_data["seed"],
            learnable_moves=test_data["lm"],
            moves_category=test_data["me"],
            pokemon_types=test_data["pt"],
            move_types=test_data["mt"],
            pokemon_stats=test_data["ps"],
            natures=test_data["natures"],
        )

        # Run optimization without history
        poke_tactician.optimize(pop_size=10, n_gen=2, verbose=False, history=False)

        # Test @with_history decorator
        try:
            with plt.rc_context({"backend": "Agg"}):
                poke_tactician.convergence_plot()
            plt.close("all")  # Close any created figures
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert str(e) == "History is not saved. Set save_history=True in optimize()."

        # Run optimization with history
        poke_tactician.optimize(pop_size=10, n_gen=2, verbose=False, history=True)

        # Now it should work
        try:
            with plt.rc_context({"backend": "Agg"}):
                poke_tactician.convergence_plot()
            plt.close("all")  # Close any created figures
        except ValueError:
            assert False, "Should not have raised ValueError"
