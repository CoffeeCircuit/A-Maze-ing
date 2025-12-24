import random


class Cell:
    """Represents a single cell in the maze."""

    NORTH = 1  # 0b0001
    EAST = 2   # 0b0010
    SOUTH = 4  # 0b0100
    WEST = 8   # 0b1000

    def __init__(self, x: int, y: int) -> None:
        """Initialize cell at coordinates (x, y)."""
        self.x = x
        self.y = y
        self.walls = self.NORTH | self.EAST | self.SOUTH | self.WEST
        self.visited = False

    def remove_wall(self, direction: int) -> None:
        """Remove wall in specified direction."""
        self.walls = self.walls & ~direction

    def has_wall(self, direction: int) -> bool:
        """Check if wall exists in direction."""
        return bool(self.walls & direction)

    def to_hex(self) -> str:
        """Convert wall configuration to hexadecimal digit."""
        return format(self.walls, 'X')


class ImperfectMazeGenerator:
    """Hunt-and-Kill algorithm for imperfect maze generation."""

    def __init__(self, width: int, height: int, seed: int | None = None) -> None:
        """Initialize maze generator."""
        self.width = width
        self.height = height
        self.grid: list[list[Cell]] = []
        if seed is not None:
            random.seed(seed)
        self._create_grid()

    def _create_grid(self) -> None:
        """Create grid with all walls closed."""
        self.grid = [[Cell(x, y) for x in range(self.width)]
                     for y in range(self.height)]

    def generate(self) -> None:
        """Generate imperfect maze using Hunt-and-Kill algorithm."""
        current = self.grid[random.randint(0, self.height - 1)][random.randint(0, self.width - 1)]
        current.visited = True

        while not self._all_visited():
            current = self._kill(current)
            found = self._hunt()
            if found:
                current = found

    def _kill(self, cell: Cell) -> Cell:
        """Recursively carve path from current cell."""
        neighbors = self._get_unvisited_neighbors(cell)
        if not neighbors:
            return cell

        next_cell, direction = random.choice(neighbors)
        cell.remove_wall(direction)
        next_cell.remove_wall(self._opposite(direction))
        next_cell.visited = True

        return self._kill(next_cell)

    def _hunt(self) -> Cell | None:
        """Find unvisited cell next to visited cell."""
        for y in range(self.height):
            for x in range(self.width):
                cell = self.grid[y][x]

                if not cell.visited:
                    neighbors = self._get_visited_neighbors(cell)
                    if neighbors:
                        neighbor, direction = random.choice(neighbors)
                        cell.remove_wall(direction)
                        neighbor.remove_wall(self._opposite(direction))
                        cell.visited = True
                        return cell
        return None

    def _get_unvisited_neighbors(self, cell: Cell) -> list[tuple[Cell, int]]:
        """Get list of unvisited neighboring cells."""
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
        """Get list of visited neighboring cells."""
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
        """Get opposite direction."""
        if direction == Cell.NORTH:
            return Cell.SOUTH
        elif direction == Cell.SOUTH:
            return Cell.NORTH
        elif direction == Cell.EAST:
            return Cell.WEST
        else:
            return Cell.EAST

    def _all_visited(self) -> bool:
        """Check if all cells visited."""
        for row in self.grid:
            for cell in row:
                if not cell.visited:
                    return False
        return True

    def get_cell(self, x: int, y: int) -> Cell:
        """Get cell at coordinates."""
        return self.grid[y][x]

    def to_output_format(self) -> str:
        """Convert maze to hexadecimal output format."""
        lines = []
        for row in self.grid:
            lines.append(''.join(cell.to_hex() for cell in row))
        return '\n'.join(lines)
