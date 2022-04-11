import math
import os
import unittest
from collections import Counter
from typing import Dict, List

import justext

from relation_extraction.html_parsing.data import DataCountries, DataGeneric, ParserModel
from relation_extraction.html_parsing.justext_wrapper import BoldJustextWrapper, JustextWrapper
from relation_extraction.html_parsing.utils import _get_language_full_from_code, _tmp_html, export_jsonl


class TestScriptData(unittest.TestCase):

    def setUp(self) -> None:
        self.FILENAME_YML = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "../../..", "relation_extraction/html_parsing/urls_data.yml"))

        self.assertTrue(os.path.exists(self.FILENAME_YML), self.FILENAME_YML)

    def test_turnhout(self,
                      url="https://www.turnhout.be/inname-openbaar-domein",
                      language_code="NL"
                      ):

        l_data = DataGeneric().extract_data(url=url,
                                            language_code=language_code
                                            )

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

    def test_bold(self,
                  url="https://laois.ie/departments/planning/applying-for-planning-permission/",
                  language_code="EN"):

        parser_config = ParserModel(titles=ParserModel.titlesChoices.html_bold)

        html = _tmp_html(url)
        stoplist = justext.get_stoplist(
            _get_language_full_from_code(language_code))

        paragraphs = JustextWrapper().justext(html,
                                              stoplist=stoplist)

        paragraphs_bold = BoldJustextWrapper().justext(html,
                                                       stoplist=stoplist)

        def count_(paragraphs):
            counter = Counter([paragraph.is_heading for paragraph in paragraphs])
            print(counter)

            return counter

        print(f"Regular justext: {count_(paragraphs)}")

        print(f"Bold justext: {count_(paragraphs_bold)}")

        # without proper parser_config
        data_gen_bad = DataGeneric(parser_config=None)
        l_data_bad = data_gen_bad.extract_data(url=url,
                                               language_code=language_code
                                               )

        data_gen = DataGeneric(parser_config=parser_config)
        l_data = data_gen.extract_data(url=url,
                                       language_code=language_code
                                       )
        export_jsonl(l_data, "DEBUG_DATA.jsonl")

        self.assertLess(len(l_data_bad), len(l_data))

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
            print(f"# URLs = {len(l_url)}")

    def test_generate_all_data(self,
                               use_parser_config=True):

        # Distribution:
        distribution_total = {}  # "label name": Number of elements

        for country in self.data_countries.countries:
            for muni in country.municipalities:
                language_code = muni.language

                if use_parser_config:
                    parser_config = muni.parser
                else:
                    parser_config = None

                data_generic = DataGeneric(parser_config)

                with self.subTest(f"{muni.name}"):
                    for url in muni.procedures:

                        foo = data_generic.extract_data(url,
                                                        language_code=language_code)

                        # Distribution:
                        d_label_names = {}
                        for item in foo:
                            k = frozenset(item.label_names)
                            d_label_names.setdefault(k, 0)
                            d_label_names[k] += 1

                            distribution_total.setdefault(k, 0)
                            distribution_total[k] += 1

                        print(f"Distr: {d_label_names}. {url}")

        print(f"Distribution total: {distribution_total}")

    def test_expected_more_results_debug(self,
                                         muni_name="Trier"):

        # Get Muni
        def get_muni():
            for country in self.data_countries.countries:
                for muni in country.municipalities:
                    if muni.name == muni_name:
                        return muni

        muni = get_muni()

        language_code = muni.language

        data_generic = DataGeneric(muni.parser)

        self.assertIsInstance(data_generic.justext_wrapper, BoldJustextWrapper)

        for url in muni.procedures:

            foo = data_generic.extract_data(url,
                                            language_code=language_code)

            # Distribution:
            d_label_names = {}
            for item in foo:
                k = frozenset(item.label_names)
                d_label_names.setdefault(k, 0)
                d_label_names[k] += 1

            print(f"Distr: {d_label_names}. {url}")

    def test_generate_training_validation_data(self):

        def split_muni_training_valid(split_train=.8):

            l_train = []
            l_valid = []

            for country in self.data_countries.countries:

                munis = country.municipalities
                n_muni = len(munis)
                thresh = math.floor(split_train * n_muni)

                for i, muni in enumerate(munis):

                    if i + 1 <= thresh:
                        l_train.append(muni)
                    else:
                        l_valid.append(muni)

            return l_train, l_valid

        l_train, l_valid = split_muni_training_valid()

        def get_all_data(l_munis):
            l_data_all = []
            for muni in l_munis:

                data_generic = DataGeneric(muni.parser)

                for url in muni.procedures:
                    l_data_i = data_generic.extract_data(url,
                                                         language_code=muni.language)

                    l_data_all.extend(l_data_i)

            return l_data_all

        l_data_train = get_all_data(l_train)
        l_data_valid = get_all_data(l_valid)

        DATA_SOURCE = os.path.join(os.path.dirname(__file__), "../../..")
        DATA_FOLDER = os.path.abspath(os.path.join(DATA_SOURCE, "data/relation_extraction/title_classifier"))

        export_jsonl(l_data_train, os.path.join(DATA_FOLDER, "train.jsonl"))
        export_jsonl(l_data_valid, os.path.join(DATA_FOLDER, "validation.jsonl"))

        return
