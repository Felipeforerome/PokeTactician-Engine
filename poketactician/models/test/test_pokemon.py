from unittest.mock import Mock

import pytest

from poketactician.models.Move import Move
from poketactician.models.Pokemon import Pokemon
from poketactician.models.Types import PokemonType


def test_pokemon_from_json() -> None:
    """
    Test case for the `Pokemon.from_json` method.

    This test case verifies that the `Pokemon.from_json` method correctly creates a `Pokemon` object from a JSON data
    dictionary.

    The test checks that the attributes of the created `Pokemon` object match the values specified in the JSON data.

    Raises:
        AssertionError: If any of the assertions fail.
    """
    pokemon_json_data = {
        "id": 25,
        "name": "Pikachu",
        "hp": 35,
        "att": 55,
        "deff": 40,
        "spatt": 50,
        "spdeff": 50,
        "spe": 90,
        "type1": "electric",
        "type2": None,
        "mythical": False,
        "legendary": False,
        "battleOnly": False,
        "mega": False,
        "games": ["Red", "Blue", "Yellow"],
        "knowable_moves": [
            {
                "id": "1",
                "name": "thunder-shock",
                "type": "electric",
                "damage_class": "special",
                "power": 40,
                "accuracy": 1,
                "pp": 30,
                "priority": 0,
            },
            {
                "id": "2",
                "name": "quick-attack",
                "type": "normal",
                "damage_class": "physical",
                "power": 40,
                "accuracy": 1,
                "pp": 30,
                "priority": 1,
            },
        ],
    }

    pokemon = Pokemon.from_json(pokemon_json_data)

    assert pokemon.id == 25
    assert pokemon.name == "Pikachu"
    assert pokemon.hp == 35
    assert pokemon.att == 55
    assert pokemon.deff == 40
    assert pokemon.spatt == 50
    assert pokemon.spdeff == 50
    assert pokemon.spe == 90
    assert pokemon.type1 == PokemonType("electric")
    assert pokemon.type2 is None
    assert pokemon.mythical is False
    assert pokemon.legendary is False
    assert pokemon.battle_only is False
    assert pokemon.mega is False
    assert pokemon.games == ["Red", "Blue", "Yellow"]
    assert len(pokemon.knowable_moves) == 2
    assert pokemon.knowable_moves[0].id == "1"
    assert pokemon.knowable_moves[0].name == "thunder-shock"
    assert pokemon.knowable_moves[1].id == "2"
    assert pokemon.knowable_moves[1].name == "quick-attack"


@pytest.fixture
def pokemon_fixture() -> Pokemon:
    """
    Creates a Pokemon object using the provided JSON data.

    Returns:
        A Pokemon object initialized with the data from the JSON.
    """
    pokemon_json_data = {
        "id": 25,
        "name": "Pikachu",
        "hp": 35,
        "att": 55,
        "deff": 40,
        "spatt": 50,
        "spdeff": 50,
        "spe": 90,
        "type1": "electric",
        "type2": None,
        "mythical": False,
        "legendary": False,
        "battleOnly": False,
        "mega": False,
        "games": ["Red", "Blue", "Yellow"],
        "knowable_moves": [
            {
                "id": "1",
                "name": "thunder-shock",
                "type": "electric",
                "damage_class": "special",
                "power": 40,
                "accuracy": 1,
                "pp": 30,
                "priority": 0,
            },
            {
                "id": "2",
                "name": "quick-attack",
                "type": "normal",
                "damage_class": "physical",
                "power": 40,
                "accuracy": 1,
                "pp": 30,
                "priority": 1,
            },
        ],
    }

    pokemon = Pokemon.from_json(pokemon_json_data)
    return pokemon


def test_add_knowable_move_new_damaging(pokemon_fixture: Pokemon) -> None:
    """
    Test case to verify adding a new damaging move, of higher expected power, to a Pokemon's knowable moves does add it.

    Args:
        pokemon_fixture (Pokemon): The Pokemon object to test.

    Returns:
        None
    """
    move_json_data = {
        "id": "3",
        "name": "thunder-bolt",
        "type": "electric",
        "damage_class": "special",
        "power": 90,
        "accuracy": 1,
        "pp": 15,
        "priority": 0,
    }
    move = Move.from_json(move_json_data)
    pokemon_fixture.add_knowable_move(move)
    assert len(pokemon_fixture.knowable_moves) == 3


def test_add_knowable_move_non_damaging(pokemon_fixture: Pokemon) -> None:
    """
    Test case to verify adding a non-damaging move to a Pokemon's knowable moves doen't add it.

    Args:
        pokemon_fixture (Pokemon): The Pokemon instance to test.

    Returns:
        None
    """
    move_json_data = {
        "id": "4",
        "name": "test_move",
        "type": "electric",
        "damage_class": "status",
        "power": 0,
        "accuracy": 1,
        "pp": 20,
        "priority": 0,
    }
    move = Move.from_json(move_json_data)
    pokemon_fixture.add_knowable_move(move)
    assert len(pokemon_fixture.knowable_moves) == 2
    assert pokemon_fixture.knowable_moves[-1].id != "4"


