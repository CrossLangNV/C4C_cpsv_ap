import os
import unittest

from relation_extraction.html_parsing.data import data_turnhout, DataCountries
# Code: language
from relation_extraction.html_parsing.utils import export_jsonl


class TestScriptData(unittest.TestCase):

    def setUp(self) -> None:
        self.FILENAME_YML = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../..", "relation_extraction/html_parsing/urls_data.yml"))

        self.assertTrue(os.path.exists(self.FILENAME_YML), self.FILENAME_YML)

    def test_turnhout(self,
                      url="https://www.turnhout.be/inname-openbaar-domein",
                      ):

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

    def test_data_countries_from_yml_template(self):

        data_countries = DataCountries.load_yaml(self.FILENAME_YML,
                                                 remove_template=False)

        KEY_TEMPLATE = "Country"
        with self.subTest("Countries"):
            self.assertIn(KEY_TEMPLATE, data_countries.country_names())

        country_template = data_countries.get(KEY_TEMPLATE, None)
        with self.subTest("Get country by name"):
            self.assertIsNotNone(country_template)

        municipalities = country_template.municipalities
        with self.subTest("Contains cities"):
            self.assertTrue(municipalities, "Should not be empty")

        with self.subTest("Cities name"):
            for municipality in municipalities:
                self.assertIsInstance(municipality.name, str)

        with self.subTest("Cities language"):
            for municipality in municipalities:
                self.assertTrue(municipality.language, "Should not be empty")
                self.assertIsInstance(municipality.language, str)

        with self.subTest("Cities URL"):
            for municipality in municipalities:
                l_urls = municipality.procedures

                self.assertIsInstance(l_urls, list)

                for url in l_urls:
                    self.assertIsInstance(url, str)

    def test_data_countries_from_yml(self):

        data_countries = DataCountries.load_yaml(self.FILENAME_YML,
                                                 remove_template=True)

        with self.subTest("Removed template data"):
            self.assertNotIn("Country", data_countries.country_names())

        KEY_BELGIUM = "Belgium"
        with self.subTest("Countries"):
            self.assertIn(KEY_BELGIUM, map(lambda d: d.name, data_countries.countries))

        belgium = data_countries.get(KEY_BELGIUM)

        with self.subTest("Get country by name"):
            self.assertIsNotNone(belgium)

        municipalities = belgium.municipalities
        with self.subTest("Contains cities"):
            self.assertTrue(municipalities, "Should not be empty")

        with self.subTest("Cities name"):
            for municipality in municipalities:
                self.assertIsInstance(municipality.name, str)

        with self.subTest("Cities language"):
            for municipality in municipalities:
                self.assertTrue(municipality.language, "Should not be empty")
                self.assertIsInstance(municipality.language, str)

        with self.subTest("Cities URL"):
            for municipality in municipalities:
                l_urls = municipality.procedures

                self.assertIsInstance(l_urls, list)

                for url in l_urls:
                    self.assertIsInstance(url, str)
