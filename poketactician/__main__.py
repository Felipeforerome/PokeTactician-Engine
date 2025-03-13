import argparse
from poketactician.MOACO import MOACO
from poketactician.glob_var import alpha, beta
from poketactician.utils import load_pokemon_from_json, define_objective_functions


def parse_arguments() -> argparse.Namespace:

    parser = argparse.ArgumentParser(description='PokeTactician Engine')

    parser.register('type', 'split_numbers', lambda x: [
                    int(a) for a in x.split(',')])

    parser.add_argument('--objfun', type=str, nargs='*', default=["Attack",],
                        help='Objective function')
    parser.add_argument('--poklist', type=str, default="data/pokemon_data.json",
                        help='Path to the list of Pokémon')
    parser.add_argument('--preselected', type=int, default=0,
                        help='Preselected Pokémon')
    parser.add_argument('--preselected_moves', type='split_numbers', nargs='*', default=[],
                        help='Preselected moves')
    parser.add_argument('--roles', type=str, nargs='*', default=[],
                        help='Roles')
    # TODO Generalist Strategy is broken
    parser.add_argument('--strategy', type=str, nargs=1, default=None,
                        help='Strategy')

    args = parser.parse_args()

    if len(args.preselected_moves) > args.preselected:
        parser.error(
            "--preselected_moves cannot have a larger length than --preselected")
    elif len(args.preselected_moves) < args.preselected:
        args.preselected_moves.extend([[]] * (args.preselected -
                                              len(args.preselected_moves)))

    return args


def main() -> None:
    args = parse_arguments()

    pokemon_pre_filter = load_pokemon_from_json(args.poklist)
    pokemon_pre_filter = [
        pok for pok in pokemon_pre_filter if not pok.battle_only]
    pokemon_pre_filter = [pok for pok in pokemon_pre_filter if not pok.mega]
    pokemon_pre_filter = [
        pok for pok in pokemon_pre_filter if "totem" not in pok.name]
    pok_list = pokemon_pre_filter

    objective_funcs = define_objective_functions(
        args.objfun, args.strategy, pok_list)

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
    print({"team": m_col.get_solution(
    ).serialize(), "objective_value": m_col.get_objective_value()})


if __name__ == "__main__":
    main()
