"""
Visualizer for the project

This will display the maze to stdout
Ref: https://gist.github.com/fnky/458719343aabd01cfb17a3a4f7296797
"""

from enum import StrEnum
from shutil import get_terminal_size
from sys import stdout


class WallGraphics(StrEnum):
    Horirzontal = "─"
    Vertical = "│"
    LTCor = "╭"
    LBCor = "╰"
    RTCor = "╮"
    RBCor = "╯"
    Cross = "┼"


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

    def read(self, file: str) -> None:
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
            path = [c for c in fp.readline().strip()]
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
        term.update()

        if self.width > term.width or self.height > term.height:
            raise Exception("Maze too big")


viz = Visualizer()
viz.read("output_maze.txt")
term = Visualizer.Terminal()
term.enter_alternate()
viz.Cursor.move_to(1, 1)
viz.render()
input()
term.exit_alternate()
