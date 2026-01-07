from __future__ import annotations
from typing import TYPE_CHECKING
from random import seed, choice
from .mask_42 import make_p42_mask
from .imperfect import make_imperfect

if TYPE_CHECKING:
    from .mazegen import MazeGenerator


def hak(maze: MazeGenerator) -> None:
    """
    Hunt-and-Kill maze generation algorithm using integer grid format.

    - Kill phase: random walk carving passages until stuck
    - Hunt phase: scan for an unvisited cell next to a visited one
    """

    assert maze.grid is not None
    assert maze.width is not None
    assert maze.height is not None
    assert maze.entry is not None

    seed(maze.seed)
    blocked = make_p42_mask(maze)
    if blocked:
        if maze.entry in blocked:
            msg = f"Entry point {maze.entry} is inside the 42 (blocked) mask."
            raise ValueError(msg)
        if maze.exit in blocked:
            msg = f"Exit point {maze.exit} is inside the 42 (blocked) mask."
            raise ValueError(msg)
    width = maze.width
    height = maze.height
    grid = maze.grid
    visited = set()
    DIRS = [(-1, 0), (0, 1), (1, 0), (0, -1)]
    OPP = [2, 3, 0, 1]

    cx, cy = maze.entry
    visited.add((cx, cy))

    def kill(x: int, y: int) -> tuple[int, int]:
        """
        Hunt stage of the algoruithm

        :param x: Coordinate
        :param y: Coordinate
        """
        while True:
            neighbors = []

            for i, (dx, dy) in enumerate(DIRS):
                nx, ny = x + dx, y + dy
                if 0 <= nx < height and 0 <= ny < width:
                    if blocked:
                        if (nx, ny) not in visited and (nx, ny) not in blocked:
                            neighbors.append((nx, ny, i))
                    else:
                        if (nx, ny) not in visited:
                            neighbors.append((nx, ny, i))

            if not neighbors:
                return x, y

            nx, ny, i = choice(neighbors)

            grid[x][y] &= ~(1 << i)
            grid[nx][ny] &= ~(1 << OPP[i])

            visited.add((nx, ny))
            x, y = nx, ny

    def hunt() -> tuple[int, int] | None:
        """
        Hunt stage of the algorithm
        """
        for x in range(height):
            for y in range(width):
                if blocked:
                    if (x, y) in visited or (x, y) in blocked:
                        continue
                else:
                    if (x, y) in visited:
                        continue

                candidates = []
                for i, (dx, dy) in enumerate(DIRS):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < height and 0 <= ny < width:
                        if blocked:
                            if (nx, ny) in visited and (x, y) not in blocked:
                                candidates.append((nx, ny, i))
                        else:
                            if (nx, ny) in visited:
                                candidates.append((nx, ny, i))

                if candidates:
                    nx, ny, i = choice(candidates)

                    grid[x][y] &= ~(1 << i)
                    grid[nx][ny] &= ~(1 << OPP[i])

                    visited.add((x, y))
                    return x, y

        return None

    x, y = cx, cy
    while True:
        x, y = kill(x, y)
        found = hunt()
        if not found:
            break
        x, y = found

    if not maze.perfect:
        make_imperfect(maze, blocked)
