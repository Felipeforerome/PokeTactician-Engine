from typing import Any, Callable

# Stores undecorated raw functions (no data yet)
PENDING_OBJECTIVES: dict[str, Callable[..., Any]] = {}

# Stores registered ObjectiveFunction factories (data injected)
OBJECTIVE_REGISTRY: dict[str, Callable[[], Any]] = {}

SEED = 42
