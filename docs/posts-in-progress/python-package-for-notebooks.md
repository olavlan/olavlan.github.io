# Making a Python package for notebooks

## Motivation

Notebooks have become immensely popular, especially in the data science world.
Keeping everything in one self-contained file - data processing, documentation, presentation - is indeed convenient.
With the rapid development of new technologies around notebooks, keeping all work in a notebook is not a restriction, but possibilities.
Organizations that embraces the use of notebooks must ensure specific possibilities within the organization.
For instance, if I work at an organization that publish data science-heavy article, I want the possibility to publish a notebook directly, without having to think too much about the specific formatting of the article.
This could be exposed as a CLI interface, or a Python interface to be used directly in the notebook:

=== "bash"

    ```bash
    my_org publish my_article.ipynb --publish-date 2026-01-01
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

The Python interface could be convenient if you want the notebook to be completely self-contained; i.e. when all the cells of the notebook are run, the updated content is sent to the server, including all necessary metadata.

Regardless of the interface, the publish command/function probably needs to send both data and authentication headers, but in this post I will focus on the data.

## Data formats

Organizations that publish content usually stores it in specific data formats on the server.
Which allows appropriate rendering of the specific components.
So the first question is; should we send the raw notebook content to the server, process it there and store it in desirable format?
This has the advantage that if we change the data formats on the server, we can update the notebook processor accordingly, and we don't have to maintain an API contract between the client and server.
However it is much less flexible, as the next example will show:

```python title="my_article.ipynb"
import pandas as pd
from my_org import Diagram

df = pd.read_csv("my_data.csv")
# processing of the data here...
diagram = Diagram(df)
diagram.preview()
```

With the preview-function, we probably only want to send the data needed for the server to render our diagram.
Then it can send back either html or a preview url - in either case it can be displayed in the notebook as an iframe.
Hence it is much more flexible to do most of the processing on the client side, and send the data on a format that is equal or close to the format that the server expects.
It makes sense to have clear restrictions on what can be sent to the server, as we safeguard against unexpected before sending data.

## Nested data

In the previous example we wanted to publish a notebook, and we created an organization-specific diagram in the notebook.
This is an example of one content item (the article) which contains (a reference to) another content item.
Now, what happens if we use our command-line interface?

```bash
my_org publish my_article.ipynb --publish-date 2026-01-01
```

Let's assume that most of the processing happens on the client sids. While parsing the notebook file, it will have to discover all of the organization-specific components.
There are several ways to go about this.
There is one option we can quickly discard; executing code cells as we parse the file.
First of all, running notebooks as scripts is a complicated problem (one which marimo tries to solve) that we shouldn't embark on ourselves.
More generally, we don't want to run arbitrary code in the background; it should be the user who explicitly decides when to run their code.
If we can't run the code cells, we have to use the output of the code cells.

```python
```