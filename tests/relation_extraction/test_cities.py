import os.path
import re
import unittest

from data.html import get_html, url2html
from relation_extraction.aalter import AalterParser
from relation_extraction.affligem import AffligemParser
from relation_extraction.austrheim import AustrheimParser
from relation_extraction.methods import RelationExtractor
from relation_extraction.nova_gorica import NovaGoricaParser
from relation_extraction.san_paolo import SanPaoloParser
from relation_extraction.wien import WienParser

DIR_EXAMPLE_FILES = os.path.join(os.path.dirname(__file__), "EXAMPLE_FILES")

url2filename = lambda page: os.path.join(DIR_EXAMPLE_FILES, re.sub(r'\W+', '_', page) + ".html")


class TestDifferentCities(unittest.TestCase):
    def setUp(self) -> None:
        # 1. Countries
        countries = ["Belgium",
                     "Italy",
                     "Slovenia",
                     "Germany",
                     "Croatia",
                     "Norway"
                     ]
        # 2. Municipality, !find list with municipalities.
        municipalities = ["Aalter",  # <- Belgium, Dutch
                          "San Paolo",  # <- Italy, Italian
                          "Nova Gorica",  # <- Slovenia, Slovenian
                          "Wien",  # <- Austria, German
                          "Zagreb",  # <- Croatia, Croatian
                          "Austrheim",  # <- Norway, Norwegian
                          ]
        self.pages = ["https://www.aalter.be/eid", "https://www.aalter.be/verhuizen",  # Dutch
                      "https://www.comune.sanpaolo.bs.it/procedure%3As_italia%3Atrasferimento.residenza.estero%3Bdichiarazione?source=1104",
                      # San Paolo, Italian. https://www.comune.sanpaolo.bs.it/activity/56 Could be useful or https://www.comune.sanpaolo.bs.it/activity/2 (Home: Life events.) OR all: https://www.comune.sanpaolo.bs.it/activity
                      "https://www.nova-gorica.si/za-obcane/postopki-in-obrazci/2011101410574355/",
                      # Legal documents + costs?
                      "https://www.wien.gv.at/amtshelfer/verkehr/fahrzeuge/aenderungen/einzelgenehmigung.html",
                      # Whole of Wien is quite ok.
                      "https://www.zagreb.hr/novcana-pomoc-za-opremu-novorodjenog-djeteta/5723",  # Not great.
                      "https://austrheim.kommune.no/innhald/helse-sosial-og-omsorg/pleie-og-omsorg/omsorgsbustader/",
                      # Acceptable site.
                      ]

        self.filenames = list(map(url2filename, self.pages))

    def test_different_cities_list(self):
        """
        For different cities, we want some examples of admnistrative procedures
        1. Get list of countries
        2. For each country, find a municipality that has a good structure for administrative procedures,
        similar to yourEurope pages.
        3. For each municipality have at least one webpage with an administrative procedure.
        3.1 Make sure all 8 languages are covered.
        4. Extract HTML (and language)
        Returns:

        """

        for page, filename in zip(self.pages, self.filenames):
            # filename = re.sub(r'\W+', '_', page) + ".html"
            url2html(page, filename=filename)

    def test_chunking(self):

        for filename in self.filenames:
            html = get_html(filename)

            if "aalter" in filename.lower():
                parser = AalterParser()
            elif "paolo" in filename.lower():
                parser = SanPaoloParser()
            elif "gorica" in filename.lower():
                parser = NovaGoricaParser()
            elif "austrheim" in filename.lower():
                pass  # TODO next
                parser = AustrheimParser()
            else:
                # backup
                parser = AffligemParser()

            l = parser.parse_page(html)

            with self.subTest(filename):
                self.assertTrue(l)

                self.assertGreaterEqual(len(l), 2, "Expected at least one other element besides Title.")

    def test_austrheim(self):

        def get_austrheim():
            for filename in self.filenames:

                if "austrheim" in filename.lower():
                    return filename

        filename = get_austrheim()
        html = get_html(filename)

        parser = AustrheimParser()

        l = parser.parse_page(html)

        self.assertTrue(l)


