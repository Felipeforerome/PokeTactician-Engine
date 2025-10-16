"""Tests for the registry module in the poketactician package."""

import numpy as np
import pytest

from poketactician.config import OBJECTIVE_REGISTRY, PENDING_OBJECTIVES
from poketactician.registry import ObjectiveFunction, register_objective, register_objective_data


class TestObjectiveFunction:
    """Tests for the ObjectiveFunction class."""

    def test_objective_function(self) -> None:
        """Test that ObjectiveFunction works correctly."""

        # Create a simple objective function
        def dummy_objective(x: np.ndarray, y: np.ndarray, val: int) -> int:
            return val

        # Create an ObjectiveFunction instance
        obj_func = ObjectiveFunction("dummy", dummy_objective, {"val": 42})

        # Create test inputs
        x = np.array([0, 1], dtype=np.int16)
        y = np.array([[0, 1, -1, -1], [2, -1, -1, -1]], dtype=np.int16)

        # Test that the function returns the expected value
        assert obj_func(x, y) == 42

        # Test with a different value
        obj_func2 = ObjectiveFunction("dummy", dummy_objective, {"val": 99})
        assert obj_func2(x, y) == 99

    def test_register_objective(self) -> None:
        """Test that register_objective works correctly."""
        # Clear any existing objectives for this test
        old_pending = PENDING_OBJECTIVES.copy()
        PENDING_OBJECTIVES.clear()

        # Define a test objective function
        @register_objective()
        def test_objective_func(x: np.ndarray, y: np.ndarray, val: int) -> int:
            return val

        # Check that the objective is in PENDING_OBJECTIVES
        assert "test_objective_func" in PENDING_OBJECTIVES

        # Define a test objective function with a custom name
        @register_objective(name="custom_name")
        def another_test_func(x: np.ndarray, y: np.ndarray, val: int) -> int:
            return val

        # Check that the objective is in PENDING_OBJECTIVES with the custom name
        assert "custom_name" in PENDING_OBJECTIVES

        assert "incorrect_name" not in PENDING_OBJECTIVES

        # Restore the original PENDING_OBJECTIVES
        PENDING_OBJECTIVES.clear()
        PENDING_OBJECTIVES.update(old_pending)

    def test_register_objective_with_data(self) -> None:
        """Test that register_objective_data works correctly."""
        # Clear any existing objectives for this test
        old_pending = PENDING_OBJECTIVES.copy()
        old_registry = OBJECTIVE_REGISTRY.copy()
        PENDING_OBJECTIVES.clear()
        OBJECTIVE_REGISTRY.clear()

        # Define a test objective function
        @register_objective()
        def test_objective_func(x: np.ndarray, y: np.ndarray, val: int) -> int:
            return val

        # Register the objective data
        register_objective_data({"test_objective_func": {"val": 42}})

        # Check that the objective is in OBJECTIVE_REGISTRY
        assert "test_objective_func" in OBJECTIVE_REGISTRY

        # Create an instance of the objective function
        obj_func = OBJECTIVE_REGISTRY["test_objective_func"]()

        # Check that it's an ObjectiveFunction
        assert isinstance(obj_func, ObjectiveFunction)

        # Test that it works correctly
        x = np.array([0, 1], dtype=np.int16)
        y = np.array([[0, 1, -1, -1], [2, -1, -1, -1]], dtype=np.int16)
        assert obj_func(x, y) == 42

        # Test with missing data
        @register_objective()
        def test_objective_missing(x: np.ndarray, y: np.ndarray, val1: int, val2: int) -> int:
            return val1 + val2

        # Register with missing data - should raise ValueError
        with pytest.raises(ValueError):
            register_objective_data(
                {
                    "test_objective_missing": {"val1": 10}  # Missing val2
                }
            )

        # Restore the original PENDING_OBJECTIVES and OBJECTIVE_REGISTRY
        PENDING_OBJECTIVES.clear()
        PENDING_OBJECTIVES.update(old_pending)
        OBJECTIVE_REGISTRY.clear()
        OBJECTIVE_REGISTRY.update(old_registry)
