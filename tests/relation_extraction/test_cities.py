import re
import unittest

from data.html import url2html


class TestDifferentCities(unittest.TestCase):
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
                          "Zagreb",
                          "Austrheim"
                          ]
        pages = ["https://www.aalter.be/eid", "https://www.aalter.be/verhuizen",  # Dutch
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

        for page in pages:
            filename = re.sub(r'\W+', '_', page) + ".html"
            url2html(page, filename=filename)
