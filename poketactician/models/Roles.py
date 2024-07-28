# https://www.smogon.com/dp/articles/pokemon_dictionary
from poketactician.models import Move
from poketactician.models.model_utils import process_items
from poketactician.models.Move import DamageClass
from poketactician.models.Types import PokemonType

from .Pokemon import Pokemon


def has_move(pokemon: Pokemon, moves: list) -> float:
    """
    Determines if a Pokemon has a specific move.

    Args:
        pokemon (Pokemon): The Pokemon to check.
        moves (list): The list of moves to check for.

    Returns:
        bool: True if the Pokemon has the move, False otherwise.
    """
    return any([move.name in moves for move in pokemon.learnt_moves]) * 1.0


def has_type(pokemon: Pokemon, types: list) -> float:
    """
    Determines if a Pokemon has a specific type.

    Args:
        pokemon (Pokemon): The Pokemon to check.
        types (list): The list of types to check for.

    Returns:
        bool: True if the Pokemon has the type, False otherwise.
    """
    return any([type in types for type in [pokemon.type1, pokemon.type2]]) * 1.0


def has_ability(pokemon: Pokemon, abilities: list) -> float:
    """
    Determines if a Pokemon has a specific ability.

    Args:
        pokemon (Pokemon): The Pokemon to check.
        abilities (list): The list of abilities to check for.

    Returns:
        bool: True if the Pokemon has the ability, False otherwise.
    """
    return (
        any(
            [
                ability in abilities
                for ability in [
                    pokemon.ability1,
                    pokemon.ability2,
                    pokemon.hiddenAbility,
                ]
            ]
        )
        * 1.0
    )


def has_good_stat(pokemon: Pokemon, stats: list) -> float:
    """
    Determines if a Pokemon has a specific stat above a certain threshold.

    Args:
        pokemon (Pokemon): The Pokemon to check.
        stats (list): The list of stats to check for.

    Returns:
        bool: True if the Pokemon has the stat above the threshold, False otherwise.
    """
    # If threshold needs to vary, create here a dictionary with the stat as key and the threshold as value.
    # If it needs to vary even more, update this t take a dicttionary with stat as key and threshold as value

    good_stat_threshold = 100
    stat_values = [getattr(pokemon, stat) / good_stat_threshold for stat in stats]
    return sum(stat_values) / len(stat_values)


def is_cleric(pokemon: Pokemon) -> float:
    """
    Determines if a Pokemon is a cleric.

    A Pokemon is considered a cleric if it knows a healing move.

    Args:
        pokemon (Pokemon): The Pokemon to check.

    Returns:
        bool: True if the Pokemon is a cleric, False otherwise.
    """
    return has_move(
        pokemon,
        [
            "heal-bell",
            "aromatherapy",
            "wish",
            "soft-boiled",
            "roost",
            "recover",
            "morning-sun",
            "moonlight",
            "synthesis",
            "shore-up",
            "slack-off",
            "rest",
        ],
    )


def is_dual_screener(pokemon: Pokemon) -> float:
    """
    Determines if a Pokemon is a dual screener.

    A Pokemon is considered a dual screener if it knows both Light Screen and Reflect.

    Args:
        pokemon (Pokemon): The Pokemon to check.

    Returns:
        bool: True if the Pokemon is a dual screener, False otherwise.
    """
    return has_move(pokemon, ["light-screen", "reflect"]) * has_move(pokemon, ["wish"])


def is_phazer(pokemon: Pokemon) -> float:
    """
    Determines if a Pokemon is a phazer.

    A Pokemon is considered a phazer if it knows moves that might make the opponent switch out.

    Args:
        pokemon (Pokemon): The Pokemon to check.

    Returns:
        bool: True if the Pokemon is a phazer, False otherwise.
    """
    return has_move(
        pokemon,
        ["roar", "whirlwind", "dragon-tail", "circle-throw", "haze", "perish-song"],
    )


def is_stallbreaker(pokemon: Pokemon) -> float:
    """
    Determines if a Pokemon is a stallbreaker.

    A Pokemon is considered a stallbreaker if it has moves that can break through defensive strategies.

    Args:
        pokemon (Pokemon): The Pokemon to check.

    Returns:
        bool: True if the Pokemon is a stallbreaker, False otherwise.
    """
    # TODO Make it so having high speed/immunities and other things makes it a better stallbreaker
    # Gliscor has all of the necessary tools to be an effective stallbreaker, in particular Taunt, Roost, high Speed, select immunities, and an excellent STAB type.
    return has_move(
        pokemon,
        [
            "taunt",
            "toxic",
            "will-o-wisp",
            "encore",
            "disable",
            "trick",
            "knock-off",
        ],
    )


