from publish_quarto.domain import Response, sync_document
from publish_quarto.adapters.document_processor import PandocDocumentProcessor
from publish_quarto.adapters.storage import LocalFileStorage
from publish_quarto.adapters.content_parser import OrgContentParser
from typing import Any
import subprocess


class MockPublishClient:
    def send_content(self, payload: dict[str, Any]) -> Response:
        print(payload)
        api_response = {"_id": "mock-id", "_path": "mock_path"}

        html = ""
        content_type = payload.get("contentType")
        id_ = api_response.get("_id")
        if content_type is not None and id_ is not None:
            html = f"<p>[ {content_type} {content_type}=&quot;{id_}&quot; /]</p>"

        return Response(
            "mock-publish-path",
            "mock-publish-id",
            "mock-publish-url",
            html,
        )


def quarto_to_pandoc(file_path: str) -> str:
    result = subprocess.run(
        [
            "quarto",
            "render",
            file_path,
            "--to",
            "json",
            "-M",
            "include:false",
            "--output",
            "-",
        ],
        text=True,
        capture_output=True,
        check=True,
    )
    return result.stdout


document_path = "example.qmd"

adapters = (
    PandocDocumentProcessor(),
    OrgContentParser(),
    LocalFileStorage(),
    MockPublishClient(),
)

pandoc_document = quarto_to_pandoc(document_path)


def test_sync():
    sync_document(pandoc_document, *adapters)
