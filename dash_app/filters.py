def filterTypes(pokPreFilter, includedTypes, monoType):
    if len(includedTypes) > 0:
        pokList = (
            [
                pok
                for pok in pokPreFilter
                if (pok.type1 in includedTypes and pok.type2 is None)
            ]
            if monoType
            else [
                pok
                for pok in pokPreFilter
                if (pok.type1 in includedTypes or pok.type2 in includedTypes)
            ]
        )
    else:
        pokList = (
            [pok for pok in pokPreFilter if (pok.type2 is None)]
            if monoType
            else pokPreFilter
        )
    return pokList


# Function to check if an id is within any of the provided ranges
def filterGenerations(pokPreFilter, gens):
    def is_id_in_range(id, ranges):
        for start, end in ranges:
            if start <= id <= end:
                return True
        return False

    pokList = []
    if len(gens) < 1:
        pokList = pokPreFilter
    else:
        pokList = [obj for obj in pokPreFilter if is_id_in_range(obj.id, gens)]

    return pokList


# Function to filter legendaries and mythicals
def filterLegendaries(pokPreFilter, legendaries):
    if legendaries:
        pokList = pokPreFilter
    else:
        pokList = [pok for pok in pokPreFilter if not (pok.legendary or pok.mythical)]
    return pokList


# Function to remove mega evolutions
def removeMegas(pokPreFilter):
    return [pok for pok in pokPreFilter if not pok.mega]


# Function to remove battle only forms
def removeBattleOnly(pokPreFilter):
    return [pok for pok in pokPreFilter if not pok.battleOnly]


# Function to filter pokemon by games
def filterGames(pokPreFilter, games):
    if len(games) < 1:
        pokList = pokPreFilter
    else:
        pokList = [
            pok for pok in pokPreFilter if all(pok.games[game] == 1 for game in games)
        ]

    return pokList


# Function to unremove preselected pokemon
def splitPreSelected(pokPreFilter, pokPreSelected):
    preSelected = [pokPreFilter[i] for i in pokPreSelected]
    pokList = [
        pokPreFilter[i] for i in range(len(pokPreFilter)) if i not in pokPreSelected
    ]
    return preSelected, pokList


def handRemoved(pokPreFilter, handSelected=[]):
    pokList = [pok for pok in pokPreFilter if pok.id not in handSelected]
    return pokList
