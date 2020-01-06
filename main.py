#Query Database

import requests

from models.Pokemon import Pokemon
import pickle

i = 1
movesTotal = 0
Pokemons = []
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
        Pokemons.append(tempPoke)
        movesTotal += pokemonJSON['moves'].__len__()
        i+=1
    else:
        lastExisted = False

print(movesTotal/i)