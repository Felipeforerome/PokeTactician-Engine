import inspect
from functools import wraps
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


# def register_objective(name: str | None = None, **data) -> Callable[..., Any]:
#     def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
#         sig = inspect.signature(func)
#         params = list(sig.parameters.keys())[2:]  # skip X and Y
#         func_name = name or func.__name__

#         @wraps(func)
#         def factory(*args, **kwargs) -> ObjectiveFunction:
#             missing = [k for k in params if k not in data and k not in kwargs]
#             if missing:
#                 raise ValueError(f"Missing keys for '{name}': {missing}")
#             return ObjectiveFunction(func_name, func, {**data, **kwargs})

#         OBJECTIVE_REGISTRY[func_name] = factory
#         return func

#     return decorator


def register_objective(name: str | None = None) -> Callable[..., Any]:
    """Create a decorator to register an objective function.

    If no name is provided, the decorated function’s __name__ is used.

    Args:
        name: Optional registry key for the objective.

    Returns:
        A decorator that stores the function in PENDING_OBJECTIVES under the resolved name and returns a metadata-preserving wrapper.
    """

    def decorator(func: FunctionType) -> Callable[..., Any]:
        func_name = name or func.__name__
        PENDING_OBJECTIVES[func_name] = func  # store raw function
        return wraps(func)

    return decorator


def register_objective_data(data_dict: dict[str, dict]) -> None:
    """Validate and register objective functions with their parameter data.
    For each function in PENDING_OBJECTIVES whose name is present in `data_dict`,
    this inspects the function signature, requiring keys for all parameters after
    the first two (X and Y). If all required keys are provided, it stores a factory
    callable in OBJECTIVE_REGISTRY that builds an ObjectiveFunction with the given
    name, function, and data.
    Args:
        data_dict: Mapping from objective name to a dict of parameter values.
    Raises:
        ValueError: If any required parameter keys are missing for a given objective.
    Side Effects:
        Mutates OBJECTIVE_REGISTRY by (over)writing entries for registered objectives.
    """

    for name, func in PENDING_OBJECTIVES.items():
        if name not in data_dict:
            continue

        sig = inspect.signature(func)
        params = list(sig.parameters.keys())[2:]  # skip X and Y
        missing = [k for k in params if k not in data_dict[name]]
        if missing:
            raise ValueError(f"Missing keys for '{name}': {missing}")

        data = data_dict[name]
        OBJECTIVE_REGISTRY[name] = lambda f=func, d=data, n=name: ObjectiveFunction(n, f, d)
