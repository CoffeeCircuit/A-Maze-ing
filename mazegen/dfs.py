"""
Maze generator using depth-first search algorithm.

Generates perfect mazes (no loops).
"""

from __future__ import annotations
from random import shuffle, seed
from .mask_42 import make_p42_mask
from .imperfect import make_imperfect
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .mazegen import MazeGenerator


def dfs(maze: MazeGenerator) -> None:
    """
    Depth-first-search algorim used by the MazeGenerator class

    :param maze: MazeGenerator class
    """
    assert maze.entry is not None
    assert maze.exit is not None
    assert maze.height is not None
    assert maze.width is not None
    assert maze.grid is not None

    blocked = make_p42_mask(maze)
    if blocked:
        if maze.entry in blocked:
            msg = f"Entry point {maze.entry} is inside the 42 (blocked) mask."
            raise ValueError(msg)
        if maze.exit in blocked:
            msg = f"Exit point {maze.exit} is inside the 42 (blocked) mask."
            raise ValueError(msg)
    seed(maze.seed)
    stack: list[tuple[int, int]] = [maze.entry]
    visited: set[tuple[int, int]] = {maze.entry}
    neighbors = [(-1, 0), (0, 1), (1, 0), (0, -1)]
    opposite_wall = [2, 3, 0, 1]
    dir = neighbors.copy()
    while stack:
        x, y = stack[-1]
        shuffle(dir)
        moved = False
        for dx, dy in dir:
            if 0 <= x + dx < maze.height and 0 <= y + dy < maze.width:
                if blocked and (x + dx, y + dy) in blocked:
                    continue
                if (x + dx, y + dy) not in visited:
                    stack.append((x + dx, y + dy))
                    visited.add((x + dx, y + dy))
                    i = neighbors.index((dx, dy))
                    maze.grid[x][y] &= ~(1 << i)
                    maze.grid[x + dx][y + dy] &= ~(1 << opposite_wall[i])
                    moved = True
                    break
        if not moved:
            stack.pop()

    if not maze.perfect:
        make_imperfect(maze, blocked)
