# ---
# title: Generating articles with Pydantic AI (2)
# date: 2026-02-27
# categories:
#   - Pydantic AI
#   - Python
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
# ## Improved approach
#

# %% [markdown]
# Imports:
#

# %%
from typing import Any
import jinja2
from pydantic import BaseModel, Field, field_validator, ValidationError
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from ssb_pubmd import Highchart as HighchartMetadata
from ssb_pubmd import Factbox as FactboxMetadata


# %% [markdown]
# 1. Define improved article model
#

# %%
class Highchart(BaseModel):
    type: str = "highchart"
    key: str = Field(description="A unique key for the highchart.")
    metadata: HighchartMetadata = Field(description="The metadata of the highchart.")
    dataframe_code: str | None = Field(
        "The code to get from the data source to the dataframe used for the highchart, given as one block with necessary imports at top and the final dataframe stored in a variable 'df'. No code comments."
    )


class Factbox(BaseModel):
    type: str = "factbox"
    key: str = Field(description="A unique key for the factbox.")
    metadata: FactboxMetadata = Field(description="The metadata of the factbox.")
    markdown_text: str = Field(description="The markdown content of the factbox.")


class Section(BaseModel):
    title: str = Field("The title of the section.")
    paragraphs: list[str] = Field(
        description="The paragraphs of the section, each written as one Markdown block with only inline formatting."
    )
    highchart: Highchart | None = Field(
        description="Optionally a highchart to put at the end of the section."
    )
    factbox: Factbox | None = Field(
        description="Optionally a factbox to put at the end of a section"
    )


class Introduction(Section):
    title: str = ""


class Article(BaseModel):
    title: str = Field(description="A title for the article.")
    ingress: str = Field(description="A short ingress for the article.")
    introduction: Introduction = Field(
        description="The introducing section of the article."
    )
    additional_sections: list[Section] = Field(
        description="Additional sections of the article."
    )


# %% [markdown]
# 2. Parse example article (mocked)
#

# %%
def parse_article_from_url(url: str) -> Article:
    """Manually parsed from https://www.ssb.no/bank-og-finansmarked/verdipapirmarkeder/statistikk/verdipapirer/artikler/mindre-utbytte-fra-aksjer, but if we implement a get endpoint for the CMS service, we can implement parsing from the structured CMS data of any article."""
    first_section = Introduction(
        paragraphs=[
            "Den samlede markedsverdien av verdipapirer registrert i Euronext Securities Oslo var på 7 698 milliarder kroner ved utgangen av 4. kvartal 2025, viser nye tall i statistikken verdipapirer. Dette er en økning på 114 milliarder kroner, eller 1,5 prosent sammenlignet med kvartalet før.",
            "Markedsverdien av noterte aksjer økte med 306 milliarder kroner eller 8,3 prosent i løpet av 2025. Økningen var i hovedsak drevet av selskaper innen bank og forsikring, mens olje bidro til å dempe veksten.",
            "Egenkapitalbevis hadde den sterkeste prosentvise veksten blant verdipapirtypene. Positiv kursutvikling og emisjoner bidro til at markedsverdien økte med 13 milliarder kroner, eller 8,6 prosent fra kvartalet før.",
        ],
        highchart=Highchart(
            key="figur-1",
            metadata=HighchartMetadata(
                title="Figur 1. Markedsverdi av noterte aksjer og obligasjoner. Utvikling i prosent",
                xlabel="Kvartal",
                ylabel="Prosent",
            ),
            dataframe_code=None,
        ),
        factbox=None,
    )
    second_section = Section(
        title="Utlandets eierandel uendret",
        paragraphs=[
            "Den totale markedsverdien av noterte aksjer var 3 985 milliarder kroner ved utgangen av kvartalet. Utlandet er største eiersektor med 1 586 milliarder kroner, tilsvarende 40 prosent av markedsverdien. Andelen til utlandet har ligget på rundt 40 prosent over flere år. Offentlig forvaltning er nest største eiersektor med 1 071 milliarder kroner, eller 27 prosent av totalen. Utlandet og offentlig forvaltning eier til sammen over to tredeler av de noterte aksjene.",
            "Husholdningenes beholdning økte med 24 milliarder kroner i løpet av 2025, fra 177 til 201 milliarder kroner. Dette tilsvarer 5 prosent av den totale markedsverdien. I kvartalet nettokjøpte husholdningene noterte aksjer for litt over 2 milliarder kroner.",
        ],
        highchart=Highchart(
            key="figur-2",
            metadata=HighchartMetadata(
                title="Figur 2. Markedsverdi av noterte aksjer hos husholdninger. Millioner kroner",
                xlabel="Kvartal",
                ylabel="Millioner kroner",
            ),
            dataframe_code=None,
        ),
        factbox=None,
    )
    third_section = Section(
        title="Utbytte faller mens renteutbetalingene øker",
        paragraphs=[
            "Etter et rekordår for utbytte fra noterte aksjer i 2024, falt utbetalingene til 224 milliarder kroner i 2025. Til tross for nedgangen er nivået fortsatt høyt i et historisk perspektiv. De største bidragene kom fra olje- og bankselskaper. Utlandet var største mottaker av utbytte med 91 milliarder kroner, etterfulgt av offentlig forvaltning med 65 milliarder kroner. Husholdningene mottok til sammenligning 11 milliarder kroner.",
            "Renteutbetalingene fra obligasjoner utgjorde 140 milliarder kroner i 2025, og har økt hvert år siden 2022. Økningen skyldes i stor grad høyere renter på nyutstedte obligasjoner som følge av renteoppgangen i norsk og internasjonalt marked.",
        ],
        highchart=Highchart(
            key="figur-3",
            metadata=HighchartMetadata(
                title="Figur 3. Utbytte fra noterte aksjer og renteutbetalinger fra obligasjoner. Millioner kroner",
                xlabel="År",
                ylabel="Millioner kroner",
            ),
            dataframe_code=None,
        ),
        factbox=None,
    )
    return Article(
        title="Mindre utbytte fra aksjer",
        ingress="Markedsverdien av børsnoterte aksjer registrert i Euronext Securities Oslo økte med 1,4 prosent eller 54 milliarder kroner gjennom 4. kvartal 2025. For året samlet sett var veksten 8,3 prosent, mens utbyttebetalingene var lavere enn i rekordåret 2024.",
        introduction=first_section,
        additional_sections=[second_section, third_section],
    )


