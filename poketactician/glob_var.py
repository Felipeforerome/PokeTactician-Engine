from .cooperationStrats import selectionByDominance
from .models.Pokemon import Pokemon
from .models.Move import Move
import json
import pickle

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


# Function to serialize a Move instance
def serialize_move(move):
    return {
        "id": move.id,
        "name": move.name,
        "type": move.type,
        "damageClass": move.damageClass,
        "power": move.power,
        "accuracy": move.accuracy,
        "pp": move.pp,
        "priority": move.priority,
    }


# Function to serialize a Pokemon instance
def serialize_pokemon(pokemon):
    serialized_moves = [serialize_move(move) for move in pokemon.knowableMoves]
    return {
        "name": pokemon.name,
        "hp": pokemon.hp,
        "att": pokemon.att,
        "deff": pokemon.deff,
        "spatt": pokemon.spatt,
        "spdeff": pokemon.spdeff,
        "spe": pokemon.spe,
        "type1": pokemon.type1,
        "type2": pokemon.type2,
        "knowableMoves": serialized_moves,
    }


# Save to a JSON file the pokemon_list

# serialized_pokemon_list = [serialize_pokemon(pokemon) for pokemon in pokemon_list]

# with open("pokemon_data.json", "w") as json_file:
#     json.dump(serialized_pokemon_list, json_file, indent=4)


# Function to deserialize a Move instance
def deserialize_move(data):
    return Move(
        data["id"],
        data["name"],
        data["type"],
        data["damageClass"],
        data["power"],
        int(data["accuracy"] * 100),
        data["pp"],
        data["priority"],
    )


# Function to deserialize a Pokemon instance
def deserialize_pokemon(data):
    moves = [deserialize_move(move_data) for move_data in data["knowableMoves"]]
    pokemon = Pokemon(
        data["name"],
        data["hp"],
        data["att"],
        data["deff"],
        data["spatt"],
        data["spdeff"],
        data["spe"],
        data["type1"],
        data["type2"],
    )
    for move in moves:
        pokemon.addKnowableMove(move)
    return pokemon


# Function to load and recreate the list of Pokemon from the JSON file
def load_pokemon_from_json(file_name):
    with open(file_name, "r") as json_file:
        data = json.load(json_file)
        return [deserialize_pokemon(pokemon_data) for pokemon_data in data]


# Function to load and recreate the list of Moves from the JSON file
def load_moves_from_json(file_name):
    with open(file_name, "r") as json_file:
        data = json.load(json_file)
        return {key: deserialize_move(value) for key, value in data.items()}


pokPreFilter = load_pokemon_from_json("data/pokemon_data.json")
moves = load_moves_from_json("data/move_data.json")
