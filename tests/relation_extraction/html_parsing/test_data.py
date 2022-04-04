import unittest

import justext
import lxml

from data.html import get_html, url2html
from relation_extraction.html_parsing.data import data_extraction
from relation_extraction.html_parsing.general_parser import GeneralHTMLParser2, \
    get_lxml_el_from_paragraph
# Code: language
from relation_extraction.html_parsing.utils import export_jsonl

D_LANG = {"NL": "Dutch"}


class TestScriptData(unittest.TestCase):
    def test_main(self):
        data_extraction()

        self.assertEqual(0, 1)

    def test_turnhout(self,
                      url="https://www.turnhout.be/inname-openbaar-domein",
                      FILENAME_INPUT_HTML="PARSER_DEBUG_THOUT.html",
                      language="Dutch"):

        def _get_parser():

            try:
                html = get_html(FILENAME_INPUT_HTML)
            except FileNotFoundError:
                url2html(url, FILENAME_INPUT_HTML)
                html = get_html(FILENAME_INPUT_HTML)

            parser = GeneralHTMLParser2(html,
                                        language=language)
            return parser

        parser = _get_parser()

        parser.get_paragraphs()

        l_data = []

        for paragraph in parser.get_paragraphs():
            if paragraph.is_boilerplate:
                continue

            label_heading = paragraph.is_heading  # bool

            text = paragraph.text

            html_root = lxml.html.fromstring(parser.html)

            # Same cleaning is needed to be able to go back from paragraphs to DOM (make use of the Xpath info).
            justext_preprocessor = justext.core.preprocessor
            html_root = justext_preprocessor(html_root)

            el = get_lxml_el_from_paragraph(html_root,
                                            paragraph)

            tree = el.getroottree()
            tree.getpath(el)

            s_html = lxml.html.tostring(el, encoding="UTF-8").decode("UTF-8")

            def makeParentLine(node, attach_head=False, questionContains=None):
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

            s_html_parents = makeParentLine(el)

            TITLE = "title"
            label_names = [TITLE] if label_heading else []

            d_item = {"label_names": label_names,
                      "text": text,
                      "html_el": s_html,
                      "html_parents": s_html_parents}

            l_data.append(d_item)

        export_jsonl(l_data, "DEBUG_DATA.jsonl")

        def get_euro_item(l_data):
            for item in l_data:
                if "€" in item["text"]:
                    return item

        item_euro = get_euro_item(l_data)

        with self.subTest("encoding text"):
            self.assertTrue(item_euro)
            self.assertIn("€", item_euro["text"])

        with self.subTest("encoding html el"):
            self.assertIn("€", item_euro["html_el"])

        with self.subTest("encoding html parent"):
            self.assertIn("€", item_euro["html_parents"])
