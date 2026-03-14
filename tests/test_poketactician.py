"""Tests for the PokeTactician class."""

from typing import Any, Dict

import numpy as np
import pytest
from matplotlib import pyplot as plt

from poketactician.engine.mutation import PokemonMutation
from poketactician.engine.sampling import PokemonTeamSampling
from poketactician.poketactician import PokeTactician


class TestPokeTactician:
    """Additional tests for the PokeTactician class."""

    def test_poketactician_with_custom_params(self, test_data: Dict[str, Any]) -> None:
        """Test that PokeTactician works with custom parameters."""
        # Create a PokeTactician instance with custom parameters
        n_pokemon = 4  # Custom number of pokemon in team

        poke_tactician = PokeTactician(
            objectives=["test_objective", "test_objective2"],
            seed=test_data["seed"],
            learnable_moves=test_data["lm"],
            moves_category=test_data["me"],
            pokemon_types=test_data["pt"],
            move_types=test_data["mt"],
            pokemon_stats=test_data["ps"],
            natures=test_data["natures"],
            n_pokemon=n_pokemon,
        )

        # Run optimization with the custom parameters
        result = poke_tactician.optimize(pop_size=10, n_gen=2, verbose=False, history=True)

        # Check that the solutions have the correct shape
        assert result.X.shape[1] == n_pokemon + n_pokemon * 4

        # Extract the pokemon indices from the solutions
        for solution in result.X:
            x = solution[:n_pokemon]

            # Check that the team size is correct
            assert len(x) == n_pokemon

            # Check that all Pokemon IDs are valid
            assert np.all(x >= 0) and np.all(x < test_data["n_pokemon"])

    def test_poketactician_without_history(self, test_data: Dict[str, Any]) -> None:
        """Test that PokeTactician works correctly when history is not saved."""
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

        # Run optimization without saving history
        result = poke_tactician.optimize(pop_size=10, n_gen=2, verbose=False, history=False)

        # Check that the results are correct
        assert result is not None

        # Check that history was not saved
        assert hasattr(result, "history") and result.history == []

        # Test that methods that require history raise an error
        with pytest.raises(ValueError):
            poke_tactician.convergence_plot()

        with pytest.raises(ValueError):
            poke_tactician.running_metric_plot()

        # Test that methods that don't require history still work
        try:
            with plt.rc_context({"backend": "Agg"}):
                poke_tactician.solutions_plot()
            plt.close("all")  # Close any created figures
        except ValueError:
            pytest.fail("solutions_plot should not require history")

    def test_poketactician_random_state(self, test_data: Dict[str, Any]) -> None:
        """Test that PokeTactician random state works correctly with different seeds."""
        # Create two PokeTactician instances with the same seed
        seed = 42
        poke_tactician1 = PokeTactician(
            objectives=["test_objective", "test_objective2"],
            seed=test_data["seed"],
            learnable_moves=test_data["lm"],
            moves_category=test_data["me"],
            pokemon_types=test_data["pt"],
            move_types=test_data["mt"],
            pokemon_stats=test_data["ps"],
            natures=test_data["natures"],
        )

        poke_tactician2 = PokeTactician(
            objectives=["test_objective", "test_objective2"],
            seed=test_data["seed"],
            learnable_moves=test_data["lm"],
            moves_category=test_data["me"],
            pokemon_types=test_data["pt"],
            move_types=test_data["mt"],
            pokemon_stats=test_data["ps"],
            natures=test_data["natures"],
        )

        # Run optimization with both instances
        result1 = poke_tactician1.optimize(pop_size=10, n_gen=2, verbose=False, history=False)
        result2 = poke_tactician2.optimize(pop_size=10, n_gen=2, verbose=False, history=False)

        # Check that the results are the same
        assert np.array_equal(result1.X, result2.X)
        assert np.array_equal(result1.F, result2.F)

        # Create a PokeTactician instance with a different seed
        poke_tactician3 = PokeTactician(
            objectives=["test_objective", "test_objective2"],
            seed=seed + 1,  # Different seed
            learnable_moves=test_data["lm"],
            moves_category=test_data["me"],
            pokemon_types=test_data["pt"],
            move_types=test_data["mt"],
            pokemon_stats=test_data["ps"],
            natures=test_data["natures"],
        )

        # Run optimization with the different seed
        result3 = poke_tactician3.optimize(pop_size=10, n_gen=2, verbose=False, history=False)

        # Check that the results are different
        assert not np.array_equal(result1.X, result3.X)

        # Create a PokeTactician instance with no seed
        poke_tactician4 = PokeTactician(
            objectives=["test_objective", "test_objective2"],
            seed=None,  # No seed
            learnable_moves=test_data["lm"],
            moves_category=test_data["me"],
            pokemon_types=test_data["pt"],
            move_types=test_data["mt"],
            pokemon_stats=test_data["ps"],
            natures=test_data["natures"],
        )

        # Run optimization with no seed
        result4 = poke_tactician4.optimize(pop_size=10, n_gen=2, verbose=False, history=False)

        # Check that the results are produced (we can't check for randomness directly)
        assert result4 is not None


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


