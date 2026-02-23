import random
from enum import StrEnum
from typing import List, Sequence, Tuple
from dataclasses import dataclass, field


class Direction(StrEnum):
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"


@dataclass
class Game2048:
    size: int = 4
    win_tile: int = 2048
    rng: random.Random = field(default_factory=random.Random)
    board: List[List[int]] = field(init=False)
    score: int = field(default=0, init=False)
    move_count: int = field(default=0, init=False)
    move_counts_by_direction: dict[str, int] = field(
        default_factory=lambda: {d: 0 for d in Direction}, init=False
    )

    def __post_init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.board = [[0 for _ in range(self.size)] for _ in range(self.size)]
        self.score = 0
        self.move_count = 0
        self.move_counts_by_direction = {d: 0 for d in Direction}
        self._spawn_tile()
        self._spawn_tile()

    def clone(self) -> "Game2048":
        cloned = object.__new__(Game2048)
        cloned.size = self.size
        cloned.win_tile = self.win_tile
        cloned.rng = random.Random()
        cloned.board = [row[:] for row in self.board]
        cloned.score = self.score
        cloned.move_count = self.move_count
        cloned.move_counts_by_direction = self.move_counts_by_direction.copy()
        return cloned

    def empty_cells(self) -> List[Tuple[int, int]]:
        return [
            (r, c)
            for r in range(self.size)
            for c in range(self.size)
            if self.board[r][c] == 0
        ]

    def _spawn_tile(self) -> bool:
        empties = self.empty_cells()
        if not empties:
            return False
        r, c = self.rng.choice(empties)
        self.board[r][c] = 4 if self.rng.random() < 0.1 else 2
        return True

    @staticmethod
    def _merge_line(line: Sequence[int]) -> Tuple[List[int], int]:
        non_zero = [x for x in line if x != 0]
        merged: List[int] = []
        score_delta = 0
        skip = False
        for i, value in enumerate(non_zero):
            if skip:
                skip = False
                continue
            if i + 1 < len(non_zero) and non_zero[i + 1] == value:
                new_value = value * 2
                merged.append(new_value)
                score_delta += new_value
                skip = True
            else:
                merged.append(value)
        merged += [0] * (len(line) - len(merged))
        return merged, score_delta

    def _apply_move_without_spawn(self, direction: Direction) -> bool:
        changed = False
        score_delta_total = 0

        for idx in range(self.size):
            if direction == "left":
                line = self.board[idx][:]
                merged, score_delta = self._merge_line(line)
                if merged != line:
                    changed = True
                    self.board[idx] = merged
                score_delta_total += score_delta
            elif direction == "right":
                line = list(reversed(self.board[idx]))
                merged, score_delta = self._merge_line(line)
                merged = list(reversed(merged))
                if merged != self.board[idx]:
                    changed = True
                    self.board[idx] = merged
                score_delta_total += score_delta
            elif direction == "up":
                line = [self.board[r][idx] for r in range(self.size)]
                merged, score_delta = self._merge_line(line)
                if merged != line:
                    changed = True
                    for r in range(self.size):
                        self.board[r][idx] = merged[r]
                score_delta_total += score_delta
            elif direction == "down":
                line = [self.board[r][idx] for r in range(self.size - 1, -1, -1)]
                merged, score_delta = self._merge_line(line)
                merged = list(reversed(merged))
                current = [self.board[r][idx] for r in range(self.size)]
                if merged != current:
                    changed = True
                    for r in range(self.size):
                        self.board[r][idx] = merged[r]
                score_delta_total += score_delta
            else:
                raise ValueError(f"Unknown direction: {direction}")

        if changed:
            self.score += score_delta_total
            self.move_count += 1
            self.move_counts_by_direction[direction] += 1
        return changed

    def can_move(self, direction: Direction) -> bool:
        clone = self.clone()
        return clone._apply_move_without_spawn(direction)

    def valid_moves(self) -> List[Direction]:
        return [d for d in Direction if self.can_move(d)]

    def move(self, direction: Direction) -> bool:
        changed = self._apply_move_without_spawn(direction)
        if changed:
            self._spawn_tile()
        return changed

    def max_tile(self) -> int:
        return max(max(row) for row in self.board)

    def is_win(self) -> bool:
        return self.max_tile() >= self.win_tile

    def is_game_over(self) -> bool:
        return len(self.valid_moves()) == 0

    def __str__(self) -> str:
        return "\n".join(" ".join(f"{cell:4d}" for cell in row) for row in self.board)
