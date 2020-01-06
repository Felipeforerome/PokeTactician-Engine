class Move:
    def __init__(self, name, type, damageClass, power, accuracy, pp, priority):
        self.name = name
        self.type = type
        self.damageClass = damageClass
        self.power = power
        self.accuracy = accuracy/100
        self.pp = pp
        self.priority = priority