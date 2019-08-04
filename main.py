class Pokemon:
    def __init__(self, name, hp, att, deff, spatt, spdeff, spe, type1, type2 = ""):
        self.name = name
        self.hp = hp
        self.att = att
        self.deff = deff
        self.spatt = spatt
        self.spdeff = spdeff
        self.spe = spe
        self.moves = []
        self.type1 = type1
        self.type2 = type2

    def addMove(self, move):
        self.moves += move

    def expectedAttacks(self):
        moves = self.moves
        expectedAttacks = []
        for move in moves:
            moveType = move.type
            movePower = move.power
            moveDamageClass = move.damageClass
            moveAccuracy = move.accuracy
            stab = 1.5 if (moveType == self.type1 or moveType == self.type2) else 1
        return expectedAttacks


class Move:
    def __init__(self, name, type, damageClass, power, accuracy):
        self.name = name
        self.type = type
        self.damageClass = damageClass
        self.power = power
        self.accuracy = accuracy/100
