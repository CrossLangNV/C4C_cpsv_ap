import unittest

from relation_extraction.html_parsing.data import data_extraction, data_turnhout
# Code: language
from relation_extraction.html_parsing.utils import export_jsonl


class TestScriptData(unittest.TestCase):
    def test_main(self):
        data_extraction()

        self.assertEqual(0, 1)

    def test_turnhout(self,
                      url="https://www.turnhout.be/inname-openbaar-domein",
                      FILENAME_INPUT_HTML="PARSER_DEBUG_THOUT.html",
                      language="Dutch"):

        l_data = data_turnhout(url=url)

        export_jsonl(l_data, "DEBUG_DATA.jsonl")

        def get_euro_item(l_data):
            for item in l_data:
                if "€" in item.text:
                    return item

        item_euro = get_euro_item(l_data)

        with self.subTest("encoding text"):
            self.assertTrue(item_euro)
            self.assertIn("€", item_euro.text)

        with self.subTest("encoding html el"):
            self.assertIn("€", item_euro.html_el)

        with self.subTest("encoding html parent"):
            self.assertIn("€", item_euro.html_parents)
