"""Definitions for Tetris tetromino pieces and rotations."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence, Tuple
import random

Coordinate = Tuple[int, int]


@dataclass(frozen=True)
class Tetromino:
    """Static description of a tetromino and its rotation states."""

    name: str
    rotations: Sequence[Sequence[Coordinate]]
    color: Tuple[int, int, int]

    def get_rotation(self, index: int) -> Sequence[Coordinate]:
        """Return the block coordinates for a rotation index."""
        return self.rotations[index % len(self.rotations)]


# Rotations are defined relative to a pivot at (0, 0).
# They follow the right-hand rotation order (clockwise).
TETROMINOS: Dict[str, Tetromino] = {
    "I": Tetromino(
        name="I",
        rotations=[
            ((-2, 0), (-1, 0), (0, 0), (1, 0)),
            ((0, -1), (0, 0), (0, 1), (0, 2)),
            ((-2, 1), (-1, 1), (0, 1), (1, 1)),
            ((-1, -1), (-1, 0), (-1, 1), (-1, 2)),
        ],
        color=(0, 240, 240),
    ),
    "O": Tetromino(
        name="O",
        rotations=[
            ((0, 0), (1, 0), (0, 1), (1, 1)),
            ((0, 0), (1, 0), (0, 1), (1, 1)),
            ((0, 0), (1, 0), (0, 1), (1, 1)),
            ((0, 0), (1, 0), (0, 1), (1, 1)),
        ],
        color=(240, 240, 0),
    ),
    "T": Tetromino(
        name="T",
        rotations=[
            ((-1, 0), (0, 0), (1, 0), (0, 1)),
            ((0, -1), (0, 0), (0, 1), (1, 0)),
            ((-1, 0), (0, 0), (1, 0), (0, -1)),
            ((0, -1), (0, 0), (0, 1), (-1, 0)),
        ],
        color=(160, 0, 240),
    ),
    "S": Tetromino(
        name="S",
        rotations=[
            ((0, 0), (1, 0), (-1, 1), (0, 1)),
            ((0, -1), (0, 0), (1, 0), (1, 1)),
            ((0, 0), (1, 0), (-1, 1), (0, 1)),
            ((0, -1), (0, 0), (1, 0), (1, 1)),
        ],
        color=(0, 240, 0),
    ),
    "Z": Tetromino(
        name="Z",
        rotations=[
            ((-1, 0), (0, 0), (0, 1), (1, 1)),
            ((1, -1), (0, 0), (1, 0), (0, 1)),
            ((-1, 0), (0, 0), (0, 1), (1, 1)),
            ((1, -1), (0, 0), (1, 0), (0, 1)),
        ],
        color=(240, 0, 0),
    ),
    "J": Tetromino(
        name="J",
        rotations=[
            ((-1, 0), (-1, 1), (0, 0), (1, 0)),
            ((0, -1), (0, 0), (0, 1), (1, 1)),
            ((-1, 0), (0, 0), (1, 0), (1, -1)),
            ((-1, -1), (0, -1), (0, 0), (0, 1)),
        ],
        color=(0, 0, 240),
    ),
    "L": Tetromino(
        name="L",
        rotations=[
            ((-1, 0), (0, 0), (1, 0), (1, 1)),
            ((0, -1), (0, 0), (0, 1), (1, -1)),
            ((-1, -1), (-1, 0), (0, 0), (1, 0)),
            ((-1, 1), (0, -1), (0, 0), (0, 1)),
        ],
        color=(240, 160, 0),
    ),
}

TETROMINO_ORDER: List[str] = list(TETROMINOS.keys())


def generate_bag(rng: random.Random | None = None) -> List[str]:
    """Return a shuffled bag containing one of each tetromino name."""
    rng = rng or random.Random()
    bag = TETROMINO_ORDER.copy()
    rng.shuffle(bag)
    return bag


__all__ = ["Coordinate", "Tetromino", "TETROMINOS", "TETROMINO_ORDER", "generate_bag"]
