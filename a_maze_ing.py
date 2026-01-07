#!/usr/bin/env python3
"""
Main module
"""

from sys import argv, exit
from pathfinder import PathFinder
import mazegen
from mazegen import MazeGenerator, Visualizer


def a_maze_ing(argv: list[str]) -> None:
    """Run maze generator and visualizer.

    Args:
        config_file: Path to configuration file.
    """
    if len(argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt")
        exit(1)
    try:
        maze = MazeGenerator()
        maze.read()
        assert maze.output is not None
        regenerate = True
        while regenerate:
            maze.generate()
            maze.write()
            path = PathFinder(maze.output)
            path.save_path()
            vis = Visualizer()
            vis.read(maze.output)
            regenerate, maze.seed = vis.render()
            maze.reset()
    except Exception as e:
        print(f"{type(e).__name__}: {e}")
        exit(1)


if __name__ == "__main__":
    print(f"Running mazegen from: {mazegen.__file__}")
    a_maze_ing(argv)
