from fastapi import FastAPI
from epubwords.webapp import epub


def setup_webapp(app: FastAPI):
    app.include_router(epub.router)