class TestAalter(unittest.TestCase):
    """
    Belgium, Dutch
    """

    def setUp(self) -> None:
        self.url1 = "https://www.aalter.be/eid"
        self.url2 = "https://www.aalter.be/verhuizen"

        self.filename1 = url2filename(self.url1)
        self.filename2 = url2filename(self.url2)

        self.html1 = get_html(self.filename1)
        self.html2 = get_html(self.filename2)

        self.parser = AalterParser()

        self.context = "https://www.aalter.be/"

    def test_chunker(self):
        l1 = self.parser.parse_page(self.html1)
        l2 = self.parser.parse_page(self.html2)

        self.assertTrue(l1)

        self.assertTrue(l2)

        with self.subTest("Other headers"):
            self.assertGreaterEqual(len(l1), 2, "Expected at least one other element besides Title.")
            self.assertGreaterEqual(len(l2), 2, "Expected at least one other element besides Title.")

    def test_chunkig_headers_sub(self):
        """
        a h1 headers should contain all h2, h3... headers within.
        Returns:

        """

        # Get h2 with h3 children

        def _get_header_with_sub_headers():

            for title, paragraph in self.parser._paragraph_generator(self.html1):
                if "hoe aanvragen" in title.lower():
                    return title, paragraph

        title, paragraph = _get_header_with_sub_headers()

        with self.subTest("subtitles"):
            self.assertIn("Afhalen".lower(), paragraph.lower())

        with self.subTest("subparagrpaphs"):
            self.assertIn("In dringende gevallen kan je een spoedprocedure aanvragen".lower(),
                          paragraph.lower())

    def test_extract_relations1(self):
        # E ID
        d_relations1 = self.parser.extract_relations(self.html1, url=self.url1)

        crit_req = d_relations1.criterionRequirement
        s_in = "De pasfoto die je meebrengt mag maximaal 6 maanden oud zijn en " \
               "moet voldoen aan de normen van de International Civil Aviation Organization (pdf)."

        with self.subTest("criterion requirement"):
            self.assertTrue(crit_req)

            self.assertIn(s_in.replace(" ", ""), crit_req.replace(" ", ""))

        with self.subTest("! TODO correct chunking"):
            self.assertIn(s_in, crit_req)

        rule1 = d_relations1.rule
        s_in = "Belgen ouder dan 12 jaar die in het buitenland wonen kunnen een eID krijgen bij de Belgische consulaire beroepspost waar ze zijn ingeschreven. De levertermijn is wel langer."
        with self.subTest("Rule"):
            self.assertTrue(rule1)

            self.assertIn(s_in, rule1)

        cost_eid = d_relations1.cost
        with self.subTest("cost"):
            self.assertTrue(cost_eid)

            self.assertIn("12 tot 18 jaar is de identiteitskaart 6 jaar geldig", cost_eid)

        with self.subTest("! TODO Chunking tables"):
            self.assertIn("Spoed: levering gemeentehuis (1 dag)", cost_eid)

    def test_extract_relations2(self):
        # Change in address
        d_relations2 = self.parser.extract_relations(self.html2, url=self.url2)

        with self.subTest("rule2"):
            rule2 = d_relations2.rule

            self.assertTrue(rule2)

            s_in = "Na deze controle word je ingeschreven op het nieuwe adres en word je uitgenodigd om jouw identiteitskaart op het gemeentehuis te laten aanpassen."
            self.assertIn(s_in, rule2)

        with self.subTest("evidence"):
            evidence = d_relations2.evidence

            self.assertTrue(evidence)

            self.assertIn("Pincode om de chip te updaten.", evidence)

    def test_RelationExtractor(self,
                               debug=False):
        relation_extractor = RelationExtractor(self.html1,
                                               context=self.context,
                                               country_code="BE")

        ps = relation_extractor.extract_all(extract_concepts=True)

        if debug:
            print(relation_extractor.export())

        self.assertTrue(ps)


