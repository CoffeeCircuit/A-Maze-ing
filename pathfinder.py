"""
Universal pathfinder that works by reading maze output file.
Works with any maze generator that follows the output format.
"""

from os import PathLike
from typing import Union
from collections import deque


class PathFinder:
    """Find shortest path in maze by reading output file."""

    def __init__(self, output_file: Union[str, PathLike[str]]) -> None:
        """Initialize pathfinder with output file.

        Args:
            output_file: Path to maze output file.
        """
        self.output_file = output_file
        self.grid: list[list[int]] = []
        self.width = 0
        self.height = 0
        self.entry: tuple[int, int] | None = None
        self.exit: tuple[int, int] | None = None
        self._load_maze()

    def _load_maze(self) -> None:
        """Load maze, entry, and exit from output file."""
        with open(self.output_file, "r") as f:
            lines = f.readlines()

        idx = 0
        while idx < len(lines):
            line = lines[idx].strip()
            if not line:
                idx += 1
                break
            row = [int(c, 16) for c in line]
            self.grid.append(row)
            idx += 1

        self.height = len(self.grid)
        self.width = len(self.grid[0]) if self.grid else 0

        if idx < len(lines):
            entry_line = lines[idx].strip()
            entry_parts = entry_line.split(',')
            self.entry = (int(entry_parts[0].strip()),
                          int(entry_parts[1].strip()))
            idx += 1

        if idx < len(lines):
            exit_line = lines[idx].strip()
            exit_parts = exit_line.split(',')
            self.exit = (int(exit_parts[0].strip()),
                         int(exit_parts[1].strip()))

    def find_path(self) -> str | None:
        """Find shortest path using BFS.

        Returns:
            Path as string of directions(N, E, S, W) or None if no path exists.
        """
        start = self.entry
        end = self.exit

        if start is None or end is None:
            return None

        queue = deque([start])
        visited = {start}
        parent: dict[tuple[int, int], tuple[int, int] | None] = {start: None}
        direction_taken: dict[tuple[int, int], str | None] = {start: None}

        while queue:
            current = queue.popleft()

            if current == end:
                return self._build_path(start, end, parent, direction_taken)

            for neighbor, dir_char in self._get_neighbors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    parent[neighbor] = current
                    direction_taken[neighbor] = dir_char
                    queue.append(neighbor)

        return None

    def _get_neighbors(
            self, pos: tuple[int, int]) -> list[tuple[tuple[int, int], str]]:
        """Get accessible neighboring cells."""
        x, y = pos
        neighbors = []
        walls = self.grid[y][x]

        if y > 0 and not (walls & (1 << 0)):
            neighbors.append(((x, y - 1), 'N'))
        if x < self.width - 1 and not (walls & (1 << 1)):
            neighbors.append(((x + 1, y), 'E'))
        if y < self.height - 1 and not (walls & (1 << 2)):
            neighbors.append(((x, y + 1), 'S'))
        if x > 0 and not (walls & (1 << 3)):
            neighbors.append(((x - 1, y), 'W'))

        return neighbors

    def _build_path(
        self, start: tuple[int, int],
        end: tuple[int, int],
        parent: dict[tuple[int, int], tuple[int, int] | None],
        direction_taken: dict[tuple[int, int], str | None]
    ) -> str:
        """Reconstruct path from start to end.

        Args:
            start: Starting position.
            end: Ending position.
            parent: Parent map from BFS.
            direction_taken: Direction map from BFS.

        Returns:
            Path as string of directions.
        """
        path = []
        current = end

        while current != start:
            direction = direction_taken[current]
            if direction:
                path.append(direction)

            next_cell = parent[current]
            if next_cell is None:
                break
            current = next_cell

        path.reverse()
        return ''.join(path)

    def save_path(self) -> None:
        """Find path and append to output file."""
        path = self.find_path()

        if path is not None:
            with open(self.output_file, "a") as f:
                f.write(path)
