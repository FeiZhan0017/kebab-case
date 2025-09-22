"""Game orchestration for a simple Tetris implementation."""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from .board import Board
from .pieces import TETROMINOS, Tetromino, generate_bag


@dataclass
class ActivePiece:
    name: str
    rotation: int = 0
    position: Tuple[int, int] = (3, -2)

    def rotated(self, step: int, tetromino: Tetromino) -> "ActivePiece":
        return ActivePiece(
            name=self.name,
            rotation=(self.rotation + step) % len(tetromino.rotations),
            position=self.position,
        )

    def moved(self, dx: int, dy: int) -> "ActivePiece":
        x, y = self.position
        return ActivePiece(name=self.name, rotation=self.rotation, position=(x + dx, y + dy))


@dataclass
class Game:
    width: int = 10
    height: int = 20
    rng: random.Random = field(default_factory=random.Random)

    board: Board = field(init=False)
    active: Optional[ActivePiece] = field(init=False, default=None)
    queue: List[str] = field(init=False, default_factory=list)
    hold: Optional[str] = field(init=False, default=None)
    hold_locked: bool = field(init=False, default=False)
    score: int = field(init=False, default=0)
    lines_cleared: int = field(init=False, default=0)
    level: int = field(init=False, default=1)
    gravity_timer: float = field(init=False, default=0.0)
    drop_interval: float = field(init=False, default=1.0)
    game_over: bool = field(init=False, default=False)

    def __post_init__(self) -> None:
        self.board = Board(self.width, self.height)
        self._refill_queue()
        self.spawn_piece()

    # Queue management -------------------------------------------------
    def _refill_queue(self) -> None:
        while len(self.queue) < 7:
            self.queue.extend(generate_bag(self.rng))

    def _pop_next(self) -> str:
        self._refill_queue()
        return self.queue.pop(0)

    # Piece state ------------------------------------------------------
    def spawn_piece(self) -> None:
        name = self._pop_next()
        self.active = ActivePiece(name=name, rotation=0, position=(self.width // 2 - 2, -2))
        self.hold_locked = False
        if not self.board.is_valid_position(self.tetromino, self.active.rotation, self.active.position):
            self.game_over = True

    @property
    def tetromino(self) -> Tetromino:
        if not self.active:
            raise ValueError("No active piece")
        return TETROMINOS[self.active.name]

    # Mechanics --------------------------------------------------------
    def update(self, dt: float) -> None:
        if self.game_over or not self.active:
            return
        self.gravity_timer += dt
        while self.gravity_timer >= self.drop_interval:
            self.gravity_timer -= self.drop_interval
            if not self._step_down():
                break

    def _step_down(self) -> bool:
        if not self.active:
            return False
        moved = self.active.moved(0, 1)
        if self.board.is_valid_position(self.tetromino, moved.rotation, moved.position):
            self.active = moved
            return True
        self._lock_piece()
        return False

    def move(self, dx: int) -> None:
        if self.game_over or not self.active:
            return
        candidate = self.active.moved(dx, 0)
        if self.board.is_valid_position(self.tetromino, candidate.rotation, candidate.position):
            self.active = candidate

    def soft_drop(self) -> None:
        if self.game_over or not self.active:
            return
        if not self._step_down():
            # Award a small bonus for soft dropping when the piece locks.
            self.score += 1

    def hard_drop(self) -> None:
        if self.game_over or not self.active:
            return
        distance = 0
        while True:
            moved = self.active.moved(0, 1)
            if self.board.is_valid_position(self.tetromino, moved.rotation, moved.position):
                self.active = moved
                distance += 1
            else:
                break
        self.score += distance * 2
        self._lock_piece()

    def rotate(self, step: int) -> None:
        if self.game_over or not self.active:
            return
        tetromino = self.tetromino
        candidate = self.active.rotated(step, tetromino)
        kicks = [(0, 0), (-1, 0), (1, 0), (0, -1)]
        for dx, dy in kicks:
            test = ActivePiece(
                name=candidate.name,
                rotation=candidate.rotation,
                position=(candidate.position[0] + dx, candidate.position[1] + dy),
            )
            if self.board.is_valid_position(tetromino, test.rotation, test.position):
                self.active = test
                return

    def hold_piece(self) -> None:
        if self.game_over or not self.active or self.hold_locked:
            return
        current_name = self.active.name
        if self.hold is None:
            self.hold = current_name
            self.spawn_piece()
        else:
            self.hold, swap = current_name, self.hold
            self.active = ActivePiece(name=swap, rotation=0, position=(self.width // 2 - 2, -2))
            if not self.board.is_valid_position(self.tetromino, self.active.rotation, self.active.position):
                self.game_over = True
        self.hold_locked = True

    # Resolution -------------------------------------------------------
    def _lock_piece(self) -> None:
        if not self.active:
            return
        tetromino = self.tetromino
        self.board.lock_piece(tetromino, self.active.rotation, self.active.position)
        lines = self.board.clear_lines()
        if lines:
            self._apply_line_clear(lines)
        self.active = None
        self.spawn_piece()

    def _apply_line_clear(self, lines: int) -> None:
        self.lines_cleared += lines
        line_scores = {0: 0, 1: 40, 2: 100, 3: 300, 4: 1200}
        self.score += line_scores.get(lines, 0) * self.level
        self.level = 1 + self.lines_cleared // 10
        self.drop_interval = max(0.1, 1.0 - (self.level - 1) * 0.1)

    # Rendering helpers -----------------------------------------------
    def settled_cells(self):
        return self.board.get_cells()

    def active_cells(self):
        if not self.active:
            return []
        tetromino = self.tetromino
        ax, ay = self.active.position
        return [
            (ax + dx, ay + dy, tetromino.color)
            for dx, dy in tetromino.get_rotation(self.active.rotation)
        ]

    def ghost_position(self) -> Optional[List[Tuple[int, int]]]:
        if not self.active:
            return None
        ghost = self.active
        while True:
            moved = ghost.moved(0, 1)
            tetromino = TETROMINOS[ghost.name]
            if self.board.is_valid_position(tetromino, moved.rotation, moved.position):
                ghost = moved
            else:
                break
        ax, ay = ghost.position
        tetromino = TETROMINOS[ghost.name]
        return [(ax + dx, ay + dy) for dx, dy in tetromino.get_rotation(ghost.rotation)]

    def next_queue(self) -> List[str]:
        return self.queue[:5]


__all__ = ["Game", "ActivePiece"]
