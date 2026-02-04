from dataclasses import dataclass
import os

PREFIX = "EPUBWORDS"


@dataclass
class Environment:
    sqlite_file: str


def _initialize_environment():
    sqlite_file = os.environ[f"{PREFIX}_SQLITE_FILE"]
    return Environment(
        sqlite_file=sqlite_file,
    )


environment = _initialize_environment()
