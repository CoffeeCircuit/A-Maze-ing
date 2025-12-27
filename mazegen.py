"""
Maze generator using depth-first search algorithm.

Generates perfect mazes (no loops) using recursive backtracking DFS.
"""

from random import shuffle, seed
from parser import ConfigParser
from os import PathLike
from typing import Union


class MazeGenerator:
    """Generate perfect mazes using DFS algorithm."""

    def __init__(self, config: ConfigParser) -> None:
        """Initialize maze generator from configuration.

        Args:
            config: Parsed configuration containing maze parameters.
        """
        self._grid: list[list[int]] | None = None
        self._output: Union[str, PathLike[str]] | None = None
        self._width: int | None = None
        self._height: int | None = None
        self._entry: tuple[int, int] | None = None
        self._exit: tuple[int, int] | None = None
        self.m_seed: int | None = None
        self.parse(config)

    def parse(self, parser: ConfigParser) -> None:
        """Parse configuration and initialize grid.

        Args:
            parser: Configuration parser with maze parameters.
        """
        self._width = parser.width
        self._height = parser.height
        self._entry = parser.entry
        self._exit = parser.exit
        self._output = parser.output_file
        self.m_seed = parser.seed
        assert self._width is not None
        assert self._height is not None
        self._grid = [[15 for _ in range(self._width)]
                      for _ in range(self._height)]

    def _dfs(self) -> None:
        """Generate maze using depth-first search with recursive backtracking.
        """
        assert self._entry is not None
        assert self._grid is not None
        assert self._width is not None
        assert self._height is not None
        seed(self.m_seed)
        stack: list[tuple[int, int]] = [self._entry]
        visited: set[tuple[int, int]] = {self._entry}
        neighbors = [(-1, 0), (0, 1), (1, 0), (0, -1)]
        opposite_wall = [2, 3, 0, 1]

        dir = neighbors.copy()
        while stack:
            x, y = stack[-1]
            shuffle(dir)
            moved = False
            for dx, dy in dir:
                if 0 <= x + dx < self._height and 0 <= y + dy < self._width:
                    if (x + dx, y + dy) not in visited:
                        stack.append((x + dx, y + dy))
                        visited.add((x + dx, y + dy))
                        i = neighbors.index((dx, dy))
                        self._grid[x][y] &= ~(1 << i)
                        self._grid[x + dx][y + dy] &= ~(1 << opposite_wall[i])
                        moved = True
                        break
            if not moved:
                stack.pop()

    def generate(self, algo: str = "dfs") -> None:
        """Generate maze using specified algorithm.

        Args:
            algo: Algorithm to use for maze generation (default: "dfs").
                  Currently only "dfs" is supported.

        Note:
            Future algorithms that could be added:
            - Prim's algorithm
            - Kruskal's algorithm
            - Wilson's algorithm
            - Aldous-Broder algorithm
        """
        if algo == "dfs":
            self._dfs()

    def save(self) -> None:
        """Save maze to output file in hexadecimal format.

        Output format:
            - Maze grid in hexadecimal (one character per cell)
            - Entry coordinates (x, y)
            - Exit coordinates (x, y)
        """
        assert self._width is not None
        assert self._height is not None
        assert self._grid is not None
        assert self._output is not None
        assert self._entry is not None
        assert self._exit is not None
        out = ""
        for i in range(self._height):
            for j in range(self._width):
                out += hex(self._grid[i][j])[2:].upper()
            out += "\n"
        with open(self._output, "w") as fp:
            fp.write(out)
            fp.write("\n")
            fp.write(f"{self._entry[0]}, {self._entry[1]}")
            fp.write("\n")
            fp.write(f"{self._exit[0]}, {self._exit[1]}")
            fp.write("\n")
