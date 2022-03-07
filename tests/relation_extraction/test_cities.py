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
                          "Wien",
                          "Zagreb"
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


class TestAustrheim(unittest.TestCase):

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
