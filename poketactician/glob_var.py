from enum import Enum

from .cooperationStrats import selectionByDominance

# from models import Pokemon

# User Defined Variables
# Pheromone amount deposited
Q = 1

# Evaporation Rate 0≤rho<1
rho = 0.1

# Relative importance of pheromones (alpha) vs heuristic (beta)
alpha = 1
beta = 0


class CooperationStats(Enum):
    SELECTION_BY_DOMINANCE = selectionByDominance
