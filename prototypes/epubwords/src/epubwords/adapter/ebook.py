from ebooklib import epub
import ebooklib
from bs4 import BeautifulSoup
import typing
from dataclasses import dataclass


class Ebook(typing.NamedTuple):
    title: str
    chapters: list[str]


class EbookExtractor(typing.Protocol):
    def extract_ebook(self, file_path: str) -> Ebook: ...


@dataclass
class EpubExtractor:
    def extract_ebook(self, file_path: str) -> Ebook:
        book = epub.read_epub(file_path)
        return Ebook(
            title=book.get_metadata("DC", "title"),
            chapters=list(self._extract_chapters(book)),
        )

    @staticmethod
    def _extract_chapters(book: epub.EpubBook) -> typing.Iterator[str]:
        for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
            soup = BeautifulSoup(item.get_content(), "html.parser")
            text = soup.get_text().strip()
            if not text:
                continue
            yield text


def get_ebook_extractor() -> EbookExtractor:
    return EpubExtractor()
