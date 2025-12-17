---
icon: lucide/notebook
---

# Publishing notebooks with custom components

## Motivation

Notebooks have become immensely popular, especially in the data science world.
Keeping everything in one self-contained file — data processing, documentation, presentation — is indeed convenient.
With the rapid development of new technologies around notebooks, keeping all work in a notebook is not a restriction, but a set of possibilities.
Organizations that embrace the use of notebooks must provide specific capabilities within the organization.
For instance, if I work at an organization that publishes data-science–heavy articles, I want the ability to publish a notebook directly, without having to think too much about the specific formatting of the article.
This could be exposed as a CLI:

```bash
my-org publish my_article.ipynb --publish-date 2026-01-01
```

In the first iteration, the publish command needs too:

- Parse the notebook content.
- Prepare request data and authentication headers.
- Send the request to the server, and optionally process the response to give user feedback.

## Data formats

Organizations that publish content usually store it in specific data formats on the server, which allows appropriate rendering of the components.
So the first question is: should we send the raw notebook content to the server, process it there, and store it in a desirable format?
This has the advantage that if we change the data formats on the server, we can update the notebook processor accordingly, and we don't have to maintain an API contract between the client and server.
However, it is much less flexible, as the next example will show:

```python title="Notebook cell"
import pandas as pd
from my_org import Diagram

df = pd.read_csv("my_data.csv")
# processing of the data here...
diagram = Diagram(df)
diagram.preview()
```

With the preview function, we probably only want to send the data needed for the server to render our diagram.
Then it can send back either HTML or a preview URL — in either case it can be displayed in the notebook as an iframe.
Hence it is much more flexible to do most of the processing on the client side, and send the data in a format that is equal to or close to what the server expects.
It makes sense to have clear restrictions on what can be sent to the server, to safeguard against unexpected content before sending data.

## Nested data

In the previous example we wanted to publish a notebook, and we created an organization-specific diagram in the notebook.
This is an example of one content item (the article) which contains (a reference to) another content item.
Now, what happens if we use our command-line interface?

```bash
my-org publish my_article.ipynb --publish-date 2026-01-01
```

