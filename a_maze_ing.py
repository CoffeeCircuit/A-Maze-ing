#!/usr/bin/env python3
"""
Main module
"""

from sys import argv, exit
from parser import ConfigParser, ParsingError
from visualizer import Visualizer
from mazegen_imperfect import ImperfectMazeGenerator


def a_maze_ing(argv: list[str]):
    """Run maze generator and visualizer.

    Args:
        config_file: Path to configuration file.
    """
    if len(argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt")
        exit(1)
    config_file = argv[1]
    config = ConfigParser()
    try:
        config.parse(config_file)
        maze = ImperfectMazeGenerator(config)
        maze.generate()
        maze.export_ouput()

        vis = Visualizer()
        vis.read(config.output_file)
        vis.render()
    except FileNotFoundError as e:
        print(f"Error: Configuration file not found: {config_file}")
        exit(1)
    except ParsingError as e:
        print(f"Configuration Error: {e}")
        exit(1)
    except ValueError as e:
        print(f"Invalid value in configuration: {e}")
        exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        exit(1)


if __name__ == "__main__":
    a_maze_ing(argv)
