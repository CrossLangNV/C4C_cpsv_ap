import unittest

from c4c_cpsv_ap.models import LifeEvent
from data.html import FILENAME_HTML_AFFLIGEM, FILENAME_HTML_AFFLIGEM_SITEMAP, get_html, url2html, URL_HTML_AFFLIGEM
from relation_extraction.affligem import AffligemParser


class TestAffligem(unittest.TestCase):
    def setUp(self) -> None:
        self.parser = AffligemParser()

    def test_url2html(self):

        html = url2html(URL_HTML_AFFLIGEM, FILENAME_HTML_AFFLIGEM)

        s_in = "Het wettigen of legaliseren van een handtekening betekent dat een daartoe bevoegde overheid de echtheid van een handtekening schriftelijk bevestigt. Deze wettiging heeft echter niet tot doel de echtheid van de inhoud van het document te bewijzen."

        self.assertIn(s_in, html)

    def test_extract(self):
        with open(FILENAME_HTML_AFFLIGEM, "r") as fp:
            html = fp.read()

        d_relations = self.parser.extract_relations(html, url=URL_HTML_AFFLIGEM)

        with self.subTest("criterionRequirement"):
            s_true = "• De persoon van wie de handtekening gewettigd moet worden, moet zijn woonplaats\n" \
                     "hebben in een Belgische gemeente.\n" \
                     "• Het document mag niet bestemd zijn voor immorele, bedrieglijke of\n" \
                     "strafbare oogmerken.\n" \
                     "• De formaliteit moet nuttig of nodig zijn. Het mag bijgevolg niet gaan om een louter\n" \
                     "private akte (een eigenhandig geschreven testament bijvoorbeeld)."
            s = d_relations.criterionRequirement
            self.assert_multiline(s_true, s)

        with self.subTest("rule"):
            s_true = "De burgemeester van de gemeente of zijn gemachtigde gaat na of de te legaliseren handtekening overeenstemt met die van de persoon van wie de identiteit wordt vastgesteld. Een handtekening op een wit vel papier kan nooit gelegaliseerd worden."
            s = d_relations.rule
            self.assert_multiline(s_true, s)
        with self.subTest("evidence"):
            s_true = "• het document waarop de handtekening moet gewettigd worden\n" \
                     "• je identiteitskaart\n" \
                     "Laat je de handtekening van iemand anders wettigen, dan moet je de identiteitskaart van deze persoon en een door hem of haar ondertekende volmacht meebrengen."
            s = d_relations.evidence
            self.assert_multiline(s_true, s)
        with self.subTest("cost"):
            s_true = "Het wettigen van een handtekening is gratis."
            s = d_relations.cost
            self.assert_multiline(s_true, s)

    def test_attest_gezinssamenstelling(self):
        url = "https://www.affligem.be/Affligem/Nederlands/Leven/identiteitsbewijzen,-rijbewijzen-en-afschriften/afschriften-uittreksels-getuigschriften/aanvraag-samenstelling-van-het-gezin/page.aspx/825"
        html = url2html(url)

        d_relations = self.parser.extract_relations(html, url=url)

        with self.subTest("criterionRequirement"):
            s_true = "De volgende partijen kunnen het attest met betrekking tot jou aanvragen:\n" \
                     "•  jij zelf (enkel voor je eigen gezin)\n" \
                     "•  je wettelijke vertegenwoordiger (bv. ouder of voogd)\n" \
                     "•  bijzondere gemachtigden zoals een notaris of advocaat\n" \
                     "•  derden (bv. publieke of private instellingen) als de afgifte ervan voorgeschreven is door of krachtens de wet\n" \
                     "•  een derde persoon op voorwaarde dat die in het bezit is van een volmacht en de identiteitskaart (of kopie ervan) van de\n" \
                     "aanvrager."

            s = d_relations.criterionRequirement

            self.assert_multiline(s_true, s)

    def test_extract_event(self):
        url = "https://www.affligem.be/Affligem/Nederlands/Leven/bouwen-en-wonen/adresverandering/page.aspx/60"
        html = url2html(url)
        events = list(self.parser.extract_event(html, url))

        self.assertEqual(1, len(events))
        event = events[0]

        with self.subTest("Life Event"):
            self.assertIsInstance(event, LifeEvent)

        with self.subTest("Name"):
            self.assertEqual(event.name, "bouwen en wonen")

    def test_adreswijziging(self):
        url = "https://www.affligem.be/Affligem/Nederlands/Leven/bouwen-en-wonen/adresverandering/page.aspx/60"
        html = url2html(url)

        d_relations = self.parser.extract_relations(html, url)

        with self.subTest("Event"):
            life_event = d_relations.get_life_events()[0]

            self.assertEqual("bouwen en wonen", life_event.name)

    def assert_multiline(self, s_true, s_pred):

        if s_true == s_pred:
            # Small assertion.
            self.assertEqual(s_true, s_pred)

        else:
            for i, (s_i, s_i_true) in enumerate(zip(s_true.splitlines(), s_pred.splitlines())):
                with self.subTest(f"line {i + 1}"):
                    self.assertEqual(s_i_true, s_i)


class TestHierarcy(unittest.TestCase):

    def setUp(self) -> None:
        self.parser = AffligemParser()

        b = 0
        if b:
            url_sitemap = "https://affligem.be/sitemap/page.aspx/182"
            self.html_sitemap = url2html(url_sitemap, FILENAME_HTML_AFFLIGEM_SITEMAP)
        else:

            self.html_sitemap = get_html(FILENAME_HTML_AFFLIGEM_SITEMAP)

    def test_extract_hierarchy(self):

        hierarchy = self.parser.extract_hierarchy(self.html_sitemap)

        # Base children
        with self.subTest("Events"):
            children = hierarchy.children

            self.assertEqual(children[0].name.lower(), 'leven', children[0])

            self.assertEqual(children[1].name.lower(), 'werken', children[1])

        # sdf
        with self.subTest("gemeentelijk Ruimtelijk Structuurplan"):
            h1 = hierarchy.children[0]
            self.assertEqual(h1.name.lower(), 'leven', h1)

            h2 = h1.children[0]
            self.assertEqual(h2.name.lower(), 'bouwen en wonen', h2)

            h3 = h2.children[5]
            self.assertEqual(h3.name.lower(), 'stedenbouw', h3)

            h4 = h3.children[1]
            self.assertEqual(h4.name.lower(), 'gemeentelijk ruimtelijk structuurplan', h4)

    def test_wijk_werken_Affligem(self):
        hierarchy = self.parser.extract_hierarchy(self.html_sitemap)

        with self.subTest("h1"):
            h1 = hierarchy.children[1]
            self.assertEqual(h1.name.lower(), 'werken', h1)
        with self.subTest("h2"):
            h2 = h1.children[4]
            self.assertEqual(h2.name.lower(), 'tewerkstelling', h2)
        with self.subTest("h3"):
            h3 = h2.children[0]
            self.assertEqual(h3.name.lower(), 'wijk-werken affligem', h3)
