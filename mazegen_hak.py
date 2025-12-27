"""
Hunt-and-Kill maze generator for perfect and imperfect mazes.

Implements the Hunt-and-Kill algorithm which creates mazes by:
1. Kill phase: Random walk from current cell, carving passages
2. Hunt phase: Scan for unvisited cells adjacent to visited cells
3. Optional loop creation for imperfect mazes
"""

from random import randint, seed, choice, sample
from parser import ConfigParser


class Cell:
    """Represents a single cell in the maze with wall configuration."""

    NORTH = 1  # 0b0001
    EAST = 2   # 0b0010
    SOUTH = 4  # 0b0100
    WEST = 8   # 0b1000

    def __init__(self, x: int, y: int) -> None:
        """Initialize cell at coordinates (x, y) with all walls closed.

        Args:
            x: X coordinate of the cell.
            y: Y coordinate of the cell.
        """
        self.x = x
        self.y = y
        self.walls = self.NORTH | self.EAST | self.SOUTH | self.WEST
        self.visited = False

    def remove_wall(self, direction: int) -> None:
        """Remove wall in specified direction using bitwise operation.

        Args:
            direction: Direction constant (NORTH, EAST, SOUTH, or WEST).
        """
        self.walls = self.walls & ~direction

    def has_wall(self, direction: int) -> bool:
        """Check if wall exists in specified direction.

        Args:
            direction: Direction constant to check.

        Returns:
            True if wall exists, False otherwise.
        """
        return bool(self.walls & direction)

    def to_hex(self) -> str:
        """Convert wall configuration to hexadecimal digit.

        Returns:
            Single uppercase hexadecimal character (0-F).
        """
        return format(self.walls, 'X')


