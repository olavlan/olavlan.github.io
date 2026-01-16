# Parsing of a Quarto Markdown file for publishing

## Overview 

- We want to publish Quarto Markdown files (qmd).
- The qmd files should be parsed into structured data and sent to a publishing service.
- The qmd files can contain organization-specific components that must be extracted and parsed individually.
- Components can be defined/configured programmatically and inserted in the document using divs, spans or shortcodes.

Example qmd file:
```py
org.Highchart(key = "my-highchart",
              title = "my_title",
              data = my_dataframe,
              xlabel = "my_xlabel")
org.FactBox(key = "my-factbox,
            title = "Factbox title"
            text = "")
```
``````markdown
Inserting highchart, recommended way:

{{< org my-highchart >}}

Inserting factbox, recommended way:

{{< org my-factbox >}}

Sometimes it's convenient to be able to set the main content/data of a component in the Markdown.

Example 1: Using a Markdown codeblock to paste Excel data for a highchart:

```{.org #my-highchart }
Column 1, Column 2
1, 2
3, 4
```

Example 2: Using a Markdown fenced div to write the content of a fact box:

::: {.org #my-factbox }
Text that go inside the factbox.
:::
``````

Q: Zensical; how to have a separate qmd file and reference it in this article?

## Domain logic - document publisher

Keeps a document and its components in sync with a publishing platform using four parts:

* A document processor that can extract data from and modify the document.
* A content parser that can parse the extracted data into content objects.
* A publish client that can send content objects to the publishing platform.
* A content storage that can store data.

Q: In which part should serialization happen? If in publish client, then where do the content models go? 

### Attributes

* Document processor
* Content parser
* Publish client
* Content storage

### Methods 

Sync document

1. Extract the metadata and html from the document.
2. Parse the data into a content.
3. Set the content's id to the value from storage. 
4. Sync the content with the publish client. Throw error if not working.
5. Set the storage's id and path to the values in the response.
6. Return the path.

Sync components

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

### Content storage

### Content parser

### Publish client

## Driving adapters

### Cli

#### Commands

Preview:

1. Loads the quarto extension for the organization.
2. Syncs the document with a new document publisher.
3. Creates a file watcher.
4. Every time the document updates, creates a document publisher, and syncs the components and then the document.



### Notebook client

Creates a storage adapter based on the current notebook file.
Creates a parser.

#### Methods

Create highchart:

1. Takes in as parameters a content key and data.
2. Processes the parameters. In particular, converts dataframe into html table.
3. Creates a content based on the processed parameters.
4. Stores the content in the storage under the given key.

Methods for other content types follow the same pattern.