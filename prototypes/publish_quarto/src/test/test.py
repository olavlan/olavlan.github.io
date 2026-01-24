from publish_quarto.domain import Response, sync_document
from publish_quarto.adapters.storage import LocalFileStorage
from typing import Any


class MockPublishClient:
    def send_content(self, serialized_content: dict[str, Any]) -> Response:
        return Response(
            "mock-publish-path",
            "mock-publish-id",
            "mock-publish-url",
            "<p>mock-publish-html</p>",
        )


adapters = LocalFileStorage(""), MockPublishClient()

sync_document("example.qmd", *adapters)
