import hashlib
import json
import os
import re
from typing import List, Union

import justext
import langcodes
import lxml.html
from lxml.etree import _Element, _ElementTree
from pydantic import BaseModel

from data.html import get_html, url2html

FOLDER_TMP = os.path.join(os.path.dirname(__file__), "TMP")


def dom_write(html_tree: Union[_ElementTree, _Element],
              filename):
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


"""
Data utils:
"""


def _tmp_html(url, filename_html=None) -> str:
    if filename_html is None:
        filename_html = _tmp_filename(url, ext=".html")

    try:
        html = get_html(filename_html)
    except FileNotFoundError:
        url2html(url, filename_html)
        html = get_html(filename_html)
    # except OSError as oserr:
    #     # Filename too long
    #     if oserr.errno == errno.ENAMETOOLONG:
    #
    #         basename = f"{basename[:50]}_{hashlib.sha1(basename.encode()).hexdigest()}"
    #         # Make a shorter filename
    #         FILENAME_INPUT_HTML = os.path.join(FOLDER_TMP, f"{basename}.html")
    #
    #         try:
    #             html = get_html(FILENAME_INPUT_HTML)
    #         except FileNotFoundError:
    #             url2html(url, FILENAME_INPUT_HTML)
    #             html = get_html(FILENAME_INPUT_HTML)
    #
    #     else:
    #         raise  # re-raise previously caught exception

    return html


def _tmp_filename(name: str,
                  ext: str = "",
                  prefix: str = "",
                  c_max: int = 100) -> str:
    """

    Args:
        name:
        prefix:
        ext:
        c_max: To prevent too long filenames, the name will be hashed.

    Returns:

    """

    # Make valid by removing non-valid chars and replace with "_"
    re_pattern = re.compile(r"[^a-zA-Z0-9]+")
    basename = re_pattern.sub("_", name)

    if len(basename) > c_max:
        basename = f"{basename[:c_max]}_{hashlib.sha1(name.encode()).hexdigest()}"

    tmp_filename = os.path.join(FOLDER_TMP, f"{prefix}{basename}{ext}")

    return tmp_filename


def _get_language_full_from_code(language_code):
    """
    For justext
    """

    language_full = "_".join(langcodes.get(language_code).display_name().split())

    if language_code.upper() == "NB":
        return "Norwegian_Bokmal"

    if language_code.upper() == "NN":
        return "Norwegian_Nynorsk"

    language_full = langcodes.get(language_code).display_name()
    if language_full == "Norwegian":  # Default Norwegian (Spoken by ~90% of Norway)
        return "Norwegian_Bokmal"

    return language_full


def get_lxml_el_from_paragraph(html_root: lxml.html.etree._Element,
                               paragraph: justext.core.Paragraph
                               ):
    l_e = html_root.xpath(paragraph.xpath)
    if len(l_e) != 1:
        raise LookupError(f"Expected exactly one element: {l_e}")

    return l_e[0]


def justext_bold_titles(*args, **kwargs):
    """
    Based on justext 3.0.0

    Same pipeline as justext, but bold titles are also considered headers.

    '
    Converts an HTML page into a list of classified paragraphs. Each paragraph
    is represented as instance of class ˙˙justext.paragraph.Paragraph˙˙.
    '
    """

    raise NotImplementedError()

    return justext.justext(*args, **kwargs)