def is_offensive_pivot(pokemon: Pokemon) -> float:
    """
    Determines if a Pokemon is an offensive pivot.

    A Pokemon is considered an offensive pivot if it has moves that can switch into attacks and pivot out.

    Args:
        pokemon (Pokemon): The Pokemon to check.

    Returns:
        bool: True if the Pokemon is an offensive pivot, False otherwise.
    """
    return has_move(
        pokemon,
        [
            "u-turn",
            "volt-switch",
            "baton-pass",
            "parting-shot",
            "flip-turn",
            "chilly-reception",
            "teleport",
        ],
    )


# TODO Add DefensivePivot


def is_physical_sweeper(pokemon: Pokemon) -> float:
    """
    Determines if a Pokemon is a physical sweeper.

    A Pokemon is considered a physical sweeper if it has high physical attack stats.

    Args:
        pokemon (Pokemon): The Pokemon to check.

    Returns:
        bool: True if the Pokemon is a physical sweeper, False otherwise.
    """
    # TODO See if it makes sense to check for physical stat-improving moves
    return (
        has_good_stat(pokemon, ["att"])
        * sum(
            [move.damage_class == DamageClass.PHYSICAL for move in pokemon.learnt_moves]
        )
        * 0.25
    )


def is_special_sweeper(pokemon: Pokemon) -> float:
    """
    Determines if a Pokemon is a special sweeper.

    A Pokemon is considered a special sweeper if it has high special attack stats.

    Args:
        pokemon (Pokemon): The Pokemon to check.

    Returns:
        bool: True if the Pokemon is a special sweeper, False otherwise.
    """
    # TODO See if it makes sense to check for special stat-improving moves
    return (
        has_good_stat(pokemon, ["spatt"])
        * sum(
            [move.damage_class == DamageClass.SPECIAL for move in pokemon.learnt_moves]
        )
        * 0.25
    )


def is_spinner(pokemon: Pokemon) -> float:
    """
    Determines if a Pokemon is a spinner.

    A Pokemon is considered a spinner if it knows a move that can remove entry hazards.

    Args:
        pokemon (Pokemon): The Pokemon to check.

    Returns:
        bool: True if the Pokemon is a spinner, False otherwise.
    """
    return has_move(pokemon, ["rapid-spin", "defog"])


def is_revenge_killer(pokemon: Pokemon) -> float:
    """
    Determines if a Pokemon is a revenge killer.

    A Pokemon is considered a revenge killer if it has high speed and priority moves.

    Args:
        pokemon (Pokemon): The Pokemon to check.

    Returns:
        bool: True if the Pokemon is a revenge killer, False otherwise.
    """
    # TODO Depends on opponent that it might be facing
    return (
        has_good_stat(pokemon, ["spe"])
        and any([move.priority > 0 for move in pokemon.learnt_moves]) * 1.0
    )


def is_hazard_setter(pokemon: Pokemon) -> float:
    """
    Determines if a Pokemon is a hazard setter.

    A Pokemon is considered a hazard setter if it knows a move that can set entry hazards.

    Args:
        pokemon (Pokemon): The Pokemon to check.

    Returns:
        bool: True if the Pokemon is a hazard setter, False otherwise.
    """
    return has_move(
        pokemon,
        ["stealth-rock", "spikes", "toxic-spikes", "sticky-web", "ceaseless-edge"],
    )


def is_spin_blocker(pokemon: Pokemon) -> float:
    """
    Determines if a Pokemon is a spin blocker.

    A Pokemon is considered a spin blocker if it is Ghost since Rapid Spin will fail.

    Args:
        pokemon (Pokemon): The Pokemon to check.

    Returns:
        bool: True if the Pokemon is a spin blocker, False otherwise.
    """
    return has_type(pokemon, [PokemonType.GHOST])


def is_stat_absorber_sleep(pokemon: Pokemon) -> float:
    """
    Determines if a Pokemon is a status absorber.

    A Pokemon is considered a status absorber if it is immune to status conditions.

    Args:
        pokemon (Pokemon): The Pokemon to check.

    Returns:
        bool: True if the Pokemon is a status absorber, False otherwise.
    """
    return has_move(pokemon, ["rest", "sleep-talk"])


def is_stat_absorber_poison(pokemon: Pokemon) -> float:
    """
    Determines if a Pokemon is a status absorber.

    A Pokemon is considered a status absorber if it is immune to status conditions.

    Args:
        pokemon (Pokemon): The Pokemon to check.

    Returns:
        bool: True if the Pokemon is a status absorber, False otherwise.
    """
    # TODO Add abilities like immunity and Poison Heal
    return has_type(pokemon, [PokemonType.POISON, PokemonType.STEEL])


