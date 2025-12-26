from select import select
from sys import stdin
from termios import tcgetattr, tcsetattr, TCSADRAIN
from tty import setcbreak


def get_key():
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


def enable_raw_mode():
    fd = stdin.fileno()
    old = tcgetattr(fd)
    setcbreak(fd)
    return old


def disable_raw_mode(old):
    tcsetattr(stdin.fileno(), TCSADRAIN, old)


old = enable_raw_mode()
try:
    while True:
        key = get_key()
        if key:
            print("Pressed:", f"{key}")
finally:
    disable_raw_mode(old)
