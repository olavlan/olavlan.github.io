# ---
# title: "Generating articles with Pydantic AI (1)"
# date: 2026-02-26
# description: "Trying to learn Pydantic AI."
# categories: ["Pydantic AI", "Python"]
# execute:
#   enabled: false
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.1
#   kernelspec:
#     display_name: olavlan-github-io
#     language: python
#     name: python3
# ---

# %% [markdown]
# ## First approach

# %% [markdown]
# Imports:

# %%
import jinja2
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
import ssb_pubmd as ssb


# %% [markdown]
# 1. Define article model

# %%
class MarkdownBlock(BaseModel):
    type: str = "markdown"
    markdown_text: str = Field(description="The markdown text of the block.")


class HighchartBlock(BaseModel):
    type: str = "highchart"
    key: str = Field(pattern=r"^hc:", description="A unique key for the highchart.")
    data: ssb.Highchart = Field(description="The metadata of the highchart.")
    dataframe_code: str = Field(
        "The code to get from the data source to the dataframe used in the highchart, given as one block with necessary imports at top and the final dataframe stored in a variable 'df'."
    )


class FactboxBlock(BaseModel):
    type: str = "factbox"
    key: str = Field(pattern=r"^fb:", description="A unique key for the highchart.")
    data: ssb.Factbox = Field(description="The metadata of the factbox.")
    markdown_text: str = Field(description="The markdown content of the factbox.")


class StatisticalArticle(BaseModel):
    title: str = Field(description="A title for the article.")
    ingress: str = Field(description="A short ingress for the article.")
    blocks: list[MarkdownBlock | HighchartBlock | FactboxBlock]


# %% [markdown]
# 2. Create and run agent with article as output

# %%
agent = Agent(
    model=OpenAIChatModel("gpt-5-mini"),
    output_type=StatisticalArticle,
)

result = await agent.run(
    "Skriv en statistisk artikkel på norsk om klimadata, med en faktaboks og ett highcharts. Jeg har en csv-fil med kolonner 'year', 'temperature' og 'co2' - bruk pandas til å hente data for highchartet."
)

article: StatisticalArticle = result.output

# %% [markdown]
# 3. Insert article output into markdown template

# %%
environment = jinja2.Environment(loader=jinja2.FileSystemLoader(""))
template = environment.get_template("_template.qmd")
output = template.render(article=article)
with open("_output.qmd", "w", encoding="utf-8") as f:
    f.write(output)

# %% [markdown]
# Next steps:
#
# 1. How can we change the model to fit SSB articles better?
# 2. How can we make the user fill in what they want and the AI fill out the rest?
# 3. How can we make the style similar to existing articles?
