import pytest

from poketactician.models.Move import DamageClass, Move
from poketactician.models.Pokemon import Pokemon
from poketactician.models.Roles import (
    has_ability,
    has_good_stat,
    has_move,
    has_type,
    is_cleric,
    is_dual_screener,
    is_hazard_setter,
    is_offensive_pivot,
    is_phazer,
    is_physical_sweeper,
    is_reliable_recovery,
    is_revenge_killer,
    is_special_sweeper,
    is_spin_blocker,
    is_spinner,
    is_stallbreaker,
    is_stat_absorber_burn,
    is_stat_absorber_freeze,
    is_stat_absorber_paralysis,
    is_stat_absorber_poison,
    is_stat_absorber_sleep,
    is_suicide_lead,
    is_tank,
    is_trapper,
    is_wall,
)
from poketactician.models.Types import PokemonType


@pytest.fixture
def sample_pokemon():
    return Pokemon(
        id="1",
        name="Sample Pokemon",
        type1=PokemonType.NORMAL,
        type2=None,
        hp=0,
        att=0,
        deff=0,
        spatt=0,
        spdeff=0,
        spe=0,
        mega=False,
        mythical=False,
        legendary=False,
        battle_only=False,
        games={"Red": 0},
        learnt_moves=[
            Move(
                id="1",
                type=PokemonType.FIRE,
                name="Move 1",
                damage_class=DamageClass.PHYSICAL,
                power=100,
                accuracy=1,
                pp=10,
                priority=0,
            ),
            Move(
                id="2",
                type=PokemonType.ELECTRIC,
                name="Move 2",
                damage_class=DamageClass.SPECIAL,
                power=100,
                accuracy=1,
                pp=10,
                priority=0,
            ),
        ],
    )


def test_has_move(sample_pokemon: Pokemon):
    assert has_move(sample_pokemon, ["Move 1"]) == 1.0
    assert has_move(sample_pokemon, ["Move 4"]) == 0.0


def test_has_type(sample_pokemon: Pokemon):
    assert has_type(sample_pokemon, [PokemonType.NORMAL]) == 1.0
    assert has_type(sample_pokemon, [PokemonType.FIRE]) == 0.0


def test_has_ability(sample_pokemon: Pokemon):
    assert has_ability(sample_pokemon, ["Sample Ability 1"]) == 1.0
    assert has_ability(sample_pokemon, ["Sample Ability 3"]) == 0.0


def test_has_good_stat(sample_pokemon: Pokemon):
    assert has_good_stat(sample_pokemon, ["att"]) == 0.0
    sample_pokemon.att = 100
    assert has_good_stat(sample_pokemon, ["att"]) == 1.0


def test_is_cleric(sample_pokemon: Pokemon):
    assert is_cleric(sample_pokemon) == 0.0
    sample_pokemon.add_knowable_move(
        Move.from_json(
            {
                "id": "273",
                "name": "wish",
                "type": "normal",
                "damage_class": "status",
                "power": 0,
                "accuracy": 0,
                "pp": 10,
                "priority": 0,
            }
        )
    )
    sample_pokemon.teach_move(0)
    assert is_cleric(sample_pokemon) == 1.0


def test_is_dual_screener(sample_pokemon: Pokemon):
    assert is_dual_screener(sample_pokemon) == 0.0
    sample_pokemon.add_knowable_move(
        Move.from_json(
            {
                "id": "273",
                "name": "wish",
                "type": "normal",
                "damage_class": "status",
                "power": 0,
                "accuracy": 0,
                "pp": 10,
                "priority": 0,
            }
        )
    )
    sample_pokemon.add_knowable_move(
        Move.from_json(
            {
                "id": "115",
                "name": "reflect",
                "type": "psychic",
                "damage_class": "status",
                "power": 0,
                "accuracy": 0,
                "pp": 20,
                "priority": 0,
            }
        )
    )
    sample_pokemon.teach_move(0)
    sample_pokemon.teach_move(1)
    assert is_dual_screener(sample_pokemon) == 1.0


