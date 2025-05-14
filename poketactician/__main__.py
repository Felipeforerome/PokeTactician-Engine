import argparse

from poketactician.glob_var import alpha, beta
from poketactician.MOACO import MOACO
from poketactician.utils import define_objective_functions, load_pokemon


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="PokeTactician Engine")

    parser.register(
        "type",
        "split_numbers",
        lambda x: [int(a) for a in x.split(",")] if x != "." else [],
    )

    parser.add_argument(
        "--objfun",
        type=str,
        nargs="*",
        default=[
            "attack",
        ],
        help="Objective function",
    )
    parser.add_argument(
        "--poklistFile",
        type=str,
        default="data/pokemon_data.json",
        help="Path to the list of Pokémon",
    )
    parser.add_argument(
        "--poklistUrl",
        type=str,
        default=None,
        help="URL to the list of Pokémon (wrap in quotes if it contains special characters)",
    )
    parser.add_argument(
        "--preselected", type=int, default=0, help="Preselected Pokémon"
    )
    parser.add_argument(
        "--preselected_moves",
        type="split_numbers",
        nargs="*",
        default=[],
        help='Preselected moves, separate same pokemon moves with "," and separate different pokemon moves with " ". Example: --preselected_moves 1,2 3,4 5,6 7,8',
    )
    parser.add_argument("--roles", type=str, nargs="*", default=[], help="Roles")
    # TODO Generalist Strategy is broken
    parser.add_argument("--strategy", type=str, default=None, help="Strategy")

    args = parser.parse_args()

    if not args.poklistFile and not args.poklistUrl:
        parser.error("Either --poklistFile or --poklistUrl must be provided")

    for i in range(args.preselected):
        if len(args.preselected_moves[i]) > 4:
            parser.error(f"Preselected moves for Pokémon {i} cannot be more than 4")

    if len(args.preselected_moves) > args.preselected:
        parser.error(
            "--preselected_moves cannot have a larger length than --preselected"
        )
    elif len(args.preselected_moves) < args.preselected:
        args.preselected_moves.extend(
            [[]] * (args.preselected - len(args.preselected_moves))
        )

    return args


def main() -> None:
    args = parse_arguments()
    pok_list = load_pokemon(args.poklistFile, args.poklistUrl)

    objective_funcs = define_objective_functions(args.objfun, args.strategy, pok_list)

    for i in range(args.preselected):
        moves = args.preselected_moves[i]
        for j, move in enumerate(moves):
            pokemon = pok_list[i]
            move_index = next(
                (
                    index
                    for index, m in enumerate(pokemon.knowable_moves)
                    if int(m.id) == move
                ),
                None,
            )
            if move_index is not None:
                moves[j] = move_index
            else:
                raise ValueError(f"Move {move} not found in {pokemon.name} moves")

    # Create an instance of the MOACO class
    m_col = MOACO(
        400,
        objective_funcs,
        pok_list,
        list(range(args.preselected)),
        args.preselected_moves,
        alpha,
        beta,
        roles=args.roles,
    )
    m_col.optimize(iters=25)
    print(
        {
            "team": m_col.get_solution().serialize(),
            "objective_value": m_col.get_objective_value(),
        }
    )


if __name__ == "__main__":
    main()
