from typing import Any, Callable

# Stores undecorated raw functions with optional data_mapping (no data yet)
PENDING_OBJECTIVES: dict[str, tuple[Callable[..., Any], dict[str, str] | None]] = {}

# Stores registered ObjectiveFunction factories (data injected)
OBJECTIVE_REGISTRY: dict[str, Callable[[], Any]] = {}

SEED = 42

NUMBER_OF_MOVES_SLOTS = 4

MAX_NUMBER_OF_POKEMON = 6

NUMBER_OF_TYPES = 18

NUMBER_OF_STATS = 6

NUMBER_OF_NATURES = 25

EMPTY_MOVE_SENTINEL = -1

STAB_BONUS = 0.5  # Bonus for moves that match the Pokémon's type, not matching gives 1

ATK_STAT_INDEX = 1

SPA_STAT_INDEX = 3

DEFAULT_CROSSOVER_PROB = 0.5

DEFAULT_MUTATION_PROB_POKEMON = 0.01

DEFAULT_MUTATION_PROB_MOVE = 0.001
