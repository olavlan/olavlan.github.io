from fastapi import APIRouter
from fastapi import Form
from fastapi.responses import HTMLResponse

router = APIRouter()


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
