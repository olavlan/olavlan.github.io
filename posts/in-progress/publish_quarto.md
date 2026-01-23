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
          id: str
          inner_html: str

     class DocumentProcessor(Protocol): # (1)!
          def extract_elements(self, target_class: str) -> list[Element]: ... # (2)!
          def replace_element(self, key: str, new_html: str) -> bool: ... # (3)!
          def extract_document(self) -> Document: ... # (4)!
     ```

     1. A class that can modify and extract content from a document. An implementation should support a specific format, and should be instantiated with a document of that format.
     2. Extracts all container elements (divs and spans) that has the target class and an id. For each element, extracts the id and inner content (converted to html).
     3. Replaces the element of the given key with the given html.
     4. Extracts the document in its current state (possibly after replacements). 

=== "Content Parser"

     ```py
     class Content:
          title: str
          publish_folder: str
          publish_id: str | None

          def to_dict() -> dict[str, Any]: ...

     class ContentParser(Protocol): # (1)!
          def parse(metadata: dict[str, Any], html: str) -> Content | None: ... # (2)!
          def serialize(content: Content) -> dict[str, Any]: ... # (3)!
     ```

     1. A class that can parse extracted document data into structured content and serialize it. An implementation should mirror the content types in a given CMS/publish service, and serialize it to a format that the service can understand.
     2. Given the metadata and html of a document or element, parses into a content object if possible. The implementation might have different subclasses that it parses into.
     3. Returns the serialized content, which can be sent to an external service for further processing.

=== "Storage"

     ```py
     class Storage(Protocol): # (1)!
          def update(key: str | int, data: dict[str, Any]): -> None: ... # (2)!
          def get(ket: str | int) -> dict[str, Any]: ... # (3)!
     ```

     1. A class that can persist data between runs, using a simple key-based storage. An implementation should use a technology suitable for the data and environment.
     2. Update the data stored under the given key, using the given data. This can overwrite existing fields and create new fields.
     3. Gets the data stored under the given key. If the key doesn't exist, an empty dictionary is returned.

=== "Publish Client"

     ```py
     class Response(TypedDict):
          publish_path: str
          publish_id: str
          publish_url: str
          publish_html: str | None

     class PublishClient(Protocol): # (1)!
          def send_content(serialized_content: dict[str, Any]) -> Response: ...
     ```

     1. A class that can send serialized content to a publish service and parse the response.

## Domain logic 

=== "Document Publisher"

     ```py 
     DOCUMENT_KEY = 0 # (1)!

     def sync_document(
          document_processor: DocumentProcessor,
          content_processor: ContentProcessor,
          storage: Storage,
          publish_client: PublishClient):

          document_metadata = self.document_processor.extract_metadata()

          document_publish_path = self.storage.get(DOCUMENT_KEY).get("publish_path") # (2)!
          if not document_publish_path:
               content = self.content_parser.parse(document_metadata, "")
               response = self.publish_client.sync_content(content.serialize())
               document_publish_path = response.publish_path

          document_elements = self.document_processor.extract_elements(target_class="ssb")
          for key, html in document_elements:
               component = self.content_parser,parse(
                    metadata = self.storage.get(key) | {"publish_folder": document_publish_path}
                    html = html
               )
               response = self.publish_client.sync_content(component.serialize())
               self.storage.update(key, response)
               self.document_processor.replace_element(key, response.publish_html)

          article = self.content_parser.parse( 
               metadata = doucment_metadata | {"publish_id": self.storage.get(DOCUMENT_KEY).get("publish_id")}
               html = self.document_processor.extract_html()
          )
          response = self.publish_client.sync_content(article.serialize())
          self.storage.update(DOCUMENT_KEY, response)
          return response.publish_url
     ```

     1. The storage allows both integer and string keys. Since we allow the user to define arbitrary string keys for components, we set an integer key for the document, avoiding conflicts.
