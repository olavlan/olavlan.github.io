# Parsing of a Quarto Markdown file for publishing


- We want to publish a Quarto Markdown file (qmd).
- The qmd file should be parsed into structured data and sent to a publishing service.
- The qmd file can contain organization-specific components that must be extracted and parsed individually.
- The components can be created programmatically and inserted in the document using [shortcodes](https://quarto.org/docs/authoring/shortcodes.html) (see examples below). 
  - Advantage: the components are self-documenting in the editor and validated immediately. 
- Alternative approach: insert components using [divs](https://quarto.org/docs/authoring/markdown-basics.html#sec-divs-and-spans), [spans](https://quarto.org/docs/authoring/markdown-basics.html#sec-divs-and-spans) or codeblocks (see examples below).

??? example

     `````qmd {title="my_article.qmd"}
     --8<-- "files/publish_quarto/example.qmd"
     `````

## Architecture diagram

## Driving adapters 

### Cli

**Implementation**

=== "Preview"

    1. Load the quarto extension for the organization.
    2. Sync the document with a new document publisher.
    3. Create a file watcher.
    4. Every time the document updates, create a document publisher, and sync the components and then the document.


### Notebook client

**Implementation**

=== "Initialization"

     Create a new component storage using the current notebook file.

=== "Create highchart"

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
    * Content parser
    * Content storage
    * Publish client

=== "Methods"

    * Sync document
    * Sync components

**Implementation**

=== "Sync document"

     1. Extract the metadata and html from the document.
     2. Parse the data into a content.
     3. Set the content's id to the value from storage. 
     4. Sync the content with the publish client. Throw error if not working.
     5. Set the storage's id and path to the values in the response.
     6. Return the path.

=== "Sync components"

    1. Get the document publish path from the storage. If not set, raise an error.
    2. Extract all the components from the document, i.e. their key and html.
    3. For each component, do:
         1. Get the component data from storage.
         2. Parse the component data and html into a content.
         3. Set the content's id to the value from storage.
         4. Sync the content with the publish client. Throw error if not working.
         5. Set the storage's id to the value from the response.
         6. Replace the component with the html from the response.


## Driven adapters

### Document processor

**Interface**

=== "Description"

     Can extract data from a document, possibly after making modifications to the document.


=== "Methods"

    * Get document metadata
    * Get document html
    * Get id and html of elements that have a certain class

**Implementation (pandoc)**

=== "Initialization"

     1. Gets a file as input, for instance Quarto Markdown.
     2. Converts the file to the pandoc AST of the document, and stores it as an attribute. The convertion depends on the original file format.

=== "Get document metadata"


=== "Get document html"


=== "Get elements of given class"


### Content processor

**Interfaces**

=== "Content"

     Attributes:

     * Content type
     * Id

=== "Content parser"

     Methods:

     * Parse content


=== "Content storage"

     Attributes:

     * Content parser

     Methods: 

     * Get content
     * Update content
     * Get id
     * Update id

=== "Content serializer"

     Methods:

     * Serialize content


**Implementation**

=== "Content (models)"

     BaseContent
     
     Article

     Highchart

=== "Content parser"

     Parse content:

     1. Test

=== "Content storage"

     Serialize content:

     1. Test

=== "Content serializer"

     Parse content:
     
     1. Test

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