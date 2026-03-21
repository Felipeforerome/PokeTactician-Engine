"""Tests for test utility functions."""

from typing import Any, Dict

import numpy as np
import pytest

from tests.utils import assert_preselected_in_solution


class TestAssertPreselectedInSolution:
    """Tests for the assert_preselected_in_solution utility function."""

    def test_valid_solution_with_preselected(self) -> None:
        """Test that valid solution with preselected pokemon passes."""
        # Create a valid solution: pokemon IDs [1, 2, 3, 4, 5, 6] + moves
        solution = np.array(
            [
                1,
                2,
                3,
                4,
                5,
                6,  # Pokemon IDs
                10,
                11,
                12,
                13,  # Moves for pokemon 1
                20,
                21,
                22,
                23,  # Moves for pokemon 2
                30,
                31,
                32,
                33,  # Moves for pokemon 3
                40,
                41,
                42,
                43,  # Moves for pokemon 4
                50,
                51,
                52,
                53,  # Moves for pokemon 5
                60,
                61,
                62,
                63,  # Moves for pokemon 6
            ],
            dtype=np.int16,
        )

        pre_selected = {
            1: [10, 11],
            2: [20, 21],
        }

        # Should not raise any assertion error
        assert_preselected_in_solution(solution, pre_selected)

    def test_valid_solution_with_three_preselected(self) -> None:
        """Test that solution with three preselected pokemon passes."""
        solution = np.array(
            [
                1,
                2,
                3,
                4,
                5,
                6,  # Pokemon IDs
                10,
                11,
                12,
                13,  # Moves for pokemon 1
                20,
                21,
                22,
                23,  # Moves for pokemon 2
                30,
                31,
                32,
                33,  # Moves for pokemon 3
                40,
                41,
                42,
                43,  # Moves for pokemon 4
                50,
                51,
                52,
                53,  # Moves for pokemon 5
                60,
                61,
                62,
                63,  # Moves for pokemon 6
            ],
            dtype=np.int16,
        )

        pre_selected = {
            1: [10, 11],
            2: [20, 21],
            3: [30, 31],
        }

        assert_preselected_in_solution(solution, pre_selected)

    def test_preselected_moves_not_all_first(self) -> None:
        """Test that preselected moves can be anywhere in pokemon's moveset."""
        solution = np.array(
            [
                1,
                2,
                3,
                4,
                5,
                6,  # Pokemon IDs
                12,
                13,
                10,
                11,  # Moves for pokemon 1 (preselected at pos 2,3)
                22,
                20,
                21,
                23,  # Moves for pokemon 2 (preselected at pos 1,2)
                30,
                31,
                32,
                33,  # Moves for pokemon 3
                40,
                41,
                42,
                43,  # Moves for pokemon 4
                50,
                51,
                52,
                53,  # Moves for pokemon 5
                60,
                61,
                62,
                63,  # Moves for pokemon 6
            ],
            dtype=np.int16,
        )

        pre_selected = {
            1: [10, 11],
            2: [20, 21],
        }

        # Should pass - preselected moves are present, just not at start
        assert_preselected_in_solution(solution, pre_selected)

    def test_wrong_pokemon_at_position(self) -> None:
        """Test that assertion fails when wrong pokemon at preselected position."""
        solution = np.array(
            [
                2,
                1,
                3,
                4,
                5,
                6,  # Pokemon IDs (2 and 1 are swapped!)
                10,
                11,
                12,
                13,  # Moves for pokemon 2
                20,
                21,
                22,
                23,  # Moves for pokemon 1
                30,
                31,
                32,
                33,  # Moves for pokemon 3
                40,
                41,
                42,
                43,  # Moves for pokemon 4
                50,
                51,
                52,
                53,  # Moves for pokemon 5
                60,
                61,
                62,
                63,  # Moves for pokemon 6
            ],
            dtype=np.int16,
        )

        pre_selected = {
            1: [10, 11],
            2: [20, 21],
        }

        with pytest.raises(AssertionError, match="should be at position 0"):
            assert_preselected_in_solution(solution, pre_selected)

    def test_missing_preselected_move(self) -> None:
        """Test that assertion fails when preselected move is missing."""
        solution = np.array(
            [
                1,
                2,
                3,
                4,
                5,
                6,  # Pokemon IDs
                10,
                99,
                12,
                13,  # Moves for pokemon 1 (11 replaced with 99!)
                20,
                21,
                22,
                23,  # Moves for pokemon 2
                30,
                31,
                32,
                33,  # Moves for pokemon 3
                40,
                41,
                42,
                43,  # Moves for pokemon 4
                50,
                51,
                52,
                53,  # Moves for pokemon 5
                60,
                61,
                62,
                63,  # Moves for pokemon 6
            ],
            dtype=np.int16,
        )

        pre_selected = {
            1: [10, 11],
            2: [20, 21],
        }

        with pytest.raises(AssertionError, match="should have move 11"):
            assert_preselected_in_solution(solution, pre_selected)

    def test_empty_preselected(self) -> None:
        """Test that function works with empty preselected dictionary."""
        solution = np.array(
            [
                1,
                2,
                3,
                4,
                5,
                6,  # Pokemon IDs
                10,
                11,
                12,
                13,  # Moves for pokemon 1
                20,
                21,
                22,
                23,  # Moves for pokemon 2
                30,
                31,
                32,
                33,  # Moves for pokemon 3
                40,
                41,
                42,
                43,  # Moves for pokemon 4
                50,
                51,
                52,
                53,  # Moves for pokemon 5
                60,
                61,
                62,
                63,  # Moves for pokemon 6
            ],
            dtype=np.int16,
        )

        pre_selected: Dict[int, list] = {}

        # Should not raise - no preselected pokemon to validate
        assert_preselected_in_solution(solution, pre_selected)

    def test_preselected_with_negative_one_moves(self) -> None:
        """Test solution where some moves are -1 (unfilled)."""
        solution = np.array(
            [
                1,
                2,
                3,
                4,
                5,
                6,  # Pokemon IDs
                10,
                11,
                -1,
                -1,  # Moves for pokemon 1 (only 2 moves)
                20,
                21,
                22,
                -1,  # Moves for pokemon 2 (3 moves)
                30,
                31,
                32,
                33,  # Moves for pokemon 3
                40,
                41,
                42,
                43,  # Moves for pokemon 4
                50,
                51,
                52,
                53,  # Moves for pokemon 5
                60,
                61,
                62,
                63,  # Moves for pokemon 6
            ],
            dtype=np.int16,
        )

        pre_selected = {
            1: [10, 11],
            2: [20, 21],
        }

        # Should pass - preselected moves are present even with -1 unfilled slots
        assert_preselected_in_solution(solution, pre_selected)

    def test_single_preselected_pokemon(self) -> None:
        """Test with only one preselected pokemon."""
        solution = np.array(
            [
                1,
                2,
                3,
                4,
                5,
                6,  # Pokemon IDs
                10,
                11,
                12,
                13,  # Moves for pokemon 1
                20,
                21,
                22,
                23,  # Moves for pokemon 2
                30,
                31,
                32,
                33,  # Moves for pokemon 3
                40,
                41,
                42,
                43,  # Moves for pokemon 4
                50,
                51,
                52,
                53,  # Moves for pokemon 5
                60,
                61,
                62,
                63,  # Moves for pokemon 6
            ],
            dtype=np.int16,
        )

        pre_selected = {1: [10, 11]}

        assert_preselected_in_solution(solution, pre_selected)

    def test_preselected_with_no_moves(self) -> None:
        """Test preselected pokemon with empty move list."""
        solution = np.array(
            [
                1,
                2,
                3,
                4,
                5,
                6,  # Pokemon IDs
                10,
                11,
                12,
                13,  # Moves for pokemon 1
                20,
                21,
                22,
                23,  # Moves for pokemon 2
                30,
                31,
                32,
                33,  # Moves for pokemon 3
                40,
                41,
                42,
                43,  # Moves for pokemon 4
                50,
                51,
                52,
                53,  # Moves for pokemon 5
                60,
                61,
                62,
                63,  # Moves for pokemon 6
            ],
            dtype=np.int16,
        )

        pre_selected = {1: [], 2: [20]}

        # Should pass - pokemon 1 has no required moves, pokemon 2 has move 20
        assert_preselected_in_solution(solution, pre_selected)

    def test_different_team_size(self) -> None:
        """Test with different team size."""
        # Team of 3 pokemon
        solution = np.array(
            [
                1,
                2,
                3,  # Pokemon IDs
                10,
                11,
                12,
                13,  # Moves for pokemon 1
                20,
                21,
                22,
                23,  # Moves for pokemon 2
                30,
                31,
                32,
                33,  # Moves for pokemon 3
            ],
            dtype=np.int16,
        )

        pre_selected = {1: [10, 11]}

        assert_preselected_in_solution(solution, pre_selected, pokemon_in_team=3)

    def test_all_four_moves_preselected(self) -> None:
        """Test when all four moves of a pokemon are preselected."""
        solution = np.array(
            [
                1,
                2,
                3,
                4,
                5,
                6,  # Pokemon IDs
                10,
                11,
                12,
                13,  # Moves for pokemon 1 (all preselected)
                20,
                21,
                22,
                23,  # Moves for pokemon 2
                30,
                31,
                32,
                33,  # Moves for pokemon 3
                40,
                41,
                42,
                43,  # Moves for pokemon 4
                50,
                51,
                52,
                53,  # Moves for pokemon 5
                60,
                61,
                62,
                63,  # Moves for pokemon 6
            ],
            dtype=np.int16,
        )

        pre_selected = {1: [10, 11, 12, 13]}

        assert_preselected_in_solution(solution, pre_selected)

    def test_integration_with_actual_fixtures(self, test_data: Dict[str, Any], pre_selected: Dict[int, list]) -> None:
        """Test using actual fixtures from conftest."""
        # Create a solution that matches the pre_selected fixture
        pokemon_ids = list(pre_selected.keys()) + [4, 5, 6][: 6 - len(pre_selected)]

        solution_parts = [np.array(pokemon_ids, dtype=np.int16)]

        # Add moves for each pokemon
        for pokemon_id in pokemon_ids:
            if pokemon_id in pre_selected:
                moves = pre_selected[pokemon_id]
                # Pad with other learnable moves if needed
                learnable = np.where(test_data["lm"][pokemon_id])[0]
                while len(moves) < 4:
                    for move in learnable:
                        if move not in moves:
                            moves.append(int(move))
                            break
                solution_parts.append(np.array(moves[:4], dtype=np.int16))
            else:
                # Random learnable moves
                learnable = np.where(test_data["lm"][pokemon_id])[0]
                solution_parts.append(np.array(learnable[:4], dtype=np.int16))

        solution = np.concatenate(solution_parts)

        # Should pass with actual fixture data
        assert_preselected_in_solution(solution, pre_selected)
