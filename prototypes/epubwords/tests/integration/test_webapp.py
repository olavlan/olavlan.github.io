import pytest
from fastapi.testclient import TestClient
from fastapi.responses import HTMLResponse
from epubwords.main import app
from epubwords.adapter.db import SqliteDatabaseClient
from epubwords.adapter import db
from typing import Callable, Any


@pytest.fixture
def client(tmp_path):
    def override_get_database_client():
        return SqliteDatabaseClient(tmp_path / "test.db")

    app.dependency_overrides[db.get_database_client] = override_get_database_client
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def post_epub() -> Callable[[str], dict[str, Any]]:
    def factory(epub_file_path: str) -> dict[str, Any]:
        # TODO
        ...

    return factory


def test_list_ebooks(client, post_epub):
    response: HTMLResponse = client.get("/")
    assert response.status_code == 200
    # make post requests
