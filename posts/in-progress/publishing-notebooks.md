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
This could be exposed as a CLI or a Python interface to be used directly in the notebook:

=== "bash"

    ```bash
    my-org publish my_article.ipynb --publish-date 2026-01-01
    ```

=== "my_article.ipynb"

    ```python
    # start of notebook
    from my_org import Article
    article = Article(publish_date="2026-01-01")
    # notebook content here
    article.publish()
    # end of notebook
    ```

The Python interface could be convenient if you want the notebook to be completely self-contained; i.e., when all the cells of the notebook are run, the updated content is sent to the server, including all necessary metadata.

Regardless of the interface, the publish command/function probably needs to send both data and authentication headers, but in this post I will focus on the data.

## Data formats

Organizations that publish content usually store it in specific data formats on the server, which allows appropriate rendering of the components.
So the first question is: should we send the raw notebook content to the server, process it there, and store it in a desirable format?
This has the advantage that if we change the data formats on the server, we can update the notebook processor accordingly, and we don't have to maintain an API contract between the client and server.
However, it is much less flexible, as the next example will show:

```python title="my_article.ipynb"
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

Let's assume that most of the processing happens on the client side. While parsing the notebook file, it will have to discover all of the organization-specific components.
There are several ways to go about this, but one thing we know is that we need access to the output of the code cells.
In IPython Notebooks (ipynb files), the [output of an object](https://ipython.readthedocs.io/en/stable/config/integrating.html) can be defined as follows:

```python title="my_org.py"
@dataclass
class Diagram:
    data: dict[str, str]

    def _repr_html_(self):
        # make api call here
        return "<p>HTML from API call.<p>"

    def _repr_mimebundle_(self, include=None, exclude=None):
        return {"application/vnd.myorg.diagram+json": self.data}
```

Now assume we run the following code cell in an ipynb notebook:

```py title="my_article.ipynb"
from my_org import Diagram
data = {"my_key": "my_value"}
diagram = Diagram(data)
diagram
```

Then only the html will be rendered to the user, but the raw ipynb file will have the following content:

```json
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
//notebook continues here
```

IPython notebooks thus allow us to store arbitrary data in the output of code cells.
In this case we store data under a custom [media type](https://en.wikipedia.org/wiki/Media_type) (`application/vnd.myorg.diagram+json`), allowing our parser to discover the organization-specific components.

Now our parser has all it needs to process the notebook and send structured data to the server.
Note that with our publish command we can run all the code cells programmatically to ensure the output is available.
However, this is not always a good idea, since IPython notebooks don't have an unambiguous execution order — it's up to the user.

## Marimo

We now have a solution that is specific to IPython notebooks, and is not easily extensible to, say, Marimo notebooks.
Marimo notebooks are just Python files that don't contain any output of code cells.
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

No output is ever stored in this file — the output only exists in memory and is meant to be processed by the Marimo UI layer.
This backs Marimo's philosophy that it should not be necessary to store outputs in files, since the output should be completely deterministic and reproducible.
To achieve this, every cell is just a Python function, and Marimo ensures that the functions are run in the correct order based on their dependencies.
In comparison, IPython notebooks are not reproducible in the same way, since the format doesn't enforce a "right order" of cells — only the creator of the notebook knows what the right execution order of the cells is.

Although we can run a Marimo notebook as a Python script and inspect the objects, we don't have a good way of parsing the output.
In particular, markdown cells in Marimo are also just code cells with markdown output, as seen in this example file:

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

This also shows how Marimo handles dependencies between cells.
Marimo makes it easy to import and run a whole notebook; we simply import the `marimo.App` object from the Python file and call the [run](https://docs.marimo.io/api/app/#marimo.App.run) method.
The return values include the outputs and definitions of the cell. However, Marimo-specific outputs, like the output from cells calling `mo.md()`, do not have a public API that we can use (they are internal objects meant to be rendered by Marimo's own UI layer).

In order to get access to the markdown content, we need to use one of Marimo's [export](https://docs.marimo.io/cli/#marimo-export) commands and work from there.
In our case, we want an IPython notebook, since it is the only notebook format that can store output.
Although the subcommand `marimo export ipynb` has an `--include-outputs` option, this only gives the output that is shown to the user.
Hence we need to convert it to an ipynb notebook without outputs, and then execute the notebook.
Here is how we can do that:

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
```

Note that in this case, we can actually be sure that the notebook is executed correctly, since Marimo will export the cells in the right execution order.

## The percent format

Can percent format files be converted to ipynb notebooks?
Can it then be executed?
What about execution order?

## The Quarto Markdown format

Same questions as above.

## Putting it together

Now let's go back to our original goals:

* The user can create an organization-specific component in a cell and show a HTML preview in the cell output.
* The notebook file can be parsed in such a way that the components are discovered and sent to the server in the right format.

What is the simplest way to achieve this across all popular notebook formats?

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

While ipynb has reproducibility challenges, its structured data format and ability to store outputs make it well suited as a compatibility layer between other notebook formats and the server.
