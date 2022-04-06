import os
import unittest
from typing import Dict, List

from relation_extraction.html_parsing.data import data_generic, data_turnhout, DataCountries
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

    def test_data_summary(self):

        data_countries = DataCountries.load_yaml(self.FILENAME_YML,
                                                 remove_template=True)

        with self.subTest("# of countries"):
            country_names = data_countries.country_names()
            self.assertGreaterEqual(len(country_names), 1)

            print(f"Countries (#={len(country_names)}): {', '.join(country_names)}")

        for country in data_countries.countries:
            name_country = country.name
            with self.subTest(f"Country: {name_country}"):
                muni_names = country.municipalities_names()
                self.assertGreaterEqual(len(muni_names), 1)

                print(f"{name_country} (#={len(muni_names)}): {', '.join(muni_names)}")

        # Languages
        d_lang: Dict[str, List[str]] = {}
        for country in data_countries.countries:
            for muni in country.municipalities:
                d_lang.setdefault(muni.language, []).append(muni.name)

        for lang, munis in d_lang.items():
            with self.subTest(f"Language: {lang}"):
                print(f"{lang} (#={len(munis)}): {', '.join(munis)}")


class TestTrainingData(unittest.TestCase):
    def setUp(self) -> None:
        FILENAME_YML = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../..", "relation_extraction/html_parsing/urls_data.yml"))

        self.assertTrue(os.path.exists(FILENAME_YML), FILENAME_YML)

        self.data_countries = DataCountries.load_yaml(FILENAME_YML,
                                                      remove_template=True)

    def test_get_all_urls(self):

        l_url = []

        for country in self.data_countries.countries:
            for muni in country.municipalities:
                for url in muni.procedures:
                    l_url.append(url)

        with self.subTest("Multiple URLs"):
            self.assertGreaterEqual(len(l_url), 1)

    def test_generate_training_data(self):

        for country in self.data_countries.countries:
            for muni in country.municipalities:
                language_code = muni.language
                for url in muni.procedures:
                    foo = data_generic(url,
                                       language_code=language_code)
                    foo
