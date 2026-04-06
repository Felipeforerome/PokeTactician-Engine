"""Tests for the PokemonProblem class."""

from typing import Any, Dict

import numpy as np

from poketactician.config import MAX_NUMBER_OF_POKEMON, NUMBER_OF_MOVES_SLOTS
from poketactician.engine.problem import PokemonProblem
from poketactician.engine.selector import ObjectiveSelector


class TestPokemonProblem:
    """Tests for the PokemonProblem class."""

    def test_problem_initialization(self, test_data: Dict[str, Any]) -> None:
        """Test that PokemonProblem initializes correctly."""
        objectives = ObjectiveSelector(objective_names=["test_objective", "test_objective2"])
        problem = PokemonProblem(
            objectives=objectives,
            lm=test_data["lm"],
            n_pokemon=test_data["n_pokemon"],
            n_moves=test_data["n_moves"],
            pokemon_in_team=MAX_NUMBER_OF_POKEMON,
        )

        assert problem.n_pokemon == test_data["n_pokemon"]
        assert problem.n_moves == test_data["n_moves"]
        assert problem.pokemon_in_team == MAX_NUMBER_OF_POKEMON
        assert problem.n_var == MAX_NUMBER_OF_POKEMON + MAX_NUMBER_OF_POKEMON * NUMBER_OF_MOVES_SLOTS  # pokemon + moves
        assert problem.n_obj == 2  # Two objectives
        assert problem.unique_pokemon_only is False

    def test_problem_with_repeat_pokemon(self, test_data: Dict[str, Any]) -> None:
        """Test PokemonProblem with repeat_pokemon=True."""
        objectives = ObjectiveSelector(objective_names=["test_objective"])
        problem = PokemonProblem(
            objectives=objectives,
            lm=test_data["lm"],
            n_pokemon=test_data["n_pokemon"],
            n_moves=test_data["n_moves"],
            pokemon_in_team=MAX_NUMBER_OF_POKEMON,
            unique_pokemon_only=True,
        )

        assert problem.unique_pokemon_only is True
        # With repeat_pokemon=True, we have one extra constraint
        assert problem.n_ieq_constr == MAX_NUMBER_OF_POKEMON * NUMBER_OF_MOVES_SLOTS + MAX_NUMBER_OF_POKEMON + 1

    def test_problem_variable_count(self, test_data: Dict[str, Any]) -> None:
        """Test that problem has correct variable count for different team sizes."""
        objectives = ObjectiveSelector(objective_names=["test_objective"])

        for team_size in [1, 3, 6]:
            problem = PokemonProblem(
                objectives=objectives,
                lm=test_data["lm"],
                n_pokemon=test_data["n_pokemon"],
                n_moves=test_data["n_moves"],
                pokemon_in_team=team_size,
            )
            expected_vars = team_size + team_size * NUMBER_OF_MOVES_SLOTS
            assert problem.n_var == expected_vars

    def test_problem_constraint_count(self, test_data: Dict[str, Any]) -> None:
        """Test that problem has correct constraint count."""
        objectives = ObjectiveSelector(objective_names=["test_objective"])
        problem = PokemonProblem(
            objectives=objectives,
            lm=test_data["lm"],
            n_pokemon=test_data["n_pokemon"],
            n_moves=test_data["n_moves"],
            pokemon_in_team=MAX_NUMBER_OF_POKEMON,
        )

        # Constraints: moves (learnable) + pokemon (unique moves) + 0 (no repeat pokemon)
        expected_constraints = MAX_NUMBER_OF_POKEMON * NUMBER_OF_MOVES_SLOTS + MAX_NUMBER_OF_POKEMON + 0
        assert problem.n_ieq_constr == expected_constraints

    def test_evaluate_valid_solution(self, problem: PokemonProblem, test_data: Dict[str, Any]) -> None:
        """Test evaluation of a valid solution."""
        pokemon_in_team = problem.pokemon_in_team

        # Create a valid solution
        x = np.zeros(pokemon_in_team + pokemon_in_team * NUMBER_OF_MOVES_SLOTS, dtype=np.int16)
        x[:pokemon_in_team] = np.arange(pokemon_in_team)

        # Assign learnable moves
        for i in range(pokemon_in_team):
            learnable = np.where(test_data["lm"][i])[0]
            if len(learnable) >= NUMBER_OF_MOVES_SLOTS:
                x[pokemon_in_team + i * NUMBER_OF_MOVES_SLOTS : pokemon_in_team + i * NUMBER_OF_MOVES_SLOTS + NUMBER_OF_MOVES_SLOTS] = learnable[
                    :NUMBER_OF_MOVES_SLOTS
                ]

        out = {}
        problem._evaluate(x, out)

        # Check that objectives were computed
        assert "F" in out
        assert out["F"].shape[0] == 1
        assert out["F"].shape[1] == problem.n_obj

        # Check that constraints were computed
        assert "G" in out
        assert out["G"].shape[0] == 1

    def test_evaluate_constraint_violations(self, problem: PokemonProblem, test_data: Dict[str, Any]) -> None:
        """Test that constraint violations are detected."""
        pokemon_in_team = problem.pokemon_in_team

        # Create a solution with unlearnable moves
        x = np.zeros(pokemon_in_team + pokemon_in_team * NUMBER_OF_MOVES_SLOTS, dtype=np.int16)
        x[:pokemon_in_team] = np.arange(pokemon_in_team)

        # Assign moves that may not be learnable
        for i in range(pokemon_in_team):
            # Find moves that this pokemon CANNOT learn
            unlearnable = np.where(~test_data["lm"][i])[0]
            if len(unlearnable) >= NUMBER_OF_MOVES_SLOTS:
                x[pokemon_in_team + i * NUMBER_OF_MOVES_SLOTS : pokemon_in_team + i * NUMBER_OF_MOVES_SLOTS + NUMBER_OF_MOVES_SLOTS] = unlearnable[
                    :NUMBER_OF_MOVES_SLOTS
                ]
                break

        out = {}
        problem._evaluate(x, out)

        # Check that we got constraints
        assert "G" in out
        # Some constraints should be violated (> 0)
        if len(np.where(~test_data["lm"][0])[0]) >= 4:
            # If we successfully assigned unlearnable moves
            assert np.any(out["G"][0] > 0), "Should have constraint violations"

    def test_evaluate_duplicate_moves(self, problem: PokemonProblem, test_data: Dict[str, Any]) -> None:
        """Test that duplicate moves are detected as constraint violations."""
        pokemon_in_team = problem.pokemon_in_team

        # Create a solution with duplicate moves
        x = np.zeros(pokemon_in_team + pokemon_in_team * NUMBER_OF_MOVES_SLOTS, dtype=np.int16)
        x[:pokemon_in_team] = np.arange(pokemon_in_team)

        # Assign same move multiple times to first pokemon
        learnable = np.where(test_data["lm"][0])[0]
        if len(learnable) > 0:
            x[pokemon_in_team : pokemon_in_team + NUMBER_OF_MOVES_SLOTS] = learnable[0]  # All same move

        out = {}
        problem._evaluate(x, out)

        # Should have constraint violations for duplicate moves
        assert "G" in out
        assert np.all(out["G"][0][24:30] == 3), "Should have constraint violations for duplicate moves"

    def test_evaluate_handles_negative_moves(self, problem: PokemonProblem, test_data: Dict[str, Any]) -> None:
        """Test that -1 moves (empty slots) are handled correctly."""
        pokemon_in_team = problem.pokemon_in_team

        # Create a solution with some -1 moves (mix of valid and -1)
        x = np.zeros(pokemon_in_team + pokemon_in_team * NUMBER_OF_MOVES_SLOTS, dtype=np.int16)
        x[:pokemon_in_team] = np.arange(pokemon_in_team)
        # Set first pokemon with one move, rest with -1
        learnable = np.where(test_data["lm"][0])[0]
        if len(learnable) > 0:
            x[pokemon_in_team] = learnable[0]
            x[pokemon_in_team + 1 : pokemon_in_team + NUMBER_OF_MOVES_SLOTS] = -1
        x[pokemon_in_team + NUMBER_OF_MOVES_SLOTS :] = -1  # Rest are -1

        out = {}
        problem._evaluate(x, out)

        # Should not crash and should have correct shape
        assert "F" in out
        assert "G" in out
        assert out["G"].shape == (1, problem.n_ieq_constr)

    def test_evaluate_objectives_shape(self, problem: PokemonProblem, test_data: Dict[str, Any]) -> None:
        """Test that objectives have correct shape."""
        pokemon_in_team = problem.pokemon_in_team

        x = np.zeros(pokemon_in_team + pokemon_in_team * NUMBER_OF_MOVES_SLOTS, dtype=np.int16)
        x[:pokemon_in_team] = np.arange(pokemon_in_team)
        x[pokemon_in_team:] = 0

        out = {}
        problem._evaluate(x, out)

        # F should have shape (1, n_obj)
        assert out["F"].shape == (1, problem.n_obj)

    def test_evaluate_constraints_shape(self, problem: PokemonProblem, test_data: Dict[str, Any]) -> None:
        """Test that constraints have correct shape."""
        pokemon_in_team = problem.pokemon_in_team

        x = np.zeros(pokemon_in_team + pokemon_in_team * NUMBER_OF_MOVES_SLOTS, dtype=np.int16)
        x[:pokemon_in_team] = np.arange(pokemon_in_team)
        x[pokemon_in_team:] = 0

        out = {}
        problem._evaluate(x, out)

        # G should have shape (1, n_constraints)
        assert out["G"].shape == (1, problem.n_ieq_constr)

    def test_evaluate_with_small_team(self, test_data: Dict[str, Any]) -> None:
        """Test evaluation with smaller team size."""
        objectives = ObjectiveSelector(objective_names=["test_objective"])
        problem = PokemonProblem(
            objectives=objectives,
            lm=test_data["lm"],
            n_pokemon=test_data["n_pokemon"],
            n_moves=test_data["n_moves"],
            pokemon_in_team=3,
        )

        x = np.zeros(3 + 3 * NUMBER_OF_MOVES_SLOTS, dtype=np.int16)
        x[:3] = [0, 1, 2]
        x[3:] = 0

        out = {}
        problem._evaluate(x, out)

        assert "F" in out
        assert "G" in out
        assert out["F"].shape == (1, 1)

    def test_evaluate_does_not_modify_input(self, problem: PokemonProblem, test_data: Dict[str, Any]) -> None:
        """Test that _evaluate does not modify the input solution."""
        pokemon_in_team = problem.pokemon_in_team

        x = np.zeros(pokemon_in_team + pokemon_in_team * NUMBER_OF_MOVES_SLOTS, dtype=np.int16)
        x[:pokemon_in_team] = np.arange(pokemon_in_team)
        x[pokemon_in_team:] = 0

        x_original = x.copy()
        out = {}
        problem._evaluate(x, out)

        # Input should not be modified
        assert np.array_equal(x, x_original)

    def test_lm_conversion_to_bool(self, test_data: Dict[str, Any]) -> None:
        """Test that learnable moves matrix is converted to bool."""
        objectives = ObjectiveSelector(objective_names=["test_objective"])

        # Pass LM as int array
        lm_int = test_data["lm"].astype(np.int16)

        problem = PokemonProblem(
            objectives=objectives,
            lm=lm_int,
            n_pokemon=test_data["n_pokemon"],
            n_moves=test_data["n_moves"],
            pokemon_in_team=MAX_NUMBER_OF_POKEMON,
        )

        # Should be converted to bool
        assert problem.LM.dtype == bool

    def test_evaluate_with_single_objective(self, test_data: Dict[str, Any]) -> None:
        """Test evaluation with single objective."""
        objectives = ObjectiveSelector(objective_names=["test_objective"])
        problem = PokemonProblem(
            objectives=objectives,
            lm=test_data["lm"],
            n_pokemon=test_data["n_pokemon"],
            n_moves=test_data["n_moves"],
            pokemon_in_team=MAX_NUMBER_OF_POKEMON,
        )

        x = np.zeros(MAX_NUMBER_OF_POKEMON + MAX_NUMBER_OF_POKEMON * NUMBER_OF_MOVES_SLOTS, dtype=np.int16)
        x[:MAX_NUMBER_OF_POKEMON] = np.arange(MAX_NUMBER_OF_POKEMON)
        x[MAX_NUMBER_OF_POKEMON:] = 0

        out = {}
        problem._evaluate(x, out)

        # Should have one objective
        assert out["F"].shape == (1, 1)

    def test_evaluate_multiple_times(self, problem: PokemonProblem, test_data: Dict[str, Any]) -> None:
        """Test that problem can be evaluated multiple times."""
        pokemon_in_team = problem.pokemon_in_team

        x = np.zeros(pokemon_in_team + pokemon_in_team * NUMBER_OF_MOVES_SLOTS, dtype=np.int16)
        x[:pokemon_in_team] = np.arange(pokemon_in_team)
        x[pokemon_in_team:] = 0

        # Evaluate multiple times
        for _ in range(5):
            out = {}
            problem._evaluate(x, out)
            assert "F" in out
            assert "G" in out

    def test_bounds(self, test_data: Dict[str, Any]) -> None:
        """Test that problem has correct variable bounds."""
        objectives = ObjectiveSelector(objective_names=["test_objective"])
        problem = PokemonProblem(
            objectives=objectives,
            lm=test_data["lm"],
            n_pokemon=test_data["n_pokemon"],
            n_moves=test_data["n_moves"],
            pokemon_in_team=MAX_NUMBER_OF_POKEMON,
        )

        # Bounds can be scalar or array depending on pymoo version
        if hasattr(problem.xl, "__iter__"):
            assert all(x == 0 for x in problem.xl)  # type: ignore
            assert all(x == test_data["n_pokemon"] for x in problem.xu)  # type: ignore
        else:
            assert problem.xl == 0
            assert problem.xu == test_data["n_pokemon"]

    def test_variable_type(self, test_data: Dict[str, Any]) -> None:
        """Test that problem initializes with correct parameters."""
        objectives = ObjectiveSelector(objective_names=["test_objective"])
        problem = PokemonProblem(
            objectives=objectives,
            lm=test_data["lm"],
            n_pokemon=test_data["n_pokemon"],
            n_moves=test_data["n_moves"],
            pokemon_in_team=MAX_NUMBER_OF_POKEMON,
        )

        # Check that problem was initialized correctly
        assert problem.n_pokemon == test_data["n_pokemon"]
        assert problem.n_var == MAX_NUMBER_OF_POKEMON + MAX_NUMBER_OF_POKEMON * NUMBER_OF_MOVES_SLOTS
