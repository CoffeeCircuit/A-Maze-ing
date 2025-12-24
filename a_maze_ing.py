#!/usr/bin/env python3
"""
Main module
"""

from sys import argv, exit
from parser import ConfigParser, ParsingError
from visualizer import Visualizer


def a_maze_ing(argv: list[str]):
    if len(argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt")
        exit(1)
    config_file = argv[1]
    parser = ConfigParser()
    try:
        parser.parse(config_file)
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

    vis = Visualizer()
    vis.read(parser.output_file)
    vis.render()


if __name__ == "__main__":
    a_maze_ing(argv)
