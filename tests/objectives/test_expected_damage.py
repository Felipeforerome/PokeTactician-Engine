"""Tests for the expected_damage objective function."""

from typing import Any, Dict

import numpy as np
import pytest

from poketactician.config import OBJECTIVE_REGISTRY
from poketactician.objectives.dummy_objectives import expected_damage
from poketactician.registry import ObjectiveFunction, register_objective_data


class TestExpectedDamage:
    """Tests for the expected_damage objective function."""

    @pytest.fixture
    def objective(self, test_data: Dict[str, Any]) -> ObjectiveFunction:
        """Register and return the expected_damage ObjectiveFunction."""
        register_objective_data(
            {
                "pokemon_stats": test_data["ps"],
                "moves_category": test_data["me"],
                "move_types": test_data["mt"],
                "pokemon_types": test_data["pt"],
            },
            objective_names=["expected_damage"],
        )
        return OBJECTIVE_REGISTRY["expected_damage"]()

    # ── Basic contract tests ─────────────────────────────────────────

    def test_returns_int(self, objective: ObjectiveFunction, test_data: Dict[str, Any]) -> None:
        """Return type must be int."""
        x = np.array([0, 1, 2, 3, 4, 5], dtype=np.int16)
        moves = []
        for i in x:
            learnable = np.where(test_data["lm"][i])[0]
            moves.extend(learnable[:4].tolist() + [-1] * (4 - min(len(learnable), 4)))
        y = np.array(moves, dtype=np.int16).reshape(len(x), 4)
        result = objective(x, y)
        assert isinstance(result, int)

    def test_result_is_nonnegative(self, objective: ObjectiveFunction, test_data: Dict[str, Any]) -> None:
        """Damage with non-negative inputs should be non-negative."""
        x = np.array([0, 1, 2, 3, 4, 5], dtype=np.int16)
        moves = []
        for i in x:
            learnable = np.where(test_data["lm"][i])[0]
            moves.extend(learnable[:4].tolist() + [-1] * (4 - min(len(learnable), 4)))
        y = np.array(moves, dtype=np.int16).reshape(len(x), 4)
        result = objective(x, y)
        assert result >= 0

    # ── Zero / empty edge cases ──────────────────────────────────────

    def test_no_moves_selected_returns_zero(self, objective: ObjectiveFunction) -> None:
        """When every move slot is -1, damage must be zero."""
        x = np.array([0, 1], dtype=np.int16)
        y = np.full((2, 4), -1, dtype=np.int16)
        assert objective(x, y) == 0

    def test_empty_team_returns_zero(self) -> None:
        """An empty team (x length 0) should produce zero damage."""
        # Minimal arrays — shapes don't matter as long as they're consistent
        pokemon_stats = np.zeros((1, 6), dtype=np.int16)
        moves_category = np.zeros((2, 1), dtype=np.int16)
        move_types = np.zeros((1, 2), dtype=bool)
        pokemon_types = np.zeros((1, 2), dtype=bool)

        x = np.array([], dtype=np.int16)
        y = np.array([], dtype=np.int16).reshape(0, 4)
        result = expected_damage(x, y, pokemon_stats, moves_category, move_types, pokemon_types)
        assert result == 0

    # ── Hand-crafted value test ──────────────────────────────────────

    def test_known_value(self) -> None:
        """Verify exact damage for a minimal hand-crafted scenario.

        Setup (1 Pokémon, 1 move, 1 type, 1 damage class):
        - Pokémon 0 is type-0 → STAB applies (0.5 * 1 + 1 = 1.5)
        - Move 0 is type-0, physical (category col 0 = 1), power = 1, accuracy = 1
        - Pokémon 0 stats: ATK = 100 (index 1), others = 0

        Expected: stab(1.5) * category(1) * ATK(100) = 150
        """
        pokemon_types = np.array([[True]], dtype=bool)  # 1 pokemon, 1 type
        move_types = np.array([[True]], dtype=bool)  # 1 move, 1 type
        moves_category = np.array([[1]], dtype=np.int16)  # 1 class, 1 move — physical
        pokemon_stats = np.array([[0, 100, 0, 0, 0, 0]], dtype=np.int16)  # ATK = 100

        x = np.array([0], dtype=np.int16)
        y = np.array([[0, -1, -1, -1]], dtype=np.int16)

        result = expected_damage(x, y, pokemon_stats, moves_category, move_types, pokemon_types)
        assert result == 150

    # ── STAB bonus test ──────────────────────────────────────────────

    def test_stab_bonus_increases_damage(self) -> None:
        """A Pokémon whose type matches the move type gets 1.5* STAB vs 1.0*."""
        # 2 pokemon, 2 types, 1 move of type-0, 1 damage class (physical)
        pokemon_types = np.array(
            [
                [True, False],  # pokemon 0: type-0 (STAB)
                [False, True],  # pokemon 1: type-1 (no STAB)
            ],
            dtype=bool,
        )
        move_types = np.array([[True, False]], dtype=bool)  # move 0 is type-0
        moves_category = np.array([[1]], dtype=np.int16)  # physical class
        pokemon_stats = np.array(
            [
                [0, 100, 0, 0, 0, 0],  # pokemon 0: ATK = 100
                [0, 100, 0, 0, 0, 0],  # pokemon 1: ATK = 100
            ],
            dtype=np.int16,
        )

        y = np.array([[0, -1, -1, -1]], dtype=np.int16)

        dmg_stab = expected_damage(np.array([0], dtype=np.int16), y, pokemon_stats, moves_category, move_types, pokemon_types)
        dmg_no_stab = expected_damage(np.array([1], dtype=np.int16), y, pokemon_stats, moves_category, move_types, pokemon_types)
        assert dmg_stab > dmg_no_stab
        assert dmg_stab == 150  # 1.5 × 1 × 100
        assert dmg_no_stab == 100  # 1.0 × 1 × 100

    # ── Attack stat scaling test ─────────────────────────────────────

    def test_higher_attack_stat_increases_damage(self) -> None:
        """Doubling the Attack stat should double physical damage."""
        pokemon_types = np.array([[True]], dtype=bool)
        move_types = np.array([[True]], dtype=bool)
        moves_category = np.array([[1]], dtype=np.int16)

        stats_low = np.array([[0, 50, 0, 0, 0, 0]], dtype=np.int16)
        stats_high = np.array([[0, 100, 0, 0, 0, 0]], dtype=np.int16)

        x = np.array([0], dtype=np.int16)
        y = np.array([[0, -1, -1, -1]], dtype=np.int16)

        dmg_low = expected_damage(x, y, stats_low, moves_category, move_types, pokemon_types)
        dmg_high = expected_damage(x, y, stats_high, moves_category, move_types, pokemon_types)
        assert dmg_high == 2 * dmg_low
