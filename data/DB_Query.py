# Query Database

import requests
import sys

sys.path.append(sys.path[0] + "/..")
from poketactician.models.Pokemon import Pokemon
from poketactician.models.Move import Move
import pickle
import re
import time
import json

tic = time.time()
i = 1
j = 1
movesTotal = 0
Pokemons = []
Moves = {}
lastMove = True
recalculateMoves = False
print("Started: " + str(tic))
if recalculateMoves:
    while lastMove:
        movepreJSON = requests.get("http://localhost:80/api/v2/move/" + str(j))
        is404 = movepreJSON.status_code == 404
        if not is404:
            moveJSON = movepreJSON.json()
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
        else:
            lastMove = False
    print("Finished Moves")
    movesDict = {k: v.serialize() for k, v in Moves.items()}
    with open("data/move_data.json", "w") as f:
        json.dump(movesDict, f, indent=4)
else:
    with open("data/move_data.json", "r") as f:
        data = json.load(f)
        Moves = {k: Move.from_json(pokemon_data) for k, pokemon_data in data.items()}


lastExisted = True
while lastExisted:
    pokemonpreJSON = requests.get("http://localhost:80/api/v2/pokemon/" + str(i))
    is404 = pokemonpreJSON.status_code == 404
    if not is404:
        pokemonJSON = pokemonpreJSON.json()
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
            type2=(
                None
                if len(pokemonJSON["types"]) < 2
                else pokemonJSON["types"][1]["type"].get("name")
            ),
        )
        availableMoves = pokemonJSON["moves"]
        for availableMove in availableMoves:
            number = re.findall(r"[0-9]{1,}(?=/$)", availableMove["move"]["url"])[0]
            appendMove = Moves[str(number)]
            tempPoke.addKnowableMove(appendMove)

        Pokemons.append(tempPoke)
        movesTotal += pokemonJSON["moves"].__len__()
        i += 1
        if i % 100 == 0:
            print(str(i) + ": " + pokemonJSON["name"])
    else:
        lastExisted = False

serialized_pokemon_list = [pokemon.serialize() for pokemon in Pokemons]
with open("data/pokemon_data.json", "w") as f:
    json.dump(serialized_pokemon_list, f, indent=4)
toc = time.time()
