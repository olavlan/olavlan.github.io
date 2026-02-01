from fastapi import FastAPI
from epubwords.webapp import books


def setup_webapp(app: FastAPI):
    app.include_router(books.router)
