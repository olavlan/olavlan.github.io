from fastapi import FastAPI
from epubwords.webapp import ebook


def setup_webapp(app: FastAPI):
    app.include_router(ebook.router)