def test_is_phazer(sample_pokemon: Pokemon):
    assert is_phazer(sample_pokemon) == 0.0
    sample_pokemon.add_knowable_move(
        Move.from_json(
            {
                "id": "114",
                "name": "haze",
                "type": "ice",
                "damage_class": "status",
                "power": 0,
                "accuracy": 0,
                "pp": 30,
                "priority": 0,
            }
        )
    )
    sample_pokemon.teach_move(0)
    assert is_phazer(sample_pokemon) == 1.0


def test_is_stallbreaker(sample_pokemon: Pokemon):
    assert is_stallbreaker(sample_pokemon) == 0.0
    sample_pokemon.add_knowable_move(
        Move.from_json(
            {
                "id": "269",
                "name": "taunt",
                "type": "dark",
                "damage_class": "status",
                "power": 0,
                "accuracy": 1.0,
                "pp": 20,
                "priority": 0,
            }
        )
    )
    sample_pokemon.teach_move(0)
    assert is_stallbreaker(sample_pokemon) == 1.0


def test_is_offensive_pivot(sample_pokemon: Pokemon):
    assert is_offensive_pivot(sample_pokemon) == 0.0
    sample_pokemon.add_knowable_move(
        Move.from_json(
            {
                "id": "521",
                "name": "volt-switch",
                "type": "electric",
                "damage_class": "special",
                "power": 70,
                "accuracy": 1.0,
                "pp": 20,
                "priority": 0,
            }
        )
    )
    sample_pokemon.teach_move(0)
    assert is_offensive_pivot(sample_pokemon) == 1.0


def test_is_physical_sweeper(sample_pokemon: Pokemon):
    assert is_physical_sweeper(sample_pokemon) == 0.00
    sample_pokemon.att = 100
    assert is_physical_sweeper(sample_pokemon) == 0.25


def test_is_special_sweeper(sample_pokemon: Pokemon):
    assert is_special_sweeper(sample_pokemon) == 0.00
    sample_pokemon.spatt = 100
    assert is_special_sweeper(sample_pokemon) == 0.25


def test_is_spinner(sample_pokemon: Pokemon):
    assert is_spinner(sample_pokemon) == 0.0
    sample_pokemon.add_knowable_move(
        Move.from_json(
            {
                "id": "229",
                "name": "rapid-spin",
                "type": "normal",
                "damage_class": "physical",
                "power": 50,
                "accuracy": 1.0,
                "pp": 40,
                "priority": 0,
            }
        )
    )
    sample_pokemon.teach_move(0)
    assert is_spinner(sample_pokemon) == 1.0


def test_is_revenge_killer(sample_pokemon: Pokemon):
    assert is_revenge_killer(sample_pokemon) == 0.0
    sample_pokemon.add_knowable_move(
        Move.from_json(
            {
                "id": "389",
                "name": "sucker-punch",
                "type": "dark",
                "damage_class": "physical",
                "power": 70,
                "accuracy": 1.0,
                "pp": 5,
                "priority": 1,
            }
        )
    )
    sample_pokemon.teach_move(0)
    assert is_revenge_killer(sample_pokemon) == 1.0


def test_is_hazard_setter(sample_pokemon: Pokemon):
    assert is_hazard_setter(sample_pokemon) == 0.0
    sample_pokemon.add_knowable_move(
        Move.from_json(
            {
                "id": "446",
                "name": "stealth-rock",
                "type": "rock",
                "damage_class": "status",
                "power": 0,
                "accuracy": 0,
                "pp": 20,
                "priority": 0,
            }
        )
    )
    sample_pokemon.teach_move(0)
    assert is_hazard_setter(sample_pokemon) == 1.0


def test_is_spin_blocker(sample_pokemon: Pokemon):
    assert is_spin_blocker(sample_pokemon) == 0.0
    sample_pokemon.type1 = PokemonType.GHOST
    assert is_spin_blocker(sample_pokemon) == 1.0


