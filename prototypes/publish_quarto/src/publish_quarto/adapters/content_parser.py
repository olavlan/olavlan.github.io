from dataclasses import asdict
from dataclasses import dataclass
from typing import Any
from typing import Literal

from publish_quarto.domain import Content

ContentType = Literal["article", "highchart", "factBox"]


@dataclass
class OrgContent:
    content_type: ContentType
    title: str = ""
    publish_folder: str = ""
    publish_path: str = ""
    publish_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def _validate(self) -> bool:
        if not (self.title and self.publish_folder):
            return False
        return True

    def serialize(self) -> dict[str, Any]:
        if not self._validate():
            raise Exception()
        s = {
            "contentType": self.content_type,
            "displayName": self.title,
            "parentPath": self.publish_folder,
            "data": {},
        }
        if self.publish_id is not None:
            s["_id"] = self.publish_id
        return s


@dataclass
class Article(OrgContent):
    content_type: ContentType = "article"
    ingress: str = ""
    html: str = ""

    def serialize(self) -> dict[str, Any]:
        s = super().serialize()
        s["data"]["ingress"] = self.ingress
        s["data"]["articleText"] = self.html
        return s


GraphType = Literal["line", "pie", "column", "bar", "area", "barNegative"]


@dataclass
class Highchart(OrgContent):
    content_type: ContentType = "highchart"
    graph_type: GraphType = "line"
    html_table: str | None = None

    def serialize(self) -> dict[str, Any]:
        s = super().serialize()
        s["data"]["graphType"] = self.graph_type
        if self.html_table is not None:
            s["data"]["htmlTable"] = self.html_table
        return s


@dataclass
class FactBox(OrgContent):
    content_type: ContentType = "factBox"
    display_type: Literal["default", "sneakPeek", "aiIcon"] = "default"
    inner_html: str = ""

    def serialize(self) -> dict[str, Any]:
        s = super().serialize()
        s["data"]["expansionBoxType"] = self.display_type
        s["data"]["text"] = self.inner_html
        return s


class OrgContentProcessor:
    def parse(self, metadata: dict[str, Any], html: str) -> Content:
        content_type = metadata.get("content_type")
        if content_type == "article":
            data = metadata | {"html": html}
            return Article(**data)
        elif content_type == "highchart":
            data = metadata | {"html_table": html} if html else metadata
            return Highchart(**data)
        elif content_type == "factBox":
            data = metadata | {"inner_html": html}
            return FactBox(**metadata)
        else:
            return OrgContent(**metadata)

    def serialize(self, content: Content) -> dict[str, Any]:
        if isinstance(content, OrgContent):
            return content.serialize()
        else:
            raise Exception(
                "Serialization handlers only implemented for content of type OrgContent."
            )
