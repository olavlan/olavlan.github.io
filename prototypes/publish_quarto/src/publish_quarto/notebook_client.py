import ipynbname
from publish_quarto.adapters.content_parser import OrgContentProcessor
from publish_quarto.adapters.storage import get_local_file_storage
from narwhals.typing import IntoDataFrame
import narwhals as nw
import nh3

CURRENT_NOTEBOOK = str(ipynbname.path())
STORAGE = get_local_file_storage(CURRENT_NOTEBOOK)
CONTENT_PROCESSOR = OrgContentProcessor()


def create_highchart(
    key: str,
    title: str,
    data: IntoDataFrame,
    graph_type: str,
):
    if not isinstance(key, str):
        raise Exception()
    metadata = {
        "content_type": "highchart",
        "title": title,
        "graph_type": graph_type,
    }
    html = _dataframe_to_html_table(data)

    content = CONTENT_PROCESSOR.parse(metadata, html)
    STORAGE.update(key, content.to_dict())

    md = _get_markdown_snippet(key)
    print(md)


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

    return nh3.clean(html, tags={"table", "tbody", "tr", "td"})


def _get_markdown_snippet(key: str):
    return f"::: {{ #{key} .org }}\n:::"
