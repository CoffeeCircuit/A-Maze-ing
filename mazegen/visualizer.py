"""
Visualizer for the project

This will display the maze to stdout
Ref: https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797
"""

from os import PathLike
from typing import Union, Any
from enum import IntEnum
from shutil import get_terminal_size
from sys import stdout, stdin
from select import select
from termios import tcgetattr, tcsetattr, TCSADRAIN
from tty import setcbreak


class Point:
    """Represents a 2D point with x and y coordinates."""

    def __init__(self, x: int, y: int) -> None:
        """Initialize point at coordinates (x, y).

        Args:
            x: X coordinate.
            y: Y coordinate.
        """
        self.x = x
        self.y = y


class Cell(Point):
    """Represents a maze cell with position and wall configuration."""

    def __init__(self, x: int, y: int, walls: int = 0) -> None:
        """Initialize cell at coordinates (x, y) with wall configuration.

        Args:
            x: X coordinate.
            y: Y coordinate.
            walls: Wall configuration as bit flags (default: 0).
        """
        super().__init__(x, y)
        self.walls = walls


class Graphics:
    """ANSI escape code utilities for terminal graphics."""

    class Color(IntEnum):
        """ANSI color codes."""

        Red = 31
        Green = 32
        Yellow = 33
        Blue = 34
        Magenta = 35
        Cyan = 36
        Default = 39

    @staticmethod
    def set(color: "Graphics.Color", background: bool = False) -> None:
        """Set terminal text or background color.

        Args:
            color: Color to set.
            background: If True, set background color; otherwise text color.
        """
        if background:
            stdout.write(f"\x1b{color};{color + 10}m")
        else:
            stdout.write(f"\x1b[{color}m")

    @staticmethod
    def reset() -> None:
        """Reset terminal colors to default."""
        stdout.write("\x1b[0m")

    @staticmethod
    def menu(item: str) -> None:
        """Display menu item with first character highlighted.

        Args:
            item: Menu item text to display.
        """
        Graphics.set(Graphics.Color.Cyan)
        stdout.write(item[0])
        Graphics.reset()
        stdout.write(item[1:])


