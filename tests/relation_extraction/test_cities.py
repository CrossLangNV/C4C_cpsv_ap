import re
import unittest

from data.html import get_html, url2html
from relation_extraction.aalter import AalterParser
from relation_extraction.affligem import AffligemParser
from relation_extraction.san_paolo import SanPaoloParser


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

        self.filenames = list(map(lambda page: re.sub(r'\W+', '_', page) + ".html", self.pages))

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
            else:
                # backup
                parser = AffligemParser()

            l = parser.parse_page(html)

            with self.subTest(filename):
                self.assertTrue(l)

                self.assertGreaterEqual(len(l), 2, "Expected at least one other element besides Title.")
