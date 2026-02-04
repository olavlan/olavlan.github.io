import datetime
import typing
import sqlite3
import pathlib


# Protocol and Type definitions provided in the prompt
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
    start_of_text: str
    end_of_text: str


class DatabaseClient(typing.Protocol):
    def add_ebook(self, ebook: Ebook) -> None: ...
    def get_ebook_list(self) -> typing.Iterator[EbookRecord]: ...
    def get_chapter_list(self, ebook_id: int) -> typing.Iterator[ChapterRecord]: ...
    def get_chapter(self, ebook_id: int, chapter_number: int) -> str: ...


class SQLiteDatabaseClient:
    def __init__(self, database_path: str):
        self.connection = sqlite3.connect(
            database_path, detect_types=sqlite3.PARSE_DECLTYPES
        )
        self.connection.row_factory = sqlite3.Row
        self._initialize_schema()

    def _initialize_schema(self) -> None:
        schema_path = pathlib.Path(__file__).parent / "schema.sql"
        schema_script = schema_path.read_text()
        self.connection.executescript(schema_script)

    def add_ebook(self, ebook: Ebook) -> None:
        cursor = self.connection.cursor()

        insert_ebook_query = "INSERT INTO ebooks (title) VALUES (?)"
        cursor.execute(insert_ebook_query, (ebook.title,))

        new_ebook_id = cursor.lastrowid

        insert_chapter_query = (
            "INSERT INTO chapters (ebook_id, chapter_number, content) VALUES (?, ?, ?)"
        )
        for index, content in enumerate(ebook.chapters):
            chapter_number = index + 1
            cursor.execute(
                insert_chapter_query, (new_ebook_id, chapter_number, content)
            )

        self.connection.commit()

    def get_ebook_list(self) -> typing.Iterator[EbookRecord]:
        query = "SELECT id, date_added, title FROM ebooks ORDER BY date_added DESC"
        cursor = self.connection.execute(query)

        for row in cursor:
            yield EbookRecord(
                id=row["id"], date_added=row["date_added"], title=row["title"]
            )

    def get_chapter_list(self, ebook_id: int) -> typing.Iterator[ChapterRecord]:
        query = (
            "SELECT ebook_id, chapter_number, content FROM chapters WHERE ebook_id = ?"
        )
        cursor = self.connection.execute(query, (ebook_id,))

        for row in cursor:
            content = row["content"]
            yield ChapterRecord(
                ebook_id=row["ebook_id"],
                chapter_number=row["chapter_number"],
                start_of_text=content[:50],
                end_of_text=content[-50:],
            )

    def get_chapter(self, ebook_id: int, chapter_number: int) -> str:
        query = "SELECT content FROM chapters WHERE ebook_id = ? AND chapter_number = ?"
        cursor = self.connection.execute(query, (ebook_id, chapter_number))
        result = cursor.fetchone()

        if not result:
            return ""

        return result["content"]


def get_database_client() -> DatabaseClient:
    from epubwords.config import environment

    return SQLiteDatabaseClient(database_path=environment.sqlite_file)
