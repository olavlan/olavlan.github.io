from fastapi import Depends


import fastapi
import jinja2
from starlette import responses

from epubwords.adapter import db


environment = jinja2.Environment(
    loader=jinja2.PackageLoader("epubwords", "webapp/ebook")
)
router = fastapi.APIRouter()


@router.post("/upload", response_class=responses.HTMLResponse)
def upload_file(
    uploaded_file: fastapi.UploadFile = fastapi.File(),
    database_client: db.DatabaseClient = fastapi.Depends(db.get_database_client),
) -> str:
    content = uploaded_file.file.read()
    # extract metadata and chapters with an epub extractor
    # add data to database
    return "File uploaded."


@router.get("/", response_class=responses.HTMLResponse)
def list_ebooks(
    request: fastapi.Request,
    database_client: db.DatabaseClient = Depends(db.get_database_client),
):
    ebook_records = database_client.get_ebook_list()
    template = environment.get_template("ebooks.html")
    rendered_html = template.render(ebook_records=ebook_records)
    return rendered_html


@router.get("/{ebook_id}", response_class=responses.HTMLResponse)
def list_ebook_chapters(
    ebook_id: int,
    database_client: db.DatabaseClient = Depends(db.get_database_client),
) -> str:
    chapter_records = database_client.get_chapter_list(ebook_id)

    html = "<table><tbody>"
    for c in chapter_records:
        html += f"""
            <tr>
                <td><a href="/{ebook_id}/{c.chapter_number}">{c.start}...{c.end}</a></td>
            </tr>
        """
    html += "</tbody></table>"

    return html


@router.get(
    "/{ebook_id}/{chapter_number}",
    response_class=responses.HTMLResponse,
)
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


@router.get("/{book_id}/{chapter_number}/{word}", response_class=responses.HTMLResponse)
def get_word_explanation(
    book_id: str,
    chapter_number: int,
    word: str,
) -> str:
    return word
