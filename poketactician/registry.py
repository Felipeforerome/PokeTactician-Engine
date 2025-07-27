import inspect
from functools import wraps
from typing import Any, Callable

import numpy as np

from poketactician.config import OBJECTIVE_REGISTRY, PENDING_OBJECTIVES


class ObjectiveFunction:
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


def register_objective(name: str = None) -> Callable[..., Any]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        func_name = name or func.__name__
        PENDING_OBJECTIVES[func_name] = func  # store raw function
        return wraps(func)

    return decorator


def register_objective_data(data_dict: dict[str, dict]) -> None:
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
