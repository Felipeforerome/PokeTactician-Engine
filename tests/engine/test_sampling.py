"""Tests for the PokemonTeamSampling class."""

from typing import Any, Dict

import numpy as np
import pytest

from poketactician.engine.problem import PokemonProblem
from poketactician.engine.sampling import PokemonTeamSampling
from poketactician.engine.selector import ObjectiveSelector


class TestPokemonTeamSampling:
    """Tests for the PokemonTeamSampling class."""

    @pytest.fixture
    def problem(self, test_data: Dict[str, Any]) -> PokemonProblem:
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
    def sampling(self, test_data: Dict[str, Any]) -> PokemonTeamSampling:
        """Create a PokemonTeamSampling instance for testing."""
        rng = np.random.default_rng(test_data["seed"])
        return PokemonTeamSampling(random_state=rng)

    def test_sampling_output_shape(self, sampling: PokemonTeamSampling, problem: PokemonProblem) -> None:
        """Test that sampling produces correct output shape."""
        n_samples = 10
        pokemon_in_team = problem.pokemon_in_team
        expected_var_size = pokemon_in_team + pokemon_in_team * 4

        samples = sampling._do(problem, n_samples)

        assert samples.shape == (n_samples, expected_var_size)
        # dtype can be int16 or int64 depending on numpy/pymoo version
        assert samples.dtype in [np.int16, np.int64, np.dtype("int16"), np.dtype("int64")]

    def test_sampling_unique_pokemon(self, sampling: PokemonTeamSampling, problem: PokemonProblem) -> None:
        """Test that each sample has unique pokemon."""
        n_samples = 20
        pokemon_in_team = problem.pokemon_in_team

        samples = sampling._do(problem, n_samples)

        for sample in samples:
            pokemon_ids = sample[:pokemon_in_team]
            # Check uniqueness
            assert len(set(pokemon_ids)) == len(pokemon_ids), "Each team should have unique pokemon"

    def test_sampling_valid_pokemon_ids(self, sampling: PokemonTeamSampling, problem: PokemonProblem) -> None:
        """Test that sampled pokemon IDs are valid."""
        n_samples = 15
        pokemon_in_team = problem.pokemon_in_team

        samples = sampling._do(problem, n_samples)

        for sample in samples:
            pokemon_ids = sample[:pokemon_in_team]
            # All IDs should be within valid range
            assert np.all(pokemon_ids >= 0)
            assert np.all(pokemon_ids < problem.n_pokemon)

    def test_sampling_learnable_moves(self, sampling: PokemonTeamSampling, problem: PokemonProblem, test_data: Dict[str, Any]) -> None:
        """Test that sampled moves are learnable by their pokemon."""
        n_samples = 10
        pokemon_in_team = problem.pokemon_in_team

        samples = sampling._do(problem, n_samples)

        for sample in samples:
            pokemon_ids = sample[:pokemon_in_team]
            moves = sample[pokemon_in_team:].reshape(pokemon_in_team, 4)

            for i, pokemon_id in enumerate(pokemon_ids):
                for move_id in moves[i]:
                    if move_id >= 0:  # -1 means no move
                        assert test_data["lm"][pokemon_id, move_id], f"Pokemon {pokemon_id} cannot learn move {move_id}"

    def test_sampling_with_preselected(self, problem: PokemonProblem, test_data: Dict[str, Any]) -> None:
        """Test that sampling respects pre-selected pokemon."""
        rng = np.random.default_rng(42)
        pre_selected = np.array([1, 2, 3], dtype=np.int16)

        sampling = PokemonTeamSampling(random_state=rng, pre_selected=pre_selected)

        n_samples = 10
        pokemon_in_team = problem.pokemon_in_team

        samples = sampling._do(problem, n_samples)

        for sample in samples:
            pokemon_ids = sample[:pokemon_in_team]
            # First three pokemon should be the pre-selected ones
            assert pokemon_ids[0] == 1
            assert pokemon_ids[1] == 2
            assert pokemon_ids[2] == 3

            # Rest should be different
            # All should still be unique
            assert len(set(pokemon_ids)) == len(pokemon_ids)

    def test_sampling_diversity(self, sampling: PokemonTeamSampling, problem: PokemonProblem) -> None:
        """Test that sampling produces diverse teams."""
        n_samples = 20
        pokemon_in_team = problem.pokemon_in_team

        samples = sampling._do(problem, n_samples)

        # Extract pokemon teams
        teams = [tuple(sample[:pokemon_in_team]) for sample in samples]

        # Most teams should be different (allowing for some duplicates due to randomness)
        unique_teams = len(set(teams))
        # With 13 pokemon and teams of 6, we can have many unique combinations
        # At least 50% should be unique
        assert unique_teams >= n_samples * 0.5, "Sampling should produce diverse teams"

    def test_sampling_reproducibility(self, problem: PokemonProblem, test_data: Dict[str, Any]) -> None:
        """Test that sampling with same seed produces same results."""
        seed = 42
        n_samples = 10

        sampling1 = PokemonTeamSampling(random_state=np.random.default_rng(seed))
        sampling2 = PokemonTeamSampling(random_state=np.random.default_rng(seed))

        samples1 = sampling1._do(problem, n_samples)
        samples2 = sampling2._do(problem, n_samples)

        assert np.array_equal(samples1, samples2)

    def test_sampling_different_seeds(self, problem: PokemonProblem, test_data: Dict[str, Any]) -> None:
        """Test that different seeds produce different samples."""
        n_samples = 10

        sampling1 = PokemonTeamSampling(random_state=np.random.default_rng(42))
        sampling2 = PokemonTeamSampling(random_state=np.random.default_rng(99))

        samples1 = sampling1._do(problem, n_samples)
        samples2 = sampling2._do(problem, n_samples)

        # Should be different (with very high probability)
        assert not np.array_equal(samples1, samples2)

    def test_sampling_single_sample(self, sampling: PokemonTeamSampling, problem: PokemonProblem, test_data: Dict[str, Any]) -> None:
        """Test that sampling works correctly for single sample."""
        n_samples = 1
        pokemon_in_team = problem.pokemon_in_team

        samples = sampling._do(problem, n_samples)

        assert samples.shape == (1, pokemon_in_team + pokemon_in_team * 4)

        # Verify validity
        pokemon_ids = samples[0, :pokemon_in_team]
        assert len(set(pokemon_ids)) == len(pokemon_ids)

    def test_sampling_large_population(self, sampling: PokemonTeamSampling, problem: PokemonProblem) -> None:
        """Test that sampling works for large populations."""
        n_samples = 100
        pokemon_in_team = problem.pokemon_in_team

        samples = sampling._do(problem, n_samples)

        assert samples.shape == (n_samples, pokemon_in_team + pokemon_in_team * 4)

        # All should have unique pokemon
        for sample in samples:
            pokemon_ids = sample[:pokemon_in_team]
            assert len(set(pokemon_ids)) == len(pokemon_ids)

    def test_sampling_move_count(self, sampling: PokemonTeamSampling, problem: PokemonProblem) -> None:
        """Test that each pokemon gets exactly 4 move slots."""
        n_samples = 10
        pokemon_in_team = problem.pokemon_in_team

        samples = sampling._do(problem, n_samples)

        for sample in samples:
            moves = sample[pokemon_in_team:].reshape(pokemon_in_team, 4)
            # Each pokemon should have 4 move slots (may include -1 for empty slots)
            assert moves.shape == (pokemon_in_team, 4)

    def test_sampling_handles_pokemon_with_few_moves(self, test_data: Dict[str, Any]) -> None:
        """Test sampling when some pokemon have fewer than 4 learnable moves."""
        # Create a modified LM where some pokemon have few moves
        modified_lm = test_data["lm"].copy()
        # Make sure at least one pokemon has fewer than 4 moves
        modified_lm[0, :] = False  # Pokemon 0 has no moves
        modified_lm[1, :3] = True  # Pokemon 1 has 3 moves
        modified_lm[1, 3:] = False

        objectives = ObjectiveSelector(objective_names=["test_objective", "test_objective2"])
        problem = PokemonProblem(
            objectives=objectives,
            lm=modified_lm,
            n_pokemon=test_data["n_pokemon"],
            n_moves=test_data["n_moves"],
            pokemon_in_team=6,
        )

        rng = np.random.default_rng(42)
        sampling = PokemonTeamSampling(random_state=rng)

        samples = sampling._do(problem, 5)

        # Should still work, with -1 for missing moves
        assert samples.shape == (5, 6 + 6 * 4)

    def test_sampling_with_small_team(self, test_data: Dict[str, Any]) -> None:
        """Test sampling with smaller team size."""
        objectives = ObjectiveSelector(objective_names=["test_objective", "test_objective2"])
        problem = PokemonProblem(
            objectives=objectives,
            lm=test_data["lm"],
            n_pokemon=test_data["n_pokemon"],
            n_moves=test_data["n_moves"],
            pokemon_in_team=3,  # Smaller team
        )

        rng = np.random.default_rng(42)
        sampling = PokemonTeamSampling(random_state=rng)

        n_samples = 10
        samples = sampling._do(problem, n_samples)

        assert samples.shape == (n_samples, 3 + 3 * 4)

        # Verify uniqueness
        for sample in samples:
            pokemon_ids = sample[:3]
            assert len(set(pokemon_ids)) == 3
