import sys
import termios
import tty
import select


def get_key():
    dr, _, _ = select.select([sys.stdin], [], [], 0)
    if not dr:
        return None

    ch = sys.stdin.read(1)

    if ch == "\x1b":  # ESC
        ch1 = sys.stdin.read(1)
        ch2 = sys.stdin.read(1)
        print(f"{ch1=}, {ch2=}")
        if ch1 == "[" and ch2 == "A":
            return "up"

        return ch + ch1 + ch2  # fallback

    return ch


def enable_raw_mode():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    tty.setcbreak(fd)
    return old


def disable_raw_mode(old):
    termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old)


old = enable_raw_mode()
try:
    while True:
        key = get_key()
        if key:
            print("Pressed:", f"{key}")
finally:
    disable_raw_mode(old)
