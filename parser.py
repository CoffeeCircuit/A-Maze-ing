"""
Parser for the maze
"""


class Point:
    """
    2D Point class (x, y)
    """
    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y


def parse_config(file: str) -> dict[str, int | Point | str]:
    """
    Parser for the configuration file. The file must contain WIDTH, HEIGHT,
    ENTRY, EXIT, OUTPUT_FILE, PERFECT

    :param file: mandatory config.txt
    :type file: str
    :return: Returns a dictionary of either int or txt or of a Point class
    :rtype: dict[str, int | Point | str]
    """
    config = {}
    with open(file, "r") as fp:
        data = fp.read()
    for line in data.split("\n"):
        if line == "":
            continue
        key, val = line.split("=")
        if "," in val:
            x, y = [int(v) for v in val.split(",")]
            config[key] = Point(x, y)
        elif "." in val:
            config[key] = val
        elif "True" in val:
            config[key] = True
        elif "False" in val:
            config[key] = False
        else:
            config[key] = int(val)
    mandatory_keys = {
        "WIDTH",
        "HEIGHT",
        "ENTRY",
        "EXIT",
        "OUTPUT_FILE",
        "PERFECT",
    }
    if len(set(config.keys()).intersection(mandatory_keys)) < 6:
        raise KeyError("Missing mandatory keys")
    return config


def print_config(config: dict[str, int | Point | str]):
    for key, val in config.items():
        if isinstance(val, Point):
            print(f"{key} = {val.x}, {val.y}")
        else:
            print(f"{key} = {val}")
