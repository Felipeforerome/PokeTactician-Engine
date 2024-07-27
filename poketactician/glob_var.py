import json
import pickle

from .cooperationStrats import selectionByDominance
from .models.Move import Move
from .models.Pokemon import Pokemon

# from models import Pokemon

# User Defined Variables
# Pheromone amount deposited
Q = 1

# Evaporation Rate 0≤rho<1
rho = 0.1

# Relative importance of pheromones (alpha) vs heuristic (beta)
alpha = 1
beta = 0

cooperationStatsDict = {1: selectionByDominance}

# Save to a JSON file the pokemon_list

# serialized_pokemon_list = [serialize_pokemon(pokemon) for pokemon in pokemon_list]

# with open("pokemon_data.json", "w") as json_file:
#     json.dump(serialized_pokemon_list, json_file, indent=4)


# Function to load and recreate the list of Pokemon from the JSON file
def load_pokemon_from_json(file_name):
    with open(file_name, "r") as json_file:
        data = json.load(json_file)
        return [Pokemon.from_json(pokemon_data) for pokemon_data in data]


# Function to load and recreate the list of Moves from the JSON file
def load_moves_from_json(file_name):
    with open(file_name, "r") as json_file:
        data = json.load(json_file)
        return {key: Move.from_json(value) for key, value in data.items()}


pokPreFilter = load_pokemon_from_json("data/pokemon_data.json")
moves = load_moves_from_json("data/move_data.json")
