"""
Visualizer for the project

This will display the maze to stdout
Ref: https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797
"""

from os import PathLike
from typing import Union
from enum import StrEnum
from shutil import get_terminal_size
from sys import stdout


class Color(StrEnum):
    Black = "30m"
    Red = "31m"
    Green = "32m"
    Yellow = "33m"
    Blue = "34m"
    Magenta = "35m"
    Cyan = "36m"
    White = "37m"
    Default = "39m"
    Reset = "0m"


class Point:
    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y


class Cell(Point):
    def __init__(self, x, y, walls=0) -> None:
        super().__init__(x, y)
        self.walls = walls


class Visualizer:

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

    class Graphics:
        @staticmethod
        def set_color(color: Color, background=False):
            if background:
                background += 10
            stdout.write(f"\x1b[{color}")

        @staticmethod
        def reset(color: Color):
            stdout.write("\x1b[0m")

    def __init__(self) -> None:
        self.maze: list[list[Cell]]
        self.start: Point
        self.end: Point
        self.path: list[str]
        self.width: int
        self.height: int
        self.wall_color: Color
        self.path_color: Color

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

    def color(self, walls: Color = Color.Default, path: Color = Color.Green):
        if walls != Color.Default:
            self.wall_color = walls
        if path != Color.Green:
            self.path_color = path

    def render(self):
        term = Visualizer.Terminal()
        cursor = Visualizer.Cursor()
        term.enter_alternate()
        term.clear()
        cursor.home()

        N = 0b0001
        E = 0b0010
        S = 0b0100
        W = 0b1000
        m_h = len(self.maze)
        m_w = len(self.maze[0])
        out = [[" " for _ in range(m_w * 2 + 1)] for _ in range(m_h * 2 + 1)]

        # handling walls
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

        # handling corners
        def set_junction(arr: list[list[str]], i: int, j: int) -> None:
            mask = 0
            checks = [
                (-1, 0, "│"),  # up
                (0, 1, "─"),  # right
                (1, 0, "│"),  # down
                (0, -1, "─"),  # left
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
            for bit, (di, dj, char) in enumerate(checks):
                ni, nj = i + di, j + dj
                if 0 <= ni < len(arr) and 0 <= nj < len(arr[ni]):
                    if arr[ni][nj] == char:
                        mask |= 1 << bit
            arr[i][j] = junction_map.get(mask, " ")

        for i in range(0, m_h * 2 + 1, 2):
            for j in range(0, m_w * 2 + 1, 2):
                set_junction(out, i, j)

        def walk(path):
            for c in path:
                if c == "N":
                    cursor.left()
                    cursor.up()
                    stdout.write("░")
                    cursor.left()
                    cursor.up()
                    stdout.write("░")
                elif c == "S":
                    cursor.left()
                    cursor.down()
                    stdout.write("░")
                    cursor.left()
                    cursor.down()
                    stdout.write("░")
                elif c == "E":
                    stdout.write("░")
                    stdout.write("░")
                elif c == "W":
                    cursor.left()
                    cursor.left()
                    stdout.write("░")
                    cursor.left()
                    cursor.left()
                    stdout.write("░")

        # handling isolated cells
        for mi in range(m_h):
            for mj in range(m_w):
                i = mi * 2 + 1
                j = mj * 2 + 1
                if all(
                    [
                        out[i - 1][j] == "─",
                        out[i + 1][j] == "─",
                        out[i][j + 1] == "│",
                        out[i][j - 1] == "│",
                    ]
                ):
                    out[i][j] = "█"

        # the rendering
        for line in out:
            stdout.write("".join(line) + "\n")

        cursor.move_to(self.start.x * 2 + 1, self.start.y * 2 + 1)
        stdout.write("S")
        walk(self.path)
        cursor.move_to(self.end.x * 2 + 1, self.end.y * 2 + 1)
        stdout.write("E")
        cursor.move_to(0, term.height - 2)

        stdout.write("\x1b[1;36mQ\x1b[0muit    \x1b[1;36mN\x1b[0mew maze    ")
        stdout.write("\x1b[1;36mC\x1b[0molors    \x1b[1;36mP\x1b[0math\n")
        input("Enter to exit...")
        term.exit_alternate()