Let's assume that most of the processing happens on the client side.
While parsing the notebook file, it will have to discover all of the organization-specific components.
There are several ways to go about this, but one thing we know is that we need access to the output of the code cells.
In IPython Notebooks (ipynb files), the [output of an object](https://ipython.readthedocs.io/en/stable/config/integrating.html) comes from class methods like these:

```python title="my_org.py"
@dataclass
class Diagram:
    data: dict[str, str]

    def _repr_html_(self):
        # make api call here
        return "<h1>HTML from API call.</h1>"

    def _repr_mimebundle_(self, include=None, exclude=None):
        return {"application/vnd.myorg.diagram+json": self.data}
```

Let's use this class in a notebook:

=== "Cell"

    ```py
    from my_org import Diagram
    data = {"my_key": "my_value"}
    diagram = Diagram(data)
    diagram
    ```

=== "Cell output"

    # HTML from API call.

As we can see, only the HTML will be rendered to the user.
On the other hand, the raw notebook file will contain the following:

```json title="my_article.ipynb (selected lines)"
{
"cells": [
{
"cell_type": "code",
"execution_count": 1,
"id": "6d01f537",
"metadata": {},
"outputs": [
    {
    "data": {
    "application/vnd.myorg.diagram+json": {
    "my_key": "my_value"
    },
    "text/html": [
    "<p>HTML from API call.<p>"
    ],
```

As we can see, the IPython format allow us to store arbitrary data in the output of code cells.
In this case we store data under a custom [media type](https://en.wikipedia.org/wiki/Media_type) (`application/vnd.myorg.diagram+json`), allowing our parser to discover the organization-specific components.

Now our parser has all it needs to process the notebook and send structured data to the server.
Note that with our publish command we can run all the code cells programmatically to ensure the output is available.
However, this is not a good idea with IPython notebooks, because only the user knows the right execution order.
We must therefore require that the user has executed all the code cells whose output should be available to the parser.

Whether notebook cells should be executed or not is actually an interesting question, because it raises the question of reproducibility.
Ideally, if two users send the same notebook (in the sense that they have the same code cells), running our publish command should produce identical articles on the server.
However, this is not possible with IPython notebooks, since the outputs depend on the execution order, which again, is only known to the user.
The alternative notebook system Marimo addresses these problems.

## Marimo

How do we make our publish command work with marimo notebooks as well?
We first need to know that Marimo notebooks are just Python files that don't contain any output of code cells.
For instance, if we create a Marimo notebook with the same code cell as above, the raw notebook file will be:

```py title="my_article.py"
import marimo

__generated_with = "0.18.4"
app = marimo.App()


@app.cell
def _():
    from my_org import Diagram
    data = {"my_key": "my_value"}
    diagram = Diagram(data)
    diagram
    return


if __name__ == "__main__":
    app.run()
```

Marimo's philosophy is that notebooks should be completely reproducible by re-running all the cells in the right order.
The right order is completely determined by the dependencies between the code cells.
Hence there should be no need to store outputs, since a second user should be able to get the same outputs by running the notebook on their own system.
Indeed, Marimo does not store outputs of cells anywhere.
Since cells are just Python functions, Marimo renders the return values directly without any intermediate storage.

So can we just run the Marimo notebook as a Python script and parse the return objects of the function?
Unfortunately, marimo does not expose a Python API to work with all type of cell outputs.
In particular, markdown cells in Marimo are also just code cells/functions, as seen in this example notebook:

```python
import marimo

__generated_with = "0.18.4"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
def _(mo):
    mo.md("""
    # This is a markdown heading in a Marimo cell
    """)
    return


if __name__ == "__main__":
    app.run()
```

Note that this also shows how Marimo handles dependencies between cells.
Now, Marimo makes it easy to import and run the whole notebook; we simply import the `marimo.App` object from the above Python file and call the [run](https://docs.marimo.io/api/app/#marimo.App.run) method.
The return values include the outputs and Python definitions of the cell. However, the cell that calls `mo.md()` does not have an output we can work with through a public API (they are internal objects meant to be rendered by Marimo's own UI layer).
This is through for all Marimo-specific outputs.

In order to get access to the markdown content, we need to use one of Marimo's [export](https://docs.marimo.io/cli/#marimo-export) commands and work from there.
In our case, we need an IPython notebook, since it is the only notebook format that store outputs.
Although the subcommand `marimo export ipynb` has an `--include-outputs` option, this only gives the output that is shown to the user, not our additional data (the highlighted lines):

```json title="my_article.ipynb (selected lines)" hl_lines="4-6"
"outputs": [
    {
    "data": {
    "application/vnd.myorg.diagram+json": {
    "my_key": "my_value"
    },
    "text/html": [
    "<p>HTML from API call.<p>"
    ],
```

Storing all of the representations of an object is a feature of the IPython notebook client.
Consequently we need to export the raw marimo notebook to an IPython notebook and only then execute the code cells:

```python
from nbclient import NotebookClient
import nbformat
import subprocess

result = subprocess.run(
    ["marimo", "export", "ipynb", "my_notebook.py"],
    capture_output=True,
    text=True,
)

notebook = nbformat.reads(result.stdout, as_version=4)

client = NotebookClient(notebook)
client.execute()

print(notebook)
```

Note that in this case, we can actually be sure that the notebook is executed correctly, since Marimo will export the cells in the right execution order.

## The percent format

How is output stored?
Can percent format files be converted to ipynb notebooks?
Can it then be executed?
What about execution order?

## The Quarto Markdown format

Same questions as above.

## Putting it together

Now let's go back to our original goals:

- The user can create an organization-specific component in a cell and show a HTML preview in the cell output.
- The notebook file can be parsed in such a way that the components are discovered and sent to the server in the right format.

What is the simplest way to achieve this across all popular notebook formats?
Note that the different formats can be divided into flat file formats (marimo, percent, qmd) and structured data format (ipynb).
Flat file formats are preferred by many because it is suitable for version control,
However, in order to achieve our goals, we need a file format that can store outputs as structured data.
Therefore, regardless of which notebook format we start with, ipynb has to be an intermediate format in our implementation.

## Server-specific considerations

How can we register article metadata to be sent to the server? YAML frontmatter?

How to have content references to already created content on the server?
One metadata file to each article file?
How can we get the filepath when we're inside a notebook? Do we need to handle specific environments differently (Marimo, Jupyter)?

## User interface

How can we make it simple for the user to start writing an article?
Template creation? Which formats to support?
ipynb, Marimo, percent format, qmd?

## Conclusion

While ipynb has reproducibility and versioning challenges, its structured data format and ability to store outputs make it well suited as a compatibility layer between other notebook formats and the server.
