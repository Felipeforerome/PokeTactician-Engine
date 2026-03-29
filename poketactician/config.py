from typing import Any, Callable

# Stores undecorated raw functions with optional data_mapping (no data yet)
PENDING_OBJECTIVES: dict[str, tuple[Callable[..., Any], dict[str, str] | None]] = {}

# Stores registered ObjectiveFunction factories (data injected)
OBJECTIVE_REGISTRY: dict[str, Callable[[], Any]] = {}

SEED = 42
