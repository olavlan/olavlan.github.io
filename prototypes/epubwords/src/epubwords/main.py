from fastapi import FastAPI
from epubwords.webapp import setup_webapp

app = FastAPI()
setup_webapp(app)


def run_webapp():
    import uvicorn

    uvicorn.run("epubwords.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    run_webapp()
