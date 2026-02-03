from typing import Protocol, NamedTuple, Iterator
from epubwords import core
import datetime
from pathlib import Path
import sqlite3

# TODO switch to sql files, best way to import?


class EbookRecord(NamedTuple):
    id: int
    date_added: datetime.datetime
    title: str


class ChapterRecord(NamedTuple):
    number: int
    title: int


class DatabaseClient(Protocol):
    def add_ebook(self, ebook: core.Ebook) -> None: ...
    def get_ebook_list(self) -> Iterator[EbookRecord]: ...
    def get_chapter_list(self, ebook_id: int) -> Iterator[ChapterRecord]: ...
    def get_chapter(self, ebook_id: int, chapter_number: int) -> core.EbookChapter: ...


class SqliteDatabaseClient:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self._init()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _init(self):
        create_ebook_table = """
            create table if not exists ebook(
                id integer primary key,
                title text,
                date_added text
            )
        """
        create_chapter_table = """
            create table if not exists chapter(
                ebook_id integer,
                number integer,
                title text,
                text text
            )
        """
        with self._connect() as connection:
            connection.execute(create_ebook_table)
            connection.execute(create_chapter_table)

    def add_ebook(self, ebook):
        insert_ebook = """
            insert into ebook(title, date_added) 
            values (?, ?)
        """
        insert_chapter = """
            insert into chapter(ebook_id, number, title, text)
            values (?, ?, ?, ?)
        """
        with self._connect() as connection:
            parameters = (ebook.title, datetime.datetime.now().isoformat())
            cursor = connection.execute(insert_ebook, parameters)
            ebook_id = cursor.lastrowid
            for i, chapter in enumerate(ebook.chapters, start=1):
                parameters = (ebook_id, i, chapter.title, chapter.text)
                connection.execute(insert_chapter, parameters)

    def get_ebook_list(self):
        select_ebooks = """
            select id, date_added, title 
            from ebook
        """
        with self._connect() as connection:
            cursor = connection.execute(select_ebooks)
            for row in cursor:
                yield EbookRecord(
                    id=row[0],
                    date_added=datetime.datetime.fromisoformat(row[1]),
                    title=row[2],
                )

    def get_chapter_list(self, ebook_id: int):
        select_chapters = """
            select number, title 
            from chapter 
            where ebook_id=? 
            order by number
        """
        with self._connect() as connection:
            cursor = connection.execute(select_chapters, (ebook_id,))
            for row in cursor:
                yield ChapterRecord(row[0], row[1])

    def get_chapter(self, ebook_id: int, chapter_number: int):
        select_chapter = """
            select title, text 
            from chapter 
            where ebook_id=? and number=?
        """
        with self._connect() as connection:
            parameters = (ebook_id, chapter_number)
            row = connection.execute(select_chapter, parameters).fetchone()
            return core.EbookChapter(row[0], row[1])


def get_database_client() -> DatabaseClient:
    from epubwords.config import environment

    return SqliteDatabaseClient(db_path=environment.sqlite_file)
