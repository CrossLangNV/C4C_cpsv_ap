import copy
import unittest
from typing import List

import justext
import lxml.html

from data.html import get_html, url2html
from relation_extraction.html_parsing.general_parser import GeneralHTMLParser, GeneralHTMLParser2, GeneralParagraph
from relation_extraction.html_parsing.utils import clean_tag_text, dom_write, hashabledict

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

    def test_clean(self):
        parser = GeneralHTMLParser(self.html, self.language)

        foo = parser.clean(FILENAME_OUT)

        self.assertEqual(0, 1)

    def test_sandbox_simple(self, ):

        parser = GeneralHTMLParser(self.html)

        parser._sandbox()

        self.assertEqual(0, 1)

    def test_sandbox_simple_inscriptis(self):

        parser = GeneralHTMLParser(self.html)

        parser._sandbox_inscriptis()

        self.assertEqual(0, 1)

    def test_sandbox(self):
        url = "https://www.comune.trento.it/Aree-tematiche/Attivita-edilizia/Interventi-edilizi/Permesso-di-costruire/Permesso-di-costruire"
        html = url2html(url)

        parser = GeneralHTMLParser(html)

        parser._sandbox()

        self.assertEqual(0, 1)


class TestSandbox(unittest.TestCase):
    def test_headers(self):

        if 0:
            url = "https://www.turnhout.be/inname-openbaar-domein"
            FILENAME_INPUT_HTML = "PARSER_DEBUG_THOUT.html"
            language = "Dutch"
        elif 1:
            url = "https://www.comune.trento.it/Aree-tematiche/Attivita-edilizia/Interventi-edilizi/Permesso-di-costruire/Permesso-di-costruire"
            FILENAME_INPUT_HTML = "PARSER_DEBUG_TRENTO.html"
            language = "Italian"

        try:
            html = get_html(FILENAME_INPUT_HTML)
        except FileNotFoundError:
            url2html(url, FILENAME_INPUT_HTML)
            html = get_html(FILENAME_INPUT_HTML)

        justext_preprocessor = justext.core.preprocessor

        paragraphs = justext.justext(html, justext.get_stoplist(language),
                                     preprocessor=justext_preprocessor)

        # Headers
        for paragraph in paragraphs:
            if paragraph.is_heading:
                print(paragraph.text)

        # Boilerplate
        for paragraph in paragraphs:
            b_good = not paragraph.is_boilerplate
            if b_good:
                print(f"\t\t{paragraph.text}")
            else:
                print("B")

        html_root = lxml.html.fromstring(html)
        # IMPORTANT clean tags. Use same cleaning as justext
        html_root = justext_preprocessor(html_root)

        if 0:
            #
            dom_write(_html_tree, FILENAME_OUT)

        paragraphs_boiler_before_after = copy.deepcopy(paragraphs)
        i_no_boiler = [i for i in range(len(paragraphs_boiler_before_after)) if
                       not paragraphs_boiler_before_after[i].is_boilerplate]
        i_first = i_no_boiler[0]
        i_last = i_no_boiler[-1]
        for i in range(i_first, i_last + 1):
            paragraphs_boiler_before_after[i].class_type = "good"

        # Boilerplate
        for paragraph in paragraphs_boiler_before_after:
            b_good = not paragraph.is_boilerplate
            if b_good:
                print(f"\t\t{paragraph.text}")
            else:
                print("B")

        def get_lxml_el_from_paragraph(html_root: lxml.html.etree._Element,
                                       paragraph: justext.core.Paragraph
                                       ):

            l_e = html_root.xpath(paragraph.xpath)
            if len(l_e) != 1:
                raise LookupError(f"Expected exactly one element: {l_e}")

            return l_e[0]

        STYLE_HEADER = "text-decoration: underline;text-decoration-color: red;"

        html_root_cleaned = copy.deepcopy(html_root)
        # roottree_cleaned = copy.deepcopy(roottree)
        l_delete = []
        for paragraph in paragraphs_boiler_before_after:
            if paragraph.is_boilerplate:
                # Remove from html

                e = get_lxml_el_from_paragraph(html_root_cleaned,
                                               paragraph)

                l_delete.append(e)


            else:
                e = get_lxml_el_from_paragraph(html_root_cleaned,
                                               paragraph)

                if paragraph.heading:
                    e.attrib["style"] = STYLE_HEADER

        for e in l_delete:
            # ! do afterwards, otherwise xpath is broken.
            try:
                e.getparent().remove(e)
            except AttributeError:
                # Parent is already gone.
                pass

        dom_write(html_root_cleaned,
                  FILENAME_OUT)

        def _boilerplate_print(paragraphs: List[justext.paragraph.Paragraph],
                               f_boiler=lambda par: print("B"),
                               f_non_boiler=lambda par: print(f"\t\t{par.text}")):
            """
            Visualation/debug tool to check which paragraphs are Boilerplate
            Returns:

            """

            for paragraph in paragraphs:
                if paragraph.is_boilerplate:
                    f_boiler(paragraph)
                else:
                    f_non_boiler(paragraph)

        # Post cleaing
        _boilerplate_print(justext.justext(lxml.html.etree.tostring(html_root_cleaned).decode("UTF-8"),
                                           justext.get_stoplist(language),
                                           preprocessor=justext_preprocessor))

        # Go over tag classes (name + attrib?), find number of OK and not_ok.

        # Debug special header
        for paragraph in paragraphs:
            if "richiedere" in paragraph.text:
                el = get_lxml_el_from_paragraph(html_root,
                                                paragraph)

                _l = tree.xpath('/html/body/div[1]/div[3]/div[1]/div[3]/div[2]/div/div')
                for _e in _l:
                    print(lxml.etree.tostring(_e))
                [lxml.etree.tostring(a) for a in tree.xpath('/html/body/div[1]/div[3]/div[1]/div[3]/div[2]/div/div')]

                list(el.iterdescendants())

                # Check if full bold
                if l_strong_children := el.xpath(".//strong"):
                    strong = l_strong_children[0]

                    if clean_tag_text(strong) == clean_tag_text(el):
                        # All text is "strong":

                        # (!) Do not use paragraph.is_heading
                        paragraph.heading = True

                    # justext.utils.normalize_whitespace()
                    #
                    # text = "".join(self.text_nodes)
                    # return justext.utils.normalize_whitespace(text.strip())
                    #
                    # ''.join(strong.itertext()).splitlines()
                    #
                    # ''.join(el.itertext())
                    #
                    # "\n".join(lxml.etree.XPath("//text()")(strong))

                # # (!) Do not use paragraph.is_heading
                # paragraph.heading =

        d_count = {}

        for paragraph in paragraphs:
            el = get_lxml_el_from_paragraph(html_root,
                                            paragraph)

            tree = html_root.getroottree()
            xp = tree.getpath(el)
            tree.xpath()

            el.tag
            el.attrib.items()
            el.get("class")

            k = hashabledict({"tag": el.tag,
                              "attrib": hashabledict(el.attrib)
                              })

            d_info = d_count.setdefault(k, {"n_boiler": 0,
                                            "n_not_boiler": 0})

            # Number of Non-boiler ; Number of boilerplate text.
            if paragraph.is_boilerplate:
                d_info["n_boiler"] += 1

            else:
                d_info["n_not_boiler"] += 1

        # Full bold/strong paragraphs: convert to header
        for paragraph in paragraphs:
            paragraph

        print(d_count)

        for k, v in d_count.items():
            if v["n_not_boiler"] >= 1:
                print(k, v)

        return


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
        parser = GeneralHTMLParser2(self.html,
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

        parser = GeneralHTMLParser2(self.html,
                                    self.language)

        sections = parser.get_sections()

        for i, section in enumerate(sections):
            with self.subTest(f"Section content: {i}"):
                self.assertTrue(section.title)
                self.assertTrue(section.paragraphs)
