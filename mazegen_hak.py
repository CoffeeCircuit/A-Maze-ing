from random import randint, seed, choice, sample
from parser import ConfigParser


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


class HaKMazeGenerator:
    """Hunt-and-Kill algorithm for imperfect maze generation."""

    def __init__(self, config: ConfigParser) -> None:
        """Initialize maze generator."""
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
        """Create grid with all walls closed."""
        self.grid = [[Cell(x, y) for x in range(self.width)]
                     for y in range(self.height)]

    def generate(self) -> None:
        """Generate imperfect maze using Hunt-and-Kill algorithm."""
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
        """Remove random walls to create loops (imperfect maze)."""
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
        num_to_remove = int(len(removable_walls) * 0.1)
        walls_to_remove = sample(removable_walls, num_to_remove)
        for cell1, cell2, direction in walls_to_remove:
            cell1.remove_wall(direction)
            cell2.remove_wall(self._opposite(direction))

    def _kill(self, cell: Cell) -> Cell:
        """Recursively carve path from current cell."""
        neighbors = self._get_unvisited_neighbors(cell)
        if not neighbors:
            return cell

        next_cell, direction = choice(neighbors)
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
                        neighbor, direction = choice(neighbors)
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

    def save(self) -> None:
        """Convert maze to hexadecimal and export to output file."""
        lines = []
        for row in self.grid:
            lines.append(''.join(cell.to_hex() for cell in row))
        output = '\n'.join(lines)
        with open(self.output_file, "w") as f:
            f.write(output)
            f.write("\n\n")
            f.write(f"{self.entry[0]},{self.entry[1]}\n")
            f.write(f"{self.exit[0]},{self.exit[1]}\n")
