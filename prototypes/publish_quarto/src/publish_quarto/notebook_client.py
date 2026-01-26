from publish_quarto.adapters.content_parser import OrgContentParser
from publish_quarto.adapters.storage import LocalFileStorage
from publish_quarto.domain import USER_KEY_PREFIX, Content
from narwhals.typing import IntoDataFrame
import narwhals as nw
from typing import Literal

STORAGE = LocalFileStorage()
CONTENT_PARSER = OrgContentParser()


def configure_factbox(
    key: str,
    title: str,
    display_type: Literal["default", "sneakPeek", "aiIcon"] = "default",
):
    metadata = {
        "content_type": "factBox",
        "title": title,
        "display_type": display_type,
    }

    content = CONTENT_PARSER.parse(
        metadata=metadata,
        html=None,
    )
    _store_user_content(user_key=key, content=content)

    md = _get_markdown_snippet(key, placeholder_text="Faktaboksens tekst skrives her.")
    print(md)


def create_highchart(
    key: str,
    title: str,
    data: IntoDataFrame,
    graph_type: str,
):
    metadata = {
        "content_type": "highchart",
        "title": title,
        "graph_type": graph_type,
    }
    html = _dataframe_to_html_table(data)

    content = CONTENT_PARSER.parse(metadata, html)
    _store_user_content(user_key=key, content=content)

    md = _get_markdown_snippet(key)
    print(md)


def _store_user_content(user_key: str, content: Content):
    key = USER_KEY_PREFIX + str(user_key)
    STORAGE.update(key, content.to_dict())


def _dataframe_to_html_table(data: IntoDataFrame) -> str:
    df = nw.from_native(data)
    html = "<table><tbody>\n"

    html += "<tr>\n"
    for name in df.columns:
        html += f"    <td>{name}</td>\n"
    html += "</tr>\n"

    for row in df.iter_rows():
        html += "  <tr>\n"
        for value in row:
            html += f"    <td>{value}</td>\n"
        html += "  </tr>\n"

    html += "</tbody></table>"

    return html


def _get_markdown_snippet(key: str, placeholder_text: str | None = None):
    div_config = f"{{ #{key} .org }}"
    div_content = f"\n{placeholder_text}\n\n" if placeholder_text is not None else ""
    return f"::: {div_config}\n{div_content}:::"
