"""Tests for the utility functions in the poketactician package."""

import numpy as np

from poketactician.config import NUMBER_OF_MOVES_SLOTS
from poketactician.utils import get_random_moves


class TestGetRandomMoves:
    N_POKEMON = 10
    N_MOVES = 20

    def make_lm(self) -> np.ndarray:
        return np.zeros((self.N_POKEMON, self.N_MOVES), dtype=bool)

    def rng(self, seed: int) -> np.random.Generator:
        return np.random.default_rng(seed)

    def test_get_random_moves_more_than_four(self) -> None:
        """Pokemon with more than 4 learnable moves should return 4 unique valid moves."""
        lm = self.make_lm()
        lm[0, 0:6] = True  # Pokemon 0 can learn moves 0-5 (6 moves)

        moves = get_random_moves(lm, 0, self.rng(42))

        valid_moves = moves[moves >= 0]
        assert len(valid_moves) == NUMBER_OF_MOVES_SLOTS
        assert all(lm[0, move] for move in valid_moves)
        assert len(set(valid_moves)) == len(valid_moves)

    def test_get_random_moves_exactly_four(self) -> None:
        """Pokemon with exactly 4 learnable moves should return those 4 unique moves."""
        lm = self.make_lm()
        lm[1, 1:5] = True  # Pokemon 1 can learn moves 1-4

        moves = get_random_moves(lm, 1, self.rng(123))

        valid_moves = moves[moves >= 0]
        assert len(valid_moves) == NUMBER_OF_MOVES_SLOTS
        assert all(lm[1, move] for move in valid_moves)
        assert len(set(valid_moves)) == len(valid_moves)

    def test_get_random_moves_fewer_than_four(self) -> None:
        """Pokemon with fewer than 4 learnable moves should return only those moves."""
        lm = self.make_lm()
        lm[2, 2:4] = True  # Pokemon 2 can learn moves 2-3 (2 moves)

        moves = get_random_moves(lm, 2, self.rng(7))

        valid_moves = moves[moves >= 0]
        assert len(valid_moves) == 2
        assert all(lm[2, move] for move in valid_moves)
        assert len(set(valid_moves)) == len(valid_moves)

    def test_get_random_moves_no_learnable_moves(self) -> None:
        """Pokemon with no learnable moves should return no valid moves and all -1s."""
        lm = self.make_lm()
        lm[3, :] = False  # Pokemon 3 can't learn any moves

        moves = get_random_moves(lm, 3, self.rng(999))

        valid_moves = moves[moves >= 0]
        assert len(valid_moves) == 0
        assert np.all(moves == -1)

    def test_get_random_moves_noncontiguous_learnable(self) -> None:
        """Selection should work with noncontiguous learnable move indices."""
        lm = self.make_lm()
        learnable = [0, 3, 7, 10, 13, 17]  # 6 noncontiguous moves
        lm[4, learnable] = True

        moves = get_random_moves(lm, 4, self.rng(2024))

        valid_moves = moves[moves >= 0]
        assert len(valid_moves) == NUMBER_OF_MOVES_SLOTS
        assert all(move in learnable for move in valid_moves)
        assert len(set(valid_moves)) == len(valid_moves)

    def test_get_random_moves_does_not_mutate_input(self) -> None:
        """get_random_moves should not modify the learnable moves matrix."""
        lm = self.make_lm()
        lm[0, :8] = True
        lm_before = lm.copy()

        _ = get_random_moves(lm, 0, self.rng(55))

        assert np.array_equal(lm, lm_before)

    def test_get_random_moves_reproducibility(self) -> None:
        """Test that get_random_moves with the same seed produces the same results."""
        lm = self.make_lm()
        seed = 42
        lm[0, 0:10] = True  # Pokemon 0 can learn moves 0-9

        # Create two random states with the same seed
        random_state1 = self.rng(seed)
        random_state2 = self.rng(seed)

        # Get random moves for Pokemon 0 with both random states
        moves1 = get_random_moves(lm, 0, random_state1)
        moves2 = get_random_moves(lm, 0, random_state2)

        # Check that the moves are the same
        assert np.array_equal(moves1, moves2)

        # Create a random state with a different seed
        random_state3 = self.rng(seed + 1)

        # Get random moves for Pokemon 0 with the different random state
        moves3 = get_random_moves(lm, 0, random_state3)

        # Check that the moves are different
        assert not np.array_equal(moves1, moves3)
