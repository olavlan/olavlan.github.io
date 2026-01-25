import json
from pathlib import Path
from typing import Any, Mapping


class LocalFileStorage:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w") as f:
            json.dump({}, f)

    def _load(self) -> dict[str | int, dict[str, Any]]:
        with self.path.open() as f:
            return json.load(f)

    def _save(self, data: dict[str | int, dict[str, Any]]) -> None:
        with self.path.open("w") as f:
            json.dump(data, f, indent=2)

    def update(self, key: str | int, data: Mapping[str, Any]) -> None:
        store = self._load()

        current = store.get(key, {})
        for field, value in data.items():
            if value is not None:
                current[field] = value

        store[key] = current
        self._save(store)

    def get(self, key: str | int) -> dict[str, Any]:
        store = self._load()
        return store.get(key, {}).copy()


def get_local_file_storage(document_path: str):
    parent = Path(document_path).parent
    return LocalFileStorage(parent / ".org.json")
