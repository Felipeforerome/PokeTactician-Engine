import inspect
from collections.abc import Collection
from types import FunctionType
from typing import Any, Callable

import numpy as np

from poketactician.config import OBJECTIVE_REGISTRY, PENDING_OBJECTIVES


class ObjectiveFunction:
    """
    Lightweight wrapper around an objective function and its bound keyword arguments.

    Args:
        name (str): Identifier for this objective.
        func (Callable): Callable with signature func(x: np.ndarray, y: np.ndarray, **kwargs) -> np.ndarray.
        data (dict): Keyword arguments bound to func and supplied on each call.

    Calling:
        obj(x: np.ndarray, y: np.ndarray) -> np.ndarray
        Evaluates func(x, y, **data).
    """

    def __init__(self, name: str, func: Callable, data: dict) -> None:
        self.name = name
        self.func = func
        self.data = data

    def __call__(self, x: np.ndarray, y: np.ndarray) -> np.ndarray:
        return self.func(x, y, **self.data)


def register_objective(
    name: str | None = None,
    data_mapping: dict[str, str] | None = None,
) -> Callable[..., Any]:
    """Create a decorator to register an objective function.

    If no name is provided, the decorated function's __name__ is used.

    Args:
        name: Optional registry key for the objective.
        data_mapping: Optional mapping from function parameter names to data
            context keys.  When omitted, parameter names are looked up directly
            in the data context (auto-wiring).

    Returns:
        A decorator that stores the function (and its mapping) in
        PENDING_OBJECTIVES under the resolved name and returns a
        metadata-preserving wrapper.
    """

    def decorator(func: FunctionType) -> Callable[..., Any]:
        func_name = name or func.__name__
        PENDING_OBJECTIVES[func_name] = (func, data_mapping)
        return func

    return decorator


def register_objective_data(
    data_context: dict[str, Any],
    objective_names: Collection[str] | None = None,
) -> None:
    """Validate and register objective functions with their parameter data.

    For each pending objective whose name is in *objective_names* (or all
    pending objectives when *objective_names* is ``None``), this inspects the
    function signature and resolves every parameter after the first two (X and
    Y) from *data_context*.

    Resolution order per parameter:
      1. If the objective was decorated with a ``data_mapping``, use it to
         translate the parameter name to a data-context key.
      2. Otherwise, look up the parameter name directly in *data_context*
         (auto-wiring).

    Args:
        data_context: Flat dict of available data keyed by attribute /
            variable name (e.g. ``{"moves_category": arr, ...}``).
        objective_names: If provided, only wire these objectives.  Any name
            not found in PENDING_OBJECTIVES raises ``ValueError``.

    Raises:
        ValueError: If a requested objective is unknown, or if required
            parameter keys cannot be resolved from *data_context*.

    Side Effects:
        Mutates OBJECTIVE_REGISTRY by (over)writing entries for registered
        objectives.
    """
    factories: dict[str, Callable[[], Any]] = {}
    names_to_wire: Collection[str]
    if objective_names is not None:
        unknown = set(objective_names) - set(PENDING_OBJECTIVES.keys())
        if unknown:
            raise ValueError(f"Unknown objective(s): {unknown}. Available: {set(PENDING_OBJECTIVES.keys())}")
        names_to_wire = objective_names
    else:
        names_to_wire = list(PENDING_OBJECTIVES.keys())

    for obj_name in names_to_wire:
        func, mapping = PENDING_OBJECTIVES[obj_name]

        sig = inspect.signature(func)
        params = list(sig.parameters.keys())[2:]  # skip X and Y

        bound: dict[str, Any] = {}
        missing: list[str] = []
        for param in params:
            context_key = mapping[param] if mapping and param in mapping else param
            if context_key in data_context:
                bound[param] = data_context[context_key]
            else:
                missing.append(f"{param} (looked up as '{context_key}')")
        if missing:
            raise ValueError(f"Missing data for objective '{obj_name}': {missing}")

        factories[obj_name] = lambda f=func, d=bound, n=obj_name: ObjectiveFunction(n, f, d)

    OBJECTIVE_REGISTRY.update(factories)
