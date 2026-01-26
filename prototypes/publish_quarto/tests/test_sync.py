from publish_quarto.domain import Response, sync_document
from publish_quarto.adapters.document_processor import PandocDocumentProcessor
from publish_quarto.adapters.storage import get_local_file_storage
from publish_quarto.adapters.content_parser import OrgContentParser
from typing import Any
import subprocess


class MockPublishClient:
    def send_content(self, serialized_content: dict[str, Any]) -> Response:
        html = "<p>"

        return Response(
            "mock-publish-path",
            "mock-publish-id",
            "mock-publish-url",
            "<p>mock-publish-html</p>",
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
    get_local_file_storage(),
    MockPublishClient(),
)

pandoc_document = quarto_to_pandoc(document_path)


def test_sync():
    sync_document(pandoc_document, *adapters)
