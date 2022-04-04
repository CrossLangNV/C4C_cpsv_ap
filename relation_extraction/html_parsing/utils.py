import json
from typing import List, Union

import justext
from lxml.etree import _Element, _ElementTree


def dom_write(html_tree: Union[_ElementTree,
                               _Element], filename):
    def _write(el):
        el.write(filename,
                 pretty_print=True,
                 encoding="utf-8",
                 xml_declaration=True)

    try:
        _write(html_tree)

    except AttributeError:
        _write(html_tree.getroottree())


class hashabledict(dict):
    def __hash__(self):
        return hash(tuple(sorted(self.items())))


def clean_tag_text(el: _Element):
    """
    TODO move out
    """
    l_text = list(el.itertext())

    text = "".join(l_text).strip()
    return justext.utils.normalize_whitespace(text)


def export_jsonl(l_d_json: List[dict], filename):
    with open(filename, 'w+', encoding="UTF-8") as f:
        f.truncate(0)

    for d_json in l_d_json:
        json_string = json.dumps(d_json, ensure_ascii=False)

        with open(filename, "a", encoding="UTF-8") as f:
            f.write(json_string + "\n")
