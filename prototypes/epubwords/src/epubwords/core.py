from dataclasses import dataclass
import typing


@dataclass
class EbookChapter:
    title: str
    text: str


@dataclass
class Ebook:
    title: str
    chapters: list[EbookChapter]


class WordOccurenceInChapter(typing.NamedTuple):
    start: int
    stop: int


@dataclass
class WordInChapter:
    chapter: EbookChapter
    chapter_occurences: list[WordOccurenceInChapter]


def get_next_word(ebook_id: int, chapter_number: int) -> WordInChapter: ...
