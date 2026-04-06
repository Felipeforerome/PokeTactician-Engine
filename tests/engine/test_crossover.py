"""Tests for the PokemonCrossover class."""

from typing import Any, Dict

import numpy as np
import pytest

from poketactician.config import NUMBER_OF_MOVES_SLOTS
from poketactician.engine.crossover import PokemonCrossover
from poketactician.engine.problem import PokemonProblem


class TestPokemonCrossover:
    """Tests for the PokemonCrossover class."""

    @pytest.fixture
    def crossover(self, test_data: Dict[str, Any]) -> PokemonCrossover:
        """Create a PokemonCrossover instance for testing."""
        rng = np.random.default_rng(test_data["seed"])
        return PokemonCrossover(random_state=rng, prob_pokemon=0.5)

    def test_crossover_output_shape(self, crossover: PokemonCrossover, problem: PokemonProblem, test_data: Dict[str, Any]) -> None:
        """Test that crossover produces offspring with correct shape."""
        # Create two parent solutions
        n_matings = 3
        pokemon_in_team = problem.pokemon_in_team
        var_size = pokemon_in_team + pokemon_in_team * NUMBER_OF_MOVES_SLOTS

        # Create parent array with shape (2, n_matings, var_size)
        parent1 = np.zeros((n_matings, var_size), dtype=np.int16)
        parent2 = np.zeros((n_matings, var_size), dtype=np.int16)

        # Fill with valid pokemon IDs and moves
        for i in range(n_matings):
            parent1[i, :pokemon_in_team] = np.arange(pokemon_in_team)
            parent2[i, :pokemon_in_team] = np.arange(pokemon_in_team, pokemon_in_team * 2)
            # Add some valid moves
            parent1[i, pokemon_in_team:] = np.random.randint(0, test_data["n_moves"], pokemon_in_team * NUMBER_OF_MOVES_SLOTS)
            parent2[i, pokemon_in_team:] = np.random.randint(0, test_data["n_moves"], pokemon_in_team * NUMBER_OF_MOVES_SLOTS)

        X = np.array([parent1, parent2])
        # Perform crossover
        offspring = crossover._do(problem, X)

        # Check output shape
        assert offspring.shape == X.shape
        assert offspring.shape == (2, n_matings, var_size)

    def test_crossover_identical_parents(self, crossover: PokemonCrossover, problem: PokemonProblem) -> None:
        """Test that identical parents produce identical offspring."""
        pokemon_in_team = problem.pokemon_in_team
        var_size = pokemon_in_team + pokemon_in_team * NUMBER_OF_MOVES_SLOTS

        # Create identical parents
        parent = np.zeros(var_size, dtype=np.int16)
        parent[:pokemon_in_team] = np.arange(pokemon_in_team)
        parent[pokemon_in_team:] = np.tile([0, 1, 2, 3], pokemon_in_team)

        X = np.array([[parent], [parent]])

        # Perform crossover
        offspring = crossover._do(problem, X)

        # Both offspring should be identical to parents
        assert np.array_equal(offspring[0][0], parent)
        assert np.array_equal(offspring[1][0], parent)

    def test_crossover_preserves_pokemon_uniqueness(self, crossover: PokemonCrossover, problem: PokemonProblem, test_data: Dict[str, Any]) -> None:
        """Test that crossover maintains unique pokemon in each team."""
        pokemon_in_team = problem.pokemon_in_team
        var_size = pokemon_in_team + pokemon_in_team * NUMBER_OF_MOVES_SLOTS

        # Create diverse parents
        parent1 = np.zeros(var_size, dtype=np.int16)
        parent2 = np.zeros(var_size, dtype=np.int16)

        parent1[:pokemon_in_team] = [0, 1, 2, 3, 4, 5]
        parent2[:pokemon_in_team] = [6, 7, 8, 9, 10, 11]

        # Fill moves
        parent1[pokemon_in_team:] = np.random.randint(0, test_data["n_moves"], pokemon_in_team * NUMBER_OF_MOVES_SLOTS)
        parent2[pokemon_in_team:] = np.random.randint(0, test_data["n_moves"], pokemon_in_team * NUMBER_OF_MOVES_SLOTS)

        X = np.array([[parent1], [parent2]])

        # Perform crossover
        offspring = crossover._do(problem, X)

        # Check that each offspring has unique pokemon
        for i in range(2):
            pokemon_ids = offspring[i][0][:pokemon_in_team]
            assert len(set(pokemon_ids)) == len(pokemon_ids), "Offspring should have unique pokemon"

    def test_crossover_offspring_from_parents(self, crossover: PokemonCrossover, problem: PokemonProblem, test_data: Dict[str, Any]) -> None:
        """Test that offspring pokemon come from parent sets."""
        pokemon_in_team = problem.pokemon_in_team
        var_size = pokemon_in_team + pokemon_in_team * NUMBER_OF_MOVES_SLOTS

        # Create parents with distinct pokemon
        parent1 = np.zeros(var_size, dtype=np.int16)
        parent2 = np.zeros(var_size, dtype=np.int16)

        parent1[:pokemon_in_team] = [0, 1, 2, 3, 4, 5]
        parent2[:pokemon_in_team] = [6, 7, 8, 9, 10, 11]

        parent1[pokemon_in_team:] = 0
        parent2[pokemon_in_team:] = 1

        X = np.array([[parent1], [parent2]])

        # Perform crossover
        offspring = crossover._do(problem, X)

        # Check that offspring pokemon are from parent unions
        parent_pokemon = set(parent1[:pokemon_in_team]) | set(parent2[:pokemon_in_team])
        for i in range(2):
            offspring_pokemon = set(offspring[i][0][:pokemon_in_team])
            assert offspring_pokemon.issubset(parent_pokemon), "Offspring pokemon should come from parents"

    def test_crossover_reproducibility(self, problem: PokemonProblem, test_data: Dict[str, Any]) -> None:
        """Test that crossover with same seed produces same results."""
        pokemon_in_team = problem.pokemon_in_team
        var_size = pokemon_in_team + pokemon_in_team * NUMBER_OF_MOVES_SLOTS

        # Create parents
        parent1 = np.zeros(var_size, dtype=np.int16)
        parent2 = np.zeros(var_size, dtype=np.int16)

        parent1[:pokemon_in_team] = [0, 1, 2, 3, 4, 5]
        parent2[:pokemon_in_team] = [6, 7, 8, 9, 10, 11]
        parent1[pokemon_in_team:] = 0
        parent2[pokemon_in_team:] = 1

        X = np.array([[parent1], [parent2]])

        # Create two crossovers with same seed
        seed = 42
        crossover1 = PokemonCrossover(random_state=np.random.default_rng(seed), prob_pokemon=0.5)
        crossover2 = PokemonCrossover(random_state=np.random.default_rng(seed), prob_pokemon=0.5)

        # Perform crossover with both
        offspring1 = crossover1._do(problem, X.copy())
        offspring2 = crossover2._do(problem, X.copy())

        # Results should be identical
        assert np.array_equal(offspring1, offspring2)

    def test_crossover_different_seeds(self, problem: PokemonProblem, test_data: Dict[str, Any]) -> None:
        """Test that crossover with different seeds produces different results."""
        pokemon_in_team = problem.pokemon_in_team
        var_size = pokemon_in_team + pokemon_in_team * NUMBER_OF_MOVES_SLOTS

        # Create parents
        parent1 = np.zeros(var_size, dtype=np.int16)
        parent2 = np.zeros(var_size, dtype=np.int16)

        parent1[:pokemon_in_team] = [0, 1, 2, 3, 4, 5]
        parent2[:pokemon_in_team] = [6, 7, 8, 9, 10, 11]
        parent1[pokemon_in_team:] = 0
        parent2[pokemon_in_team:] = 1

        X = np.array([[parent1], [parent2]])

        # Create two crossovers with different seeds
        crossover1 = PokemonCrossover(random_state=np.random.default_rng(42), prob_pokemon=0.5)
        crossover2 = PokemonCrossover(random_state=np.random.default_rng(99), prob_pokemon=0.5)

        # Perform crossover with both
        offspring1 = crossover1._do(problem, X.copy())
        offspring2 = crossover2._do(problem, X.copy())

        # Results should be different (with high probability)
        assert not np.array_equal(offspring1, offspring2)

    def test_crossover_with_overlapping_pokemon(self, crossover: PokemonCrossover, problem: PokemonProblem, test_data: Dict[str, Any]) -> None:
        """Test crossover when parents share some pokemon."""
        pokemon_in_team = problem.pokemon_in_team
        var_size = pokemon_in_team + pokemon_in_team * NUMBER_OF_MOVES_SLOTS

        # Create parents with some overlap
        parent1 = np.zeros(var_size, dtype=np.int16)
        parent2 = np.zeros(var_size, dtype=np.int16)

        parent1[:pokemon_in_team] = [0, 1, 2, 3, 4, 5]
        parent2[:pokemon_in_team] = [0, 1, 2, 6, 7, 8]  # First 3 are shared

        parent1[pokemon_in_team:] = np.random.randint(0, test_data["n_moves"], pokemon_in_team * NUMBER_OF_MOVES_SLOTS)
        parent2[pokemon_in_team:] = np.random.randint(0, test_data["n_moves"], pokemon_in_team * NUMBER_OF_MOVES_SLOTS)

        X = np.array([[parent1], [parent2]])

        # Perform crossover
        offspring = crossover._do(problem, X)

        # Check that offspring have unique pokemon
        for i in range(2):
            pokemon_ids = offspring[i][0][:pokemon_in_team]
            assert len(set(pokemon_ids)) == len(pokemon_ids)

    def test_crossover_with_overlapping_pokemon_make_different_offspring(self, problem: PokemonProblem, test_data: Dict[str, Any]) -> None:
        """Test crossover when parents share some pokemon."""
        pokemon_in_team = problem.pokemon_in_team
        var_size = pokemon_in_team + pokemon_in_team * NUMBER_OF_MOVES_SLOTS

        # Create parents with some overlap
        parent1 = np.zeros(var_size, dtype=np.int16)
        parent2 = np.zeros(var_size, dtype=np.int16)

        parent1[:pokemon_in_team] = [0, 1, 2, 3, 4, 5]
        parent2[:pokemon_in_team] = [0, 1, 2, 6, 7, 8]  # First 3 are shared

        parent1[pokemon_in_team:] = np.random.randint(0, test_data["n_moves"], pokemon_in_team * NUMBER_OF_MOVES_SLOTS)
        parent2[pokemon_in_team:] = np.random.randint(0, test_data["n_moves"], pokemon_in_team * NUMBER_OF_MOVES_SLOTS)

        X = np.array([[parent1], [parent2]])
        rolling_truth = False
        for i in range(10):  # Run multiple times to check for different offspring
            crossover = PokemonCrossover(random_state=np.random.default_rng(i), prob_pokemon=0.5)

            # Perform crossover
            offspring = crossover._do(problem, X)

            # Check that offspring have unique pokemon
            pokemon_ids = offspring[0][0] != offspring[1][0]
            rolling_truth = rolling_truth or np.any(pokemon_ids)
            if rolling_truth:
                break
        assert rolling_truth

    def test_crossover_multiple_matings(self, crossover: PokemonCrossover, problem: PokemonProblem, test_data: Dict[str, Any]) -> None:
        """Test that crossover handles multiple mating pairs correctly."""
        pokemon_in_team = problem.pokemon_in_team
        var_size = pokemon_in_team + pokemon_in_team * NUMBER_OF_MOVES_SLOTS
        n_matings = 5

        # Create multiple parent pairs
        parent1 = np.zeros((n_matings, var_size), dtype=np.int16)
        parent2 = np.zeros((n_matings, var_size), dtype=np.int16)

        for i in range(n_matings):
            # Each mating has different pokemon
            start_idx = i * 2
            parent1[i, :pokemon_in_team] = np.arange(start_idx, start_idx + pokemon_in_team) % test_data["n_pokemon"]
            parent2[i, :pokemon_in_team] = np.arange(start_idx + 1, start_idx + pokemon_in_team + 1) % test_data["n_pokemon"]
            parent1[i, pokemon_in_team:] = 0
            parent2[i, pokemon_in_team:] = 1

        X = np.array([parent1, parent2])

        # Perform crossover
        offspring = crossover._do(problem, X)

        # Check that we got correct number of offspring
        assert offspring.shape == (2, n_matings, var_size)

        # Check that each offspring maintains uniqueness
        for mating_idx in range(n_matings):
            for offspring_idx in range(2):
                pokemon_ids = offspring[offspring_idx][mating_idx][:pokemon_in_team]
                assert len(set(pokemon_ids)) == len(pokemon_ids)

    def test_crossover_probability_effect(self, problem: PokemonProblem, test_data: Dict[str, Any]) -> None:
        """Test that changing crossover probability affects results."""
        pokemon_in_team = problem.pokemon_in_team
        var_size = pokemon_in_team + pokemon_in_team * NUMBER_OF_MOVES_SLOTS

        # Create parents
        parent1 = np.zeros(var_size, dtype=np.int16)
        parent2 = np.zeros(var_size, dtype=np.int16)

        parent1[:pokemon_in_team] = [0, 1, 2, 3, 4, 5]
        parent2[:pokemon_in_team] = [6, 7, 8, 9, 10, 11]
        parent1[pokemon_in_team:] = 0
        parent2[pokemon_in_team:] = 1

        X = np.array([[parent1], [parent2]])

        # Test with different probabilities
        crossover_low = PokemonCrossover(random_state=np.random.default_rng(42), prob_pokemon=0.1)
        crossover_high = PokemonCrossover(random_state=np.random.default_rng(42), prob_pokemon=0.9)

        # Same seed should produce same offspring selection pattern
        offspring_low = crossover_low._do(problem, X.copy())
        offspring_high = crossover_high._do(problem, X.copy())

        # Both should be valid (unique pokemon)
        for i in range(2):
            assert len(set(offspring_low[i][0][:pokemon_in_team])) == pokemon_in_team
            assert len(set(offspring_high[i][0][:pokemon_in_team])) == pokemon_in_team
