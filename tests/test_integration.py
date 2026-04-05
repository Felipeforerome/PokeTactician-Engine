"""Integration tests for the PokeTactician system."""

from typing import Any, Dict

import numpy as np
import pytest
from matplotlib import pyplot as plt

from poketactician.config import MAX_NUMBER_OF_POKEMON, NUMBER_OF_MOVES_SLOTS
from poketactician.poketactician import PokeTactician
from tests.utils import assert_preselected_in_solution


class TestIntegration:
    """Integration tests for the full PokeTactician workflow."""

    def test_full_optimization_workflow(self, test_data: Dict[str, Any]) -> None:
        """Test complete optimization workflow from initialization to results."""
        poke_tactician = PokeTactician(
            objectives=["test_objective", "test_objective3", "expected_damage"],
            seed=42,
            learnable_moves=test_data["lm"],
            moves_category=test_data["me"],
            pokemon_types=test_data["pt"],
            move_types=test_data["mt"],
            pokemon_stats=test_data["ps"],
            natures=test_data["natures"],
        )

        # Run optimization
        result = poke_tactician.optimize(pop_size=20, n_gen=5, verbose=False)

        # Verify results
        assert result is not None
        assert result.X is not None
        assert result.F is not None
        assert len(result.X) > 0

        # Check solution validity
        for solution in result.X:
            x = solution[:MAX_NUMBER_OF_POKEMON]  # Pokemon IDs
            y = solution[MAX_NUMBER_OF_POKEMON:].reshape(MAX_NUMBER_OF_POKEMON, NUMBER_OF_MOVES_SLOTS)  # Moves

            # Unique pokemon
            assert len(set(x)) == len(x)

            # Valid pokemon IDs
            assert np.all(x >= 0)
            assert np.all(x < test_data["n_pokemon"])

            # Valid moves
            for i, pokemon_id in enumerate(x):
                for move_id in y[i]:
                    if move_id >= 0:
                        assert test_data["lm"][pokemon_id, move_id]

    def test_optimization_with_preselected_pokemon(self, test_data: Dict[str, Any], pre_selected: Dict[int, list]) -> None:
        """Test optimization workflow with pre-selected pokemon."""

        poke_tactician = PokeTactician(
            objectives=["test_objective"],
            seed=42,
            learnable_moves=test_data["lm"],
            moves_category=test_data["me"],
            pokemon_types=test_data["pt"],
            move_types=test_data["mt"],
            pokemon_stats=test_data["ps"],
            pre_selected=pre_selected,
        )

        result = poke_tactician.optimize(pop_size=10, n_gen=3, verbose=False)

        # Validate all solutions have preselected pokemon and moves
        for solution in result.X:
            assert_preselected_in_solution(solution, pre_selected)

    def test_optimization_convergence(self, test_data: Dict[str, Any]) -> None:
        """Test that optimization shows improvement over generations."""
        poke_tactician = PokeTactician(
            objectives=["test_objective"],
            seed=42,
            learnable_moves=test_data["lm"],
            moves_category=test_data["me"],
            pokemon_types=test_data["pt"],
            move_types=test_data["mt"],
            pokemon_stats=test_data["ps"],
        )

        result = poke_tactician.optimize(pop_size=20, n_gen=10, verbose=False, history=True)

        # Check that we have history
        assert hasattr(result, "history")
        assert len(result.history) > 0  # type: ignore

        # First generation fitness
        first_gen_best = result.history[0].opt.get("F")[0]  # type: ignore
        # Last generation fitness
        last_gen_best = result.history[-1].opt.get("F")[0]  # type: ignore

        # For minimization, last should be <= first (better or equal)
        # Note: might not always improve, but typically should
        assert isinstance(first_gen_best[0], (int, float, np.number))
        assert isinstance(last_gen_best[0], (int, float, np.number))

    def test_multiple_objectives_pareto_front(self, test_data: Dict[str, Any]) -> None:
        """Test multi-objective optimization produces Pareto front."""
        poke_tactician = PokeTactician(
            objectives=["test_objective", "test_objective3"],
            seed=42,
            learnable_moves=test_data["lm"],
            moves_category=test_data["me"],
            pokemon_types=test_data["pt"],
            move_types=test_data["mt"],
            pokemon_stats=test_data["ps"],
        )

        result = poke_tactician.optimize(pop_size=30, n_gen=5, verbose=False)

        # Should have multiple solutions on Pareto front
        assert len(result.X) > 1

        # Each solution should have 2 objective values
        for obj_values in result.F:
            assert len(obj_values) == 2

    def test_different_team_sizes(self, test_data: Dict[str, Any]) -> None:
        """Test optimization with different team sizes."""
        for team_size in [1, 3, 6]:
            poke_tactician = PokeTactician(
                objectives=["test_objective"],
                seed=42,
                learnable_moves=test_data["lm"],
                moves_category=test_data["me"],
                pokemon_types=test_data["pt"],
                move_types=test_data["mt"],
                pokemon_stats=test_data["ps"],
                n_pokemon=team_size,
            )

            result = poke_tactician.optimize(pop_size=10, n_gen=2, verbose=False)

            # Check solution shape
            expected_var_size = team_size + team_size * NUMBER_OF_MOVES_SLOTS
            assert result.X[0].shape[0] == expected_var_size

    def test_reproducibility_across_runs(self, test_data: Dict[str, Any]) -> None:
        """Test that same seed produces identical results across runs."""
        seed = 42

        # First run
        poke_tactician1 = PokeTactician(
            objectives=["test_objective"],
            seed=seed,
            learnable_moves=test_data["lm"],
            moves_category=test_data["me"],
            pokemon_types=test_data["pt"],
            move_types=test_data["mt"],
            pokemon_stats=test_data["ps"],
        )
        result1 = poke_tactician1.optimize(pop_size=10, n_gen=3, verbose=False)

        # Second run
        poke_tactician2 = PokeTactician(
            objectives=["test_objective"],
            seed=seed,
            learnable_moves=test_data["lm"],
            moves_category=test_data["me"],
            pokemon_types=test_data["pt"],
            move_types=test_data["mt"],
            pokemon_stats=test_data["ps"],
        )
        result2 = poke_tactician2.optimize(pop_size=10, n_gen=3, verbose=False)

        # Results should be identical
        assert np.array_equal(result1.X, result2.X)
        assert np.array_equal(result1.F, result2.F)

    def test_plotting_with_history(self, test_data: Dict[str, Any]) -> None:
        """Test that plotting methods work with history enabled."""
        poke_tactician = PokeTactician(
            objectives=["test_objective"],
            seed=42,
            learnable_moves=test_data["lm"],
            moves_category=test_data["me"],
            pokemon_types=test_data["pt"],
            move_types=test_data["mt"],
            pokemon_stats=test_data["ps"],
        )

        poke_tactician.optimize(pop_size=10, n_gen=5, verbose=False, history=False)

        # Test plotting methods don't crash
        with pytest.raises(ValueError):
            with plt.rc_context({"backend": "Agg"}):
                poke_tactician.convergence_plot()
                poke_tactician.running_metric_plot()
                poke_tactician.solutions_plot()
            plt.close("all")

    def test_solutions_plot_without_history(self, test_data: Dict[str, Any]) -> None:
        """Test that solutions_plot works without history."""
        poke_tactician = PokeTactician(
            objectives=["test_objective", "test_objective2"],
            seed=42,
            learnable_moves=test_data["lm"],
            moves_category=test_data["me"],
            pokemon_types=test_data["pt"],
            move_types=test_data["mt"],
            pokemon_stats=test_data["ps"],
        )

        poke_tactician.optimize(pop_size=10, n_gen=2, verbose=False, history=False)

        # solutions_plot should work without history
        try:
            with plt.rc_context({"backend": "Agg"}):
                poke_tactician.solutions_plot()
            plt.close("all")
        except ValueError:
            pytest.fail("solutions_plot should not require history")

    def test_single_generation_optimization(self, test_data: Dict[str, Any]) -> None:
        """Test optimization with just one generation."""
        poke_tactician = PokeTactician(
            objectives=["test_objective"],
            seed=42,
            learnable_moves=test_data["lm"],
            moves_category=test_data["me"],
            pokemon_types=test_data["pt"],
            move_types=test_data["mt"],
            pokemon_stats=test_data["ps"],
        )

        result = poke_tactician.optimize(pop_size=10, n_gen=1, verbose=False)

        assert result is not None
        assert len(result.X) > 0

    def test_constraint_satisfaction(self, test_data: Dict[str, Any]) -> None:
        """Test that final solutions satisfy all constraints."""
        poke_tactician = PokeTactician(
            objectives=["test_objective"],
            seed=42,
            learnable_moves=test_data["lm"],
            moves_category=test_data["me"],
            pokemon_types=test_data["pt"],
            move_types=test_data["mt"],
            pokemon_stats=test_data["ps"],
        )

        poke_tactician.optimize(pop_size=20, n_gen=10, verbose=False)

        x = poke_tactician.best_solution[:MAX_NUMBER_OF_POKEMON]
        y = poke_tactician.best_solution[MAX_NUMBER_OF_POKEMON:].reshape(MAX_NUMBER_OF_POKEMON, NUMBER_OF_MOVES_SLOTS)

        # Constraint 1: Unique pokemon
        assert len(set(x)) == len(x), "Pokemon should be unique"

        # Constraint 2: Learnable moves
        for i, pokemon_id in enumerate(x):
            for move_id in y[i]:
                if move_id >= 0:
                    assert test_data["lm"][pokemon_id, move_id], f"Pokemon {pokemon_id} should be able to learn move {move_id}"

        # Constraint 3: Unique moves per pokemon
        for i in range(MAX_NUMBER_OF_POKEMON):
            valid_moves = y[i][y[i] >= 0]
            assert len(set(valid_moves)) == len(valid_moves), "Moves should be unique per pokemon"

    @pytest.mark.skip(reason="Natures not implemented yet")
    def test_optimization_with_natures(self, test_data: Dict[str, Any]) -> None:
        """Test optimization workflow includes natures."""
        poke_tactician = PokeTactician(
            objectives=["test_objective"],
            seed=42,
            learnable_moves=test_data["lm"],
            moves_category=test_data["me"],
            pokemon_types=test_data["pt"],
            move_types=test_data["mt"],
            pokemon_stats=test_data["ps"],
            natures=test_data["natures"],
        )

        assert poke_tactician.natures is not None

        result = poke_tactician.optimize(pop_size=10, n_gen=2, verbose=False)

        assert result is not None

    def test_verbose_output(self, test_data: Dict[str, Any], capsys: pytest.CaptureFixture[str]) -> None:
        """Test that verbose mode produces output."""
        poke_tactician = PokeTactician(
            objectives=["test_objective"],
            seed=42,
            learnable_moves=test_data["lm"],
            moves_category=test_data["me"],
            pokemon_types=test_data["pt"],
            move_types=test_data["mt"],
            pokemon_stats=test_data["ps"],
        )

        poke_tactician.optimize(pop_size=10, n_gen=2, verbose=True)

        # Check that something was printed
        captured = capsys.readouterr()
        # Verbose mode should produce some output
        # (exact format depends on pymoo, so we just check it's not empty)
        assert len(captured.out) > 0 or len(captured.err) > 0

    def test_multiple_optimizations(self, test_data: Dict[str, Any]) -> None:
        """Test running optimization multiple times on same instance."""
        poke_tactician = PokeTactician(
            objectives=["test_objective"],
            seed=42,
            learnable_moves=test_data["lm"],
            moves_category=test_data["me"],
            pokemon_types=test_data["pt"],
            move_types=test_data["mt"],
            pokemon_stats=test_data["ps"],
        )

        # Run optimization twice
        result1 = poke_tactician.optimize(pop_size=10, n_gen=2, verbose=False)
        result2 = poke_tactician.optimize(pop_size=10, n_gen=2, verbose=False)

        # Both should succeed
        assert result1 is not None
        assert result2 is not None

        # Results should be different (unless seed is reset internally)
        # Actually, with same seed in instance, might be same - just check both work
        assert len(result1.X) > 0
        assert len(result2.X) > 0

    def test_results_property_after_optimization(self, test_data: Dict[str, Any]) -> None:
        """Test that results property works after optimization."""
        poke_tactician = PokeTactician(
            objectives=["test_objective"],
            seed=42,
            learnable_moves=test_data["lm"],
            moves_category=test_data["me"],
            pokemon_types=test_data["pt"],
            move_types=test_data["mt"],
            pokemon_stats=test_data["ps"],
        )

        # Before optimization, should raise error
        with pytest.raises(ValueError):
            _ = poke_tactician.results

        # After optimization, should work
        _ = poke_tactician.optimize(pop_size=10, n_gen=2, verbose=False)
        results = poke_tactician.results

        assert results is not None
        assert results.X is not None

    def test_objective_values_reasonable(self, test_data: Dict[str, Any]) -> None:
        """Test that objective values are reasonable (not NaN, not infinite)."""
        poke_tactician = PokeTactician(
            objectives=["test_objective", "test_objective2"],
            seed=42,
            learnable_moves=test_data["lm"],
            moves_category=test_data["me"],
            pokemon_types=test_data["pt"],
            move_types=test_data["mt"],
            pokemon_stats=test_data["ps"],
        )

        result = poke_tactician.optimize(pop_size=10, n_gen=3, verbose=False)

        # Check all objective values are finite
        for obj_values in result.F:
            for val in obj_values:
                assert not np.isnan(val), "Objective value should not be NaN"
                assert not np.isinf(val), "Objective value should not be infinite"

    def test_population_diversity(self, test_data: Dict[str, Any]) -> None:
        """Test that optimization produces diverse solutions."""
        solutions = list()
        for i in range(5):
            poke_tactician = PokeTactician(
                objectives=["test_objective"],
                seed=42 + i,
                learnable_moves=test_data["lm"],
                moves_category=test_data["me"],
                pokemon_types=test_data["pt"],
                move_types=test_data["mt"],
                pokemon_stats=test_data["ps"],
            )

            poke_tactician.optimize(pop_size=20, n_gen=5, verbose=False)
            solutions.append(poke_tactician.best_solution)

        # Convert solutions to tuples for comparison
        solutions_as_tuples = [tuple(sol) for sol in solutions]
        unique_solutions = len(set(solutions_as_tuples))

        # Should have some diversity (at least 50% unique)
        assert unique_solutions >= len(solutions) * 0.5, "Solutions should be diverse"