class HaKMazeGenerator:
    """Hunt-and-Kill algorithm for perfect and imperfect maze generation."""

    def __init__(self, config: ConfigParser) -> None:
        """Initialize maze generator from configuration.

        Args:
            config: Parsed configuration containing maze parameters.
        """
        if config.width is None or config.height is None:
            return
        if config.entry is None or config.exit is None:
            return
        self.width = config.width
        self.height = config.height
        self.entry = config.entry
        self.exit = config.exit
        self.output_file = config.output_file
        self.perfect = config.perfect
        self.grid: list[list[Cell]] = []
        if config.seed is not None:
            seed(config.seed)
        self._create_grid()

    def _create_grid(self) -> None:
        """Create 2D grid of cells with all walls initially closed."""
        self.grid = [[Cell(x, y) for x in range(self.width)]
                     for y in range(self.height)]

    def generate(self) -> None:
        """Generate maze using Hunt-and-Kill algorithm.

        Starts from random cell, alternates between kill and hunt phases
        until all cells are visited. Creates loops if perfect=False.
        """
        current = self.grid[randint(
            0, self.height - 1)][randint(0, self.width - 1)]
        current.visited = True

        while not self._all_visited():
            current = self._kill(current)
            found = self._hunt()
            if found:
                current = found
        if self.perfect is False:
            self._create_loops()

    def _create_loops(self) -> None:
        """Remove random walls to create loops (imperfect maze).

        Randomly removes 5% of remaining walls to create multiple paths
        and cycles in the maze, making it imperfect.
        """
        removable_walls = []
        for y in range(self.height):
            for x in range(self.width):
                cell = self.grid[y][x]
                if x < self.width - 1 and cell.has_wall(Cell.EAST):
                    removable_walls.append(
                        (cell, self.grid[y][x + 1], Cell.EAST))
                if y < self.height - 1 and cell.has_wall(Cell.SOUTH):
                    removable_walls.append(
                        (cell, self.grid[y + 1][x], Cell.SOUTH))
        num_to_remove = int(len(removable_walls) * 0.05)
        walls_to_remove = sample(removable_walls, num_to_remove)
        for cell1, cell2, direction in walls_to_remove:
            cell1.remove_wall(direction)
            cell2.remove_wall(self._opposite(direction))

    def _kill(self, cell: Cell) -> Cell:
        """Recursively carve path from current cell (kill phase).

        Performs random walk, removing walls between current and unvisited
        neighbors until no unvisited neighbors remain.

        Args:
            cell: Current cell to carve from.

        Returns:
            Final cell reached when no unvisited neighbors available.
        """
        neighbors = self._get_unvisited_neighbors(cell)
        if not neighbors:
            return cell

        next_cell, direction = choice(neighbors)
        cell.remove_wall(direction)
        next_cell.remove_wall(self._opposite(direction))
        next_cell.visited = True

        return self._kill(next_cell)

    def _hunt(self) -> Cell | None:
        """Find unvisited cell adjacent to visited cell (hunt phase).

        Scans grid row by row to find first unvisited cell that has
        at least one visited neighbor, then connects them.

        Returns:
            Unvisited cell adjacent to visited cell, or None if all visited.
        """
        for y in range(self.height):
            for x in range(self.width):
                cell = self.grid[y][x]

                if not cell.visited:
                    neighbors = self._get_visited_neighbors(cell)
                    if neighbors:
                        neighbor, direction = choice(neighbors)
                        cell.remove_wall(direction)
                        neighbor.remove_wall(self._opposite(direction))
                        cell.visited = True
                        return cell
        return None

    def _get_unvisited_neighbors(self, cell: Cell) -> list[tuple[Cell, int]]:
        """Get list of unvisited neighboring cells with directions.

        Args:
            cell: Cell to find neighbors for.

        Returns:
            List of (neighbor_cell, direction) tuples for unvisited neighbors.
        """
        neighbors = []
        x, y = cell.x, cell.y

        if y > 0 and not self.grid[y - 1][x].visited:
            neighbors.append((self.grid[y - 1][x], Cell.NORTH))
        if x < self.width - 1 and not self.grid[y][x + 1].visited:
            neighbors.append((self.grid[y][x + 1], Cell.EAST))
        if y < self.height - 1 and not self.grid[y + 1][x].visited:
            neighbors.append((self.grid[y + 1][x], Cell.SOUTH))
        if x > 0 and not self.grid[y][x - 1].visited:
            neighbors.append((self.grid[y][x - 1], Cell.WEST))
        return neighbors

    def _get_visited_neighbors(self, cell: Cell) -> list[tuple[Cell, int]]:
        """Get list of visited neighboring cells with directions.

        Args:
            cell: Cell to find neighbors for.

        Returns:
            List of (neighbor_cell, direction) tuples for visited neighbors.
        """
        neighbors = []
        x, y = cell.x, cell.y

        if y > 0 and self.grid[y - 1][x].visited:
            neighbors.append((self.grid[y - 1][x], Cell.NORTH))
        if x < self.width - 1 and self.grid[y][x + 1].visited:
            neighbors.append((self.grid[y][x + 1], Cell.EAST))
        if y < self.height - 1 and self.grid[y + 1][x].visited:
            neighbors.append((self.grid[y + 1][x], Cell.SOUTH))
        if x > 0 and self.grid[y][x - 1].visited:
            neighbors.append((self.grid[y][x - 1], Cell.WEST))
        return neighbors

    def _opposite(self, direction: int) -> int:
        """Get opposite direction for wall removal.

        Args:
            direction: Direction constant.

        Returns:
            Opposite direction constant.
        """
        if direction == Cell.NORTH:
            return Cell.SOUTH
        elif direction == Cell.SOUTH:
            return Cell.NORTH
        elif direction == Cell.EAST:
            return Cell.WEST
        else:
            return Cell.EAST

    def _all_visited(self) -> bool:
        """Check if all cells in the maze have been visited.

        Returns:
            True if all cells visited, False otherwise.
        """
        for row in self.grid:
            for cell in row:
                if not cell.visited:
                    return False
        return True

    def save(self) -> None:
        """Convert maze to hexadecimal format and save to output file.

        Output format:
            - Maze grid in hexadecimal (one character per cell)
            - Entry coordinates (x,y)
            - Exit coordinates (x,y)
        """
        lines = []
        for row in self.grid:
            lines.append(''.join(cell.to_hex() for cell in row))
        output = '\n'.join(lines)
        with open(self.output_file, "w") as f:
            f.write(output)
            f.write("\n\n")
            f.write(f"{self.entry[0]},{self.entry[1]}\n")
            f.write(f"{self.exit[0]},{self.exit[1]}\n")
