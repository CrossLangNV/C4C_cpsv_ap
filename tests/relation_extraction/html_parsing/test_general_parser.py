import unittest

from data.html import url2html
from relation_extraction.html_parsing.general_parser import GeneralHTMLParser


class TestGeneralHTMLParser(unittest.TestCase):

    def setUp(self) -> None:
        pass

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

    def test_sandbox(self):
        url = "https://www.comune.trento.it/Aree-tematiche/Attivita-edilizia/Interventi-edilizi/Permesso-di-costruire/Permesso-di-costruire"
        html = url2html(url)

        parser = GeneralHTMLParser(html)

        parser._sandbox()

        self.assertEqual(0, 1)
