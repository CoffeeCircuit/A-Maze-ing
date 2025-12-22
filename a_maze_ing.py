#!/usr/bin/env python3
"""
Main module
"""

from sys import argv


def a_maze_ing(argv: list[str]):
    try:
        print(argv)
    except Exception as e:
        print("Error: ", e)


if __name__ == "__main__":
    a_maze_ing(argv)
