# ---
# title: "Generating articles with Pydantic AI (4)"
# date: 2026-03-01
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
#     display_name: olavlan.github.io
#     language: python
#     name: python3
# ---

# %% [markdown]
# ## Separate data processing and article writing
#
# - We give the LLM the prepared data, so it only produces natural language
# - If we want the LLM to help with writing data processing code, that can be an independent step before producing the article

# %% [markdown]
#
# 1. Define interface:
#

# %%
from narwhals.typing import IntoDataFrame


def generate_article(prompt: str, **kwargs: IntoDataFrame) -> None:
    """
    Generer en artikkel basert på en prompt og data.

    Args:
        prompt: Instruksjoner for den nye artikkel. For gode resultater bør en modellartikkel refereres til, ettersom agenten er tilpasset for å lese og bruke eksisterende SSB-artikler. For beste resultater bør man også gi hovedtittel og ønskede seksjoner og figurer. Se eksempel under.
        **kwargs: Dataframes som skal brukes for å lage highcharts.
            * Én dataframe skal gis per ønsket highchart.
            * Dersom man har en dataframe i en variabel `df`, skal denne gis som `df=df`. Se eksempel.

    Example:
        ```
        generate_article(
            prompt="Artikkelen skal ha språklig stil og struktur lik følgende artikkel: https://www.ssb.no/bank-og-finansmarked/verdipapirmarkeder/statistikk/verdipapirer/artikler/mindre-utbytte-fra-aksjer. Tittelen skal være 'Oppgang for obligasjoner' og skal ha tre seksjoner: 'Olje og forsvar', 'Nedgang i noterte aksjer hos offentlig forvaltning' og 'Høye emisjoner for obligasjoner'. Det skal være ett highchart på slutten av hver seksjon.",
            df1=df1,
            df2=df2,
            df3=df3,
        )
        ```
    """
    raise NotImplementedError()


# %% [markdown]
# 2. Define improved article model
#

# %%
from pydantic import BaseModel, Field
import typing
from ssb_pubmd import Highchart as HighchartMetadata
from ssb_pubmd import Factbox as FactboxMetadata

Column = typing.Annotated[
    list[int] | list[float] | list[str], Field(description="The column of a table.")
]


class Highchart(BaseModel):
    type: typing.Literal["highchart"] = "highchart"
    id: str = Field(description="A unique id for the highchart.")
    metadata: HighchartMetadata = Field(description="The metadata of the highchart.")
    data: dict[str, Column] = Field(
        description="The data of the highchart, given as a mapping from column names to column values."
    )


class Factbox(BaseModel):
    type: typing.Literal["factbox"] = "factbox"
    id: str = Field(description="A unique id for the factbox.")
    metadata: FactboxMetadata = Field(description="The metadata of the factbox.")


class Section(BaseModel):
    title: str | None = Field("The title of the section, written as plain text.")
    highcharts: list[Highchart] = Field(
        description="Highcharts to include in the section, each with a unique id."
    )
    factboxes: list[Factbox] = Field(
        description="Factboxes to include in the section, each with a unique id."
    )
    markdown_text: str = Field(
        description=(
            "The published text of the section, written in Pandoc Markdown. The text is meant for the general audience and should not contain author notes. Highcharts and factboxes included as fenced divs referencing their id's, e.g.:\n"
            "::: {{ #my-highchart }}\n"
            ":::\n"
            "Note that factboxes are included with their markdown content:\n"
            "::: {{ #my-factbox }}\n"
            "The markdown text of the factbox goes here.\n"
            ":::\n"
        )
    )


class Article(BaseModel):
    title: str = Field(description="The title of the article, written as plain text.")
    ingress: str = Field(
        description="A short ingress written as plain text, summarizing the article in 1-3 sentences."
    )
    sections: list[Section] = Field(
        description="Sections of the article. All sections should have a title, except the first section."
    )


Article.model_json_schema()

# %% [markdown]
# 3. Parse example article (mocked)
#

# %%
import narwhals as nw


