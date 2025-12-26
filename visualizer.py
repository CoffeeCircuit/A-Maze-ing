"""
Visualizer for the project

This will display the maze to stdout
Ref: https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797
"""

from os import PathLike
from typing import Union
from enum import IntEnum
from shutil import get_terminal_size
from sys import stdout, stdin
from select import select
from termios import tcgetattr, tcsetattr, TCSADRAIN
from tty import setcbreak


class Point:
    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y


class Cell(Point):
    def __init__(self, x, y, walls=0) -> None:
        super().__init__(x, y)
        self.walls = walls


class Graphics:
    class Color(IntEnum):
        Red = 31
        Green = 32
        Yellow = 33
        Blue = 34
        Magenta = 35
        Cyan = 36
        Default = 39

    @staticmethod
    def set(color: Color, background=False):
        if background:
            stdout.write(f"\x1b{color};{color + 10}m")
        else:
            stdout.write(f"\x1b[{color}m")

    @staticmethod
    def reset():
        stdout.write("\x1b[0m")

    @staticmethod
    def menu(item: str):
        Graphics.set(Graphics.Color.Cyan)
        stdout.write(item[0])
        Graphics.reset()
        stdout.write(item[1:])


class Visualizer:
    menu = {
        "Main": ["New maze", "Color", "Path", "Quit"],
        "Color": {
            "Walls": ["Red", "Green", "Yellow", "Blue", "Magenta", "Cyan"],
            "Path": ["Red", "Green", "Yellow", "Blue", "Magenta", "Cyan"],
            "Logo": ["Red", "Green", "Yellow", "Blue", "Magenta", "Cyan"],
        },
    }

    class Keyboard:
        """
        Event handler for the keyboard
        """

        @staticmethod
        def enable_raw_mode():
            fd = stdin.fileno()
            old = tcgetattr(fd)
            setcbreak(fd)
            return old

        @staticmethod
        def disable_raw_mode(old):
            tcsetattr(stdin.fileno(), TCSADRAIN, old)

        @staticmethod
        def get_key():

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
        @staticmethod
        def up(n=1):
            stdout.write(f"\x1b[{n}A")

        @staticmethod
        def up_and_begining(n=1):
            stdout.write(f"\x1b[{n}F")

        @staticmethod
        def down(n=1):
            stdout.write(f"\x1b[{n}B")

        @staticmethod
        def right(n=1):
            stdout.write(f"\x1b[{n}C")

        @staticmethod
        def left(n=1):
            stdout.write(f"\x1b[{n}D")

        @staticmethod
        def save():
            stdout.write("\x1b7")

        @staticmethod
        def load():
            stdout.write("\x1b8")

        @staticmethod
        def hide():
            stdout.write("\x1b[?25l")

        @staticmethod
        def show():
            stdout.write("\x1b[?25h")

        @staticmethod
        def home() -> None:
            stdout.write("\x1b[H")

        @staticmethod
        def move_to(x, y):
            stdout.write(f"\x1b[{y+1};{x+1}H")
        
        @staticmethod
        def clear_line():
            stdout.write("\x1b[2K\x1b[0G")

    class Terminal:
        def __init__(self) -> None:
            self.width, self.height = get_terminal_size()

        def update(self):
            self.width, self.height = get_terminal_size()

        @staticmethod
        def clear() -> None:
            stdout.write("\x1b[2J")

        @staticmethod
        def enter_alternate() -> None:
            stdout.write("\x1b[?1049h")

        @staticmethod
        def exit_alternate() -> None:
            stdout.write("\x1b[?1049l")

    def __init__(self) -> None:
        self.maze: list[list[Cell]]
        self.start: Point
        self.end: Point
        self.path: list[str]
        self.width: int
        self.height: int
        self.wall_color: Graphics.Color = Graphics.Color.Default
        self.path_color: Graphics.Color = Graphics.Color.Green
        self.logo_color: Graphics.Color = Graphics.Color.Yellow
        self.path_symbol = "░"

    def read(self, file: Union[str, PathLike]) -> None:
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

    def render(self):
        term = Visualizer.Terminal()
        cursor = Visualizer.Cursor()
        N = 0b0001
        E = 0b0010
        S = 0b0100
        W = 0b1000
        m_h = len(self.maze)
        m_w = len(self.maze[0])
        out = [[" " for _ in range(m_w * 2 + 1)] for _ in range(m_h * 2 + 1)]

        def _walls():

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

        def _logo():
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

        def _path():
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
        menu = Visualizer.menu
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
                            break
                        case 'n' if menu_type == "Main":
                            cursor.clear_line()
                            cursor.show()
                            Visualizer.Keyboard.disable_raw_mode(mode)
                            return input("Enter seed: ")
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
        return 0