def is_stat_absorber_burn(pokemon: Pokemon) -> float:
    """
    Determines if a Pokemon is a status absorber.

    A Pokemon is considered a status absorber if it is immune to status conditions.

    Args:
        pokemon (Pokemon): The Pokemon to check.

    Returns:
        bool: True if the Pokemon is a status absorber, False otherwise.
    """
    # TODO Add abilities like Water Veil, Water Bubble, Flash Fire, Guts, Magic Guard,
    return has_type(pokemon, [PokemonType.FIRE])


def is_stat_absorber_freeze(pokemon: Pokemon) -> float:
    """
    Determines if a Pokemon is a status absorber.

    A Pokemon is considered a status absorber if it is immune to status conditions.

    Args:
        pokemon (Pokemon): The Pokemon to check.

    Returns:
        bool: True if the Pokemon is a status absorber, False otherwise.
    """
    # TODO Add abilities like Magma Armor, Flame Body, Ice Body, Comatose or Purifying Salt, having flash fire,
    # is negative since it prevents fire-type moves from thawing the user
    # There are also partial helps like having Natural Care, Hydration, Shed Skin
    return has_type(pokemon, [PokemonType.ICE])


def is_stat_absorber_paralysis(pokemon: Pokemon) -> float:
    """
    Determines if a Pokemon is a status absorber.

    A Pokemon is considered a status absorber if it is immune to status conditions.

    Args:
        pokemon (Pokemon): The Pokemon to check.

    Returns:
        bool: True if the Pokemon is a status absorber, False otherwise.
    """
    # TODO Add abilities like Limber, Electric Surge, Electric Skin, Quick Feet, Guts, Magic Guard.
    # Being ground could also give something since most paralysis causing moves are electric
    return has_type(pokemon, [PokemonType.ELECTRIC])


def is_suicide_lead(pokemon: Pokemon) -> float:
    """
    Determines if a Pokemon is a suicide lead.

    A Pokemon is considered a suicide lead if it is designed to set up entry hazards and then faint quickly.

    Args:
        pokemon (Pokemon): The Pokemon to check.

    Returns:
        bool: True if the Pokemon is a suicide lead, False otherwise.
    """
    return (
        has_move(pokemon, ["stealth-rock", "spikes", "toxic-spikes", "sticky-web"])
        * has_move(
            pokemon,
            [
                "taunt",
            ],
        )
        * has_good_stat(pokemon, "spe")
    )


def is_tank(pokemon: Pokemon) -> float:
    """
    Determines if a Pokemon is a tank.

    A Pokemon is considered a tank if it has high defensive stats and can withstand attacks.

    Args:
        pokemon (Pokemon): The Pokemon to check.

    Returns:
        bool: True if the Pokemon is a tank, False otherwise.
    """
    return max(has_good_stat(pokemon, ["deff"]), has_good_stat(pokemon, ["spdeff"]))


def is_trapper(pokemon: Pokemon) -> float:
    """
    Determines if a Pokemon is a trapper.

    A Pokemon is considered a trapper if it has the ability to trap and eliminate opposing Pokemon.

    Args:
        pokemon (Pokemon): The Pokemon to check.

    Returns:
        bool: True if the Pokemon is a trapper, False otherwise.
    """
    # TODO Add logic to check for trapping moves or abilities
    return has_ability(pokemon, ["arena-trap", "shadow-tag", "magnet-pull"])


def is_reliable_recovery(pokemon: Pokemon) -> float:
    """
    Determines if a Pokemon has reliable recovery.

    A Pokemon is considered to have reliable recovery if it can recover HP consistently.

    Args:
        pokemon (Pokemon): The Pokemon to check.

    Returns:
        bool: True if the Pokemon has reliable recovery, False otherwise.
    """
    return has_move(
        pokemon,
        [
            "recover",
            "roost",
            "soft-boiled",
            "synthesis",
            "moonlight",
            "morning-sun",
            "shore-up",
            "slack-off",
        ],
    )


def is_wall(pokemon: Pokemon) -> float:
    """
    Determines if a Pokemon is a wall.

    A Pokemon is considered a wall if it has high defensive stats and can withstand attacks.

    Args:
        pokemon (Pokemon): The Pokemon to check.

    Returns:
        bool: True if the Pokemon is a wall, False otherwise.
    """
    return (
        is_tank(pokemon)
        * is_reliable_recovery(pokemon)
        * has_good_stat(pokemon, ["hp"])
    )
