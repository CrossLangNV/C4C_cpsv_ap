import os
import re

import pandas as pd

from connectors.translate_connector import ETranslationConnector
from data.html import get_html
from relation_extraction.aalter import AalterParser
from relation_extraction.austrheim import AustrheimParser
from relation_extraction.cities import CPSVAPRelationsClassifier
from relation_extraction.nova_gorica import NovaGoricaParser
from relation_extraction.san_paolo import SanPaoloParser
from relation_extraction.wien import WienParser
from relation_extraction.zagreb import ZagrebParser

DIR_EXAMPLE_FILES = os.path.join(os.path.dirname(__file__), "../tests/relation_extraction/EXAMPLE_FILES")
url2filename = lambda page: os.path.join(DIR_EXAMPLE_FILES, re.sub(r'\W+', '_', page) + ".html")

CEF_LOGIN = os.environ.get("CEF_LOGIN")
CEF_PASSW = os.environ.get("CEF_PASSW")


class Dataset:
    """
    TODO
     * Define what info is needed:
        * header, paragraph, classification, Source (website/webpage), municipality (main page), language,
        * Original language?
        * Also save negative examples (without classification)
     * Save as Pandas?
    """

    def __init__(self):
        urls = ["https://www.aalter.be/eid", "https://www.aalter.be/verhuizen",  # Dutch
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

        translator = ETranslationConnector(username=CEF_LOGIN,
                                           password=CEF_PASSW)
        EN = "EN"

        l_d = []

        for url in urls:

            filename = url2filename(url)
            html = get_html(filename)
            if "aalter" in filename.lower():
                parser = AalterParser()
                lang = "NL"
            elif "sanpaolo" in filename.lower():
                parser = SanPaoloParser()
                lang = "IT"
            elif "gorica" in filename.lower():
                parser = NovaGoricaParser()
                lang = "SI"
            elif "wien" in filename.lower():
                parser = WienParser()
                lang = "DE"
            elif "zagreb" in filename.lower():
                parser = ZagrebParser()
                lang = "HR"
            elif "austrheim" in filename.lower():
                parser = AustrheimParser()
                lang = "NO"
            else:
                continue

            for header, paragraph in parser._paragraph_generator(html):
                # Only if has paragraph
                if not paragraph:
                    continue

                pred_crit_req = parser.classifier.predict_criterion_requirement(header, paragraph)

                d_i = {"title": header,
                       "criterion_requirement": pred_crit_req,
                       "lang": lang,
                       "translated": False}
                l_d.append(d_i)

                translate = False
                if translate:
                    target = EN
                    header_EN = translator.trans_snippet_blocking(lang, target, header).strip()

                    d_i = {"title": header_EN,
                           "criterion_requirement": pred_crit_req,
                           "lang": target,
                           "lang_orig": lang,
                           "translated": True}
                    l_d.append(d_i)

        df_all = pd.DataFrame(l_d)
        print(df_all[["title", "criterion_requirement"]])

        print("Summary labels:")
        print(df_all['criterion_requirement'].value_counts())

        # TODO translate all to English.


class GeneralClassifier(CPSVAPRelationsClassifier):
    """
    A general classifier regarding classifying different relationships defined within CPSV-AP.
    """

    def predict_rule(self, title: str = None, paragraph: str = None) -> bool:
        pass  # TODO

    def predict_evidence(self, title: str = None, paragraph: str = None) -> bool:
        pass  # TODO

    def predict_cost(self, title: str = None, paragraph: str = None) -> bool:
        pass  # TODO

    def predict_criterion_requirement(self, title: str = None, paragraph: str = None):
        pass  # TODO
