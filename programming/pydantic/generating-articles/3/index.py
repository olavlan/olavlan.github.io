# %% [markdown]
# ---
# title: "Generating articles with Pydantic AI (3)"
# date: 2026-02-28
# categories: ["Pydantic AI", "Python"]
# execute:
#   enabled: false
# ---

# %% [markdown]
# ## A more general approach
#
# - Only based on one user prompt
# - More general article model
# - The LLM decides the types and order of the blocks in a section
# - Add instructions for more predictable results

# %% [markdown]
# Imports:
#

# %% [markdown]
# 1. Define improved article model
#

# %%
from pydantic import BaseModel, Field
import typing
from ssb_pubmd import Highchart as HighchartMetadata
from ssb_pubmd import Factbox as FactboxMetadata


class Highchart(BaseModel):
    type: typing.Literal["highchart"] = "highchart"
    key: str = Field(description="A unique key for the highchart.")
    metadata: HighchartMetadata = Field(description="The metadata of the highchart.")
    dataframe: str | None = Field("""
        The Python code to get from the data source to the dataframe used by the highchart. Requirements: 
            - Given as one block of code withou comments. 
            - Necessary imports at top. 
            - Final dataframe stored in a variable `df`.
    """)


class Factbox(BaseModel):
    type: typing.Literal["factbox"] = "factbox"
    key: str = Field(description="A unique key for the factbox.")
    metadata: FactboxMetadata = Field(description="The metadata of the factbox.")
    markdown_text: str = Field(description="The markdown content of the factbox.")


class Paragraph(BaseModel):
    type: typing.Literal["paragraph"] = "paragraph"
    markdown_text: str = Field(
        description="""
            A single paragraph, written as one Markdown block with only inline formatting.
        """
    )


class Section(BaseModel):
    title: str | None = Field("The title of the section, written as plain text.")
    blocks: typing.Sequence[Paragraph | Highchart | Factbox] = Field(
        description="A list of blocks, in the order they should appear in the section.."
    )


class Article(BaseModel):
    title: str = Field(description="The title of the article, written as plain text.")
    ingress: str = Field(
        description="A short ingress written as plain text, summarizing the article, 1-3 sentences.."
    )
    sections: typing.Sequence[Section] = Field(
        description="Sections of the article. All sections should have a title, except the first section."
    )


# %% [markdown]
# 2. Parse example article (mocked)
#


