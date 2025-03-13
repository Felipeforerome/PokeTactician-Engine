from dataclasses import dataclass, field

from .Move import DamageClass, Move
from .Types import PokemonType


@dataclass
class Pokemon:
    """
    Represents a Pokemon with its attributes and moves.

    Attributes:
        id (int): The ID of the Pokemon.
        name (str): The name of the Pokemon.
        hp (int): The hit points of the Pokemon.
        att (int): The attack stat of the Pokemon.
        deff (int): The defense stat of the Pokemon.
        spatt (int): The special attack stat of the Pokemon.
        spdeff (int): The special defense stat of the Pokemon.
        spe (int): The speed stat of the Pokemon.
        type1 (PokemonType): The primary type of the Pokemon.
        type2 (PokemonType): The secondary type of the Pokemon.
        knowable_moves (list): The list of moves that the Pokemon can potentially learn.
        learntMoves (list): The list of moves that the Pokemon has learned.

    Methods:
        addKnowableMove(move): Adds a move to the list of knowable moves.
        from_json(data): Creates a Pokemon instance from JSON data.
        serialize(): Serializes the Pokemon instance into a dictionary.
        serialize_instance(): Serializes the Pokemon instance into a dictionary.
        teachMove(index): Adds a knowable move to the learnt moves list.
        overall_stats(): Calculates the sum of stats.
        current_power(): Calculates the current power of the Pokemon based on stats, attacks, and type.
        isRole(role_checker): Checks if the Pokemon fulfills a specific role.
    """

    id: int
    name: str
    hp: int
    att: int
    deff: int
    spatt: int
    spdeff: int
    spe: int
    type1: PokemonType
    type2: PokemonType
    knowable_moves: list = field(default_factory=list)
    learnt_moves: list = field(default_factory=list)

    def add_knowable_move(self, move: Move):
        """
        TODO This should be changed once more info about the moves is added, like effects or whatever. Right now it does reduce the decision space
        Adds move to list of knowable move if it has power greater to 0, its between the best 3 moves wtht that type and class
        :param move: Move to add
        """
        same_type_class = False
        same_type_class_moves = []
        num_type_class = 0
        if move.power == 0:
            return

        for known_move in self.knowable_moves:
            diff_type = known_move.type != move.type
            diff_class = known_move.damage_class != move.damage_class
            if diff_type or diff_class:
                continue
            else:
                num_type_class = num_type_class + 1
                same_type_class_moves.append(known_move)
                num_same_type_class_moves = same_type_class_moves.__len__()

                if num_same_type_class_moves == 3:
                    same_type_class = True
                    same_type_class_moves.sort(
                        key=lambda x: x.power * x.accuracy)
                    for known_type_class in same_type_class_moves:
                        increased_power_accuracy = (
                            known_type_class.power * known_type_class.accuracy
                            <= move.power * move.accuracy
                        )
                        increased_pp = known_move.pp * 0.75 <= move.pp

                        if increased_power_accuracy:
                            if (
                                increased_pp
                                or known_type_class.power + 30 <= move.power
                            ):
                                self.knowable_moves.remove(known_type_class)
                                self.knowable_moves.append(move)
                                return
                        else:
                            return

        if not same_type_class:
            self.knowable_moves.append(move)

    @classmethod
    def from_json(cls, data: dict):
        """
        Creates a Pokemon instance from JSON data.

        :param data: The JSON data representing the Pokemon.
        :return: The created Pokemon instance.
        """
        pokemon = cls(
            data["id"],
            data["name"],
            data["hp"],
            data["att"],
            data["deff"],
            data["spAtt"],
            data["spDeff"],
            data["spe"],
            PokemonType(data["type1"].lower()),
            PokemonType(data["type2"].lower()) if data["type2"] else None,
        )
        moves = [Move.from_json(move_data)
                 for move_data in data["knowableMoves"]]

        for move in moves:
            pokemon.add_knowable_move(move)
        return pokemon

    def serialize(self):
        """
        Serializes the Pokemon instance into a dictionary.

        :param pokemon: The Pokemon instance to serialize.
        :return: The serialized dictionary.
        """
        serialized_moves = [move.serialize() for move in self.knowable_moves]
        # Prevent empty move list
        if serialized_moves.__len__() == 0:
            serialized_moves.append(
                Move.from_json(
                    {
                        "id": "0",
                        "name": "no-move",
                        "type": "Normal",
                        "damage_class": "physical",
                        "power": 1,
                        "accuracy": 0,
                        "pp": 0,
                        "priority": 0,
                    }
                ).serialize()
            )
        return {
            "id": self.id,
            "name": self.name,
            "hp": self.hp,
            "att": self.att,
            "deff": self.deff,
            "spatt": self.spatt,
            "spdeff": self.spdeff,
            "spe": self.spe,
            "type1": self.type1.value,
            "type2": self.type2.value if self.type2 else None,
            "knowable_moves": serialized_moves,
        }

    def serialize_instance(self):
        """
        Serializes the Pokemon instance into a dictionary.

        :return: The serialized dictionary.
        """
        serialized_moves = [move.serialize() for move in self.learnt_moves]
        return {
            "id": self.id,
            "name": self.name,
            "hp": self.hp,
            "att": self.att,
            "deff": self.deff,
            "spatt": self.spatt,
            "spdeff": self.spdeff,
            "spe": self.spe,
            "type1": self.type1.value,
            "type2": self.type2.value if self.type2 else None,
            "mythical": self.mythical,
            "legendary": self.legendary,
            "battleOnly": self.battle_only,  # Include battleOnly attribute
            "mega": self.mega,  # Include battleOnly attribute
            "moves": serialized_moves
        }

    def teach_move(self, move_id: int):
        """
        Adds a knowable move to the learnt moves list.

        :param int: The index of the knowable move to teach.
        """
        if move_id == -1:
            return
        if len(self.learnt_moves) < 4:
            if (
                move_id != -1
                and self.knowable_moves[move_id].id != "0"
                and self.knowable_moves[move_id].id
                in [learnt_move.id for learnt_move in self.learnt_moves]
            ):
                raise ValueError("Can't teach the same move twice")
            self.learnt_moves += [self.knowable_moves[move_id]]
        else:
            raise ValueError("Can't teach more than 4 moves")

    def overall_stats(self):
        """
        Calculates the sum of stats.

        :return: The sum of stats.
        """
        return self.hp + self.att + self.deff + self.spatt + self.spdeff + self.spe

    def current_power(self):
        """
        Calculates the current power of the pokemon based on Stats, Attacks, and Type
        :return: Returns total power of the learned moves
        """
        current_power = 0
        for learned_move in self.learnt_moves:
            move_type = learned_move.type
            move_power = learned_move.power
            move_damage_class = learned_move.damage_class
            move_accuracy = learned_move.accuracy
            stab = 1.5 if (
                move_type == self.type1 or move_type == self.type2) else 1
            split = (
                self.att if (move_damage_class ==
                             DamageClass.PHYSICAL) else self.spatt
            )
            expected_power = (stab * move_power) * split * move_accuracy
            current_power += expected_power
        return current_power

    def is_role(self, role_checker: callable) -> bool:
        """
        Checks if the Pokemon fulfills a specific role.

        :param role_checker: A function that takes a Pokemon and returns True if the Pokemon fulfills a role.
        :return: True if the Pokemon fulfills the role, False otherwise.
        """
        return role_checker(self)
