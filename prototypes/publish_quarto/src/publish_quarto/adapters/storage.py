import json
from pathlib import Path
from typing import Any, Mapping


class LocalFileStorage:
    path: Path

    def __init__(self) -> None:
        self.path = Path.cwd() / ".org.json"
        if not self.path.exists():
            with self.path.open("w") as f:
                json.dump({}, f)

    def _load(self) -> dict[str, dict[str, Any]]:
        with self.path.open() as f:
            return json.load(f)

    def _save(self, data: dict[str, dict[str, Any]]) -> None:
        with self.path.open("w") as f:
            json.dump(data, f, indent=2)

    def update(self, key: str, data: Mapping[str, Any]) -> None:
        store = self._load()

        current = store.get(key, {})
        for field, value in data.items():
            if value is not None:
                current[field] = value

        store[key] = current
        self._save(store)

    def get(self, key: str) -> dict[str, Any]:
        store = self._load()
        return store.get(key, {}).copy()
