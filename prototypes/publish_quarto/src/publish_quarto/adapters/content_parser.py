from dataclasses import asdict
from dataclasses import dataclass
from typing import Any
from typing import Literal
from typing import Mapping
import nh3

from publish_quarto.domain import Content


@dataclass
class OrgContent:
    title: str
    publish_folder: str | None = None
    content_type: str | None = None
    publish_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def is_publishable(self) -> bool:
        if self.title == "":
            return False
        if self.publish_id is None and self.publish_folder is None:
            return False
        return True

    def serialize(self) -> dict[str, Any]:
        if not self.is_publishable():
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
    content_type: str | None = "article"
    ingress: str = ""
    html_text: str = ""

    def serialize(self) -> dict[str, Any]:
        s = super().serialize()
        s["data"]["ingress"] = self.ingress
        s["data"]["articleText"] = self.html_text
        return s


GraphType = Literal["line", "pie", "column", "bar", "area", "barNegative"]


@dataclass
class Highchart(OrgContent):
    content_type: str | None = "highchart"
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
    content_type: str | None = "factBox"
    display_type: Literal["default", "sneakPeek", "aiIcon"] = "default"
    html_text: str = ""

    def serialize(self) -> dict[str, Any]:
        s = super().serialize()
        s["data"]["expansionBoxType"] = self.display_type
        s["data"]["text"] = self.html_text
        return s


BASIC_HTML_TAGS = {
    "p",
    "br",
    "strong",
    "em",
    "b",
    "i",
    "ul",
    "ol",
    "li",
    "blockquote",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "a",
}


class OrgContentParser:
    def parse(self, metadata: Mapping[str, Any], html: str | None) -> Content:
        match metadata.get("content_type"):
            case "article":
                return self._parse_article(metadata, html)
            case "factBox":
                return self._parse_factbox(metadata, html)
            case "highchart":
                return self._parse_highchart(metadata, html)
            case _:
                return OrgContent(**metadata)

    def serialize(self, content: Content) -> dict[str, Any]:
        if isinstance(content, OrgContent):
            return content.serialize()
        else:
            raise Exception()

    @classmethod
    def _parse_article(cls, metadata: Mapping[str, Any], html: str | None) -> Article:
        article = Article(
            title=metadata["title"],
            publish_folder=metadata["path"],
            ingress=metadata.get("ingress", ""),
        )
        if html is not None:
            allowed_html_tags = BASIC_HTML_TAGS
            html_text = nh3.clean(html, tags=allowed_html_tags)
            article.html_text = html_text
        return article

    @classmethod
    def _parse_factbox(cls, metadata: Mapping[str, Any], html: str | None) -> FactBox:
        factbox = FactBox(**metadata)
        if html is not None:
            allowed_html_tags = BASIC_HTML_TAGS - {"h2"}
            html_text = nh3.clean(html, tags=allowed_html_tags)
            factbox.html_text = html_text
        return factbox

    @classmethod
    def _parse_highchart(
        cls, metadata: Mapping[str, Any], html: str | None
    ) -> Highchart:
        highchart = Highchart(**metadata)
        if html is not None:
            allowed_html_tags = {"table", "tbody", "tr", "td"}
            html_table = nh3.clean(html, tags=allowed_html_tags)
            highchart.html_table = html_table
        return highchart
