# Parsing of a Quarto Markdown file for publishing

- We want to publish a Quarto Markdown file (qmd).
- The qmd file should be parsed into structured data and sent to a publishing server.
- The qmd file can contain organization-specific components that must be parsed and sent individually.
- The components can be created or configured programmatically and inserted in the document (see examples file).

??? example

     `````qmd {title="my_article.qmd"}
     --8<-- "files/publish_quarto/example.qmd"
     `````

Notes:

- Insertion of components happens with Pandoc [fenced divs](https://pandoc.org/MANUAL.html#extension-fenced_divs), using a class to mark it as an organization-specific component, and an id to reference the python object.
- For some component types, markdown content can be added inside the fenced div.

## Overview

We will make a Python package with two main features:

1. Programmatically creating components in the  notebook. The entry point is a notebook client where we expose functions to create the components.
2. Send parsed notebook content to the publish platform. The entry point is a CLI where we offer a preview command that sends the updated data when the notebook file changes.

Dependency graph:

``` mermaid
graph LR
     subgraph driving[Driving adapters]
          cli[<i>Command-line Interface</i>]
          notebookclient[<i>Notebook Client</i>]
     end
     subgraph domain[Domain]
          docpublisher[<i>Document Publisher</i>]
          componentstorage[<i>Component Storage</i>]
     end
     subgraph driven[Driven adapters]
          docprocessor[<i>Document Processor</i><br>Document<br>Element<br>]
          contentprocessor[<i>Content Parser</i><br>Content]
          publishclient[<i>Publish Client</i><br>Response]
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

## Interfaces

=== "Document processor"

     ```py
     class Document(NamedTuple):
          metadata: dict[str, Any]
          html: str

     class Element(NamedTuple):
          key: str
          inner_html: str

     class DocumentProcessor(Protocol):
          def extract_document(self) -> Document: ...
          def extract_elements(self) -> list[Element]: ...
          def replace_element(self, key: str, new_html: str) -> None: ...
     ```
=== "Content Parser"

     ```py
     class Content:
          title: str
          publish_folder: str
          publish_id: str | None

          def to_dict() -> dict[str, Any]: ...
          def serialize() -> dict[str, Any]: ...

     class ContentParser(Protocol):
          def parse_element(metadata: dict[str, Any], html: str) -> Content: ...
     ```

=== "Storage"

     ```py
     class Storage(Protocol):
          def update(key: str | int, data: dict[str, Any]): -> None: ...
          def get(ket: str | int) -> dict[str, Any]: ...
     ```

=== "Publish Client"

     ```py
     class Response(TypedDict):
          publish_id: str
          publish_path: str
          publish_url: str
          publish_html: str | None

     class PublishClient(Protocol):
          def send_content(payload: dict[str, Any]) -> Response: ...
     ```

## Domain logic 

### General flow

### Code

=== "Document Publisher"

     ```py 
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
               publish_folder = self.storage.get(DOCUMENT_KEY).get("publish_path") # (1)!
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

     1. A content needs a publish folder. For a document, this is set in the document metadata, while a component uses the document path. This means that a document needs to have been synced once before components can be synced.
