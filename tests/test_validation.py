"""Tests for data validation and error handling."""

from typing import Any, Dict

import numpy as np
import pytest

from poketactician.engine.problem import PokemonProblem
from poketactician.engine.selector import ObjectiveSelector
from poketactician.poketactician import PokeTactician


class TestDataValidation:
    """Tests for data validation and error handling."""

    def test_poketactician_with_mismatched_dimensions(self, test_data: Dict[str, Any]) -> None:
        """Test that PokeTactician handles mismatched array dimensions."""
        # Create learnable_moves with wrong shape
        wrong_lm = np.zeros((5, 10), dtype=bool)  # Wrong number of pokemon

        # This should work but might cause issues during optimization
        poke_tactician = PokeTactician(
            objectives=["test_objective"],
            seed=42,
            learnable_moves=wrong_lm,
            moves_category=test_data["me"],
            pokemon_types=test_data["pt"],
            move_types=test_data["mt"],
            pokemon_stats=test_data["ps"],
            n_pokemon=6,
        )

        # Should create successfully
        assert poke_tactician is not None

    @pytest.mark.skip(reason="Not implemented yet")
    def test_poketactician_with_invalid_team_size(self, test_data: Dict[str, Any]) -> None:
        """Test PokeTactician with team size larger than available pokemon."""
        # Try to create a team of 20 but only have 13 pokemon
        poke_tactician = PokeTactician(
            objectives=["test_objective"],
            seed=42,
            learnable_moves=test_data["lm"],
            moves_category=test_data["me"],
            pokemon_types=test_data["pt"],
            move_types=test_data["mt"],
            pokemon_stats=test_data["ps"],
            n_pokemon=20,  # More than actual pokemon in data
        )

        # Should create, but optimization might fail
        assert poke_tactician is not None

    def test_poketactician_with_zero_team_size(self, test_data: Dict[str, Any]) -> None:
        """Test PokeTactician with zero team size."""
        # This should probably fail or handle gracefully, the added fluff is in case something changes later
        try:
            poke_tactician = PokeTactician(
                objectives=["test_objective"],
                seed=42,
                learnable_moves=test_data["lm"],
                moves_category=test_data["me"],
                pokemon_types=test_data["pt"],
                move_types=test_data["mt"],
                pokemon_stats=test_data["ps"],
                n_pokemon=0,
            )
            # If it doesn't error, at least check it was created
            assert poke_tactician is not None
        except (ValueError, AssertionError, IndexError):
            # Expected behavior
            pass

        assert poke_tactician is not None

    def test_poketactician_with_empty_objectives(self, test_data: Dict[str, Any]) -> None:
        """Test that PokeTactician with empty objectives list."""

        with pytest.raises(ValueError, match="At least one objective must be provided"):
            PokeTactician(
                objectives=[],
                seed=42,
                learnable_moves=test_data["lm"],
                moves_category=test_data["me"],
                pokemon_types=test_data["pt"],
                move_types=test_data["mt"],
                pokemon_stats=test_data["ps"],
            )

    def test_poketactician_with_invalid_objective(self, test_data: Dict[str, Any]) -> None:
        """Test that PokeTactician raises error for invalid objective."""
        with pytest.raises(AssertionError, match="Some objectives are not registered: {'nonexistent_objective'}"):
            PokeTactician(
                objectives=["nonexistent_objective"],
                seed=42,
                learnable_moves=test_data["lm"],
                moves_category=test_data["me"],
                pokemon_types=test_data["pt"],
                move_types=test_data["mt"],
                pokemon_stats=test_data["ps"],
            )

    @pytest.mark.skip(reason="Not implemented yet")
    def test_poketactician_with_preselected_out_of_range(self, test_data: Dict[str, Any]) -> None:
        """Test PokeTactician with pre_selected pokemon IDs out of range."""
        # Pre-select pokemon that don't exist
        pre_selected = {100: [], 200: []}

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

        assert poke_tactician is not None

        # Should create, behavior during optimization is undefined
        assert poke_tactician is not None

    def test_optimize_with_zero_generations(self, test_data: Dict[str, Any]) -> None:
        """Test optimization with zero generations."""
        poke_tactician = PokeTactician(
            objectives=["test_objective"],
            seed=42,
            learnable_moves=test_data["lm"],
            moves_category=test_data["me"],
            pokemon_types=test_data["pt"],
            move_types=test_data["mt"],
            pokemon_stats=test_data["ps"],
        )

        with pytest.raises(ZeroDivisionError):
            poke_tactician.optimize(pop_size=10, n_gen=0, verbose=False)
            # If it works, check that we got some result

    def test_optimize_with_zero_population(self, test_data: Dict[str, Any]) -> None:
        """Test optimization with zero population size."""
        poke_tactician = PokeTactician(
            objectives=["test_objective"],
            seed=42,
            learnable_moves=test_data["lm"],
            moves_category=test_data["me"],
            pokemon_types=test_data["pt"],
            move_types=test_data["mt"],
            pokemon_stats=test_data["ps"],
        )

        # Try to optimize with 0 population
        with pytest.raises(ValueError, match="attempt to get argmin of an empty sequence"):
            poke_tactician.optimize(pop_size=0, n_gen=2, verbose=False)

    def test_results_without_optimization(self, test_data: Dict[str, Any]) -> None:
        """Test accessing results before running optimization."""
        poke_tactician = PokeTactician(
            objectives=["test_objective"],
            seed=42,
            learnable_moves=test_data["lm"],
            moves_category=test_data["me"],
            pokemon_types=test_data["pt"],
            move_types=test_data["mt"],
            pokemon_stats=test_data["ps"],
        )

        # Try to access results before optimization
        with pytest.raises(ValueError, match="No results available"):
            _ = poke_tactician.results

    def test_plotting_without_optimization(self, test_data: Dict[str, Any]) -> None:
        """Test plotting methods before running optimization."""
        poke_tactician = PokeTactician(
            objectives=["test_objective"],
            seed=42,
            learnable_moves=test_data["lm"],
            moves_category=test_data["me"],
            pokemon_types=test_data["pt"],
            move_types=test_data["mt"],
            pokemon_stats=test_data["ps"],
        )

        # Try to plot before optimization
        with pytest.raises(ValueError, match=r"No results available. Run optimize\(\) first\."):
            poke_tactician.convergence_plot()

    def test_poketactician_with_all_false_learnable_moves(self, test_data: Dict[str, Any]) -> None:
        """Test PokeTactician when no pokemon can learn any moves."""
        # Create LM where no pokemon can learn moves
        empty_lm = np.zeros_like(test_data["lm"], dtype=bool)

        poke_tactician = PokeTactician(
            objectives=["test_objective"],
            seed=42,
            learnable_moves=empty_lm,
            moves_category=test_data["me"],
            pokemon_types=test_data["pt"],
            move_types=test_data["mt"],
            pokemon_stats=test_data["ps"],
        )

        with pytest.raises(Exception, match="Problem Error: G can not be set, expected shape .+"):
            poke_tactician.optimize(pop_size=10, n_gen=2, verbose=False)

    def test_objective_selector_with_partial_match(self) -> None:
        """Test ObjectiveSelector with objective that doesn't exist."""
        with pytest.raises(AssertionError, match=r"Some objectives are not registered: .+"):
            ObjectiveSelector(objective_names=["test_objective", "fake_objective"])

    @pytest.mark.skip(reason="Check not implemented yet")
    def test_problem_with_negative_team_size(self, test_data: Dict[str, Any]) -> None:
        """Test PokemonProblem with negative team size."""
        objectives = ObjectiveSelector(objective_names=["test_objective"])

        try:
            problem = PokemonProblem(
                objectives=objectives,
                lm=test_data["lm"],
                n_pokemon=test_data["n_pokemon"],
                n_moves=test_data["n_moves"],
                pokemon_in_team=-1,
            )
            # If it doesn't error, behavior is undefined
            assert problem is not None
        except (ValueError, AssertionError):
            # Expected
            pass

    def test_poketactician_with_none_natures(self, test_data: Dict[str, Any]) -> None:
        """Test that PokeTactician handles None natures correctly."""
        poke_tactician = PokeTactician(
            objectives=["test_objective"],
            seed=42,
            learnable_moves=test_data["lm"],
            moves_category=test_data["me"],
            pokemon_types=test_data["pt"],
            move_types=test_data["mt"],
            pokemon_stats=test_data["ps"],
            natures=None,
        )

        poke_tactician.optimize(pop_size=5, n_gen=2, verbose=False)
