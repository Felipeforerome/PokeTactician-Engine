import pytest

from poketactician.models.Move import DamageClass, Move
from poketactician.models.Types import PokemonType


def test_move_from_json() -> None:
    move_json_data = {
        "id": "520",
        "name": "grass-pledge",
        "type": "grass",
        "damage_class": "special",
        "power": 0.8,
        "accuracy": 1,
        "pp": 10,
        "priority": 0,
    }
    move = Move.from_json(move_json_data)
    assert move.id == "520"
    assert move.name == "grass-pledge"
    assert move.type == PokemonType("grass")
    assert move.damage_class == DamageClass("special")
    assert move.power == 0.8
    assert move.accuracy == 1
    assert move.pp == 10
    assert move.priority == 0


@pytest.fixture
def move_fixture() -> Move:
    move_json_data = {
        "id": "520",
        "name": "grass-pledge",
        "type": "grass",
        "damage_class": "special",
        "power": 0.8,
        "accuracy": 1,
        "pp": 10,
        "priority": 0,
    }
    move = Move.from_json(move_json_data)
    return move


def test_move_expected_power(move_fixture: Move) -> None:
    """
    Test case to verify the expected power of a move.

    Args:
        move_fixture (Move): The move object to be tested.

    Returns:
        None
    """
    assert move_fixture.expected_power == 0.8


def test_move_serialize(move_fixture: Move) -> None:
    """
    Test case to verify the serialization of a move.

    Args:
        move_fixture (Move): The move object to be tested.

    Returns:
        None
    """
    move_serialized = move_fixture.serialize()
    assert move_serialized == {
        "id": "520",
        "name": "grass-pledge",
        "type": "grass",
        "damage_class": "special",
        "power": 0.8,
        "accuracy": 1,
        "pp": 10,
        "priority": 0,
    }


########### Intergation Test ###########
import json


@pytest.fixture
def test_move_from_db_query() -> Move:
    with open("data/move_data.json", "r") as json_file:
        data = json.load(json_file)
        move_json_data = next(iter(data.values()))
        move = Move.from_json(move_json_data)
    return move