# %%
def parse_article_from_url(url: str) -> Article:
    """Manually parsed from https://www.ssb.no/bank-og-finansmarked/verdipapirmarkeder/statistikk/verdipapirer/artikler/mindre-utbytte-fra-aksjer. If we implement a get endpoint for the CMS service, we can implement parsing from the structured CMS data of any article."""
    first_section = Section(
        title=None,
        blocks=[
            Paragraph(
                type="paragraph",
                markdown_text="Den samlede markedsverdien av verdipapirer registrert i Euronext Securities Oslo var på 7 698 milliarder kroner ved utgangen av 4. kvartal 2025, viser nye tall i statistikken verdipapirer. Dette er en økning på 114 milliarder kroner, eller 1,5 prosent sammenlignet med kvartalet før.",
            ),
            Paragraph(
                type="paragraph",
                markdown_text="Markedsverdien av noterte aksjer økte med 306 milliarder kroner eller 8,3 prosent i løpet av 2025. Økningen var i hovedsak drevet av selskaper innen bank og forsikring, mens olje bidro til å dempe veksten.",
            ),
            Paragraph(
                type="paragraph",
                markdown_text="Egenkapitalbevis hadde den sterkeste prosentvise veksten blant verdipapirtypene. Positiv kursutvikling og emisjoner bidro til at markedsverdien økte med 13 milliarder kroner, eller 8,6 prosent fra kvartalet før.",
            ),
            Highchart(
                type="highchart",
                key="figur-1",
                metadata=HighchartMetadata(
                    title="Figur 1. Markedsverdi av noterte aksjer og obligasjoner. Utvikling i prosent",
                    xlabel="Kvartal",
                    ylabel="Prosent",
                ),
                dataframe=None,
            ),
        ],
    )
    second_section = Section(
        title="Utlandets eierandel uendret",
        blocks=[
            Paragraph(
                type="paragraph",
                markdown_text="Den totale markedsverdien av noterte aksjer var 3 985 milliarder kroner ved utgangen av kvartalet. Utlandet er største eiersektor med 1 586 milliarder kroner, tilsvarende 40 prosent av markedsverdien. Andelen til utlandet har ligget på rundt 40 prosent over flere år. Offentlig forvaltning er nest største eiersektor med 1 071 milliarder kroner, eller 27 prosent av totalen. Utlandet og offentlig forvaltning eier til sammen over to tredeler av de noterte aksjene.",
            ),
            Paragraph(
                type="paragraph",
                markdown_text="Husholdningenes beholdning økte med 24 milliarder kroner i løpet av 2025, fra 177 til 201 milliarder kroner. Dette tilsvarer 5 prosent av den totale markedsverdien. I kvartalet nettokjøpte husholdningene noterte aksjer for litt over 2 milliarder kroner.",
            ),
            Highchart(
                type="highchart",
                key="figur-2",
                metadata=HighchartMetadata(
                    title="Figur 2. Markedsverdi av noterte aksjer hos husholdninger. Millioner kroner",
                    xlabel="Kvartal",
                    ylabel="Millioner kroner",
                ),
                dataframe=None,
            ),
        ],
    )
    third_section = Section(
        title="Utbytte faller mens renteutbetalingene øker",
        blocks=[
            Paragraph(
                type="paragraph",
                markdown_text="Etter et rekordår for utbytte fra noterte aksjer i 2024, falt utbetalingene til 224 milliarder kroner i 2025. Til tross for nedgangen er nivået fortsatt høyt i et historisk perspektiv. De største bidragene kom fra olje- og bankselskaper. Utlandet var største mottaker av utbytte med 91 milliarder kroner, etterfulgt av offentlig forvaltning med 65 milliarder kroner. Husholdningene mottok til sammenligning 11 milliarder kroner.",
            ),
            Paragraph(
                type="paragraph",
                markdown_text="Renteutbetalingene fra obligasjoner utgjorde 140 milliarder kroner i 2025, og har økt hvert år siden 2022. Økningen skyldes i stor grad høyere renter på nyutstedte obligasjoner som følge av renteoppgangen i norsk og internasjonalt marked.",
            ),
            Highchart(
                type="highchart",
                key="figur-3",
                metadata=HighchartMetadata(
                    title="Figur 3. Utbytte fra noterte aksjer og renteutbetalinger fra obligasjoner. Millioner kroner",
                    xlabel="År",
                    ylabel="Millioner kroner",
                ),
                dataframe=None,
            ),
        ],
    )
    return Article(
        title="Mindre utbytte fra aksjer",
        ingress="Markedsverdien av børsnoterte aksjer registrert i Euronext Securities Oslo økte med 1,4 prosent eller 54 milliarder kroner gjennom 4. kvartal 2025. For året samlet sett var veksten 8,3 prosent, mens utbyttebetalingene var lavere enn i rekordåret 2024.",
        sections=[first_section, second_section, third_section],
    )


# %% [markdown]
# 4. Create and run agent with tool to get article
#

# %%
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel

agent = Agent(
    model=OpenAIChatModel("gpt-5-mini"),
    output_type=Article,
    instructions="Du skriver artikler basert på modellartikler og instruksjoner gitt av brukeren. Alle datafelter som har naturlig språk skal skrives for den generelle befolkningen, og skal derfor ikke ha forfatternotater eller referanser til kode.",
)


@agent.tool_plain
def get_article_from_url(url: str) -> Article:
    """Given a url from the user, returns the corresponding article."""
    return parse_article_from_url(url)


prompt = """
Jeg ønsker en artikkel som følger samme struktur og eksempel som denne: https://www.ssb.no/bank-og-finansmarked/verdipapirmarkeder/statistikk/verdipapirer/artikler/mindre-utbytte-fra-aksjer. Skriv om størrelsen på boliger i Norge. Legg til highcharts som bruker pandas-dataframes som input - skriv eksempelkode som jeg selv kan modifisere.
"""
result = await agent.run(prompt)

for message in result.all_messages():
    print(message)

article: Article = result.output

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
# * The LLM still produces author notes and code references in text blocks that are supposed to be user-facing.
# * We could try to make the LLM produce the whole section text in one string, then validating the text against the defined components of the section.
# * The next goal could be to make the agent take in one article and some new data tables, and then produce a similar style article with those new data tables.
# * We can eventually expose a Python function that takes in the data frames, example articles, and extra instructions, and creates a new file with both the correct code and the generated article content. We should make sure that it is the actual dataframes that are being passed into the highchart functions.
