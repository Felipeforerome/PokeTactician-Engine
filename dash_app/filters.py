from poketactician.models.Pokemon import Pokemon
from poketactician.models.Types import PokemonType


def filter_types(
    pokemon_pre_filter: list[Pokemon],
    included_types: list[PokemonType],
    mono_Type: bool,
):
    if len(included_types) > 0:
        included_types = [PokemonType(includedType) for includedType in included_types]
        pokemon_list = (
            [
                pok
                for pok in pokemon_pre_filter
                if (pok.type1 in included_types and pok.type2 is None)
            ]
            if mono_Type
            else [
                pok
                for pok in pokemon_pre_filter
                if (pok.type1 in included_types or pok.type2 in included_types)
            ]
        )
    else:
        pokemon_list = (
            [pok for pok in pokemon_pre_filter if (pok.type2 is None)]
            if mono_Type
            else pokemon_pre_filter
        )
    return pokemon_list


# Function to check if an id is within any of the provided ranges
def filter_generations(pokemon_pre_filter: list[Pokemon], generations: list):
    def is_id_in_range(id, ranges):
        for start, end in ranges:
            if start <= id <= end:
                return True
        return False

    pokList = []
    if len(generations) < 1:
        pokList = pokemon_pre_filter
    else:
        pokList = [
            obj for obj in pokemon_pre_filter if is_id_in_range(obj.id, generations)
        ]

    return pokList


# Function to filter legendaries and mythicals
def filter_legendaries(pokemon_pre_filter: list[Pokemon], legendaries: bool):
    if legendaries:
        pokemon_list = pokemon_pre_filter
    else:
        pokemon_list = [
            pok for pok in pokemon_pre_filter if not (pok.legendary or pok.mythical)
        ]
    return pokemon_list


# Function to remove mega evolutions
def remove_megas(pokemon_pre_filter: list[Pokemon]):
    return [pok for pok in pokemon_pre_filter if not pok.mega]


# Function to remove battle only forms
def remove_battle_only(pokemon_pre_filter: list[Pokemon]):
    return [pok for pok in pokemon_pre_filter if not pok.battle_only]


# Function to filter pokemon by games
def filter_games(pokemon_pre_filter: list[Pokemon], games: list[str]):
    if len(games) < 1:
        pokemon_list = pokemon_pre_filter
    else:
        pokemon_list = [
            pok
            for pok in pokemon_pre_filter
            if all(pok.games[game] == 1 for game in games)
        ]

    return pokemon_list


# Function to unremove preselected pokemon
def split_preselected(
    pokemon_pre_filter: list[Pokemon], preselected_pokemon: list[int]
):
    preselected = [pokemon_pre_filter[i] for i in preselected_pokemon]
    pokemon_list = [
        pokemon_pre_filter[i]
        for i in range(len(pokemon_pre_filter))
        if i not in preselected_pokemon
    ]
    return preselected, pokemon_list


def remove_totems(pokemon_pre_filter: list[Pokemon]):
    return [pok for pok in pokemon_pre_filter if "totem" not in pok.name]


def hand_removed(pokemon_pre_filter: list[Pokemon], hand_selected: list = []):
    pokemon_list = [pok for pok in pokemon_pre_filter if pok.id not in hand_selected]
    return pokemon_list
