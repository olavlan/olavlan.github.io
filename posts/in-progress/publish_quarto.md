# Parsing of a Quarto Markdown file for publishing

## Reqirements

- User wants to send a Quarto Markdown (qmd) file to a publishing service, and get a preview URL back.
- The qmd file should be parsed into structured data and sent to a publishing service.
- The qmd file can contain organization-specific components that must be parsed and sent individually.
- The components can be created or configured programmatically and inserted in the document (see examples file below).

??? example

     ````` {title="my_article.qmd"}
     Defining components in code cells:
     
     ```{python}
     org.create_highchart(
         key="my-highchart",
         title="Highchart title",
         data=my_dataframe,
         graph_type="line",
     )
     ```
     
     ```{python}
     org.configure_factbox(
         key = "my-factbox,
         title = "Factbox title",
         box_type = "default")
     ```
     
     Inserting a highchart:
     
     ::: { #my-highchart .org }
     :::
     
     Inserting the configuration of a factbox:
     
     ::: { #my-factbox .org }
     
     The text of the factbox, written with Markdown inside a fenced div.
     
     :::
     `````
     Notes:

     1. Insertion of components is done with Pandoc [fenced divs](https://pandoc.org/MANUAL.html#extension-fenced_divs), using a class and id to reference the Python object.
     2. For some component types, markdown content can be added inside the fenced div.

## Overview

We will create a Python package with the following entry points:

1. A notebook client that exposes functions to create components.
2. A CLI with a preview command that:
     - Prints a preview URL for the rendered qmd file.
     - Keeps the preview up to date with the qmd file; watches for file changes in the qmd and sends updated content to the publish service.

## Dependency graph
     
``` mermaid
graph LR
     subgraph driving[Driving adapters]
          cli[<i>Command-line Interface</i>]
          notebookclient[<i>Notebook Client</i>]
     end
     subgraph domain[Domain]
          docpublisher[<i>Document Publisher</i>]
     end
     subgraph driven[Driven adapters]
          docprocessor[<i>Document Processor</i><br>Element<br>]
          contentprocessor[<i>Content Parser</i><br>Content]
          publishclient[<i>Publish Client</i><br>Response]
          storage[<i>Storage</i>]
     end

     cli --> docpublisher

     docpublisher --- split[ ]:::empty
     split --> docprocessor
     split --> publishclient
     split --> contentprocessor
     split --> storage

     notebookclient --- split2[ ]:::empty
     split2 --> contentprocessor
     split2 --> storage

     classDef empty width:0px,height:0px;
```

## Interfaces

Click the plus icons for descriptions.

=== "Document processor"

     ```py
     class Element(NamedTuple):
          id: str
          inner_html: str

     class DocumentProcessor(Protocol): # (1)!
          def extract_metadata(self) -> dict[str, Any]: ... # (5)!
          def extract_elements(self, target_class: str) -> list[Element]: ... # (2)!
          def replace_element(self, key: str, new_html: str) -> bool: ... # (3)!
          def extract_html(self) -> str: ... # (4)!
     ```

     1. A class that can modify and extract content from a document. An implementation should support a specific format, and should be instantiated with a document of that format.
     2. Extracts all container elements (divs and spans) that has the target class and an id. For each element, extracts the id and inner content (converted to html).
     3. Replaces the element of the given key with the given html.
     4. Extracts the document (converted to html) in its current state (possibly after replacements). 
     5. Extracts the document metadata.

=== "Content Parser"

     ```py
     class Content:
          title: str
          publish_folder: str
          publish_id: str | None

          def to_dict() -> dict[str, Any]: ...

     class ContentParser(Protocol): # (1)!
          def parse(metadata: dict[str, Any], html: str) -> Content: ... # (2)!
          def serialize(content: Content) -> dict[str, Any]: ... # (3)!
     ```

     1. A class that can parse extracted document data into structured content and serialize it. An implementation should mirror the content types in a given CMS/publish service, and serialize it to a format that the service can understand.
     2. Given the metadata and html of a document or element, tries to parse into a content object.
     3. Returns the serialized content, which can be sent to an external service for further processing.

=== "Storage"

     ```py
     class Storage(Protocol): # (1)!
          def update(key: str | int, data: dict[str, Any]): -> None: ... # (2)!
          def get(ket: str | int) -> dict[str, Any]: ... # (3)!
     ```

     1. A class that can persist data between runs, using a simple key-based storage. An implementation should use a technology suitable for the data and environment.
     2. Update the data stored under the given key, using the given data. This can overwrite existing fields and create new fields. Creates a new key if the given key doesn't exist.
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

## Notebook client

A simplified example of a notebook client:

```py 
import org # (1)!
import get_storage

storage = get_storage() # (2)!

def create_highchart(
     key: str,
     title: str,
     data: DataFrame,
     graph_type: str,
):
     if not isinstance(key, str): # (4)!
          raise Exception()
     content = org.Highchart(
          title = title,
          html_table = _dataframe_to_html(data), # (3)!
          graph_type = graph_type
     )
     storage.update(key, content)
     return _get_markdown_snippet(key)

def _dataframe_to_html(data: DataFrame) -> str: ...

def _get_markdown_snippet(key: str):
     return f"::: {{ #{key} .org }}\n:::"
```

1. We import the organization-specific models. More on this later.
2. We assume that the storage interface has an implementation that we can use.
3. Notebook client allows a specific data format, which is converted to the format expected by the organization-specific model.
4. In order to avoid conflicts with integer keys used by the program.

All functions we expose will have the same steps: 

 1. Convert the user-input.
 2. Create an organization-specific content object.
 3. Store the content.
 4. Return a markdown snippet.
 
The user can now put the snippet in the document, and the document publisher can find those snippets, get the stored data by key, and send it to the publishing service.

## Document publisher

The document publisher has three main steps:

1. Ensure that the document has a publish path.
2. Sync all the components in the document.
3. Sync the final document.

```py 
DOCUMENT_KEY = 0 # (1)!

def sync_document(
     document_processor: DocumentProcessor,
     content_processor: ContentProcessor,
     storage: Storage,
     publish_client: PublishClient):
     
     document_metadata = self.document_processor.extract_metadata()
     document_publish_path = self.storage.get(DOCUMENT_KEY).get("publish_path")
     if not document_publish_path: # (2)!
          content = self.content_parser.parse(document_metadata, "")
          response = self.publish_client.sync_content(content.serialize())
          document_publish_path = response.publish_path

     document_elements = self.document_processor.extract_elements(target_class="ssb")
     for key, html in document_elements:
          component = self.content_parser,parse(
               metadata = self.storage.get(key) | {"publish_folder": document_publish_path} # (3)!
               html = html
          )
          response = self.publish_client.sync_content(component.serialize())
          self.storage.update(key, response) # (4)!
          self.document_processor.replace_element(key, response.publish_html) # (5)!

     article = self.content_parser.parse( # (6)!
          metadata = doucment_metadata | {"publish_id": self.storage.get(DOCUMENT_KEY).get("publish_id")}
          html = self.document_processor.extract_html()
     )
     response = self.publish_client.sync_content(article.serialize())
     self.storage.update(DOCUMENT_KEY, response)
     return response.publish_url
```

1. We set an integer key for the document, which cannot conflict with the user-defined keys, which are always strings.
2. If the document publish path is not found in storage, we send a simplified version of the content to the publish server first. This is necessary because the components needs to be published under this path.
3. We ensure that the component is sent to the right publish folder.
4. It's important to store the response, since the publish id will be used on the next sync, ensuring that we update the existing component rather than creating a new one.
5. In the same way as we insert components with markdown snippets, the publish service offers to insert components with html snippets. We therefore replace the markdown snippets with the html snippets in the internal document.
6. With the snippets replaced, we are now ready to parse and send the whole document. The flow is very similar to syncing components, except that the data is fetched directly from the document rather than storage; but we do need to include the publish id!
