import xml.etree.ElementTree as ET
from datetime import datetime
import sys


def sort_rss(input_file, output_file):
    tree = ET.parse(input_file)
    root = tree.getroot()

    channel = root.find(".//channel")
    if channel is None:
        raise Exception()
    items = channel.findall("item")

    for item in items:
        pub_date = item.findtext("pubDate")
        if pub_date is None:
            raise Exception()
        dt = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %z")
        title_elem = item.find("title")
        if title_elem is None:
            raise Exception()
        title_elem.text = f"[{dt:%m-%d-%Y}] {title_elem.text}"

    tree.write(output_file, encoding="utf-8", xml_declaration=True)


sort_rss(sys.argv[1], sys.argv[2])
