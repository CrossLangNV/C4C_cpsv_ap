import unittest

from data.html import url2html
from relation_extraction.html_parsing.parsers import HeaderHTMLParser


class TestHeaderHTMLParser(unittest.TestCase):
    def test_get_sections(self):
        url = "https://www.turnhout.be/inname-openbaar-domein"
        html = url2html(url)

        parser = HeaderHTMLParser(html)

        sections = parser.get_sections()

        # Introduction
        section_intro = sections[0]

        with self.subTest("intro - title"):
            self.assertEqual("Inname openbaar domein", section_intro.title)

        with self.subTest("#TODO Improve chunking: intro - text"):
            self.assertTrue(section_intro.paragraphs_text(),
                            "Should have found introduction text.")
            self.assertIn("Toch is het soms nodig dat je een stukje van dit openbaar domein inneemt.",
                          section_intro.paragraphs_text())

        with self.subTest("subsection"):
            sub_title = "Betalen"

            section_titles = [section.title for section in sections]
            self.assertIn(sub_title, section_titles)

            sub_section = [section for section in sections if section.title == sub_title][0]

        with self.subTest("subsection - text"):
            # Prev sub test has to succeed in order for this to work

            self.assertIn("LET OP: de parkeerverboden worden pas geplaatst wanneer de betaling in orde is.",
                          sub_section.paragraphs_text())