class TestAustrheim(unittest.TestCase):
    """
    Norway, Norwegian
    """

    def setUp(self) -> None:
        self.url = "https://austrheim.kommune.no/innhald/helse-sosial-og-omsorg/pleie-og-omsorg/omsorgsbustader/"
        self.filename = url2filename(self.url)
        self.html = get_html(self.filename)

        self.parser = AustrheimParser()

        self.context = "https://austrheim.kommune.no/"

    def test_chunker(self):
        l = self.parser.parse_page(self.html)

        self.assertTrue(l)

        with self.subTest("Other headers"):
            self.assertGreaterEqual(len(l), 2, "Expected at least one other element besides Title.")

    def test_extract_relations(self):
        d_relations = self.parser.extract_relations(self.html, url=self.url)

        with self.subTest("criterionRequirement"):
            crit_requirement = d_relations.criterionRequirement

            self.assertTrue(crit_requirement)

            self.assertIn("ha eit fysisk eller psykisk funksjonstap", crit_requirement)

            # Check encoding!
            self.assertIn("du må ha legeuttale", crit_requirement)

        with self.subTest("rule"):
            rule = d_relations.rule

            self.assertTrue(rule)

        with self.subTest("cost"):
            cost = d_relations.cost

            self.assertTrue(cost)

    def test_RelationExtractor(self,
                               debug=False):
        relation_extractor = RelationExtractor(self.html,
                                               context=self.context,
                                               country_code="NO")

        ps = relation_extractor.extract_all(extract_concepts=True)

        if debug:
            print(relation_extractor.export())

        self.assertTrue(ps)


