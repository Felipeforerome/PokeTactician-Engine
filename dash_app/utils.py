import re

from poketactician.glob_var import pok_pre_filter
from poketactician.models import Roles


def generate_move_list_and_selector_status(
    pok_id: int, move_id: list[int] = []
) -> tuple[list[dict] | list[str], bool]:
    """
    Generates a move list and selector status based on the provided Pokemon ID and move ID.

    Args:
        pok_id (int): The ID of the Pokemon.
        move_id (list[int], optional): The list of move IDs. Defaults to [].

    Returns:
        tuple[list[dict[str, Any]] | list[str], bool]: A tuple containing the move list and selector status.
            - moveList (list[dict[str, Any]] | list[str]): The generated move list. Each move is represented as a dictionary with 'value' and 'label' keys.
            - moveSelectorDisabled (bool): The status of the move selector. True if disabled, False otherwise.
    """
    move_selector_disabled = True
    move_list = [
        "------",
    ]
    if pok_id:
        pok = next(
            (pokemon for pokemon in pok_pre_filter if pokemon.id == pok_id), None
        )
        move_list = [
            {"value": i, "label": pok.knowable_moves[i].name.replace("-", " ").title()}
            for i in range(len(pok.knowable_moves))
            if i not in move_id
        ]
        move_selector_disabled = False
    return move_list, move_selector_disabled


def generate_roles_list() -> list:
    return [
        {
            "value": role.lower().replace(" ", "_"),
            "label": " "
            + re.sub(r"(?<=[a-z])(?=[A-Z])", " ", role[3:]).title().replace("_", " "),
        }
        for role in dir(Roles)
        if role.startswith("is_")
    ]