def parse_article_from_url(url: str) -> Article:
    """Manually parsed from https://www.ssb.no/bank-og-finansmarked/verdipapirmarkeder/statistikk/verdipapirer/artikler/mindre-utbytte-fra-aksjer. If we implement a get endpoint for the CMS service, we can implement parsing from the structured CMS data of any article."""
    first_section = Section(
        title="",
        markdown_text=(
            "Den samlede markedsverdien av verdipapirer registrert i Euronext Securities Oslo var på 7 698 milliarder kroner ved utgangen av 4. kvartal 2025, viser nye tall i statistikken verdipapirer. Dette er en økning på 114 milliarder kroner, eller 1,5 prosent sammenlignet med kvartalet før.\n\n"
            "Markedsverdien av noterte aksjer økte med 306 milliarder kroner eller 8,3 prosent i løpet av 2025. Økningen var i hovedsak drevet av selskaper innen bank og forsikring, mens olje bidro til å dempe veksten.\n\n"
            "Egenkapitalbevis hadde den sterkeste prosentvise veksten blant verdipapirtypene. Positiv kursutvikling og emisjoner bidro til at markedsverdien økte med 13 milliarder kroner, eller 8,6 prosent fra kvartalet før.\n\n"
            ":::{ #figur-1 }\n"
            ":::"
        ),
        highcharts=[
            Highchart(
                id="figur-1",
                metadata=HighchartMetadata(
                    title="Figur 1. Markedsverdi av noterte aksjer og obligasjoner. Utvikling i prosent",
                    graph_type="line",
                    xlabel="Kvartal",
                    ylabel="Prosent",
                ),
                data=nw.read_csv(
                    "data/figur-1-markedsverdi-av.csv", backend="polars", separator=";"
                ).to_dict(as_series=False),
            ),
        ],
        factboxes=[],
    )

    second_section = Section(
        title="Utlandets eierandel uendret",
        markdown_text=(
            "Den totale markedsverdien av noterte aksjer var 3 985 milliarder kroner ved utgangen av kvartalet. Utlandet er største eiersektor med 1 586 milliarder kroner, tilsvarende 40 prosent av markedsverdien. Andelen til utlandet har ligget på rundt 40 prosent over flere år. Offentlig forvaltning er nest største eiersektor med 1 071 milliarder kroner, eller 27 prosent av totalen. Utlandet og offentlig forvaltning eier til sammen over to tredeler av de noterte aksjene.\n\n"
            "Husholdningenes beholdning økte med 24 milliarder kroner i løpet av 2025, fra 177 til 201 milliarder kroner. Dette tilsvarer 5 prosent av den totale markedsverdien. I kvartalet nettokjøpte husholdningene noterte aksjer for litt over 2 milliarder kroner.\n\n"
            ":::{ #figur-2 }\n"
            ":::"
        ),
        highcharts=[
            Highchart(
                id="figur-2",
                metadata=HighchartMetadata(
                    title="Figur 2. Markedsverdi av noterte aksjer hos husholdninger. Millioner kroner",
                    graph_type="bar",
                    xlabel="Kvartal",
                    ylabel="Millioner kroner",
                ),
                data=nw.read_csv(
                    "data/figur-2-markedsverdi-av.csv", backend="polars", separator=";"
                ).to_dict(as_series=False),
            ),
        ],
        factboxes=[],
    )

    third_section = Section(
        title="Utbytte faller mens renteutbetalingene øker",
        markdown_text=(
            "Etter et rekordår for utbytte fra noterte aksjer i 2024, falt utbetalingene til 224 milliarder kroner i 2025. Til tross for nedgangen er nivået fortsatt høyt i et historisk perspektiv. De største bidragene kom fra olje- og bankselskaper. Utlandet var største mottaker av utbytte med 91 milliarder kroner, etterfulgt av offentlig forvaltning med 65 milliarder kroner. Husholdningene mottok til sammenligning 11 milliarder kroner.\n\n"
            "Renteutbetalingene fra obligasjoner utgjorde 140 milliarder kroner i 2025, og har økt hvert år siden 2022. Økningen skyldes i stor grad høyere renter på nyutstedte obligasjoner som følge av renteoppgangen i norsk og internasjonalt marked.\n\n"
            ":::{ #figur-3 }\n"
            ":::"
        ),
        highcharts=[
            Highchart(
                id="figur-3",
                metadata=HighchartMetadata(
                    title="Figur 3. Utbytte fra noterte aksjer og renteutbetalinger fra obligasjoner. Millioner kroner.",
                    graph_type="bar",
                    xlabel="År",
                    ylabel="Millioner kroner",
                ),
                data=nw.read_csv(
                    "data/figur-3-utbytte-fra-note.csv", backend="polars", separator=";"
                ).to_dict(as_series=False),
            ),
        ],
        factboxes=[],
    )

    return Article(
        title="Mindre utbytte fra aksjer",
        ingress="Markedsverdien av børsnoterte aksjer registrert i Euronext Securities Oslo økte med 1,4 prosent eller 54 milliarder kroner gjennom 4. kvartal 2025. For året samlet sett var veksten 8,3 prosent, mens utbyttebetalingene var lavere enn i rekordåret 2024.",
        sections=[first_section, second_section, third_section],
    )


