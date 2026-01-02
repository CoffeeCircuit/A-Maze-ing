from typing import Union
from pathlib import Path
from os import PathLike, access, R_OK
from .dfs import dfs
from .hak import hak


class MazeGenerator:
    def __init__(self) -> None:
        self._grid: list[list[int]] | None = None
        self._output: Union[str, PathLike[str]] | None = None
        self._width: int | None = None
        self._height: int | None = None
        self._entry: tuple[int, int] | None = None
        self._exit: tuple[int, int] | None = None
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
        self.output = file

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
    def entry(sefl, entry: tuple[int, int]) -> None:
        sefl._entry = entry

    @property
    def exit(self) -> tuple[int, int] | None:
        return self._exit

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
        """
        Reads the configuration file. By default the file is config.txt.
        The file must contain WIDTH, HEIGHT, ENTRY, EXIT, OUTPUT_FILE, PERFECT
        The file can also contain optional SEED and ALGORITHM = [dfs | hak]

        :param self: Reference to class instance
        :param file: The target configuration file (config.txt by default)
        :type file: Union[str, PathLike[str]]
        """
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

        data = {}

        with open(path, "r") as fp:
            for raw_line in fp:
                line = raw_line.strip()

                if not line or line.startswith("#") or "=" not in line:
                    continue

                key, val = map(str.strip, line.split("=", 1))
                key = key.lower()

                if val.strip("-").isdigit():
                    if int(val) < 0:
                        msg = f"{key} must contain only non-negative integers"
                        raise ValueError(msg)
                    data[key] = int(val)
                elif val.lower() in ("true", "1", "on", "yes"):
                    data[key] = True
                elif val.lower() in ("false", "0", "off", "no"):
                    data[key] = False
                elif "," in val:
                    parts = [p.strip() for p in val.split(",")]
                    if len(parts) != 2:
                        msg = f"{key} must contain exactly two integers"
                        raise ValueError(msg)
                    if not all(p.strip("-").isdigit() for p in parts):
                        raise ValueError(f"{key} must contain only integers")
                    ints = tuple(map(int, parts))
                    if any(x < 0 for x in ints):
                        msg = f"{key} must contain only non-negative integers"
                        raise ValueError(msg)
                    data[key] = ints
                else:
                    data[key] = val

        missing = mandatory_keys - data.keys()
        if missing:
            msg = ", ".join(m.upper() for m in missing)
            raise KeyError(f"Missing keys: {msg}")

        if data.get("width") == 0 or data.get("height") == 0:
            raise ValueError("width and/or height must be greater than zero")

        if data.get("entry") == data.get("exit"):
            raise ValueError("Entry and and exit must be different")

        entry = data.get("entry")
        exit_ = data.get("exit")
        width = data.get("width")
        height = data.get("height")

        if entry and width and height:
            ex, ey = entry
            if not (0 <= ex < width and 0 <= ey < height):
                raise ValueError("entry coordinates are out of bounds")

        if exit_ and width and height:
            ex, ey = exit_
            if not (0 <= ex < width and 0 <= ey < height):
                raise ValueError("exit coordinates are out of bounds")

        if not isinstance(data.get("perfect"), bool):
            raise ValueError("perfect must be true/false")

        if "algorithm" in data:
            if data.get("algorithm") not in {"dfs", "hak"}:
                raise ValueError("algorithm must be one of: dfs, hak")

        for k in ("entry", "exit"):
            value = data.get(k)
            if not isinstance(value, tuple):
                msg = f"{k} must be a tuple, got {type(value).__name__}"
                raise ValueError(msg)

        # initialize the grid with all the cell having closed walls
        if width and height:
            self._grid = [[15 for _ in range(width)] for _ in range(height)]

        self._width = data.get("width")
        self._height = data.get("height")
        self._entry = data.get("entry")
        self._exit = data.get("exit")
        self._output = data.get("output_file")
        self._seed = data.get("seed")
        self._algorithm = data.get("algorithm")

    def write(self) -> None:
        """
        Write the maze configuration to the output_file from config.txt
        """
        if self._grid and self._output:
            with open(self._output, "w") as fp:
                for row in self._grid:
                    fp.write("".join([hex(v)[2:].upper() for v in row]))
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
        assert self._width is not None
        assert self._height is not None
        width = self._width
        height = self._height
        self._grid = [[15 for _ in range(width)] for _ in range(height)]
