import unittest

from data.html import FILENAME_HTML_AFFLIGEM
from relation_extraction.affligem import AffligemParser


class TestAffligem(unittest.TestCase):
    def setUp(self) -> None:
        self.parser = AffligemParser()

    def test_url2html(self):
        url = "https://www.affligem.be/Affligem/Nederlands/Leven/identiteitsbewijzen,-rijbewijzen-en-afschriften/afschriften-uittreksels-getuigschriften/wettiging-van-handtekening/page.aspx/169#"

        html = self.parser.url2html(url, FILENAME_HTML_AFFLIGEM)

        s_in = "Het wettigen of legaliseren van een handtekening betekent dat een daartoe bevoegde overheid de echtheid van een handtekening schriftelijk bevestigt. Deze wettiging heeft echter niet tot doel de echtheid van de inhoud van het document te bewijzen."

        self.assertIn(s_in, html)

    def test_extract(self):
        with open(FILENAME_HTML_AFFLIGEM, "r") as fp:
            html = fp.read()

        d_relations = self.parser.extract_relations(html)

        with self.subTest("criterionRequirement"):
            s_true = "• De persoon van wie de handtekening gewettigd moet worden, moet zijn woonplaats\n" \
                     "hebben in een Belgische gemeente.\n" \
                     "• Het document mag niet bestemd zijn voor immorele, bedrieglijke of\n" \
                     "strafbare oogmerken.\n" \
                     "• De formaliteit moet nuttig of nodig zijn. Het mag bijgevolg niet gaan om een louter\n" \
                     "private akte (een eigenhandig geschreven testament bijvoorbeeld)."
            s = d_relations.criterionRequirement
            self.assertEqual(s_true, s)

        with self.subTest("rule"):
            s_true = "De burgemeester van de gemeente of zijn gemachtigde gaat na of de te legaliseren handtekening overeenstemt met die van de persoon van wie de identiteit wordt vastgesteld. Een handtekening op een wit vel papier kan nooit gelegaliseerd worden."
            s = d_relations.rule
            self.assertEqual(s_true, s)
        with self.subTest("evidence"):
            s_true = "• het document waarop de handtekening moet gewettigd worden\n" \
                     "• je identiteitskaart\n" \
                     "Laat je de handtekening van iemand anders wettigen, dan moet je de identiteitskaart van deze persoon en een door hem of haar ondertekende volmacht meebrengen."
            s = d_relations.evidence
            self.assertEqual(s_true, s)
        with self.subTest("cost"):
            s_true = "Het wettigen van een handtekening is gratis."
            s = d_relations.cost
            self.assertEqual(s_true, s)

    def test_attest_gezinssamenstelling(self):
        url = "https://www.affligem.be/Affligem/Nederlands/Leven/identiteitsbewijzen,-rijbewijzen-en-afschriften/afschriften-uittreksels-getuigschriften/aanvraag-samenstelling-van-het-gezin/page.aspx/825"
        html = self.parser.url2html(url)

        d_relations = self.parser.extract_relations(html)

        with self.subTest("criterionRequirement"):
            s_true = "De volgende partijen kunnen het attest met betrekking tot jou aanvragen:\n" \
                     "•  jij zelf (enkel voor je eigen gezin)\n" \
                     "•  je wettelijke vertegenwoordiger (bv. ouder of voogd)\n" \
                     "•  bijzondere gemachtigden zoals een notaris of advocaat\n" \
                     "•  derden (bv. publieke of private instellingen) als de afgifte ervan voorgeschreven is door of krachtens de wet\n" \
                     "•  een derde persoon op voorwaarde dat die in het bezit is van een volmacht en de identiteitskaart (of kopie ervan) van de\n" \
                     "aanvrager."

            s = d_relations.criterionRequirement

            with self.subTest("total"):
                self.assertEqual(s_true, s)

            for i, (s_i, s_i_true) in enumerate(zip(s_true.splitlines(), s.splitlines())):
                with self.subTest(f"line {i + 1}"):
                    self.assertEqual(s_i_true, s_i)
