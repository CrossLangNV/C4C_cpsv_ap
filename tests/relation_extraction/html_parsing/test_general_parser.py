import unittest

from data.html import get_html, url2html
from relation_extraction.html_parsing.general_parser import GeneralHTMLParser
from relation_extraction.html_parsing.justext_wrapper import GeneralParagraph

FILENAME_INPUT_HTML = "PARSER_DEBUG.html"
FILENAME_OUT = "GEN_PARSER_DEBUG.html"


class TestGeneralHTMLParser(unittest.TestCase):

    def setUp(self) -> None:

        case = 1
        if case == 0:
            url = "https://www.turnhout.be/inname-openbaar-domein"
            FILENAME_INPUT_HTML = "PARSER_DEBUG_THOUT.html"
            language = "Dutch"
        elif case == 1:
            url = "https://www.comune.trento.it/Aree-tematiche/Attivita-edilizia/Interventi-edilizi/Permesso-di-costruire/Permesso-di-costruire"
            FILENAME_INPUT_HTML = "PARSER_DEBUG_TRENTO.html"
            language = "Italian"

        try:
            html = get_html(FILENAME_INPUT_HTML)
        except FileNotFoundError:
            url2html(url, FILENAME_INPUT_HTML)
            html = get_html(FILENAME_INPUT_HTML)

        self.html = html
        self.language = language

    def interesting_webstites(self):
        """
        https://www.comune.trento.it/Aree-tematiche/Attivita-edilizia/Interventi-edilizi/Permesso-di-costruire/Permesso-di-costruire
        https://www.salzgitter.de/rathaus/fachdienste/bauordnung/Bauordnung.php
        https://sede.malaga.eu/es/tramitacion/detalle-del-tramite/?id=4080&tipoVO=5#!tab1
        https://rathaus.dortmund.de/wps/portal/dortmund/home/dortmund/rathaus/domap/services.domap.de/product.services.domap.de/!ut/p/z1/04_Sj9CPykssy0xPLMnMz0vMAfIjo8zijQItjAwN3Q18DEwdzQwcfc2dw3wDwwwsQo31w8EKDHAARwP9KGL041EQhd_4cP0ovFa4muJX4G5oiF-BQZgBAQW-JgQUmMFMwOOPgtzQCINMz0xPR0VFAIMqPLQ!/dz/d5/L2dBISEvZ0FBIS9nQSEh/?p_id=reisepasspasseuropap0
        https://www.trier.de/leben-in-trier/familie-kinder/heiraten-in-trier/
        https://www.moers.de/de/stichwoerter/melderegisterauskuenfte-erweiterte-9498826/
        https://sede.malaga.eu/es/tramitacion/detalle-del-tramite/index.html?id=119&tipoVO=5#.Yjsh13rMJmM

        h2 tagger works:
        https://www.turnhout.be/inname-openbaar-domein (h2 tagger works)
        https://www.turnhout.be/subsidie-mondiale-vorming
        https://stad.gent/nl/over-gent-stadsbestuur/belastingen/online-aangiften/belasting-op-woningen-zonder-inschrijving-het-bevolkingsregister-zogenaamde-tweede-verblijven
        https://www.beerse.be/producten/detail/839/cofinanciering

        Complex:
        https://www.sint-niklaas.be/onze-dienstverlening/persoonlijke-documenten/reizen/internationaal-paspoort
        """


class TestParagraphExtraction(unittest.TestCase):
    def setUp(self) -> None:

        url = "https://www.turnhout.be/inname-openbaar-domein"
        FILENAME_INPUT_HTML = "PARSER_DEBUG_THOUT.html"
        language = "Dutch"

        try:
            html = get_html(FILENAME_INPUT_HTML)
        except FileNotFoundError:
            url2html(url, FILENAME_INPUT_HTML)
            html = get_html(FILENAME_INPUT_HTML)

        self.html = html
        self.language = language

    def test_paragraph_extraction(self):
        parser = GeneralHTMLParser(self.html,
                                   self.language)

        paragraphs = parser.get_paragraphs()

        with self.subTest("Non-empty"):
            self.assertGreaterEqual(len(paragraphs), 1, paragraphs)

        with self.subTest("type"):
            for paragraph in paragraphs:
                self.assertIsInstance(paragraph, GeneralParagraph)

        with self.subTest("Text"):

            for paragraph in paragraphs:
                self.assertTrue(paragraph.text, paragraph)

    def test_section_extraction(self):

        parser = GeneralHTMLParser(self.html,
                                   self.language)

        sections = parser.get_sections()

        for i, section in enumerate(sections):
            with self.subTest(f"Section content: {i}"):
                self.assertTrue(section.title)
                self.assertTrue(section.paragraphs)
