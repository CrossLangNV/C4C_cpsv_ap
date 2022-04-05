import os
import unittest

from relation_extraction.html_parsing.data import data_extraction, data_turnhout, DataCountries, DataMunicipality
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

    def test_data_countries_from_yml(self):

        FILENAME_YML = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../..", "relation_extraction/html_parsing/urls_data.yml"))

        with self.subTest("YML exists"):
            self.assertTrue(os.path.exists(FILENAME_YML), FILENAME_YML)

        data_countries = DataCountries.load_yaml(FILENAME_YML)

        KEY_BELGIUM = "Belgium"
        with self.subTest("Countries"):

            self.assertIn(KEY_BELGIUM, data_countries)

        belgium = data_countries.get(KEY_BELGIUM)

        with self.subTest("Cities name"):

            for name in belgium:
                self.assertIsInstance(name, str)

        with self.subTest("Cities data"):

            for name, municipality in belgium.items():
                self.assertIsInstance(municipality, DataMunicipality)

                self.assertEqual(name, municipality.name)

        with self.subTest("Cities URL"):

            for municipality in belgium.values():
                l_urls = municipality.procedures

                self.assertIsInstance(l_urls, list)

                for url in l_urls:
                    self.assertIsInstance(url, str)

        # for

        # yaml.
