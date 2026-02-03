from fastapi import APIRouter
from fastapi import Depends
from fastapi.responses import HTMLResponse

from fastapi import UploadFile, File
from epubwords.adapter import db

router = APIRouter()


@router.post("/upload", response_class=HTMLResponse)
def upload_file(
    uploaded_file: UploadFile = File(),
    database_client: db.DatabaseClient = Depends(db.get_database_client),
) -> str:
    content = uploaded_file.file.read()
    # extract metadata and chapters with an epub extractor
    # add data to database
    return "File uploaded."


@router.get("/", response_class=HTMLResponse)
def list_ebooks(
    database_client: db.DatabaseClient = Depends(db.get_database_client),
) -> str:
    ebook_records = database_client.get_ebook_list()

    add_ebook_html = """
        <form action="/upload" method="post" enctype="multipart/form-data">
          <input type="file" name="file">
          <button type="submit">Upload</button>
        </form>
    """

    html = f"""
        <table>
            <thead><tr><td>{add_ebook_html}</td></tr></thead>
            <tbody>
    """
    for e in ebook_records:
        html += f"""
            <tr>
                <td><a href="/{e.id}">{e.title}</a></td>
            </tr>
        """
    html += """
            </tbody>
        </table>
    """

    return html


@router.get("/{ebook_id}", response_class=HTMLResponse)
def list_ebook_chapters(
    ebook_id: int,
    database_client: db.DatabaseClient = Depends(db.get_database_client),
) -> str:
    chapter_records = database_client.get_chapter_list(ebook_id)

    html = "<table><tbody>"
    for c in chapter_records:
        html += f"""
            <tr>
                <td><a href="/{ebook_id}/{c.number}">{c.title}</a></td>
            </tr>
        """
    html += "</tbody></table>"

    return html


@router.get("/{ebook_id}/{chapter_number}", response_class=HTMLResponse)
def show_chapter_words(
    ebook_id: int,
    chapter_number: int,
    database_client: db.DatabaseClient = Depends(db.get_database_client),
) -> str:
    chapter = database_client.get_chapter(ebook_id, chapter_number)
    # extract words from chapter
    words = []

    html = "<table><tbody>"
    for word in words:
        html += f"""
            <tr>
                <td><a href="/{ebook_id}/{chapter_number}/{word}">{word}</a></td>
            </tr>
        """
    html += "</tbody></table>"

    return html


@router.get("/{book_id}/{chapter_number}/{word}", response_class=HTMLResponse)
def get_word_explanation(
    book_id: str,
    chapter_number: int,
    word: str,
) -> str:
    return word
