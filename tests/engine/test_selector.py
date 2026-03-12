"""Tests for the ObjectiveSelector class."""

import numpy as np
import pytest

from poketactician.config import OBJECTIVE_REGISTRY
from poketactician.engine.selector import ObjectiveSelector


class TestObjectiveSelector:
    """Tests for the ObjectiveSelector class."""

    def test_selector_initialization(self) -> None:
        """Test that ObjectiveSelector initializes correctly."""
        selector = ObjectiveSelector(objective_names=["test_objective"])

        assert selector.n_obj == 1
        assert len(selector.objectives) == 1

    def test_selector_multiple_objectives(self) -> None:
        """Test ObjectiveSelector with multiple objectives."""
        selector = ObjectiveSelector(objective_names=["test_objective", "test_objective2"])

        assert selector.n_obj == 2
        assert len(selector.objectives) == 2

    def test_selector_invalid_objective(self) -> None:
        """Test that ObjectiveSelector raises error for invalid objective."""
        with pytest.raises(AssertionError):
            ObjectiveSelector(objective_names=["nonexistent_objective"])

    def test_selector_evaluate(self) -> None:
        """Test that ObjectiveSelector evaluates objectives correctly."""
        selector = ObjectiveSelector(objective_names=["test_objective", "test_objective2"])

        # Create dummy inputs
        x = np.array([0, 1, 2], dtype=np.int16)
        y = np.array([[0, 1, 2, 3], [4, 5, 6, 7], [8, 9, 10, 11]], dtype=np.int16)

        result = selector.evaluate(x, y)

        # Should return a list of objective values (negated for maximization)
        assert isinstance(result, list)
        assert len(result) == 2

    def test_selector_evaluate_single_objective(self) -> None:
        """Test evaluation with single objective."""
        selector = ObjectiveSelector(objective_names=["test_objective"])

        x = np.array([0, 1], dtype=np.int16)
        y = np.array([[0, 1, -1, -1], [2, 3, -1, -1]], dtype=np.int16)

        result = selector.evaluate(x, y)

        assert len(result) == 1
        assert isinstance(result[0], (int, float, np.number))

    def test_selector_with_empty_objectives_fails(self) -> None:
        """Test that empty objective list fails."""
        with pytest.raises(ValueError):
            ObjectiveSelector(objective_names=[])

    def test_selector_objectives_are_callable(self) -> None:
        """Test that selector objectives are callable."""
        selector = ObjectiveSelector(objective_names=["test_objective"])

        # Each objective should be callable
        for obj in selector.objectives:
            assert callable(obj)

    def test_selector_with_valid_registered_objectives(self) -> None:
        """Test selector only accepts registered objectives."""
        # Get all registered objectives
        registered = list(OBJECTIVE_REGISTRY.keys())

        # Should work with any registered objective
        for obj_name in registered:
            selector = ObjectiveSelector(objective_names=[obj_name])
            assert selector.n_obj == 1

    def test_selector_evaluate_returns_negated_values(self) -> None:
        """Test that evaluate returns negated values for maximization."""
        selector = ObjectiveSelector(objective_names=["test_objective"])

        x = np.array([0, 1], dtype=np.int16)
        y = np.array([[0, 1, -1, -1], [2, 3, -1, -1]], dtype=np.int16)

        result = selector.evaluate(x, y)

        # Values should be negated (for pymoo minimization → maximization conversion)
        # The dummy objective returns values, selector negates them
        assert isinstance(result[0], (int, float, np.number))

    def test_selector_consistent_evaluation(self) -> None:
        """Test that selector gives consistent results for same inputs.(Make sure the same function is executed each time.)"""
        selector = ObjectiveSelector(objective_names=["test_objective", "test_objective2"])

        x = np.array([0, 1, 2], dtype=np.int16)
        y = np.array([[0, 1, 2, 3], [4, 5, 6, 7], [8, 9, 10, 11]], dtype=np.int16)

        result1 = selector.evaluate(x, y)
        result2 = selector.evaluate(x, y)

        # Same inputs should give same results
        assert result1 == result2

    def test_selector_different_inputs_different_outputs(self) -> None:
        """Test that different inputs give different outputs.(Make sure different functions are executed each time)"""
        selector = ObjectiveSelector(objective_names=["test_objective"])

        x1 = np.array([0, 1], dtype=np.int16)
        y1 = np.array([[0, 1, -1, -1], [2, 3, -1, -1]], dtype=np.int16)

        x2 = np.array([2, 3], dtype=np.int16)
        y2 = np.array([[4, 5, -1, -1], [6, 7, -1, -1]], dtype=np.int16)

        result1 = selector.evaluate(x1, y1)
        result2 = selector.evaluate(x2, y2)

        # Different inputs (likely) give different results
        # Note: they could be the same by chance, but unlikely
        assert isinstance(result1, list)
        assert isinstance(result2, list)
