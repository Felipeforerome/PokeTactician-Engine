import numpy as np

from .glob_var import moves
from .models.Pokemon import Pokemon
from .models.Team import Team
from .models.Types import typeChart, typeOrder


def moveExactCounter(PokemonsList):
    """
    Count the number of pokemon that have X number of knowable attacks (until 36)
    :param PokemonsList: List of Pokemon to run through
    :return: Array containing the amount of pokemons that can learn X amount of moves
    """
    numberofmoves = []
    i_s = []
    i = 0
    while i < 36:
        quantPok = 0
        for pok in PokemonsList:
            quantMoves = pok.knowableMoves.__len__()
            if quantMoves == i:
                quantPok = quantPok + 1
        numberofmoves.append(quantPok)
        i_s.append(i)
        i = i + 1
    print(i_s)
    return numberofmoves


def moveTotalCounter(PokemonsList):
    """
    Count the number of pokemon that have at least X number of knowable attacks (until 36)
    :param PokemonsList: List of Pokemon to run through
    :return: Array containing the amount of pokemon that can learn at least X amount of moves
    """
    numberofmoves = []
    i_s = []
    tempmove = None
    i = 0
    while tempmove != 1:
        quantPok = 0
        for pok in PokemonsList:
            quantMoves = pok.knowableMoves.__len__()
            if quantMoves >= i:
                quantPok = quantPok + 1
        numberofmoves.append(quantPok)
        i_s.append(i)
        i = i + 1
        tempmove = quantPok
    print(i_s)
    return numberofmoves


def getLearnedMoves(pokemonList, pok, ids):
    # TODO Handle -1 in ids because it has no attack (Like Ditto)
    temp = []
    for id in ids:
        if id != -1:
            temp.append(pokemonList[pok[0]].knowableMoves[id])
    return temp


def getWeakness(pok):
    weakness = typeChart[:, typeOrder.index(pok.type1)]
    try:
        weakness2 = typeChart[:, typeOrder.index(pok.type2)]
        weakness = np.multiply(weakness, weakness2)
    except:
        pass

    return weakness


def getMoveWeakness(pok, pokMoves, pokList):
    weakness = np.ones(18)
    for move in pokMoves:
        if move == -1:
            pass
        else:
            moveType = moves.get(pokList[pok].knowableMoves[move].id).type
            weakness = np.multiply(weakness, typeChart[:, typeOrder.index(moveType)])
            weakness = np.multiply(weakness, getWeakness(pokList[pok]))
            weakness = [weak if weak <= 256 else 512 for weak in weakness]
    return weakness


def hoyerSparseness(x):
    k = x.__len__()
    value = (np.sqrt(k) - ((np.linalg.norm(x, 1)) / (np.linalg.norm(x, 2)))) / (
        np.sqrt(k) - 1
    )
    return value


def getTeamNames(team, pokList):
    for pok in team:
        print(pokList[pok[0]].name)


# Add feature to choose cooperation algorithms
def dominatedCandSet(candSets, objFuns):
    """
    Performs multi-objective optimization using a cooperative colony approach.
    The function operates as follows:
    1. Combine all candidate solutions from different sets into one 'totalCandSet'.
    2. Evaluate each candidate solution in 'totalCandSet' against multiple objective functions.
    3. Normalize the objective function values by dividing them by their maximum value.
    4. Create a dominance vector to represent the overall dominance of solutions.
    5. Identify a subset of candidate solutions that exhibit the highest dominance across multiple objectives.

    Args:
    - candSets (list): A list of candidate sets, each containing potential solutions to the optimization problem.
    - objFuns (list): A list of objective functions representing different objectives to optimize.

    Returns:
    - list: A subset of candidate solutions from the input sets that dominate across multiple objectives.
    """

    totalCandSet = []
    candSetObjs = []
    for i in candSets:
        totalCandSet += i

    for j in objFuns:
        candSetObjsTemp = np.array(list(map(j, totalCandSet)))
        candSetObjs += [candSetObjsTemp / (candSetObjsTemp.max())]

    dominanceVector = np.ones(totalCandSet.__len__())

    for x in candSetObjs:
        dominanceVector = np.multiply(dominanceVector, x)

    dominatedCandSet = [
        x
        for _, x in sorted(
            zip(dominanceVector, totalCandSet), key=lambda pair: pair[0], reverse=True
        )
    ][0 : int(dominanceVector.__len__() / candSets.__len__())]

    return dominatedCandSet
