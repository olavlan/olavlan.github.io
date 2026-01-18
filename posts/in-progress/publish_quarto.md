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

### Interfaces

=== "Models"

     ```py
     class Content(Protocoll):
          content_type: str
          identifier: str
          path: str

          to_dict() -> dict[str, Any]: ...
     ```

=== "Document Processor"

     ```py
     class DocumentProcessor(Protocol):
          ...

     class ContentProcessor(Protocol):
          ...

     class Storage(Protocol):
          ...

     class PublishClient(Protocol):
          ...

     ```

### Domain logic

=== "Component Storage"

     ```py
     class ComponentStorage:
          content_processor: ContentProcessor
          storage: Storage

          def store_component(self) -> None:
               ...
     ``` 

=== "Document Publisher"

     ```py
     class DocumentPublisher:
          document_processor: DocumentProcessor
          content_processor: ContentProcessor
          storage: Storage
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

## Driving adapters

### Cli

=== "Command: preview"

    1. Load the quarto extension for the organization.
    2. Sync the document with a new document publisher. This ensures that the document exists in the publish platform.
    3. Create a file watcher.
    4. Every time the document updates:
          1. Create a new document publisher.
          2. Sync the components.
          3. Sync the document.

### Notebook client

=== "Module initialization"

     Create a new component storage using the current notebook file.

=== "Function: create highchart"

     1. Takes in as parameters a content key and data.
     2. Process the parameters.
        1. Convert the dataframe into a html table.
     3. Use the component storage to store the highchart.

## Domain

### Component storage

**Interface**

=== "Description"

     Can put document components in a storage that can later be accessed by a document publisher.

=== "Attributes"

     * Content parser
     * Content storage

=== "Methods"

     * Store components

**Implementation**

=== "Store component"

     1. Take in the key and arbitrary keyword arguments.
     2. Use content parser to parse the keyword arguments into the right content.
     3. Store the content using the content storage.

### Document publisher

**Interface**

=== "Description"

     Keeps a document and its components in sync with a publishing platform using four parts:

     * A document processor that can extract data from and modify the document.
     * A content parser that can parse the extracted data into content objects.
     * A publish client that can send content objects to the publishing platform.
     * A content storage that can store data.

=== "Attributes"

    * Document processor
    * Content processor
    * Storage
    * Publish client

=== "Methods"

    * Sync document
    * Sync components

**Implementation**

=== "Sync document"

     2. Use the content processor to parse extracted data from the document processor.
     3. Use the storage to set the content's id
     4. Use the publish client to send the serialized content. Throw error if not working.
     5. Use the storage to store the id and path from the response.
     6. Return the path.

=== "Sync components"

    1. Use the storage to get the document publish path. If not set, raise an error.
    2. Define a replace function, i.e. a mapping from a key to html:
         1. Use the storage to get the stored data of the content.
         1. Use the content processor to create a content from stored data and html.
         3. Use the publish client to send the serialized content. 
         4. Use the storage to store the id from the response.
         5. Return the html from the response.
     3. Use the document processor. 

## Driven adapters

### Document processor

**Interface**

=== "Description"

     Can extract data from a document, possibly after making modifications to the document.

=== "Methods"

    * Get document metadata
    * Get document html
    * Replace elements

**Implementation (pandoc)**

=== "Initialization"

     1. Gets a file as input, for instance Quarto Markdown.
     2. Converts the file to the pandoc AST of the document, and stores it as an attribute. The convertion depends on the original file format.

=== "Get document metadata"

=== "Get document html"

=== "Replace elements"

     1. Takes in a target class name and a replacement function (from id to html)
     2. Defines an "action", i.e. a function that takes in a pandoc element and produces a new one
          1. The action returns nothing if the element does not have the target class or an id 
          2. Otherwise the action uses the replacement function to set the new html

### Content processor

**Interface**

=== "Models"

     Content:

     * Content type
     * Id

=== "Methods"

     * Parse content
     * Serialize content

**Implementation**

=== "Models"

     BaseContent

     Article

     Highchart

=== "Parse content"

     1. Test

=== "Serialize content"

     1. Test

### Storage

**Interface**

=== "Methods"

     * Get
     * Update
     * Get value
     * Update value

**Implementation**

=== "Get"

### Publish client (driven adapter)

**Interface**

=== "Attributes"

    * Serializer
    * Base url
    * Endpoint
    * Preview base path

=== "Methods"

    * Send content

**Implementation**

=== "Send content"

    1. Receives the content object and uses the serializer to create a payload.
    2. Creates a post request with:
         * Authentication headers with a token fetched from environment.
         * Body with the content payload.
         * URL: concatinating the base url and the endpoint.
    3. Parses the response and creates a response object containing:
         * The id of the content: parsed from response.
         * The full preview URL of the content: concatinating the base URL, preview base path, and the received content path.
         * The html representation of the content: uses the id to create a reference to the object that can be put in HTML and understood by the publishing platform.
