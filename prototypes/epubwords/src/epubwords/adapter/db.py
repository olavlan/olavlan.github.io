from typing import Protocol, NamedTuple
from epubwords import domain
import datetime


class EbookRecord(NamedTuple):
    id: int
    date_added: datetime.datetime
    title: str


class ChapterRecord(NamedTuple):
    number: int
    title: int


class DatabaseClient(Protocol):
    def add_ebook(self, ebook: domain.Ebook) -> None: ...
    def get_ebook_list(self) -> list[EbookRecord]: ...
    def get_chapter_list(self, ebook_id: int) -> list[ChapterRecord]: ...
    def get_chapter(
        self, ebook_id: int, chapter_number: int
    ) -> domain.EbookChapter: ...


def get_database_client() -> DatabaseClient: ...
