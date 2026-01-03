from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .mazegen import MazeGenerator


def make_p42_mask(maze: MazeGenerator) -> set[tuple[int, int]] | None:
    """
    Function sets a mask of the 42 logo in the center of the maze
    This is used in the dfs and hak maze generators

    :param maze: MazeGenerator class
    """
    if maze.width and maze.height:
        cx = maze.width // 2
        cy = maze.height // 2
    else:
        raise ValueError("Width and/or height can't be None")

    patern_7x5 = {
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

    patern_5x5 = {
        (-2, -2),
        (1, -2),
        (2, -2),
        (-2, -1),
        (2, -1),
        (-2, 0),
        (-1, 0),
        (1, 0),
        (2, 0),
        (-1, 1),
        (1, 1),
        (-1, 2),
        (1, 2),
        (2, 2),
    }

    pattern = patern_7x5
    blocked = None

    if maze.width <= 8:
        pattern = patern_5x5

    if maze.width < 7 or maze.height < 7:
        return blocked
    else:
        blocked = set()
        for ox, oy in pattern:
            x = cx + ox
            y = cy + oy
            if 0 <= x < maze.width and 0 <= y < maze.height:
                blocked.add((y, x))
    return blocked
