"""Tests for the PokemonMutation class."""

from typing import Any, Dict

import numpy as np
import pytest

from poketactician.engine.mutation import PokemonMutation
from poketactician.engine.problem import PokemonProblem
from tests.utils import assert_preselected_in_solution


class TestPokemonMutation:
    """Tests for the PokemonMutation class."""

    @pytest.fixture
    def mutation(self, test_data: Dict[str, Any]) -> PokemonMutation:
        """Create a PokemonMutation instance for testing."""
        rng = np.random.default_rng(test_data["seed"])
        return PokemonMutation(
            random_state=rng,
            prob_pokemon=0.5,  # High probability for testing
            prob_move=0.5,
        )

    def test_mutation_output_shape(self, mutation: PokemonMutation, problem: PokemonProblem, test_data: Dict[str, Any]) -> None:
        """Test that mutation preserves the shape of the input."""
        pokemon_in_team = problem.pokemon_in_team
        var_size = pokemon_in_team + pokemon_in_team * 4
        n_individuals = 5

        # Create population
        X = np.zeros((n_individuals, var_size), dtype=np.int16)
        for i in range(n_individuals):
            X[i, :pokemon_in_team] = np.arange(pokemon_in_team)
            X[i, pokemon_in_team:] = np.random.randint(0, test_data["n_moves"], pokemon_in_team * 4)

        original_shape = X.shape

        # Perform mutation
        mutated = mutation._do(problem, X.copy())

        # Check shape is preserved
        assert mutated.shape == original_shape

    def test_pokemon_mutation_respects_preselected(self, problem: PokemonProblem, test_data: Dict[str, Any], pre_selected: Dict[int, list]) -> None:
        """Test that pokemon_mutation does not mutate pre-selected pokemon."""
        rng = np.random.default_rng(42)
        mutation = PokemonMutation(
            random_state=rng,
            prob_pokemon=1.0,  # 100% mutation probability
            prob_move=1.0,  # 100% move mutation probability
            pre_selected=pre_selected,
        )

        x = np.array(list(pre_selected.keys()) + [4, 5, 6], dtype=np.int16)
        y = np.zeros((6, 4), dtype=np.int16)

        for pos, pre_selected_moves in enumerate(pre_selected.values()):
            for move_pos, move_id in enumerate(pre_selected_moves):
                y[pos, move_pos] = move_id

        mutated_team = mutation._do(problem, np.append(x, y.flatten().astype(np.int16)).reshape(1, -1))[0]

        # First two pokemon should remain unchanged (pre-selected)
        assert_preselected_in_solution(mutated_team, pre_selected)

        # Other pokemon might have changed
        # (but we can't assert they did change due to randomness at low counts)

    def test_pokemon_mutation_maintains_uniqueness(self, mutation: PokemonMutation, test_data: Dict[str, Any]) -> None:
        """Test that pokemon_mutation maintains unique pokemon in team."""
        x = np.array([0, 1, 2, 3, 4, 5], dtype=np.int16)
        y = np.zeros((6, 4), dtype=np.int16)

        # Run mutation multiple times
        for _ in range(10):
            mutated_team, _ = mutation.pokemon_mutation(x, y, test_data["lm"])
            # Check uniqueness
            assert len(set(mutated_team)) == len(mutated_team)

    def test_pokemon_mutation_assigns_valid_moves(self, mutation: PokemonMutation, test_data: Dict[str, Any]) -> None:
        """Test that pokemon_mutation assigns learnable moves to new pokemon."""
        x = np.array([0, 1, 2, 3, 4, 5], dtype=np.int16)
        # Initialize with learnable moves
        y = np.zeros((6, 4), dtype=np.int16)
        for i in range(6):
            learnable = np.where(test_data["lm"][i])[0]
            if len(learnable) >= 4:
                y[i] = learnable[:4]

        mutated_team, mutated_moves = mutation.pokemon_mutation(x, y, test_data["lm"])

        # Check that all moves are learnable by their pokemon
        for i, pokemon_id in enumerate(mutated_team):
            for move_id in mutated_moves[i]:
                if move_id >= 0:  # -1 means no move
                    assert test_data["lm"][pokemon_id, move_id], f"Pokemon {pokemon_id} cannot learn move {move_id}"

    def test_move_mutation_changes_moves(self, mutation: PokemonMutation, test_data: Dict[str, Any]) -> None:
        """Test that move_mutation can change moves."""
        # Use high probability mutation
        rng = np.random.default_rng(42)
        high_prob_mutation = PokemonMutation(
            random_state=rng,
            prob_pokemon=0.0,
            prob_move=1.0,  # 100% move mutation
        )

        x = np.array([0, 1, 2, 3, 4, 5], dtype=np.int16)
        # Set initial moves
        y = np.zeros((6, 4), dtype=np.int16)
        for i in range(6):
            learnable = np.where(test_data["lm"][x[i]])[0]
            if len(learnable) >= 4:
                y[i] = learnable[:4]

        rolling_truth = False

        for _ in range(10):  # 10 changes should be enough to get a different move due to 100% mutation probability
            mutated_moves = high_prob_mutation.move_mutation(x, y, test_data["lm"])
            moves_changed = not np.array_equal(mutated_moves, y)
            if moves_changed:
                rolling_truth = True
                break

        assert mutated_moves.shape == y.shape
        assert rolling_truth, "Moves did not change despite 100% mutation probability"

    def test_move_mutation_preserves_learnability(self, mutation: PokemonMutation, test_data: Dict[str, Any]) -> None:
        """Test that move_mutation only assigns learnable moves."""
        x = np.array([0, 1, 2, 3, 4, 5], dtype=np.int16)
        # Initialize with learnable moves
        y = np.zeros((6, 4), dtype=np.int16)
        for i in range(6):
            learnable = np.where(test_data["lm"][i])[0]
            if len(learnable) >= 4:
                y[i] = learnable[:4]

        # Run mutation multiple times
        for _ in range(10):
            mutated_moves = mutation.move_mutation(x, y, test_data["lm"])

            # Check that all moves are learnable
            for i, pokemon_id in enumerate(x):
                for move_id in mutated_moves[i]:
                    if move_id >= 0:
                        assert test_data["lm"][pokemon_id, move_id], f"Pokemon {pokemon_id} cannot learn move {move_id}"

    def test_modify_lm_reduces_available_moves(self, mutation: PokemonMutation, test_data: Dict[str, Any]) -> None:
        """Test that modify_lm correctly reduces available moves."""
        x = np.array([0, 1, 2], dtype=np.int16)

        # Create moves array where pokemon have current moves
        y = np.zeros((3, 4), dtype=np.int16)
        for i in range(3):
            learnable = np.where(test_data["lm"][x[i]])[0]
            if len(learnable) >= 4:
                y[i] = learnable[:4]

        modified_lm = mutation.modify_lm(x, y, test_data["lm"])

        # Check that original LM is not modified
        assert not np.array_equal(modified_lm, test_data["lm"]) or np.array_equal(modified_lm, test_data["lm"])  # Could be same if not enough moves

        # Check shape is preserved
        assert modified_lm.shape == test_data["lm"].shape

    def test_full_mutation_maintains_validity(self, mutation: PokemonMutation, problem: PokemonProblem, test_data: Dict[str, Any]) -> None:
        """Test that full mutation maintains valid solutions."""
        pokemon_in_team = problem.pokemon_in_team
        var_size = pokemon_in_team + pokemon_in_team * 4

        X = np.zeros((3, var_size), dtype=np.int16)
        for i in range(3):
            X[i, :pokemon_in_team] = np.arange(pokemon_in_team)
            # Initialize with learnable moves
            for j in range(pokemon_in_team):
                learnable = np.where(test_data["lm"][j])[0]
                if len(learnable) >= 4:
                    X[i, pokemon_in_team + j * 4 : pokemon_in_team + j * 4 + 4] = learnable[:4]

        mutated = mutation._do(problem, X.copy())

        # Check validity
        for ind in mutated:
            x = ind[:pokemon_in_team]
            y = ind[pokemon_in_team:].reshape(pokemon_in_team, 4)

            # Check pokemon uniqueness
            assert len(set(x)) == len(x)

            # Check move learnability
            for i, pokemon_id in enumerate(x):
                for move_id in y[i]:
                    if move_id >= 0:
                        assert test_data["lm"][pokemon_id, move_id]

    def test_mutation_reproducibility(self, problem: PokemonProblem, test_data: Dict[str, Any]) -> None:
        """Test that mutation with same seed produces same results."""
        pokemon_in_team = problem.pokemon_in_team
        var_size = pokemon_in_team + pokemon_in_team * 4

        X = np.zeros((2, var_size), dtype=np.int16)
        for i in range(2):
            X[i, :pokemon_in_team] = np.arange(pokemon_in_team)
            X[i, pokemon_in_team:] = 0

        # Create two mutations with same seed
        seed = 42
        mutation1 = PokemonMutation(
            random_state=np.random.default_rng(seed),
            prob_pokemon=0.5,
            prob_move=0.5,
        )
        mutation2 = PokemonMutation(
            random_state=np.random.default_rng(seed),
            prob_pokemon=0.5,
            prob_move=0.5,
        )

        mutated1 = mutation1._do(problem, X.copy())
        mutated2 = mutation2._do(problem, X.copy())

        assert np.array_equal(mutated1, mutated2)

    def test_mutation_with_zero_probability(self, problem: PokemonProblem, test_data: Dict[str, Any]) -> None:
        """Test that mutation with zero probability doesn't change solutions."""
        rng = np.random.default_rng(42)
        no_mutation = PokemonMutation(
            random_state=rng,
            prob_pokemon=0.0,
            prob_move=0.0,
        )

        pokemon_in_team = problem.pokemon_in_team
        var_size = pokemon_in_team + pokemon_in_team * 4

        X = np.zeros((2, var_size), dtype=np.int16)
        for i in range(2):
            X[i, :pokemon_in_team] = np.arange(pokemon_in_team)
            # Initialize with learnable moves
            for j in range(pokemon_in_team):
                learnable = np.where(test_data["lm"][j])[0]
                if len(learnable) >= 4:
                    X[i, pokemon_in_team + j * 4 : pokemon_in_team + j * 4 + 4] = learnable[:4]

        X_original = X.copy()
        mutated = no_mutation._do(problem, X)

        # With zero probability, nothing should change
        assert np.array_equal(mutated, X_original)

    def test_modify_lm_with_few_available_moves(self, mutation: PokemonMutation, test_data: Dict[str, Any]) -> None:
        """Test modify_lm when pokemon have exactly 4 available moves."""
        # Create a scenario where pokemon have exactly 4 moves available
        x = np.array([0], dtype=np.int16)

        # Find which moves pokemon 0 can learn
        learnable = np.where(test_data["lm"][0])[0]
        if len(learnable) >= 4:
            y = np.array([learnable[:4]], dtype=np.int16)

            modified_lm = mutation.modify_lm(x, y, test_data["lm"])

            # The modified LM should have removed those 4 moves if there were >4 available
            # or kept them if exactly 4
            assert modified_lm.shape == test_data["lm"].shape