def test_add_knowable_move_better_damaging(pokemon_fixture: Pokemon) -> None:
    """
    Test case to verify the behavior of the `add_knowable_move` method when adding a better damaging move.

    Args:
        pokemon_fixture (Pokemon): The Pokemon instance to test.

    Returns:
        None
    """
    move_json_data = {
        "id": "5",
        "name": "test_move",
        "type": "electric",
        "damage_class": "status",
        "power": 100,
        "accuracy": 1,
        "pp": 20,
        "priority": 0,
    }
    move = Move.from_json(move_json_data)
    pokemon_fixture.add_knowable_move(move)
    assert pokemon_fixture.knowable_moves[-1].id == "5"


# TODO Finish creating tests for add_knoable_moves


def test_teach_move(pokemon_fixture: Pokemon) -> None:
    """
    Test the `teach_move` method of the `Pokemon` class.

    This test verifies that the `teach_move` method correctly adds a move to the
    `learnt_moves` list of the `Pokemon` instance.

    Args:
        pokemon_fixture (Pokemon): The `Pokemon` instance to test.

    Returns:
        None
    """
    pokemon_fixture.teach_move(0)
    assert len(pokemon_fixture.learnt_moves) == 1


def test_too_many_teach_moves(pokemon_fixture: Pokemon) -> None:
    """
    Test case to verify that an error is raised when trying to teach more moves than the maximum allowed.

    Args:
        pokemon_fixture (Pokemon): The Pokemon instance to test.

    Returns:
        None
    """
    move_json_data_3 = {
        "id": "3",
        "name": "test_move",
        "type": "grass",
        "damage_class": "special",
        "power": 90,
        "accuracy": 1,
        "pp": 15,
        "priority": 0,
    }
    move_json_data_4 = {
        "id": "4",
        "name": "test_move",
        "type": "fire",
        "damage_class": "special",
        "power": 90,
        "accuracy": 1,
        "pp": 15,
        "priority": 0,
    }
    move_json_data_5 = {
        "id": "5",
        "name": "test_move",
        "type": "poison",
        "damage_class": "special",
        "power": 90,
        "accuracy": 1,
        "pp": 15,
        "priority": 0,
    }
    move_3 = Move.from_json(move_json_data_3)
    pokemon_fixture.add_knowable_move(move_3)
    move_4 = Move.from_json(move_json_data_4)
    pokemon_fixture.add_knowable_move(move_4)
    move_5 = Move.from_json(move_json_data_5)
    pokemon_fixture.add_knowable_move(move_5)
    pokemon_fixture.teach_move(0)
    pokemon_fixture.teach_move(1)
    pokemon_fixture.teach_move(2)
    pokemon_fixture.teach_move(3)
    with pytest.raises(ValueError):
        pokemon_fixture.teach_move(4)


def test_teach_same_move_multiple(pokemon_fixture: Pokemon) -> None:
    """
    Test that teaching the same move multiple times raises a ValueError.

    Args:
        pokemon_fixture (Pokemon): The Pokemon instance to test.

    Returns:
        None
    """
    pokemon_fixture.teach_move(0)
    with pytest.raises(ValueError):
        pokemon_fixture.teach_move(0)


def test_overall_stats(pokemon_fixture: Pokemon) -> None:
    """
    Test case to verify the overall_stats property of the Pokemon class.

    Args:
        pokemon_fixture (Pokemon): The Pokemon instance to be tested.

    Returns:
        None
    """
    assert pokemon_fixture.overall_stats == 320


def test_current_power(pokemon_fixture: Pokemon) -> None:
    """
    Test case to verify the current power of a Pokemon.

    Args:
        pokemon_fixture (Pokemon): The Pokemon object to be tested.

    Returns:
        None
    """
    pokemon_fixture.teach_move(0)
    print(pokemon_fixture.learnt_moves)
    assert pokemon_fixture.current_power == 3000


def test_role(pokemon_fixture: Pokemon) -> None:
    """
    Test the `isRole` method of the `Pokemon` class.

    Args:
        pokemon_fixture (Pokemon): An instance of the `Pokemon` class.

    Returns:
        None
    """

    mock_role = Mock(return_value=True)

    result = pokemon_fixture.is_role(mock_role)
    mock_role.assert_called_once_with(pokemon_fixture)
    assert result == True

    mock_role.return_value = False
    result = pokemon_fixture.is_role(mock_role)
    mock_role.assert_called_with(pokemon_fixture)
    assert result == False