class Visualizer:
    """Interactive terminal-based maze visualizer."""

    menu = {
        "Main": ["New maze", "Color", "Path", "Quit"],
        "Color": {
            "Walls": ["Red", "Green", "Yellow", "Blue", "Magenta", "Cyan"],
            "Path": ["Red", "Green", "Yellow", "Blue", "Magenta", "Cyan"],
            "Logo": ["Red", "Green", "Yellow", "Blue", "Magenta", "Cyan"],
        },
    }

    class Keyboard:
        """Event handler for keyboard input in raw mode."""

        @staticmethod
        def enable_raw_mode() -> list[Any]:
            """Enable raw keyboard input mode.

            Returns:
                Previous terminal attributes for restoration.
            """
            fd = stdin.fileno()
            old = tcgetattr(fd)
            setcbreak(fd)
            return old

        @staticmethod
        def disable_raw_mode(old: list[Any]) -> None:
            """Restore terminal to normal mode.

            Args:
                old: Previous terminal attributes from enable_raw_mode().
            """
            tcsetattr(stdin.fileno(), TCSADRAIN, old)

        @staticmethod
        def get_key() -> str | None:
            """Get a single keypress without blocking.

            Returns:
                Key character or special key name ('up'), or None if no key
                pressed.
            """
            dr, _, _ = select([stdin], [], [], 0)
            if not dr:
                return None
            ch = stdin.read(1)
            if ch == "\x1b":
                ch1 = stdin.read(1)
                ch2 = stdin.read(1)
                if ch1 == "[" and ch2 == "A":
                    return "up"
            return ch

    class Cursor:
        """Terminal cursor manipulation utilities."""

        @staticmethod
        def up(n: int = 1) -> None:
            """Move cursor up by n lines.

            Args:
                n: Number of lines to move (default: 1).
            """
            stdout.write(f"\x1b[{n}A")

        @staticmethod
        def up_and_begining(n: int = 1) -> None:
            """Move cursor up n lines to beginning of line.

            Args:
                n: Number of lines to move (default: 1).
            """
            stdout.write(f"\x1b[{n}F")

        @staticmethod
        def down(n: int = 1) -> None:
            """Move cursor down by n lines.

            Args:
                n: Number of lines to move (default: 1).
            """
            stdout.write(f"\x1b[{n}B")

        @staticmethod
        def right(n: int = 1) -> None:
            """Move cursor right by n columns.

            Args:
                n: Number of columns to move (default: 1).
            """
            stdout.write(f"\x1b[{n}C")

        @staticmethod
        def left(n: int = 1) -> None:
            """Move cursor left by n columns.

            Args:
                n: Number of columns to move (default: 1).
            """
            stdout.write(f"\x1b[{n}D")

        @staticmethod
        def save() -> None:
            """Save current cursor position."""
            stdout.write("\x1b7")

        @staticmethod
        def load() -> None:
            """Restore saved cursor position."""
            stdout.write("\x1b8")

        @staticmethod
        def hide() -> None:
            """Hide terminal cursor."""
            stdout.write("\x1b[?25l")

        @staticmethod
        def show() -> None:
            """Show terminal cursor."""
            stdout.write("\x1b[?25h")

        @staticmethod
        def home() -> None:
            """Move cursor to home position (0, 0)."""
            stdout.write("\x1b[H")

        @staticmethod
        def move_to(x: int, y: int) -> None:
            """Move cursor to specific position.

            Args:
                x: Column position (0-indexed).
                y: Row position (0-indexed).
            """
            stdout.write(f"\x1b[{y+1};{x+1}H")

        @staticmethod
        def clear_line() -> None:
            """Clear current line and move cursor to beginning."""
            stdout.write("\x1b[2K\x1b[0G")

    class Terminal:
        """Terminal properties and control."""

        def __init__(self) -> None:
            """Initialize terminal with current size."""
            self.width, self.height = get_terminal_size()

        def update(self) -> None:
            """Update terminal dimensions."""
            self.width, self.height = get_terminal_size()

        @staticmethod
        def clear() -> None:
            """Clear entire terminal screen."""
            stdout.write("\x1b[2J")

        @staticmethod
        def enter_alternate() -> None:
            """Enter alternate screen buffer."""
            stdout.write("\x1b[?1049h")

        @staticmethod
        def exit_alternate() -> None:
            """Exit alternate screen buffer and restore original."""
            stdout.write("\x1b[?1049l")

    def __init__(self) -> None:
        """Initialize visualizer with default settings."""
        self.maze: list[list[Cell]]
        self.start: Point
        self.end: Point
        self.path: list[str]
        self.width: int
        self.height: int
        self.wall_color: Graphics.Color = Graphics.Color.Default
        self.path_color: Graphics.Color = Graphics.Color.Green
        self.logo_color: Graphics.Color = Graphics.Color.Yellow
        self.path_symbol: str = "░"

    def read(self, file: Union[str, PathLike[str]]) -> None:
        """Load maze from output file.

        Args:
            file: Path to maze file containing grid, entry, exit, and path.
        """
        maze: list[list[Cell]] = []
        with open(file, "r") as fp:
            for y, line in enumerate(fp):
                if line == "\n":
                    break
                maze.append(
                    [
                        Cell(
                            x,
                            y,
                            int(c, 16),
                        )
                        for x, c in enumerate(line.strip())
                    ]
                )
            start = Point(*(int(x) for x in fp.readline().strip().split(",")))
            end = Point(*(int(x) for x in fp.readline().strip().split(",")))
            path = [c.upper() for c in fp.readline().strip()]
        self.maze = maze
        self.start = start
        self.end = end
        self.path = path
        self.width = len(maze[0]) * 3
        self.height = len(maze) * 3

    def render(self) -> tuple[bool, int | None]:
        """Render and interact with maze visualization.

        Returns:
            Tuple of (should_regenerate, new_seed).
            (False, None) means quit, (True, seed) means regenerate maze.
        """
        term = Visualizer.Terminal()
        cursor = Visualizer.Cursor()
        N = 0b0001
        E = 0b0010
        S = 0b0100
        W = 0b1000
        m_h = len(self.maze)
        m_w = len(self.maze[0])
        out = [[" " for _ in range(m_w * 2 + 1)] for _ in range(m_h * 2 + 1)]

        def _walls() -> None:
            """Render maze walls and junctions."""
            checks = [
                (-1, 0, "│"),
                (0, 1, "─"),
                (1, 0, "│"),
                (0, -1, "─"),
            ]
            junction_map = {
                1: "╵",
                2: "╶",
                3: "╰",
                4: "╷",
                5: "│",
                6: "╭",
                7: "├",
                8: "╴",
                9: "╯",
                10: "─",
                11: "┴",
                12: "╮",
                13: "┤",
                14: "┬",
                15: "┼",
            }

            for mi in range(m_h):
                for mj in range(m_w):
                    i = mi * 2 + 1
                    j = mj * 2 + 1
                    cell = self.maze[mi][mj].walls
                    if cell & N:
                        out[i - 1][j] = "─"
                    if cell & S:
                        out[i + 1][j] = "─"
                    if cell & E:
                        out[i][j + 1] = "│"
                    if cell & W:
                        out[i][j - 1] = "│"

            for i in range(0, m_h * 2 + 1, 2):
                for j in range(0, m_w * 2 + 1, 2):
                    mask = 0
                    for bit, (di, dj, char) in enumerate(checks):
                        ni, nj = i + di, j + dj
                        if 0 <= ni < len(out) and 0 <= nj < len(out[ni]):
                            if out[ni][nj] == char:
                                mask |= 1 << bit
                    out[i][j] = junction_map.get(mask, " ")
            Graphics.set(self.wall_color)
            for line in out:
                stdout.write("".join(line) + "\n")
            Graphics.reset()

        def _logo() -> None:
            """Render logo (filled cells with all walls)."""
            m_h = len(self.maze)
            m_w = len(self.maze[0])
            Graphics.set(self.logo_color)
            for mi in range(m_h):
                for mj in range(m_w):
                    i = mi * 2 + 1
                    j = mj * 2 + 1
                    if self.maze[mi][mj].walls == 15:
                        cursor.move_to(j, i)
                        stdout.write("█")
            Graphics.reset()

        def _path() -> None:
            """Render solution path through maze."""
            Graphics.set(self.path_color)
            for c in self.path:
                if c == "N":
                    cursor.left()
                    cursor.up()
                    stdout.write(self.path_symbol)
                    cursor.left()
                    cursor.up()
                    stdout.write(self.path_symbol)
                elif c == "S":
                    cursor.left()
                    cursor.down()
                    stdout.write(self.path_symbol)
                    cursor.left()
                    cursor.down()
                    stdout.write(self.path_symbol)
                elif c == "E":
                    stdout.write(self.path_symbol)
                    stdout.write(self.path_symbol)
                elif c == "W":
                    cursor.left()
                    cursor.left()
                    stdout.write(self.path_symbol)
                    cursor.left()
                    cursor.left()
                    stdout.write(self.path_symbol)
            Graphics.reset()

        kbd = Visualizer.Keyboard()
        mode = Visualizer.Keyboard.enable_raw_mode()
        refresh = True
        menu_type = "Main"
        menu: Any = Visualizer.menu
        term.enter_alternate()

        try:
            while True:
                if refresh:
                    term.clear()
                    cursor.hide()
                    cursor.home()
                    _walls()
                    _logo()
                    cursor.move_to(self.start.x * 2 + 1, self.start.y * 2 + 1)
                    stdout.write("S")
                    _path()
                    cursor.move_to(self.end.x * 2 + 1, self.end.y * 2 + 1)
                    stdout.write("E")
                    if self.width <= 18 or self.height <= 18:
                        cursor.move_to(0, term.height - 3)
                        stdout.write("Info: Maze too small for the 42 pattern")
                    cursor.move_to(0, term.height - 2)
                    stdout.write("─" * term.width)
                    for item in menu[menu_type]:
                        Graphics.menu(item)
                        stdout.write("    ")
                    stdout.flush()
                    refresh = False

                key = kbd.get_key()
                if key:
                    match key.lower():
                        case "q":
                            return False, None
                        case "n" if menu_type == "Main":
                            cursor.clear_line()
                            cursor.show()
                            Visualizer.Keyboard.disable_raw_mode(mode)
                            seed_msg = "Enter seed or press 'Enter' for None: "
                            while True:
                                new_seed = input(seed_msg)
                                if new_seed == "":
                                    new_seed_value = None
                                    break
                                elif new_seed.isdigit():
                                    new_seed_value = int(new_seed)
                                    break
                            return True, new_seed_value
                        case "c" if menu_type == "Main":
                            menu_type = "Color"
                            refresh = True
                        case "p" if menu_type == "Main":
                            if self.path_symbol == "░":
                                self.path_symbol = " "
                            else:
                                self.path_symbol = "░"
                            refresh = True
                        case "w" if menu_type == "Color":
                            menu = Visualizer.menu["Color"]
                            menu_type = "Walls"
                            refresh = True
                        case "p" if menu_type == "Color":
                            menu = Visualizer.menu["Color"]
                            menu_type = "Path"
                            refresh = True
                        case "l" if menu_type == "Color":
                            menu = Visualizer.menu["Color"]
                            menu_type = "Logo"
                            refresh = True

                        # Walls color handling
                        case "r" if menu_type == "Walls":
                            self.wall_color = Graphics.Color.Red
                            menu = Visualizer.menu
                            menu_type = "Main"
                            refresh = True
                        case "g" if menu_type == "Walls":
                            self.wall_color = Graphics.Color.Green
                            menu = Visualizer.menu
                            menu_type = "Main"
                            refresh = True
                        case "y" if menu_type == "Walls":
                            self.wall_color = Graphics.Color.Yellow
                            menu = Visualizer.menu
                            menu_type = "Main"
                            refresh = True
                        case "b" if menu_type == "Walls":
                            self.wall_color = Graphics.Color.Blue
                            menu = Visualizer.menu
                            menu_type = "Main"
                            refresh = True
                        case "m" if menu_type == "Walls":
                            self.wall_color = Graphics.Color.Magenta
                            menu = Visualizer.menu
                            menu_type = "Main"
                            refresh = True
                        case "c" if menu_type == "Walls":
                            self.wall_color = Graphics.Color.Cyan
                            menu = Visualizer.menu
                            menu_type = "Main"
                            refresh = True

                        # Path color handling
                        case "r" if menu_type == "Path":
                            self.path_color = Graphics.Color.Red
                            menu = Visualizer.menu
                            menu_type = "Main"
                            refresh = True
                        case "g" if menu_type == "Path":
                            self.path_color = Graphics.Color.Green
                            menu = Visualizer.menu
                            menu_type = "Main"
                            refresh = True
                        case "y" if menu_type == "Path":
                            self.path_color = Graphics.Color.Yellow
                            menu = Visualizer.menu
                            menu_type = "Main"
                            refresh = True
                        case "b" if menu_type == "Path":
                            self.path_color = Graphics.Color.Blue
                            menu = Visualizer.menu
                            menu_type = "Main"
                            refresh = True
                        case "m" if menu_type == "Path":
                            self.path_color = Graphics.Color.Magenta
                            menu = Visualizer.menu
                            menu_type = "Main"
                            refresh = True
                        case "c" if menu_type == "Path":
                            self.path_color = Graphics.Color.Cyan
                            menu = Visualizer.menu
                            menu_type = "Main"
                            refresh = True

                        # Logo color handling
                        case "r" if menu_type == "Logo":
                            self.logo_color = Graphics.Color.Red
                            menu = Visualizer.menu
                            menu_type = "Main"
                            refresh = True
                        case "g" if menu_type == "Logo":
                            self.logo_color = Graphics.Color.Green
                            menu = Visualizer.menu
                            menu_type = "Main"
                            refresh = True
                        case "y" if menu_type == "Logo":
                            self.logo_color = Graphics.Color.Yellow
                            menu = Visualizer.menu
                            menu_type = "Main"
                            refresh = True
                        case "b" if menu_type == "Logo":
                            self.logo_color = Graphics.Color.Blue
                            menu = Visualizer.menu
                            menu_type = "Main"
                            refresh = True
                        case "m" if menu_type == "Logo":
                            self.logo_color = Graphics.Color.Magenta
                            menu = Visualizer.menu
                            menu_type = "Main"
                            refresh = True
                        case "c" if menu_type == "Logo":
                            self.logo_color = Graphics.Color.Cyan
                            menu = Visualizer.menu
                            menu_type = "Main"
                            refresh = True

        finally:
            Visualizer.Keyboard.disable_raw_mode(mode)
            cursor.show()
            term.exit_alternate()
