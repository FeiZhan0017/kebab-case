"""Board representation and logic for the Tetris playfield."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Sequence, Tuple

from .pieces import Tetromino


@dataclass
class Board:
    """Represents the grid that tetrominoes fall into."""

    width: int = 10
    height: int = 20
    grid: List[List[Optional[Tuple[int, int, int]]]] = field(init=False)

    def __post_init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        """Clear the board grid."""
        self.grid = [[None for _ in range(self.width)] for _ in range(self.height)]

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and y < self.height

    def is_valid_position(
        self,
        tetromino: Tetromino,
        rotation_index: int,
        position: Tuple[int, int],
    ) -> bool:
        """Check if the tetromino can occupy the given position."""
        ox, oy = position
        for dx, dy in tetromino.get_rotation(rotation_index):
            x = ox + dx
            y = oy + dy
            if not self.in_bounds(x, y):
                if y < 0:
                    # Allow spawning above the top boundary.
                    continue
                return False
            if y >= 0 and self.grid[y][x] is not None:
                return False
        return True

    def lock_piece(
        self,
        tetromino: Tetromino,
        rotation_index: int,
        position: Tuple[int, int],
    ) -> None:
        """Commit the tetromino's blocks to the grid."""
        ox, oy = position
        for dx, dy in tetromino.get_rotation(rotation_index):
            x = ox + dx
            y = oy + dy
            if 0 <= y < self.height and 0 <= x < self.width:
                self.grid[y][x] = tetromino.color

    def clear_lines(self) -> int:
        """Clear any completely filled lines and return how many were removed."""
        new_rows = [row for row in self.grid if not all(cell is not None for cell in row)]
        cleared = self.height - len(new_rows)
        if cleared:
            for _ in range(cleared):
                new_rows.insert(0, [None for _ in range(self.width)])
            self.grid = new_rows
        return cleared

    def get_cells(self) -> Sequence[Sequence[Optional[Tuple[int, int, int]]]]:
        """Expose the board grid (read-only)."""
        return self.grid


__all__ = ["Board"]
