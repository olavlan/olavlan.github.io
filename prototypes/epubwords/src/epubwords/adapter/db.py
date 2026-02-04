import typing
import datetime


class Ebook(typing.NamedTuple):
    title: str
    chapters: list[str]


class EbookRecord(typing.NamedTuple):
    id: int
    date_added: datetime.datetime
    title: str


class ChapterRecord(typing.NamedTuple):
    ebook_id: int
    chapter_number: int
    start: str
    end: str


class DatabaseClient(typing.Protocol):
    def add_ebook(self, ebook: Ebook) -> None: ...
    def get_ebook_list(self) -> typing.Iterator[EbookRecord]: ...
    def get_chapter_list(self, ebook_id: int) -> typing.Iterator[ChapterRecord]: ...
    def get_chapter(self, ebook_id: int, chapter_number: int) -> str: ...


def get_database_client() -> DatabaseClient:
    from epubwords.config import environment

    return SqliteDatabaseClient(db_path=environment.sqlite_file)
