import os.path
import unittest

from data.html import get_html, url2html
from relation_extraction.html_parsing.general_parser import GeneralHTMLParser
from relation_extraction.html_parsing.justext_wrapper import TitleClassificationJustextWrapper
from relation_extraction.html_parsing.utils import _tmp_filename

DIRNAME = os.path.dirname(__file__)


class MyTestCase(unittest.TestCase):
    def setUp(self, download_html=False) -> None:
        url_adreswijziging = "https://www.berlare.be/adreswijziging-nieuwe-inwoner.html"

        filename_html = _tmp_filename('test_tmp', ext='.html',
                                      dir=DIRNAME)

        if download_html or (not os.path.exists(filename_html)):
            url2html(url_adreswijziging, filename_html)

        filename_html_parsing = _tmp_filename('test_parsing_tmp', ext='.html',
                                              dir=DIRNAME)

        self.url = url_adreswijziging
        self.filename_html = filename_html
        self.filename_html_parsing = filename_html_parsing

        self.lang_code = 'NL'
        self.justext_wrapper_class = TitleClassificationJustextWrapper  # or BoldJustextWrapper

    def test_sections(self):
        s_html = get_html(self.filename_html)

        html_parser = GeneralHTMLParser(s_html,
                                        language=self.lang_code,
                                        justext_wrapper_class=self.justext_wrapper_class
                                        )

        html_parser._justext_wrapper._export_debugging(self.filename_html_parsing)

        sections = html_parser.get_sections(include_sub=True
                                            )

        self.assertGreaterEqual(len(sections), 1, 'Expect to extract at least one section.')

        with self.subTest('First section - Title'):
            section0 = sections[0]
            self.assertIn('Adreswijziging nieuwe inwoner', section0.title)

        with self.subTest('Section1: Wat'):
            section1 = sections[1]

            self.assertIn('Wat?', section1.title)

        with self.subTest('Section2: Hoe'):
            section2 = sections[2]

            self.assertIn('Hoe aanvragen?', section2.title)

        with self.subTest('Section1: Wat meebrengen'):
            self.assertGreaterEqual(len(sections), 4, "Expected at least 4 sections (including title)")
            section3 = sections[3]

            self.assertIn('Wat breng je mee??', section3.title)

        with self.subTest('Limited sections'):
            self.assertLessEqual(len(sections), 4, "Expected at most 4 sections (including title)")


if __name__ == '__main__':
    unittest.main()
