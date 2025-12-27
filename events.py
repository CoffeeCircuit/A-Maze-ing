"""
Keyboard event handler for raw terminal input.

Provides utilities for capturing keyboard input in raw mode,
including support for special keys like arrow keys.
"""

from select import select
from sys import stdin
from termios import tcgetattr, tcsetattr, TCSADRAIN
from tty import setcbreak
from typing import Any


def get_key() -> str | None:
    """Get a single keypress without blocking.

    Returns:
        Key character, special key name ('up'), escape sequence, or None if no
        key pressed.
    """
    dr, _, _ = select([stdin], [], [], 0)
    if not dr:
        return None

    ch = stdin.read(1)

    if ch == "\x1b":  # ESC
        ch1 = stdin.read(1)
        ch2 = stdin.read(1)
        print(f"{ch1=}, {ch2=}")
        if ch1 == "[" and ch2 == "A":
            return "up"

        return ch + ch1 + ch2  # fallback

    return ch


def enable_raw_mode() -> list[Any]:
    """Enable raw keyboard input mode.

    Disables line buffering and echo, allowing immediate key capture.

    Returns:
        Previous terminal attributes for restoration.
    """
    fd = stdin.fileno()
    old = tcgetattr(fd)
    setcbreak(fd)
    return old


def disable_raw_mode(old: list[Any]) -> None:
    """Restore terminal to normal mode.

    Args:
        old: Previous terminal attributes from enable_raw_mode().
    """
    tcsetattr(stdin.fileno(), TCSADRAIN, old)


old = enable_raw_mode()
try:
    while True:
        key = get_key()
        if key:
            print("Pressed:", f"{key}")
finally:
    disable_raw_mode(old)
