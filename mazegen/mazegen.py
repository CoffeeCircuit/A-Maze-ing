from typing import Union, TypedDict, cast
from pathlib import Path
from os import PathLike, access, R_OK
from .dfs import dfs
from .hak import hak


class Config(TypedDict):
    width: int
    height: int
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str
    perfect: bool
    seed: int | None
    algorithm: str | None


class MazeGenerator:
    def __init__(self) -> None:
        self._grid: list[list[int]] | None = None
        self._output: Union[str, PathLike[str]] | None = None
        self._width: int | None = None
        self._height: int | None = None
        self._entry: tuple[int, int] | None = None
        self._exit: tuple[int, int] | None = None
        self._perfect: bool | None = None
        self._seed: int | None = None
        self._algorithm: str | None = None

    @property
    def grid(self) -> list[list[int]] | None:
        return self._grid

    @grid.setter
    def grid(self, grid: list[list[int]]) -> None:
        self._grid = grid

    @property
    def output(self) -> Union[str, PathLike[str]] | None:
        return self._output

    @output.setter
    def output(self, file: Union[str, PathLike[str]]) -> None:
        self._output = file

    @property
    def width(self) -> int | None:
        return self._width

    @width.setter
    def width(self, width: int) -> None:
        self._width = width

    @property
    def height(self) -> int | None:
        return self._height

    @height.setter
    def height(self, height: int) -> None:
        self._height = height

    @property
    def entry(self) -> tuple[int, int] | None:
        return self._entry

    @entry.setter
    def entry(self, entry: tuple[int, int]) -> None:
        self._entry = entry

    @property
    def exit(self) -> tuple[int, int] | None:
        return self._exit

    @exit.setter
    def exit(self, exit: tuple[int, int]) -> None:
        self._exit = exit

    @property
    def perfect(self) -> bool | None:
        return self._perfect

    @perfect.setter
    def perfect(self, perfect: bool) -> None:
        self._perfect = perfect

    @property
    def seed(self) -> int | None:
        return self._seed

    @seed.setter
    def seed(self, seed: int | None = None) -> None:
        self._seed = seed

    @property
    def algorithm(self) -> str | None:
        return self._algorithm

    @algorithm.setter
    def algorithm(self, algorithm: str) -> None:
        self._algorithm = algorithm

    def read(self, file: Union[str, PathLike[str]] = "config.txt") -> None:
        path = Path(file)

        if not path.exists():
            raise FileNotFoundError(f"No such file: {file}")

        if not access(path, R_OK):
            raise PermissionError(f"No read permission for file: {file}")

        mandatory_keys = {
            "width",
            "height",
            "entry",
            "exit",
            "output_file",
            "perfect",
        }

        raw: dict[str, object] = {}

        with open(path, "r") as fp:
            for raw_line in fp:
                line = raw_line.strip()

                if not line or line.startswith("#") or "=" not in line:
                    continue

                key, val = map(str.strip, line.split("=", 1))
                key = key.lower()

                if val.strip("-").isdigit():
                    iv = int(val)
                    if iv < 0:
                        raise ValueError(f"{key} must be non-negative")
                    raw[key] = iv
                    continue

                lowered = val.lower()
                if lowered in ("true", "1", "on", "yes"):
                    raw[key] = True
                    continue
                if lowered in ("false", "0", "off", "no"):
                    raw[key] = False
                    continue

                if "," in val:
                    parts = [p.strip() for p in val.split(",")]
                    if len(parts) != 2:
                        msg = f"{key} must contain exactly two integers"
                        raise ValueError(msg)
                    if not all(p.strip("-").isdigit() for p in parts):
                        raise ValueError(f"{key} must contain only integers")
                    ints = tuple(map(int, parts))
                    if any(x < 0 for x in ints):
                        msg = f"{key} must contain non-negative integers"
                        raise ValueError(msg)
                    raw[key] = ints
                    continue

                raw[key] = val

        missing = mandatory_keys - raw.keys()
        if missing:
            msg = ", ".join(m.upper() for m in missing)
            raise KeyError(f"Missing keys: {msg}")

        try:
            config: Config = {
                "width": cast(int, raw["width"]),
                "height": cast(int, raw["height"]),
                "entry": cast(tuple[int, int], raw["entry"]),
                "exit": cast(tuple[int, int], raw["exit"]),
                "output_file": cast(str, raw["output_file"]),
                "perfect": cast(bool, raw["perfect"]),
                "seed": cast(int | None, raw.get("seed")),
                "algorithm": cast(str | None, raw.get("algorithm")),
            }
        except Exception as e:
            raise ValueError(f"Invalid configuration: {e}")

        ex, ey = config["entry"]
        if not (0 <= ex < config["width"] and 0 <= ey < config["height"]):
            raise ValueError("entry coordinates out of bounds")

        ex, ey = config["exit"]
        if not (0 <= ex < config["width"] and 0 <= ey < config["height"]):
            raise ValueError("exit coordinates out of bounds")

        if config["entry"] == config["exit"]:
            raise ValueError("entry and exit must be different")

        i_width = range(config["width"])
        i_height = range(config["height"])
        self._grid = [[15 for _ in i_width] for _ in i_height]
        self._width = config["width"]
        self._height = config["height"]
        self._entry = config["entry"]
        self._exit = config["exit"]
        self._output = config["output_file"]
        self._perfect = config["perfect"]
        self._seed = config["seed"]
        self._algorithm = config["algorithm"]

    def write(self) -> None:
        if self._grid is None or self._output is None:
            return

        with open(self._output, "w") as fp:
            for row in self._grid:
                fp.write("".join(hex(v)[2:].upper() for v in row))
                fp.write("\n")

            fp.write("\n")

            if self._entry:
                fp.write(f"{self._entry[0]}, {self._entry[1]}\n")
            if self._exit:
                fp.write(f"{self._exit[0]}, {self._exit[1]}\n")

    def generate(self) -> None:
        match self._algorithm:
            case "dfs":
                dfs(self)
            case "hak":
                hak(self)
            case _:
                dfs(self)

    def reset(self) -> None:
        if self._width is None or self._height is None:
            raise ValueError("Width/height not set")
        i_width = range(self._width)
        i_height = range(self._height)
        self._grid = [[15 for _ in i_width] for _ in i_height]
