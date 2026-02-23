import random
import argparse
from rich import print
from rich.progress import Progress
from typing import Dict, List
from statistics import mean
from dataclasses import dataclass
from game2048 import Direction, Game2048
from solvers import Solver, build_solvers
from multiprocessing import Pool, cpu_count

progress = Progress()


@dataclass
class GameResult:
    score: int
    win: bool
    max_tile: int
    moves: int
    move_counts_by_direction: Dict[str, int]


def run_game(params):
    return play_game(*params)


def play_game(
    solver: Solver, seed: int, board_size: int = 4, win_tile: int = 2048
) -> GameResult:
    game = Game2048(size=board_size, win_tile=win_tile, rng=random.Random(seed))
    while not game.is_game_over() and not game.is_win():
        move = solver.choose_move(game)
        moved = game.move(move)
        if not moved:
            # Fallback to any valid move (rare for some heuristics)
            valid = game.valid_moves()
            if not valid:
                break
            game.move(valid[0])

    return GameResult(
        score=game.score,
        win=game.is_win(),
        max_tile=game.max_tile(),
        moves=game.move_count,
        move_counts_by_direction=game.move_counts_by_direction,
    )


def summarize(results: List[GameResult]) -> Dict[str, float]:
    wins = sum(1 for r in results if r.win)
    losses = len(results) - wins
    direction_totals = {
        d: sum(r.move_counts_by_direction[d] for r in results) for d in Direction
    }
    total_moves = sum(r.moves for r in results)

    return {
        "best_score": max(r.score for r in results),
        "worst_score": min(r.score for r in results),
        "avg_score": mean(r.score for r in results),
        "wins": wins,
        "losses": losses,
        "avg_max_tile": mean(r.max_tile for r in results),
        "avg_moves_total": mean(r.moves for r in results),
        **{f"avg_moves_{d}": (direction_totals[d] / len(results)) for d in Direction},
        "total_moves": total_moves,
    }


def print_summary(solver_name: str, summary: Dict[str, float], games: int) -> None:
    print(f"\n=== Solver: {solver_name} ({games} her) ===")
    print(f"Nejlepší skóre: {summary['best_score']}")
    print(f"Nejhorší skóre: {summary['worst_score']}")
    print(f"Průměrné skóre: {summary['avg_score']:.2f}")
    print(f"Výhry/Prohry: {int(summary['wins'])}/{int(summary['losses'])}")
    print(f"Průměrná max buňka: {summary['avg_max_tile']:.1f}")
    print(f"Průměrný počet tahů (celkem): {summary['avg_moves_total']:.1f}")
    print(
        "Průměrný počet tahů podle směru: "
        + ", ".join(f"{d}={summary[f'avg_moves_{d}']:.1f}" for d in Direction)
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="2048 solver experiment runner")
    parser.add_argument("--games", type=int, default=10, help="Počet her na solver")
    parser.add_argument(
        "--seed",
        type=int,
        default=random.randint(0, 1000),
        help="Seed pro reprodukovatelnost",
    )
    parser.add_argument(
        "--board-size", type=int, default=4, help="Velikost hrací plochy"
    )
    parser.add_argument(
        "--win-tile", type=int, default=2048, help="Cílová hodnota buňky"
    )
    args = parser.parse_args()

    solvers = build_solvers(args.seed)

    with progress:
        with Pool(processes=cpu_count()) as pool:
            for solver in solvers:
                task_id = progress.add_task(solver.name, start=False, total=args.games)
                game_args = [
                    (
                        solver,
                        args.seed + game_idx,
                        args.board_size,
                        args.win_tile,
                    )
                    for game_idx in range(args.games)
                ]

                results = []
                for result in pool.imap(run_game, game_args):
                    results.append(result)
                    progress.advance(task_id)

                progress.stop_task(task_id)
                print_summary(solver.name, summarize(results), args.games)


if __name__ == "__main__":
    main()
