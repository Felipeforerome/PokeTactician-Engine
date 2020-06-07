def moveExactCounter(PokemonsList):
    """
    Count the number of pokemon that have X number of knowable attacks (until 36)
    :param PokemonsList: List of Pokemon to run through
    :return: Array containing the amount of pokemons that can learn X amount of moves
    """
    numberofmoves = []
    i_s = []
    i = 0
    while(i < 36):
        quantPok = 0
        for pok in PokemonsList:
            quantMoves = pok.knowableMoves.__len__()
            if(quantMoves == i):
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
    while(tempmove != 1):
        quantPok = 0
        for pok in PokemonsList:
            quantMoves = pok.knowableMoves.__len__()
            if(quantMoves >= i):
                quantPok = quantPok + 1
        numberofmoves.append(quantPok)
        i_s.append(i)
        i = i + 1
        tempmove = quantPok
    print(i_s)
    return numberofmoves

def currentPower(self):
    """
    Calculates the current power of the pokemon based on Stats, Attacks, and Type
    :return: Returns total power of the learned moves
    """
    currentPower = 0
    if self.learnedMoves.__len__() <1:
        raise Exception("This Pokemon Needs To Learn A Move")
    else:
        for learnedMove in self.learnedMoves:
            moveType = learnedMove.type
            movePower = learnedMove.power
            moveDamageClass = learnedMove.damageClass
            moveAccuracy = learnedMove.accuracy
            stab = 1.5 if (moveType == self.type1 or moveType == self.type2) else 1
            split = self.att if (moveDamageClass == "physical") else self.spatt
            expectedPower = (stab * movePower) * split * moveAccuracy
            currentPower += expectedPower
        return currentPower