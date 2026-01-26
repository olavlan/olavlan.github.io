from typing import NamedTuple, Protocol, Any, Mapping, Iterator


class Element(NamedTuple):
    id: str
    inner_html: str


class DocumentProcessor(Protocol):
    def load(self, raw_content: str): ...
    def extract_metadata(self) -> dict[str, Any]: ...
    def extract_elements(self, target_class: str) -> Iterator[Element]: ...
    def replace_element(self, id_: str, new_html: str) -> None: ...
    def extract_html(self) -> str: ...


class Content(Protocol):
    title: str
    publish_folder: str | None
    publish_id: str | None
    content_type: str | None

    def to_dict(self) -> dict[str, Any]: ...


class ContentParser(Protocol):
    def parse(self, metadata: Mapping[str, Any], html: str) -> Content: ...
    def serialize(self, content: Content) -> dict[str, Any]: ...


class Storage(Protocol):
    def update(self, key: str | int, data: Mapping[str, Any]) -> None: ...
    def get(self, key: str | int) -> dict[str, Any]: ...


class Response(NamedTuple):
    publish_path: str
    publish_id: str
    publish_url: str
    publish_html: str


class PublishClient(Protocol):
    def send_content(self, payload: dict[str, Any]) -> Response: ...


DOCUMENT_KEY = 0  # (1)!


def sync_document(
    raw_document_content: str,
    document_processor: DocumentProcessor,
    content_parser: ContentParser,
    storage: Storage,
    publish_client: PublishClient,
):
    document_processor.load(raw_document_content)

    document_metadata = document_processor.extract_metadata()
    document_metadata["content_type"] = "article"
    document_publish_path = storage.get(DOCUMENT_KEY).get("publish_path")
    if not document_publish_path:
        content = content_parser.parse(document_metadata, "")
        response = publish_client.send_content(content_parser.serialize(content))
        document_publish_path = response.publish_path

    document_elements = document_processor.extract_elements(target_class="org")
    for key, html in document_elements:
        metadata = storage.get(key) | {"publish_folder": document_publish_path}
        component = content_parser.parse(metadata, html)
        response = publish_client.send_content(content_parser.serialize(component))
        storage.update(key, {"publish_id": response.publish_id})
        print(response.publish_html)
        document_processor.replace_element(key, response.publish_html)

    metadata = document_metadata | {
        "publish_id": storage.get(DOCUMENT_KEY).get("publish_id")
    }
    html = document_processor.extract_html()
    article = content_parser.parse(metadata, html)
    response = publish_client.send_content(content_parser.serialize(article))
    storage.update(
        DOCUMENT_KEY,
        {"publish_id": response.publish_id, "publish_path": response.publish_path},
    )
    print(html)
    return response