def test_is_stat_absorber_sleep(sample_pokemon: Pokemon):
    assert is_stat_absorber_sleep(sample_pokemon) == 0.0
    sample_pokemon.add_knowable_move(
        Move.from_json(
            {
                "id": "214",
                "name": "sleep-talk",
                "type": "normal",
                "damage_class": "status",
                "power": 0,
                "accuracy": 0,
                "pp": 10,
                "priority": 0,
            }
        )
    )
    sample_pokemon.teach_move(0)
    assert is_stat_absorber_sleep(sample_pokemon) == 1.0


def test_is_stat_absorber_poison(sample_pokemon: Pokemon):
    assert is_stat_absorber_poison(sample_pokemon) == 0.0
    sample_pokemon.type1 = PokemonType.POISON
    assert is_stat_absorber_poison(sample_pokemon) == 1.0


def test_is_stat_absorber_burn(sample_pokemon: Pokemon):
    assert is_stat_absorber_burn(sample_pokemon) == 0.0
    sample_pokemon.type1 = PokemonType.FIRE
    assert is_stat_absorber_burn(sample_pokemon) == 1.0


def test_is_stat_absorber_freeze(sample_pokemon: Pokemon):
    assert is_stat_absorber_freeze(sample_pokemon) == 0.0
    sample_pokemon.type1 = PokemonType.ICE
    assert is_stat_absorber_freeze(sample_pokemon) == 1.0


def test_is_stat_absorber_paralysis(sample_pokemon: Pokemon):
    assert is_stat_absorber_paralysis(sample_pokemon) == 0.0
    sample_pokemon.type1 = PokemonType.ELECTRIC
    assert is_stat_absorber_paralysis(sample_pokemon) == 1.0


def test_is_suicide_lead(sample_pokemon: Pokemon):
    assert is_suicide_lead(sample_pokemon) == 0.0
    sample_pokemon.add_knowable_move(
        Move.from_json(
            {
                "id": "446",
                "name": "stealth-rock",
                "type": "rock",
                "damage_class": "status",
                "power": 0,
                "accuracy": 0,
                "pp": 20,
                "priority": 0,
            }
        )
    )
    sample_pokemon.add_knowable_move(
        Move.from_json(
            {
                "id": "269",
                "name": "taunt",
                "type": "dark",
                "damage_class": "status",
                "power": 0,
                "accuracy": 1.0,
                "pp": 20,
                "priority": 0,
            }
        )
    )
    sample_pokemon.teach_move(0)
    sample_pokemon.teach_move(1)
    sample_pokemon.spe = 100
    assert is_suicide_lead(sample_pokemon) == 1.0


def test_is_tank(sample_pokemon: Pokemon):
    assert is_tank(sample_pokemon) == 0.0
    sample_pokemon.deff = 100
    assert is_tank(sample_pokemon) == 1.0


def test_is_trapper(sample_pokemon: Pokemon):
    assert is_trapper(sample_pokemon) == 0.0
    sample_pokemon.ability1 = "arena-trap"
    assert is_trapper(sample_pokemon) == 1.0


def test_is_reliable_recovery(sample_pokemon: Pokemon):
    assert is_reliable_recovery(sample_pokemon) == 0.0
    sample_pokemon.add_knowable_move(
        Move.from_json(
            {
                "id": "105",
                "name": "recover",
                "type": "normal",
                "damage_class": "status",
                "power": 0,
                "accuracy": 0,
                "pp": 5,
                "priority": 0,
            }
        )
    )
    sample_pokemon.teach_move(0)
    assert is_reliable_recovery(sample_pokemon) == 1.0


def test_is_wall(sample_pokemon: Pokemon):
    assert is_wall(sample_pokemon) == 0.0
    # meet "is_tank"
    sample_pokemon.deff = 100
    # meet "is_reliable_recovery"
    sample_pokemon.add_knowable_move(
        Move.from_json(
            {
                "id": "105",
                "name": "recover",
                "type": "normal",
                "damage_class": "status",
                "power": 0,
                "accuracy": 0,
                "pp": 5,
                "priority": 0,
            }
        )
    )
    sample_pokemon.teach_move(0)
    # meet the rest of the role
    sample_pokemon.hp = 100
    assert is_wall(sample_pokemon) == 1.0
