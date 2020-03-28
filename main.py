#Query Database

import requests

from models.Pokemon import Pokemon
from models.Move import Move
import pickle
import re
import time

tic = time.time()
i = 1
j = 1
movesTotal = 0
Pokemons = []
Moves = {}
lastMove = True
recalculateMoves = False

if(recalculateMoves):
    while(lastMove):
        movepreJSON = requests.get('http://127.0.0.1:8000/api/v2/move/'+str(j))
        is404 = movepreJSON.status_code == 404
        if(not is404):
            moveJSON = movepreJSON.json()
            tempMove = Move(
                moveJSON['name'],
                moveJSON['type']['name'],
                moveJSON['damage_class']['name'],
                moveJSON['power'],
                moveJSON['accuracy'],
                moveJSON['pp'],
                moveJSON['priority']
            )
            Moves[str(j)] = tempMove
            j += 1
        else:
            lastMove = False

    with open("Moves.pkl", "wb") as f:
        pickle.dump(Moves, f)
else:
    with open("Moves.pkl", "rb") as f:
        Moves = pickle.load(f)


lastExisted = True
while (lastExisted):
    pokemonpreJSON = requests.get('http://127.0.0.1:8000/api/v2/pokemon/'+str(i))
    is404 = pokemonpreJSON.status_code == 404
    if(not is404):
        pokemonJSON = pokemonpreJSON.json()
        tempPoke = Pokemon(
            pokemonJSON['name'],
            pokemonJSON['stats'][0]['base_stat'],
            pokemonJSON['stats'][1]['base_stat'],
            pokemonJSON['stats'][2]['base_stat'],
            pokemonJSON['stats'][3]['base_stat'],
            pokemonJSON['stats'][4]['base_stat'],
            pokemonJSON['stats'][5]['base_stat'],
            pokemonJSON['types'][0]['type'].get('name'),
            type2= None if len(pokemonJSON['types'])<2 else pokemonJSON['types'][1]['type'].get('name')
        )
        availableMoves = pokemonJSON['moves']
        for availableMove in availableMoves:
            number = re.findall(r'[0-9]{1,}(?=/$)', availableMove['move']['url'])[0]
            appendMove = Moves[str(number)]
            tempPoke.addKnowableMove(appendMove)

        Pokemons.append(tempPoke)
        movesTotal += pokemonJSON['moves'].__len__()
        i+=1
    else:
        lastExisted = False

toc = time.time()


print(toc-tic)