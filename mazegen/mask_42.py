from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .mazegen import MazeGenerator


def make_p42_mask(maze: MazeGenerator) -> set[tuple[int, int]]:
    """
    Function sets a mask of the 42 log in the center of the maze
    This is used in the dfs and hak maze generators

    :param maze: MazeGenerator class
    """
    if maze.width and maze.height:
        cx = maze.width // 2
        cy = maze.height // 2
    else:
        raise ValueError("Width and/or height can't be None")

    blocked_offsets = {
        (-3, -2),
        (-1, -2),
        (1, -2),
        (2, -2),
        (3, -2),
        (-3, -1),
        (-1, -1),
        (3, -1),
        (-3, 0),
        (-2, 0),
        (-1, 0),
        (1, 0),
        (2, 0),
        (3, 0),
        (-1, 1),
        (1, 1),
        (-1, 2),
        (1, 2),
        (2, 2),
        (3, 2),
    }

    blocked = set()

    for ox, oy in blocked_offsets:
        x = cx + ox
        y = cy + oy
        if 0 <= x < maze.width and 0 <= y < maze.height:
            blocked.add((y, x))

    return blocked
