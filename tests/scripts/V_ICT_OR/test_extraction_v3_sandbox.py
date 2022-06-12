import os.path
import unittest

import pandas as pd

from data.html import get_html, url2html
from relation_extraction.html_parsing.utils import _tmp_filename
from scripts.V_ICT_OR.extraction_v3_sandbox import Berlare_rule_based_extraction, Berlare_rule_based_summary, \
    extract_cpsv_ap_from_html_v3


class TestBerlareRuleBasedSummary(unittest.TestCase):
    def test_cherry_picked(self):
        """
        Get some info to produce a rule based extraction.
        Returns:

        """
        url_adreswijziging = "https://www.berlare.be/adreswijziging-nieuwe-inwoner.html"
        url_recyclage = "https://www.berlare.be/recyclagepark-1.html"
        url_vergunningen = "https://www.berlare.be/omgevingsvergunning-3.html"
        url_geboorte = "https://www.berlare.be/tc111vhzg1477b96.aspx"

        l_url = [url_adreswijziging, url_recyclage, url_vergunningen, url_geboorte]

        l_section_info_all = []
        for url in l_url:
            l_section_info = Berlare_rule_based_summary(url)
            l_section_info_all.extend(l_section_info)

        # TODO pandas.DataFrame

        df = pd.DataFrame([section_info.dict() for section_info in l_section_info_all])

        # Group by label:
        df_grouped = df.groupby('label')
        # Print info for each label:

        for label, df_grouped_label in df_grouped:
            print(label)

            # Print set of each label:

            for key in df_grouped_label.keys():
                value_counts = df_grouped_label[key].value_counts()
                print(f'\t{key}:', value_counts.to_dict())

        # No label:
        print('\nNo label:')
        df_no_label = df[df['label'].isnull()]
        for key in df_no_label.keys():
            value_counts = df_no_label[key].value_counts()
            print(f'\t{key}:', value_counts.to_dict())


class TestBerlareRuleBased(unittest.TestCase):
    def test_call(self):
        """
        Get some info to produce a rule based extraction.
        Returns:

        """
        url_adreswijziging = "https://www.berlare.be/adreswijziging-nieuwe-inwoner.html"
        url_recyclage = "https://www.berlare.be/recyclagepark-1.html"
        url_vergunningen = "https://www.berlare.be/omgevingsvergunning-3.html"
        url_geboorte = "https://www.berlare.be/tc111vhzg1477b96.aspx"

        with self.subTest("adreswijziging"):
            l_sections = Berlare_rule_based_extraction(url_adreswijziging)

            self.assertEqual(len(l_sections), 3)

        with self.subTest("recyclage"):
            l_sections = Berlare_rule_based_extraction(url_recyclage)

            self.assertEqual(len(l_sections), 8)

        with self.subTest("vergunningen"):
            l_sections = Berlare_rule_based_extraction(url_vergunningen)

            self.assertEqual(len(l_sections), 2)

        with self.subTest("geboorte"):
            l_sections = Berlare_rule_based_extraction(url_geboorte)

            self.assertEqual(len(l_sections), 3)


class TestExtractCPSVAP_V3(unittest.TestCase):
    def test_call(self):

        url_adreswijziging = "https://www.berlare.be/adreswijziging-nieuwe-inwoner.html"
        url_recyclage = "https://www.berlare.be/recyclagepark-1.html"
        url_vergunningen = "https://www.berlare.be/omgevingsvergunning-3.html"
        url_geboorte = "https://www.berlare.be/tc111vhzg1477b96.aspx"

        translation = ["NL", "FR", "DE", "EN"]
        context = "https://www.berlare.be"
        country_code = "BE"
        lang = "NL"

        for url in [url_adreswijziging, url_recyclage, url_vergunningen, url_geboorte]:

            filename_html = _tmp_filename(url, ext=".html")

            filename_rdf = _tmp_filename(url, ext=".rdf", dir=os.path.dirname(__file__))
            filename_html_parsing = _tmp_filename(url, prefix="parsing_", ext=".html", dir=os.path.dirname(__file__))

            if not os.path.exists(filename_html):
                url2html(url, filename_html)

            html = get_html(filename_html)

            extract_cpsv_ap_from_html_v3(html,
                                         filename_rdf,
                                         context=context,
                                         country_code=country_code,
                                         lang=lang,
                                         url=url,
                                         extract_concepts=False,
                                         filename_html_parsing=filename_html_parsing,
                                         translation=translation)

            with self.subTest(url):
                self.assertTrue(os.path.exists(filename_rdf))
                self.assertTrue(os.path.exists(filename_html_parsing))
