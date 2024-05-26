class Move:
    def __init__(
        self,
        id: str,
        name: str,
        type: str,
        damageClass: str,
        power: int,
        accuracy: int,
        pp: int,
        priority: int,
    ):
        self.id = id
        self.name = name
        self.type = type
        self.damageClass = damageClass
        self.power = power if power is not None else 0
        self.accuracy = accuracy if accuracy is not None else 1
        self.pp = pp
        self.priority = priority

    @staticmethod
    def from_json(moveJSON):
        return Move(
            moveJSON["id"],
            moveJSON["name"],
            moveJSON["type"],
            moveJSON["damageClass"],
            moveJSON["power"],
            moveJSON["accuracy"],
            moveJSON["pp"],
            moveJSON["priority"],
        )

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "damageClass": self.damageClass,
            "power": self.power,
            "accuracy": self.accuracy,
            "pp": self.pp,
            "priority": self.priority,
        }
