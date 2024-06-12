from poketactician.glob_var import pokPreFilter


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
    moveSelectorDisabled = True
    moveList = [
        "------",
    ]
    if pok_id:
        pok = next((pokemon for pokemon in pokPreFilter if pokemon.id == pok_id), None)
        moveList = [
            {"value": i, "label": pok.knowableMoves[i].name.replace("-", " ").title()}
            for i in range(len(pok.knowableMoves))
            if pok.knowableMoves[i].id not in move_id
        ]
        moveSelectorDisabled = False
    return moveList, moveSelectorDisabled
