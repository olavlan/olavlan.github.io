from dataclasses import dataclass
import os
from pathlib import Path

PREFIX = "EPUBWORDS"


@dataclass
class Environment:
    sqlite_file: Path


def _initialize_environment():
    sqlite_file = os.environ[f"{PREFIX}_SQLITE_FILE"]
    return Environment(
        sqlite_file=Path(sqlite_file),
    )


environment = _initialize_environment()
