# Parsing of a Quarto Markdown file for publishing

- We want to publish a Quarto Markdown file (qmd).
- The qmd file should be parsed into structured data and sent to a publishing service.
- The qmd file can contain organization-specific components that must be parsed and sent individually.
- The components can be created or configured programmatically and inserted in the document (see examples below).
    - Advantage: the creation/configuration of components is self-documenting in the editor and validated immediately.

??? example

     `````qmd {title="my_article.qmd"}
     --8<-- "files/publish_quarto/example.qmd"
     `````

Notes:

- Insertion happens through Quarto [shortcodes](https://quarto.org/docs/authoring/shortcodes.html), which is parsed with a custom Quarto [extension](https://quarto.org/docs/extensions/shortcodes.html). 
- A fact box is defined with a Pandoc [fenced div](https://pandoc.org/MANUAL.html#extension-fenced_divs) with the configuration inserted.

## Architecture

### Dependency graph

``` mermaid
graph LR
     subgraph driving[Driving adapters]
          cli["Command-line Interface"]
          notebookclient[Notebook Client]
     end
     subgraph domain[Domain]
          docpublisher[Document Publisher]
          componentstorage[Component Storage]
     end
     subgraph driven[Driven adapters]
          docprocessor[Document Processor]
          publishclient[Publish Client]
          contentprocessor[Content Processor]
          storage[Storage]
     end

     cli --> docpublisher
     notebookclient --> componentstorage

     docpublisher --- split[ ]:::empty
     split --> docprocessor
     split --> publishclient
     split --> contentprocessor
     split --> storage

     componentstorage --- split2[ ]:::empty
     split2 --> contentprocessor
     split2 --> storage

     classDef empty width:0px,height:0px;
```

=== "Document Processor"

     ```py
     class Element(NamedTuple):
          key: str
          inner_html: str

     class Document(NamedTuple):
          metadata: dict[str, Any]
          html: str

     class DocumentProcessor(Protocol):
          def extract_document(self) -> Document: ...
          def extract_elements(self) -> list[Element]: ...
          def replace_element(self, key: str, html: str) -> None: ...


     class Content:
          title: str
          publish_folder: str
          publish_id: str | None

          def to_dict() -> dict[str, Any]: ...
          def serialize() -> dict[str, Any]: ...

     class ContentParser(Protocol):
          def parse_element(metadata: dict[str, Any], html: str) -> Content: ...

     class Storage(Protocol):
          def update(key: str | int, data: dict[str, Any]): -> None: ...
          def get(ket: str | int) -> dict[str, Any]: ...

     class Response(TypedDict):
          publish_id: str
          publish_path: str
          publish_url: str
          publish_html: str | None

     class PublishClient(Protocol):
          def send_content(payload: dict[str, Any]) -> Response: ...


     DOCUMENT_KEY = 0

     class DocumentPublisher:

          def sync_document(self) -> str:
               metadata, html = self.document_processor.extract_document()
               content = self.content_parser.parse_element(
                    metadata = metadata | {"publish_id": self.storage.get(DOCUMENT_KEY).get("publish_id")}
                    html = html
               )
               response = self.publish_client.sync_content(content.serialize())
               self.storage.update(DOCUMENT_KEY, response)
               return response.publish_url

          def sync_components(self) -> None:
               publish_folder = self.storage.get(DOCUMENT_KEY).get("publish_folder")
               if publish_folder is None:
                    raise Exception()

               for key, html in self.document_processor.extract_elements():
                    content = self.content_parser.parse_element(
                         metadata = self.storage.get(key) | {"publish_folder": publish_folder}
                         html = html
                    )
                    response = self.publish_client.sync_content(content.serialize())
                    self.storage.update(key, response)
                    self.document_processor.replace_element(key, response.publish_html)
     ```

### Domain logic

=== "Component Storage"

     ```py
     class ComponentStorage:
          content_processor: ContentProcessor
          storage: ComponentStorage

          def store_component(self) -> None:
               ...
     ``` 

=== "Document Publisher"

     ```py
     class DocumentPublisher:
          ContentType: type[Content]
          document_processor: DocumentProcessor
          storage: ComponentStorage
          publish_client: PublishClient

          def sync_document(self) -> str:
               ...

          def sync_components(self) -> str:
               document_path = storage.get_value(0, "path")
               if document_path is None:
                    raise Exception()

               def element_transformer(key: str, original_html: str) -> str:
                    content = content_processor.parse(
                         data = storage.get(key),
                         html = original_html)
                    content.parent_path = document_path
                    response = publish_client.send_content(
                         data = content_processor.serialize(content)
                    )
                    storage.update_value(key, "id", response.id)
                    return response.html
               
               document_processor.replace_elements(target_class="org", transformer=element_transformer)
     ```
