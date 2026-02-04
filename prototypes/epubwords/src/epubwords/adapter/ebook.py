from ebooklib import epub
import ebooklib
from bs4 import BeautifulSoup
import typing


class Ebook(typing.NamedTuple):
    title: str
    chapters: list[str]


class EpubExtractor:
    def extract_ebook(self, epub_path: str) -> Ebook:
        book = epub.read_epub(epub_path)
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