# %% [markdown]
# 3. Define article request model
#

# %%
class DataSource(BaseModel):
    """What should go here?"""

    pass


class ArticleRequest(BaseModel):
    template_article: Article = Field(
        description="The template article to base the new article on."
    )
    data_source: DataSource | None = Field(
        description="The available data source that can be processed with Python."
    )
    requested_changes: str = Field(
        description="Changes to the original article requested by the user."
    )


# %% [markdown]
# 4. Parse user input
#

# %%
user_input = {
    "template_article_url": "https://www.ssb.no/bank-og-finansmarked/verdipapirmarkeder/statistikk/verdipapirer/artikler/mindre-utbytte-fra-aksjer",
    "requested_changes": "For hver av figurene, legg til kode med pandas som viser et eksempel på hvordan de kan bli generert. Anta at datakilden er en parquet-fil. Legg til en faktaboks på slutten av artikkelen som forklarer hvor dataene i figurene kommer fra.",
    "data_source": None,
}
template_article = parse_article_from_url(user_input["template_article_url"])
article_request = ArticleRequest(**user_input, template_article=template_article)

# %% [markdown]
# 5. Create and run agent with improved prompt
#

# %%
agent = Agent(
    model=OpenAIChatModel("gpt-5-mini"),
    output_type=Article,
)

prompt = f"""
Opprett en ny artikkel basert på følgende eksempel:

{article_request.template_article.model_dump()}

Den nye artikkelen skal følge samme format og ny tekst skal skrives i samme stil.

Forfatteren ønsker følgende endringer:

{article_request.requested_changes}

Forfatteren har følgende datakilde som kan prosesseres med Python-kode:

{article_request.data_source}
"""
result = await agent.run(prompt)

article: Article = result.output

# %% [markdown]
# 6. Insert article output into new markdown template
#

# %%
sections = [article.introduction] + article.additional_sections
highcharts = [s.highchart for s in sections if s.highchart is not None]
factboxes = [s.factbox for s in sections if s.factbox is not None]

environment = jinja2.Environment(loader=jinja2.FileSystemLoader(""))
template = environment.get_template("_template.qmd")
output = template.render(
    article=article,
    sections=sections,
    highcharts=highcharts,
    factboxes=factboxes,
)
with open("_output.qmd", "w", encoding="utf-8") as f:
    f.write(output)

# %% [markdown]
# :::: {.callout-note title="Jinja template" collapse=true}
# ````{.markdown}
# {{< include _template.qmd >}}
# ````
# ::::
#
# :::: {.callout-note title="Template output" collapse=true}
# ````{.markdown}
# {{< include _output.qmd >}}
# ````
# ::::
#

# %% [markdown]
# Next steps:
#
# 1. How can a data source be defined?
#
