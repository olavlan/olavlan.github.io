from fastapi import APIRouter
from fastapi import Form, Depends
from fastapi.responses import HTMLResponse

from epubwords.adapter import db

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
def list_ebooks(database_client: db.DatabaseClient = Depends(db.get_database_client)):
    ebook_records = database_client.get_ebook_list()
    html = "<table>"
    html += "<thead><tr><td>Date added</td><td>Title</td></tr></thead>"
    html += "<tbody>"
    for e in ebook_records:
        html += f"<tr><td>{e.date_added}</td><td>{e.title}</td></tr>"
    html += "</tbody>"
    html += "</table>"
    return html


@router.get("/{book_id}/{chapter_number}", response_class=HTMLResponse)
def practice_words(book_id: str, chapter_number: int):
    return """
    <h1>Word</h1>
    <form method="POST">
        <input type="hidden" name="word_id" value="42">
        <button name="action" value="explain">Explain</button>
        <button name="action" value="next">Next</button>
    </form>
    """


@router.post("/{book_id}/{chapter_number}", response_class=HTMLResponse)
def handle_word(
    book_id: str, chapter_number: int, action: str = Form(...), word_id: str = Form(...)
):
    print("Action:", action)
    print("Word ID:", word_id)
    return practice_words(book_id, chapter_number)
