import math
import random
from typing import List
from dataclasses import dataclass
from abc import ABC, abstractmethod
from game2048 import Direction, Game2048


def snakeHeuristic(game: Game2048) -> float:
    snake = [[0, 1, 2, 3], [7, 6, 5, 4], [8, 9, 10, 11], [15, 14, 13, 12]]
    score = 0
    for r in range(game.size):
        for c in range(game.size):
            value = game.board[r][c]
            score += value * snake[r][c]
    return score


class Solver(ABC):
    name: str

    @abstractmethod
    def choose_move(self, game: Game2048) -> Direction:
        raise NotImplementedError


@dataclass
class RandomSolver(Solver):
    rng: random.Random
    name: str = "random"

    def choose_move(self, game: Game2048) -> Direction:
        valid = game.valid_moves()
        return self.rng.choice(valid)


@dataclass
class PriorityCornerSolver(Solver):
    name: str = "priority_corner"

    def choose_move(self, game: Game2048) -> Direction:
        valid = game.valid_moves()
        priority = [Direction.LEFT, Direction.DOWN, Direction.UP, Direction.RIGHT]
        for move in priority:
            if move in valid:
                return move
        return valid[0]


@dataclass
class AlphaBetaSolver(Solver):
    max_depth: int = 1
    name: str = "alpha_beta"

    def choose_move(self, game: Game2048) -> Direction:
        valid = game.valid_moves()
        best_score = -math.inf
        best_move = valid[0]
        alpha = -math.inf
        beta = math.inf

        for move in valid:
            new_game = game.clone()
            new_game.move(move)
            score = self.alpha_beta(
                new_game, depth=self.max_depth, maximizing=False, alpha=alpha, beta=beta
            )
            if score > best_score:
                best_score = score
                best_move = move

        return best_move

    def alpha_beta(
        self, game: Game2048, depth: int, maximizing: bool, alpha: float, beta: float
    ) -> float:
        if depth <= 0:
            return snakeHeuristic(game)
        if game.is_game_over():
            return math.inf if game.is_win() else -math.inf

        if maximizing:
            best_score = -math.inf
            for move in game.valid_moves():
                new_game = game.clone()
                new_game.move(move)
                score = self.alpha_beta(
                    new_game, depth=depth - 1, maximizing=False, alpha=alpha, beta=beta
                )
                best_score = max(score, best_score)
                alpha = max(alpha, best_score)
                if beta <= alpha:
                    break
            return best_score
        else:
            best_score = math.inf
            empty_cells = game.empty_cells()
            empty_cells = random.sample(empty_cells, k=min(6, len(empty_cells)))
            if not empty_cells:
                return snakeHeuristic(game)
            for r, c in empty_cells:
                for val in [2, 4]:
                    new_game = game.clone()
                    new_game.board[r][c] = val
                    score = self.alpha_beta(
                        new_game,
                        depth=depth - 1,
                        maximizing=True,
                        alpha=alpha,
                        beta=beta,
                    )
                    best_score = min(score, best_score)
                    beta = min(beta, best_score)
                    if beta <= alpha:
                        break
                if beta <= alpha:
                    break
            return best_score


@dataclass
class ExpectiminimaxSolver(Solver):
    rng: random.Random
    max_depth: int = 1
    name: str = "expectiminimax"

    def choose_move(self, game: Game2048) -> Direction:
        valid = game.valid_moves()
        best_score = -math.inf
        best_move = valid[0]

        for move in valid:
            new_game = game.clone()
            new_game.move(move)
            score = self.expectiminimax(
                new_game, depth=self.max_depth, maximizing=False
            )
            if score > best_score:
                best_score = score
                best_move = move

        return best_move

    def expectiminimax(self, game: Game2048, depth: int, maximizing: bool) -> float:
        if depth <= 0:
            return snakeHeuristic(game)
        if game.is_game_over():
            return math.inf if game.is_win() else -math.inf

        if maximizing:
            best_score = -math.inf
            for move in game.valid_moves():
                new_game = game.clone()
                new_game.move(move)
                score = self.expectiminimax(new_game, depth=depth - 1, maximizing=False)
                best_score = max(score, best_score)
            return best_score
        else:
            total_score = 0
            empty_cells = game.empty_cells()
            empty_cells = random.sample(empty_cells, k=min(6, len(empty_cells)))
            if not empty_cells:
                return snakeHeuristic(game)
            for r, c in empty_cells:
                for value, prob in [(2, 0.9), (4, 0.1)]:
                    new_game = game.clone()
                    new_game.board[r][c] = value
                    score = self.expectiminimax(
                        new_game, depth=depth - 1, maximizing=True
                    )
                    total_score += prob * score

            return total_score / len(empty_cells)


def build_solvers(seed: int) -> List[Solver]:
    return [
        RandomSolver(rng=random.Random(seed)),
        PriorityCornerSolver(),
        AlphaBetaSolver(max_depth=3),
        ExpectiminimaxSolver(rng=random.Random(seed), max_depth=3),
    ]
