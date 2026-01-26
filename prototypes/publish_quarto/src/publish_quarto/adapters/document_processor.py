import json
import subprocess
from typing import Any
from typing import TypedDict, Iterator

import pandocfilters as pf

from publish_quarto.domain import Element


class PandocElement(TypedDict):
    t: str
    c: Any


PandocDocument = TypedDict(
    "PandocDocument",
    {
        "pandoc-api-version": list[int],
        "meta": dict[str, Any],
        "blocks": list[PandocElement],
    },
)


class PandocDocumentProcessor:
    """
    Processor for a pandoc document, i.e. the JSON-serialized pandoc AST of a document.

    Example pandoc AST with exactly one div:

    ```json
    {
        "pandoc-api-version": [1, 23, 1],
        "meta": {},
        "blocks": [
        {
            "t": "Div",
            "c": [
            ["my-highchart", ["ssb"], [["title", "My highchart"]]],
            []
            ]
        }
        ]
    }
    ```
    Html equivalent:
    ```html
    <div id="my-highchart" class="ssb" title="My highchart">
    </div>
    ```
    References:
    - Studying the result of command `pandoc FILE -t json`, where FILE is a minimal example document (e.g. Markdown or html).
    - https://github.com/jgm/pandocfilters has some examples of how to work with the format.
    - Note: no formal specification exists.
    """

    document: PandocDocument
    _element_index: dict[str, int]

    def load(self, raw_content: str) -> None:
        self.document: PandocDocument = json.loads(raw_content)
        self._element_index = {}

    def extract_metadata(self) -> dict[str, Any]:
        def meta_to_dict(meta: Any) -> Any:
            t, c = meta.get("t"), meta.get("c")
            if t == "MetaInlines":
                return pf.stringify(c)
            elif t == "MetaMap":
                return {k: meta_to_dict(v) for k, v in c.items()}
            elif t == "MetaList":
                return [meta_to_dict(v) for v in c]
            else:
                return c

        meta = self.document["meta"]

        return {k: meta_to_dict(v) for k, v in meta.items()}

    def extract_html(self) -> str:
        return self._document_to_html(self.document)

    def extract_elements(self, target_class: str) -> Iterator[Element]:
        self._element_index = self._generate_element_index(target_class)

        for id_, i in self._element_index.items():
            element = self.document["blocks"][i]
            inner_blocks: list[PandocElement] = element["c"][1]
            yield Element(
                id=id_,
                inner_html=self._blocks_to_html(inner_blocks),
            )

    def replace_element(self, id_: str, new_html: str) -> None:
        i = self._element_index[id_]
        self.document["blocks"][i] = {
            "t": "RawBlock",
            "c": ["html", new_html],
        }

    def _generate_element_index(self, target_class: str) -> dict[str, int]:
        index = {}
        for i, element in enumerate(self.document["blocks"]):
            if element["t"] != "Div":
                continue

            id_: str = element["c"][0][0]
            if not id_:
                continue

            classes: list[str] = element["c"][0][1]
            if target_class not in classes:
                continue

            index[id_] = i

        return index

    @classmethod
    def _blocks_to_html(cls, blocks: list[PandocElement]) -> str:
        document: PandocDocument = {
            "pandoc-api-version": [1, 23, 1],
            "meta": {},
            "blocks": blocks,
        }
        return cls._document_to_html(document)

    @classmethod
    def _document_to_html(cls, document: PandocDocument) -> str:
        result = subprocess.run(
            ["pandoc", "-f", "json", "-t", "html"],
            input=json.dumps(document),
            text=True,
            capture_output=True,
            check=True,
        )
        html = result.stdout
        return html