class TestPreSelected:
    """Tests for the PokeTactician class."""

    def test_pre_selected_poketactician(self, test_data: Dict[str, Any]) -> None:
        """Test that pre-selected Pokémon are handled correctly."""
        pre_selected = [1, 3, 5]

        poke_tactician = PokeTactician(
            objectives=["test_objective", "test_objective2"],
            seed=test_data["seed"],
            learnable_moves=test_data["lm"],
            moves_category=test_data["me"],
            pokemon_types=test_data["pt"],
            move_types=test_data["mt"],
            pokemon_stats=test_data["ps"],
            natures=test_data["natures"],
            pre_selected=pre_selected,
        )

        poke_tactician.optimize(pop_size=10, n_gen=10, verbose=False)

        res = poke_tactician.results
        pokemon = res.X[0][:6]
        assert all(item in pokemon for item in pre_selected), "Pre-selected Pokémon should be in the optimized team."

    def test_pre_selected_sampling(self, test_data: Dict[str, Any]) -> None:
        """Test that pre-selected Pokémon are handled correctly in sampling."""
        pre_selected = [1, 3, 5]

        poke_tactician = PokeTactician(
            objectives=["test_objective", "test_objective2"],
            seed=test_data["seed"],
            learnable_moves=test_data["lm"],
            moves_category=test_data["me"],
            pokemon_types=test_data["pt"],
            move_types=test_data["mt"],
            pokemon_stats=test_data["ps"],
            natures=test_data["natures"],
            pre_selected=pre_selected,
        )
        sampling = PokemonTeamSampling(random_state=poke_tactician.random_state, pre_selected=pre_selected)
        # Sample a team
        sampled_team = sampling._do(problem=poke_tactician.problem, n_samples=1)
        sampled_pokemon = sampled_team[0][:6]
        assert all(item in sampled_pokemon for item in pre_selected), "Pre-selected Pokémon should be in the sampled team."

    def test_pre_selected_mutation(self, test_data: Dict[str, Any]) -> None:
        """Test that pre-selected Pokémon are handled correctly in mutation."""
        pre_selected = [1, 3, 5]

        poke_tactician = PokeTactician(
            objectives=["test_objective", "test_objective2"],
            seed=test_data["seed"],
            learnable_moves=test_data["lm"],
            moves_category=test_data["me"],
            pokemon_types=test_data["pt"],
            move_types=test_data["mt"],
            pokemon_stats=test_data["ps"],
            natures=test_data["natures"],
            pre_selected=pre_selected,
        )

        # Create a sample team to pass to the mutation
        sampling = PokemonTeamSampling(random_state=poke_tactician.random_state, pre_selected=pre_selected)

        sampled_team = sampling._do(problem=poke_tactician.problem, n_samples=1)

        mutation = PokemonMutation(
            random_state=poke_tactician.random_state,
            prob_pokemon=0.5,
            prob_move=0.5,
            pre_selected_size=len(pre_selected),
        )

        mutated_team = mutation._do(problem=poke_tactician.problem, X=sampled_team)[0]

        mutated_pokemon = mutated_team[:6]
        assert all(item in mutated_pokemon for item in pre_selected), "Pre-selected Pokémon should be in the mutated team."
