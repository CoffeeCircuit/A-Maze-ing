from __future__ import annotations
from random import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .mazegen import MazeGenerator


def make_imperfect(
    maze: MazeGenerator,
    blocked: set[tuple[int, int]] | None,
    probability: float = 0.5,
) -> None:
    """
    Remove some walls to create loops (imperfect maze).
    probability: chance to remove a wall at each dead end.
    """
    neighbors = [(-1, 0), (0, 1), (1, 0), (0, -1)]
    opposite_wall = [2, 3, 0, 1]
    assert maze.entry is not None
    assert maze.height is not None
    assert maze.width is not None
    assert maze.grid is not None
    for x in range(maze.height):
        for y in range(maze.width):
            if blocked and (x, y) in blocked:
                continue
            open_count = 0
            for i in range(4):
                if not (maze.grid[x][y] & (1 << i)):
                    open_count += 1
            if open_count != 1:
                continue
            for i, (dx, dy) in enumerate(neighbors):
                nx, ny = x + dx, y + dy
                if not (0 <= nx < maze.height and 0 <= ny < maze.width):
                    continue
                if blocked and (nx, ny) in blocked:
                    continue
                if (maze.grid[x][y] & (1 << i)) and (
                    maze.grid[nx][ny] & (1 << opposite_wall[i])
                ):
                    if random() < probability:
                        maze.grid[x][y] &= ~(1 << i)
                        maze.grid[nx][ny] &= ~(1 << opposite_wall[i])
                    break
