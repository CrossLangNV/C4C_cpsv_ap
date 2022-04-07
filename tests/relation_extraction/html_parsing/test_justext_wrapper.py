import os.path
import unittest
from typing import List

import justext

from relation_extraction.html_parsing.justext_wrapper import BoldJustextWrapper, JustextWrapper
from relation_extraction.html_parsing.utils import _get_language_full_from_code, _tmp_html


class TestJustTextWrapper(unittest.TestCase):
    def test_equivalence(self,
                         url="https://laois.ie/departments/planning/applying-for-planning-permission/",
                         language_code="EN"):
        # Input
        html = _tmp_html(url)
        stoplist = justext.get_stoplist(language=_get_language_full_from_code(language_code))

        # Baseline
        paras_baseline = justext.justext(html, stoplist)

        # To test
        wrapper = JustextWrapper()
        paras = wrapper.justext(html, stoplist)

        with self.subTest("Same number of items"):
            self.assertEqual(len(paras_baseline), len(paras))

        keys = paras_baseline[0].__dict__.keys()

        for key in keys:
            with self.subTest(f"Paragraph attribute equal: {key}"):
                for par_baseline, par in zip(paras_baseline, paras):
                    self.assertEqual(par_baseline.__dict__[key],
                                     par.__dict__.get(key))


class TestBoldJustTextWrapper(unittest.TestCase):
    def test_extraction_bold_headers(self,
                                     url="https://laois.ie/departments/planning/applying-for-planning-permission/",
                                     language_code="EN",
                                     subtitle_text="Decision Process"
                                     ):
        # Input
        html = _tmp_html(url)
        stoplist = justext.get_stoplist(language=_get_language_full_from_code(language_code))

        # Baseline
        paras_baseline = justext.justext(html, stoplist)

        # Output to test
        wrapper = BoldJustextWrapper()
        paras = wrapper.justext(html, stoplist)

        def _get_subtitle(paras: List[justext.core.Paragraph], subtitle_text: str) -> justext.core.Paragraph:

            for par in paras:
                if par.text.lower() == subtitle_text.lower():
                    return par

        par_baseline_sub = _get_subtitle(paras_baseline, subtitle_text)

        with self.subTest("Sanity check. Justext has wrong classification"):
            self.assertFalse(par_baseline_sub.is_heading, "Weird. Should be wrongly not be classified as heading")
            self.assertTrue(par_baseline_sub.is_boilerplate, "Weird. Should be wrongly classified as boilerplate")

        par_sub = _get_subtitle(paras, subtitle_text)

        with self.subTest("Mayor content still the same"):
            self.assertEqual(len(paras_baseline), len(paras))

            for par_baseline, par in zip(paras_baseline, paras):
                self.assertEqual(par_baseline.text,
                                 par.text)

        with self.subTest("Equivalence .is_heading and .heading"):
            for par in paras:
                self.assertEqual(par.is_heading, par.heading, f"par \"{par.text}\"")

        with self.subTest("Heading correct"):
            self.assertTrue(par_sub.is_heading, "Should be detected as heading")

        with self.subTest("Boilerplate correct"):
            self.assertFalse(par_sub.is_boilerplate, "Shouldn't be boilerplate")

    def test_debug_export(self,
                          url="https://laois.ie/departments/planning/applying-for-planning-permission/",
                          language_code="EN",
                          FILENAME_OUT=os.path.join(os.path.dirname(__file__), "GEN_PARSER_DEBUG.html")
                          ):

        # Input
        html = _tmp_html(url)
        stoplist = justext.get_stoplist(language=_get_language_full_from_code(language_code))

        # Output to test
        wrapper = BoldJustextWrapper()

        wrapper._export_debugging(html, stoplist, FILENAME_OUT)