class TestNovaGorica(unittest.TestCase):
    """
    Slovenia, Slovenian
    """

    def setUp(self, write=False) -> None:
        self.url = "https://www.nova-gorica.si/za-obcane/postopki-in-obrazci/2011101410574355/"
        self.url2 = "https://www.nova-gorica.si/za-obcane/postopki-in-obrazci/2011102511410147/"
        self.filename = url2filename(self.url)
        self.filename2 = url2filename(self.url2)

        if write:
            for page, filename in zip([self.url, self.url2], [self.filename, self.filename2]):
                url2html(page, filename=filename)

        self.html = get_html(self.filename)
        self.html2 = get_html(self.filename2)

        self.parser = NovaGoricaParser()
        self.context = "https://www.nova-gorica.si/"

    def test_chunker(self):
        l = self.parser.parse_page(self.html)

        self.assertTrue(l)

        with self.subTest("Other headers"):
            self.assertGreaterEqual(len(l), 2, "Expected at least one other element besides Title.")

        titles = [title for title, _ in self.parser._paragraph_generator(self.html)]
        paragraphs = [paragraph for _, paragraph in self.parser._paragraph_generator(self.html)]

        with self.subTest("Forms"):
            self.assertIn("Obrazci:", titles)

        with self.subTest("Contact"):
            title = "Kontakt:"
            self.assertIn(title, titles)

            paragraph = paragraphs[titles.index(title)]
            self.assertIn("telefon: 05/335-0-352", paragraph)

        with self.subTest("Procedure"):
            self.assertIn("Opis postopka:", titles)

        with self.subTest("Legal basis"):
            self.assertIn("Pravna podlaga:", titles)

        with self.subTest("Cost"):
            title = "Taksa:"
            self.assertIn("Taksa:", titles)

            paragraph = paragraphs[titles.index(title)]
            self.assertIn("Takse ni.", paragraph)

        with self.subTest("Specific bug #1"):
            # "Vloga za enkratno denarno pomoč ob rojstvu otroka"
            s_in = "Vloga za enkratno denarno pomo"
            for title in titles:
                self.assertNotIn(s_in, title)

    def test_extract_relations1(self):
        # Birth
        d_relations = self.parser.extract_relations(self.html, url=self.url)

        crit_req = d_relations.criterionRequirement
        with self.subTest("criterion requirement"):
            self.assertTrue(crit_req)

            s_in = "Vloga za enkratno denarno pomoč ob rojstvu otroka"
            self.assertEqual(s_in, crit_req)

        rule_birth = d_relations.rule
        s_in = "Višina enkratne občinske denarne pomoči ob rojstvu otroka znaša 500,00 EUR"
        with self.subTest("Rule"):
            self.assertTrue(rule_birth)

            self.assertIn(s_in, rule_birth)

        cost_birth = d_relations.cost
        with self.subTest("cost"):
            self.assertTrue(cost_birth)

            self.assertEqual("Takse ni.",
                             cost_birth)

    def test_extract_relations2(self):
        # Change in address
        d_relations = self.parser.extract_relations(self.html2, url=self.url2)

        crit_req = d_relations.criterionRequirement
        with self.subTest("criterion requirement"):
            self.assertTrue(crit_req)

            s_in = "a prenehanja opravljanja dejavnosti avto-taksi prevozov"
            self.assertIn(s_in, crit_req)

        rule = d_relations.rule
        with self.subTest("Rule"):
            self.assertTrue(rule)

            # different tags act weird, so separate test
            s_in = "potrebna sprememba dovoljenja"
            self.assertIn(s_in, rule)

            s_in = " ko se spremeni katerikoli pogoj in s tem priloga k vlogi podani ob pridobitvi dovoljenja; vlogo za spremembo je potrebno podati v"
            self.assertIn(s_in, rule)

        evidence = d_relations.evidence
        with self.subTest("Evidence"):
            self.assertTrue(evidence)

            s_in = "taksi (glej postopek Prijava obveznosti plačila občinske takse - Pri"

            self.assertIn(s_in, evidence)

        cost = d_relations.cost
        with self.subTest("cost"):
            self.assertTrue(cost)

            self.assertIn("22,60 EUR.",
                          cost)

    def test_RelationExtractor(self,
                               debug=False):
        relation_extractor = RelationExtractor(self.html,
                                               context=self.context,
                                               country_code="SL")

        ps = relation_extractor.extract_all(extract_concepts=True)

        if debug:
            print(relation_extractor.export())

        self.assertTrue(ps)


class TestSanPaolo(unittest.TestCase):
    """
    Italy, Italian
    """

    def setUp(self, write=False) -> None:
        self.url = "https://www.comune.sanpaolo.bs.it/procedure%3As_italia%3Atrasferimento.residenza.estero%3Bdichiarazione?source=1104"
        self.filename = url2filename(self.url)
        self.html = get_html(self.filename)

        self.parser = SanPaoloParser()
        self.context = "https://www.comune.sanpaolo.bs.it/"

    def test_chunker(self):
        l = self.parser.parse_page(self.html)

        self.assertTrue(l)

        with self.subTest("Other headers"):
            self.assertGreaterEqual(len(l), 2, "Expected at least one other element besides Title.")

        titles = [title for title, _ in self.parser._paragraph_generator(self.html)]
        paragraphs = [paragraph for _, paragraph in self.parser._paragraph_generator(self.html)]

        with self.subTest("Cost"):
            title = "Pagamenti"
            self.assertIn(title, titles)

            paragraph = paragraphs[titles.index(title)]
            self.assertIn("La presentazione della pratica non prevede alcun pagamento", paragraph)

        with self.subTest("Evidence"):
            title = "Moduli da compilare e documenti da allegare"
            self.assertIn(title, titles, "TODO chunker did not include evidence block.")

    def test_extract_relations(self):
        d_relations = self.parser.extract_relations(self.html, url=self.url)

        evidence = d_relations.evidence
        with self.subTest("evidence"):
            self.assertTrue(evidence)

            s_in = "Dichiarazione di trasferimento di residenza all'estero	"
            self.assertIn(s_in,
                          evidence)

            s_in = "Copia del documento d'identità di tutti i soggetti"
            self.assertIn(s_in,
                          evidence)

        cost = d_relations.cost
        with self.subTest("cost"):
            self.assertTrue(cost)

            self.assertIn("La presentazione della pratica non prevede alcun pagamento",
                          cost)

    def test_RelationExtractor(self,
                               debug=False):
        relation_extractor = RelationExtractor(self.html,
                                               context=self.context,
                                               country_code="IT")

        ps = relation_extractor.extract_all(extract_concepts=True)

        if debug:
            print(relation_extractor.export())

        self.assertTrue(ps)


