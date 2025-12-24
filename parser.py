"""
Parser for the maze configuration file.
"""

from os import PathLike
from typing import Union


class ParsingError(Exception):
    """Exception raised for configuration parsing errors."""

    def __init__(self, message: str, key: str | None = None) -> None:
        """Initialize ParsingError.

        Args:
            message: Error message.
            key: Configuration key where error occurred (optional).
        """
        if key:
            super().__init__(f"Key '{key}': {message}")
        else:
            super().__init__(message)
        self.key = key


class ConfigParser:
    """
    Parser for the configuration file. The file must contain WIDTH, HEIGHT,
    ENTRY, EXIT, OUTPUT_FILE, PERFECT

    :param file: mandatory config.txt
    :type file: str
    :return: Returns a dictionary of either int or txt or of a Point class
    :rtype: dict[str, int | Point | str]
    """

    def __init__(self) -> None:
        """Initialize ConfigParser with default values."""
        self.width: int | None = None
        self.height: int | None = None
        self.entry: tuple[int, int] | None = None
        self.exit: tuple[int, int] | None = None
        self.output_file: Union[str, PathLike[str]] = ""
        self.perfect: bool | None = None
        self.seed: int | None = None

    def parse(self, file: Union[str, PathLike[str]]) -> None:
        """Parse configuration file.

        Args:
            file: Path to configuration file.
        """
        with open(file, "r") as fp:
            data = fp.read()
        for line in data.split("\n"):
            if not line or line.startswith('#'):
                continue
            if '=' not in line:
                raise ParsingError(
                    f"Invalid format: '{line}' (expected KEY=VALUE)")

            key, val = line.split("=", maxsplit=1)
            key = key.strip()
            val = val.strip()

            if key == "WIDTH":
                self.width = int(val)
            elif key == "HEIGHT":
                self.height = int(val)
            elif key == "ENTRY":
                x, y = map(int, val.split(","))
                self.entry = (x, y)
            elif key == "EXIT":
                x, y = map(int, val.split(","))
                self.exit = (x, y)
            elif key == "OUTPUT_FILE":
                self.output_file = val
            elif key == "PERFECT":
                self.perfect = val == "True"
            elif key == "SEED":
                self.seed = int(val)

        self._validate()

    def _validate(self) -> None:
        """Validate that all required keys are present and values are
            consistent.

        Raises:
            ParsingError: If validation fails.
        """
        # Check mandatory keys
        missing = []
        if self.width is None:
            missing.append("WIDTH")
        if self.height is None:
            missing.append("HEIGHT")
        if self.entry is None:
            missing.append("ENTRY")
        if self.exit is None:
            missing.append("EXIT")
        if not self.output_file:
            missing.append("OUTPUT_FILE")
        if self.perfect is None:
            missing.append("PERFECT")

        if missing:
            raise ParsingError(f"Missing required keys: {', '.join(missing)}")

        # None checks (to satisfy type checker)
        if self.width is None or self.height is None:
            return
        if self.entry is None or self.exit is None:
            return

        # Validate positive dimensions
        if self.width < 1:
            raise ParsingError(f"must be positive, got {self.width}", "WIDTH")
        if self.height < 1:
            raise ParsingError(
                f"must be positive, got {self.height}", "HEIGHT")

        # Validate minimum size
        if self.width * self.height < 2:
            raise ParsingError(
                f"Maze too small ({self.width}x{self.height})"
            )

        # Validate entry coordinates
        entry_x, entry_y = self.entry
        if entry_x < 0 or entry_y < 0:
            raise ParsingError(
                f"coordinates can't be negative ({entry_x},{entry_y})", "ENTRY"
            )
        if not (0 <= entry_x < self.width and 0 <= entry_y < self.height):
            raise ParsingError(
                f"coordinates ({entry_x},{entry_y}) outside maze bounds "
                f"(0-{self.width-1}, 0-{self.height-1})", "ENTRY"
            )

        # Validate exit coordinates
        exit_x, exit_y = self.exit
        if exit_x < 0 or exit_y < 0:
            raise ParsingError(
                f"coordinates can't be negative({exit_x},{exit_y})", "EXIT"
            )
        if not (0 <= exit_x < self.width and 0 <= exit_y < self.height):
            raise ParsingError(
                f"coordinates ({exit_x},{exit_y}) outside maze bounds "
                f"(0-{self.width-1}, 0-{self.height-1})", "EXIT"
            )

        # Check entry != exit
        if self.entry == self.exit:
            raise ParsingError("Entry and exit must be different cells")

        # Warning for "42" pattern
        if self.width < 7 or self.height < 7:
            print(f"Warning: Maze {self.width}x{self.height} may be too small "
                  f"for '42' pattern (recommended: 7x7 minimum)")
