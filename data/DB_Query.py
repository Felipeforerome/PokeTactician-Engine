# Query Database
# To run this script, you need to have the PokeAPI running on your local machine. To do this do the following steps:
# - Clone the repository from
# - If you already had the repo, delete the volumes and images of the containers
# - Run the docker configuration from the README
# - Go into Hasura and import all tables and foreign keys (this can take a bit)
# - Import the hasura metadata from the metadata file in the repo

import sys

import requests

sys.path.append(sys.path[0] + "/..")
import json
import pickle
import re
import time

from poketactician.models.Move import Move
from poketactician.models.Pokemon import Pokemon


def build_data(recalculateMoves):
    """
    Builds the data for the PokemonOpti application.

    Args:
        recalculateMoves (bool): Flag indicating whether to recalculate the moves or use existing data.

    Returns:
        None
    """
    tic = time.time()
    i = 1
    j = 1
    movesTotal = 0
    Pokemons = []
    # Initialize Moves with a no-move for cases where the pokemon has no moves
    Moves = {
        "0": Move.from_json(
            {
                "id": "0",
                "name": "no-move",
                "type": "Normal",
                "damageClass": "physical",
                "power": 1,
                "accuracy": 0,
                "pp": 0,
                "priority": 0,
            }
        )
    }
    lastMove = True
    print("Started: " + time.strftime("%H:%M:%S", time.gmtime(tic + 7200)))
    if recalculateMoves:
        while lastMove:
            movepreJSON = requests.get(
                "http://localhost:8080/api/rest/moves/" + str(j),
                headers={"x-hasura-admin-secret": "pokemon"},
            )
            moveJSON = movepreJSON.json()["moves"]
            emptyListResp = len(moveJSON) == 0
            if not emptyListResp:
                moveJSON = moveJSON[0]
                tempMove = Move(
                    str(j),
                    moveJSON["name"],
                    moveJSON["type"]["name"],
                    moveJSON["damage_class"]["name"],
                    moveJSON["power"],
                    moveJSON["accuracy"],
                    moveJSON["pp"],
                    moveJSON["priority"],
                )
                Moves[str(j)] = tempMove
                j += 1
                if j % 100 == 0:
                    print(str(j) + ": " + moveJSON["name"])
            else:
                lastMove = False
        movesDict = {k: v.serialize() for k, v in Moves.items()}
        with open("data/move_data.json", "w") as f:
            json.dump(movesDict, f, indent=4)
    else:
        with open("data/move_data.json", "r") as f:
            data = json.load(f)
            Moves = {
                k: Move.from_json(pokemon_data) for k, pokemon_data in data.items()
            }

    print("Finished Moves")
    lastExisted = True
    normalForms = True
    print("Starting Pokemons")
    while lastExisted:
        pokemonpreJSON = requests.get(
            "http://localhost:8080/api/rest/pokemon/" + str(i),
            headers={"x-hasura-admin-secret": "pokemon"},
        )
        pokemonJSON = pokemonpreJSON.json()["pokemon"]
        emptyListResp = len(pokemonJSON) == 0
        if not emptyListResp:
            pokemonJSON = pokemonJSON[0]
            tempPoke = Pokemon(
                pokemonJSON["id"],
                pokemonJSON["name"],
                pokemonJSON["stats"][0]["base_stat"],
                pokemonJSON["stats"][1]["base_stat"],
                pokemonJSON["stats"][2]["base_stat"],
                pokemonJSON["stats"][3]["base_stat"],
                pokemonJSON["stats"][4]["base_stat"],
                pokemonJSON["stats"][5]["base_stat"],
                pokemonJSON["types"][0]["type"].get("name"),
                (
                    None
                    if len(pokemonJSON["types"]) < 2
                    else pokemonJSON["types"][1]["type"].get("name")
                ),
                bool(pokemonJSON["legend"]["is_mythical"]),
                bool(pokemonJSON["legend"]["is_legendary"]),
                bool(pokemonJSON["formAbout"][0]["is_battle_only"]),
                bool(pokemonJSON["formAbout"][0]["is_mega"]),
            )
            availableMoves = pokemonJSON["moves"]
            for availableMove in availableMoves:
                number = availableMove["move"]["id"]
                appendMove = Moves[str(number)]
                tempPoke.addKnowableMove(appendMove)

            Pokemons.append(tempPoke)
            movesTotal += pokemonJSON["moves"].__len__()
            i += 1
            if i % 100 == 0:
                print(str(i) + ": " + pokemonJSON["name"])
        else:
            if not normalForms:
                lastExisted = False
            normalForms = False
            i = 10001

    serialized_pokemon_list = [pokemon.serialize() for pokemon in Pokemons]
    with open("data/pokemon_data.json", "w") as f:
        json.dump(serialized_pokemon_list, f, indent=4)
    toc = time.time()
    elapsed_time = toc - tic
    print("Elapsed Time: {:.2f} seconds".format(elapsed_time))


build_data(True)
