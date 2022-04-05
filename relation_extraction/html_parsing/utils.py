import json
from typing import List, Union

import justext
import lxml
from lxml.etree import _Element, _ElementTree
from pydantic import BaseModel


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


def export_jsonl(l_d_json: List[Union[dict, BaseModel]], filename):
    with open(filename, 'w+', encoding="UTF-8") as f:
        f.truncate(0)

    for d_json in l_d_json:

        if isinstance(d_json, BaseModel):
            # d_json = d_json.dict()
            json_string = d_json.json(ensure_ascii=False)
        else:
            json_string = json.dumps(d_json, ensure_ascii=False)

        with open(filename, "a", encoding="UTF-8") as f:
            f.write(json_string + "\n")


def makeParentLine(node, attach_head=False):
    # Add how much text context is given. e.g. 2 would mean 2 parent's text
    # nodes are also displayed
    # if questionContains is not None:
    #     newstr = doesThisElementContain(questionContains, lxml.html.tostring(node))
    # else:
    newstr = lxml.html.tostring(node, encoding="UTF-8").decode('utf8')
    parent = node.getparent()
    while parent is not None:
        if attach_head and parent.tag == 'html':
            newstr = lxml.html.tostring(parent.find(
                './/head'), encoding='utf8').decode('utf8') + newstr
        tag, items = parent.tag, parent.items()
        attrs = " ".join(['{}="{}"'.format(x[0], x[1]) for x in items if len(x) == 2])
        newstr = '<{} {}>{}</{}>'.format(tag, attrs, newstr, tag)
        parent = parent.getparent()
    return newstr