parse_article_from_url("").model_dump()

# %% [markdown]
# 4. Implement interface

# %%
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
import json

agent = Agent(
    model=OpenAIChatModel("gpt-5-mini"),
    output_type=Article,
    instructions="Du skriver artikler basert på modellartikler, data  og instruksjoner gitt av brukeren.",
)


@agent.tool_plain
def get_article_from_url(url: str) -> Article:
    """Given a url from the user, returns the corresponding article."""
    return parse_article_from_url(url)


async def generate_article(prompt: str, **kwargs: IntoDataFrame) -> Article:
    new_prompt = prompt + "\n\nHighcharts skal lages med følgende data:"
    for _, df in kwargs.items():
        table = nw.from_native(df).to_dict(as_series=False)
        new_prompt += json.dumps(table)

    result = await agent.run(prompt)

    for message in result.all_messages():
        print(message)

    return result.output


# %% [markdown]
# 5. Try interface

# %%
df1 = nw.read_csv(
    "data/figur-1-markedsverdi-av-new.csv", backend="polars", separator=";"
)
df2 = nw.read_csv(
    "data/figur-2-markedsverdi-av-new.csv", backend="polars", separator=";"
)
df3 = nw.read_csv("data/figur-3-plydende-verdi-a.csv", backend="polars", separator=";")


article = await generate_article(
    prompt="Artikkelen skal ha språklig stil og struktur lik følgende artikkel: https://www.ssb.no/bank-og-finansmarked/verdipapirmarkeder/statistikk/verdipapirer/artikler/mindre-utbytte-fra-aksjer. Tittelen skal være 'Oppgang for obligasjoner' og skal ha tre seksjoner: 'Olje og forsvar', 'Nedgang i noterte aksjer hos offentlig forvaltning' og 'Høye emisjoner for obligasjoner'. Referér til konkrete tall i teksten. Sett inn ett highchart per seksjon.",
    df1=df1,
    df2=df2,
    df3=df3,
)

article.model_dump()

# %% [markdown]
# 5. Insert article output into new markdown template
#

# %%
import jinja2

environment = jinja2.Environment(loader=jinja2.FileSystemLoader(""))
template = environment.get_template("_template.qmd")
output = template.render(
    article=article,
)
with open("_output.qmd", "w", encoding="utf-8") as f:
    f.write(output)

# %% [markdown]
# :::: {.callout-note title="Jinja template" collapse=true}
#
# ````{.markdown}
# {{< include _template.qmd >}}
# ````
#
# ::::
#
# :::: {.callout-note title="Template output" collapse=true}
#
# ````{.markdown}
# {{< include _output.qmd >}}
# ````
#
# ::::
#

# %% [markdown]
# Conclusions:
#
# * It needs more context to be able to create a meaningful discussion.
# * The LLM is not able to reference specific numbers from the highchart properly.
#
# Next steps to try:
#
# * Instead of passing in dataframes, pass in custom objects which describes both the data and context. (e.g. `DataSet("df", df, "This dataset describes ..., has columns ...., and the results are related to ...")`).
# * The output article shouldn't have any data, just references to the input data (e.g. above data would be referenced as `"df"`).
# * Instruct the agent to not put any actual numbers in the text, just placeholders (spans - []).
# * Change `get_article_from_url` to `parse_example_from_url` which shows both the input data and the output article.
# * Try a prompt like: "Example input data:", "Example output article:", "Use this as a model to create a new article based on the following new input data:", "Additional instructions:".
# * Try to drop the sections and have the LLM write the whole article as one string.
# * Try with completely different model articles.

# %% [raw] vscode={"languageId": "raw"}
#
