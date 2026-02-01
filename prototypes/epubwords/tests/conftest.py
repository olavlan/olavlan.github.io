import pytest
from fastapi import testclient

from epubwords.main import app


@pytest.fixture(scope="session")
def test_app():
    yield testclient.TestClient(app)