class TestWien(unittest.TestCase):
    """
    Austria, German
    """

    def setUp(self, write=False) -> None:
        self.url = "https://www.wien.gv.at/amtshelfer/verkehr/fahrzeuge/aenderungen/einzelgenehmigung.html"
        self.filename = url2filename(self.url)
        self.html = get_html(self.filename)

        self.parser = WienParser()  # Or AalterParser()
        self.context = "https://www.wien.gv.at/"

    def test_chunker(self):
        l = self.parser.parse_page(self.html)

        self.assertTrue(l)

        with self.subTest("Other headers"):
            self.assertGreaterEqual(len(l), 2, "Expected at least one other element besides Title.")

        titles = [title for title, _ in self.parser._paragraph_generator(self.html)]
        paragraphs = [paragraph for _, paragraph in self.parser._paragraph_generator(self.html)]

        with self.subTest("Additional info"):
            title = "Zusätzliche Informationen"
            self.assertIn(title, titles)

            paragraph = paragraphs[titles.index(title)]
            self.assertIn(
                "Dateneingabe in die Genehmigungsdatenbank für vom Ausland importierte Fahrzeuge mit EU",
                paragraph)

        with self.subTest("Requirements"):
            title = "Voraussetzungen"
            self.assertIn(title, titles)

    def test_extract_relations(self):
        d_relations = self.parser.extract_relations(self.html, url=self.url)

        criterionRequirement = d_relations.criterionRequirement
        with self.subTest("criterion requirement"):
            self.assertTrue(criterionRequirement)

            s_in = "Das Fahrzeug muss den Baujahrsvorschriften des österreichischen Kraftfahrrecht bzw. den EU"
            self.assertIn(s_in,
                          criterionRequirement)

        rule = d_relations.rule
        with self.subTest("rule"):
            self.assertTrue(rule)

            s_in = "technische Verkehrsangelegenheiten ("
            self.assertIn(s_in,
                          rule)

            s_in = "MA 46) gesondert genehmigt werden."
            self.assertIn(s_in,
                          rule)

        evidence = d_relations.evidence
        with self.subTest("evidence"):
            self.assertTrue(evidence)

            s_in = "Vollmacht, falls die FahrzeugbesitzerInnen nicht persönlich kommen"
            self.assertIn(s_in,
                          evidence)

        cost = d_relations.cost
        with self.subTest("cost"):
            self.assertTrue(cost)

            s_in = "Zirka 60 bis 160 Euro"
            self.assertIn(s_in,
                          cost)

    def test_RelationExtractor(self,
                               debug=False):
        relation_extractor = RelationExtractor(self.html,
                                               context=self.context,
                                               country_code="AT")

        ps = relation_extractor.extract_all(extract_concepts=True)

        if debug:
            print(relation_extractor.export())

        self.assertTrue(ps)


class TestZagreb(unittest.TestCase):
    """
    Croatia, Croatian
    """

    def test_foo(self):
        self.assertEqual(0, 1)
