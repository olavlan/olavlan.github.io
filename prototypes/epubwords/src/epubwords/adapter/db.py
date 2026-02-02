from typing import Protocol, NamedTuple
from epubwords import core
import datetime
from pathlib import Path


class EbookRecord(NamedTuple):
    id: int
    date_added: datetime.datetime
    title: str


class ChapterRecord(NamedTuple):
    number: int
    title: int


class DatabaseClient(Protocol):
    def add_ebook(self, ebook: core.Ebook) -> None: ...
    def get_ebook_list(self) -> list[EbookRecord]: ...
    def get_chapter_list(self, ebook_id: int) -> list[ChapterRecord]: ...
    def get_chapter(self, ebook_id: int, chapter_number: int) -> core.EbookChapter: ...


class SqliteDatabaseClient:
    db_path: Path

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path

    def add_ebook(self, ebook: core.Ebook) -> None: ...
    def get_ebook_list(self) -> list[EbookRecord]: ...
    def get_chapter_list(self, ebook_id: int) -> list[ChapterRecord]: ...
    def get_chapter(self, ebook_id: int, chapter_number: int) -> core.EbookChapter: ...


def get_database_client() -> DatabaseClient:
    from epubwords.config import environment

    return SqliteDatabaseClient(db_path=environment.sqlite_file)
