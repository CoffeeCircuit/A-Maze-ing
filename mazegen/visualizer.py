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
from time import sleep


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
                Key character or special key name ('up', 'down', 'left', 'right'),
                or None if no key pressed.
            """
            dr, _, _ = select([stdin], [], [], 0)
            if not dr:
                return None
            ch = stdin.read(1)
            if ch == "\x1b":
                ch1 = stdin.read(1)
                ch2 = stdin.read(1)
                if ch1 == "[":
                    if ch2 == "A":
                        return "up"
                    if ch2 == "B":
                        return "down"
                    if ch2 == "C":
                        return "right"
                    if ch2 == "D":
                        return "left"
                return ch
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
        self.path_drawn = False

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
                maze.append([Cell(x, y, int(c, 16))
                            for x, c in enumerate(line.strip())])
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

        # Viewport offsets (top-left corner in `out`)
        off_x = 0
        off_y = 0

        # Viewport size (computed on refresh)
        view_w = term.width
        view_h = max(1, term.height - 3)

        def clamp_offsets() -> None:
            nonlocal off_x, off_y, view_w, view_h
            out_h = len(out)
            out_w = len(out[0]) if out else 0
            max_off_x = max(0, out_w - view_w)
            max_off_y = max(0, out_h - view_h)
            if off_x < 0:
                off_x = 0
            elif off_x > max_off_x:
                off_x = max_off_x
            if off_y < 0:
                off_y = 0
            elif off_y > max_off_y:
                off_y = max_off_y

        def to_screen(x: int, y: int) -> tuple[int, int]:
            return x - off_x, y - off_y

        def in_view(sx: int, sy: int) -> bool:
            return 0 <= sx < view_w and 0 <= sy < view_h

        def _walls() -> None:
            """Render maze walls and junctions into `out` then print viewport."""
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

            # reset out
            for i in range(len(out)):
                for j in range(len(out[i])):
                    out[i][j] = " "

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
            for row_i in range(off_y, min(off_y + view_h, len(out))):
                stdout.write("".join(out[row_i][off_x:off_x + view_w]) + "\n")
            Graphics.reset()

        def _logo() -> None:
            """Render logo (filled cells with all walls) inside viewport."""
            Graphics.set(self.logo_color)
            for mi in range(m_h):
                for mj in range(m_w):
                    i = mi * 2 + 1
                    j = mj * 2 + 1
                    if self.maze[mi][mj].walls == 15:
                        sx, sy = to_screen(j, i)
                        if in_view(sx, sy):
                            cursor.move_to(sx, sy)
                            stdout.write("█")
            Graphics.reset()

        def _path(animate: bool = False) -> None:
            """Render solution path through maze (viewport-aware, continuous)."""
            x = self.start.x * 2 + 1
            y = self.start.y * 2 + 1

            def draw(px: int, py: int) -> None:
                sx = px - off_x
                sy = py - off_y
                if 0 <= sx < view_w and 0 <= sy < view_h:
                    cursor.move_to(sx, sy)
                    stdout.write(self.path_symbol)

            Graphics.set(self.path_color)

            for c in self.path:
                if c == "N":
                    draw(x, y - 1)
                    draw(x, y - 2)
                    y -= 2
                elif c == "S":
                    draw(x, y + 1)
                    draw(x, y + 2)
                    y += 2
                elif c == "E":
                    draw(x + 1, y)
                    draw(x + 2, y)
                    x += 2
                elif c == "W":
                    draw(x - 1, y)
                    draw(x - 2, y)
                    x -= 2

                stdout.flush()
                if animate:
                    sleep(0.02)
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
                    term.update()
                    view_w = max(1, term.width)
                    menu_lines = 3
                    view_h = max(1, term.height - menu_lines)
                    clamp_offsets()

                    term.clear()
                    cursor.hide()
                    cursor.home()
                    _walls()
                    _logo()
                    if self.width <= 18 or self.height <= 18:
                        cursor.move_to(0, term.height - 3)
                        Graphics.set(Graphics.Color.Yellow)
                        stdout.write("⚠️ Info: Maze too small for the 42 pattern")
                        Graphics.reset()
                    cursor.move_to(0, term.height - 2)
                    stdout.write("─" * term.width)
                    for item in menu[menu_type]:
                        Graphics.menu(item)
                        stdout.write("    ")

                    # Draw E/S if visible
                    ex = self.end.x * 2 + 1
                    ey = self.end.y * 2 + 1
                    sx0 = self.start.x * 2 + 1
                    sy0 = self.start.y * 2 + 1

                    e_scr_x, e_scr_y = to_screen(ex, ey)
                    s_scr_x, s_scr_y = to_screen(sx0, sy0)

                    if in_view(s_scr_x, s_scr_y):
                        cursor.move_to(s_scr_x, s_scr_y)
                        stdout.write("S")

                    if not self.path_drawn:
                        _path(animate=True)
                        self.path_drawn = True
                    else:
                        _path()

                    if in_view(e_scr_x, e_scr_y):
                        cursor.move_to(e_scr_x, e_scr_y)
                        stdout.write("E")

                    stdout.flush()
                    refresh = False

                key = kbd.get_key()
                if key:
                    match key.lower():
                        case "q":
                            return False, None

                        # Viewport panning with arrow keys
                        case "up":
                            off_y = max(0, off_y - 1)
                            refresh = True
                        case "down":
                            out_h = len(out)
                            max_off_y = max(0, out_h - view_h)
                            off_y = min(max_off_y, off_y + 1)
                            refresh = True
                        case "left":
                            off_x = max(0, off_x - 2)
                            refresh = True
                        case "right":
                            out_w = len(out[0]) if out else 0
                            max_off_x = max(0, out_w - view_w)
                            off_x = min(max_off_x, off_x + 2)
                            refresh = True

                        case "n" if menu_type == "Main":
                            cursor.move_to(0, term.height - 1)
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
