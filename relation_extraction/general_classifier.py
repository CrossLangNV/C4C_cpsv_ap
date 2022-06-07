import json
import os
import re
import warnings
from functools import lru_cache
from typing import List

import pandas as pd
from nltk.tokenize import sent_tokenize

from connectors.bert_classifier import BERTConnector
from connectors.translation import ETranslationConnector
from data.html import get_html
from relation_extraction.aalter import AalterParser
from relation_extraction.austrheim import AustrheimParser
from relation_extraction.cities import ClassifierCityParser, CPSVAPRelationsClassifier
from relation_extraction.html_parsing.data import ParserModel
from relation_extraction.html_parsing.general_parser import GeneralHTMLParser, GeneralSection
from relation_extraction.nova_gorica import NovaGoricaParser
from relation_extraction.san_paolo import SanPaoloParser
from relation_extraction.wien import WienParser
from relation_extraction.zagreb import ZagrebParser

DIR_EXAMPLE_FILES = os.path.join(os.path.dirname(__file__), "../tests/relation_extraction/EXAMPLE_FILES")
url2filename = lambda page: os.path.join(DIR_EXAMPLE_FILES, re.sub(r'\W+', '_', page) + ".html")

CEF_API = os.environ.get("CEF_API")
CEF_LOGIN = os.environ.get("CEF_LOGIN")
CEF_PASSW = os.environ.get("CEF_PASSW")

SEP = '⚫'
EN = "EN"


class Dataset:
    """
    TODO
     * Define what info is needed:
        * header, paragraph, classification, Source (website/webpage), municipality (main page), language,
        * Original language?
        * Also save negative examples (without classification)
     * Save as Pandas?
    """

    KEY_TEXT = "text"
    KEY_LANG = "lang"
    KEY_HEADER = "header"
    KEY_TRANSLATED = "translated"
    KEY_LANG_ORIG = "lang_orig"

    KEY_CRIT_REQ = "criterion_requirement"
    KEY_RULE = "rule"
    KEY_EVIDENCE = 'evidence'
    KEY_COST = "cost"

    def __init__(self):
        self.df_all = pd.DataFrame()

    def generate(self, filename=None, separator=SEP):
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
                                           password=CEF_PASSW,
                                           url=CEF_API)

        l_d = []

        for url in urls:

            filename_html = url2filename(url)
            html = get_html(filename_html)
            if "aalter" in filename_html.lower():
                parser = AalterParser()
                lang = "NL"
            elif "sanpaolo" in filename_html.lower():
                parser = SanPaoloParser()
                lang = "IT"
            elif "gorica" in filename_html.lower():
                parser = NovaGoricaParser()
                lang = "SL"
            elif "wien" in filename_html.lower():
                parser = WienParser()
                lang = "DE"
            elif "zagreb" in filename_html.lower():
                parser = ZagrebParser()
                lang = "HR"
            elif "austrheim" in filename_html.lower():
                parser = AustrheimParser()
                lang = "NO"
            else:
                continue

            # Important to not include subsection, to avoid double data.
            for header, paragraph in parser._paragraph_generator(html,
                                                                 include_sub=False
                                                                 ):
                # Only if has paragraph
                if not paragraph:
                    continue

                pred_crit_req = parser.classifier.predict_criterion_requirement(header, paragraph)
                pred_rule = parser.classifier.predict_rule(header, paragraph)
                pred_evidence = parser.classifier.predict_evidence(header, paragraph)
                pred_cost = parser.classifier.predict_cost(header, paragraph)

                d_i = {self.KEY_TEXT: header,
                       self.KEY_CRIT_REQ: pred_crit_req,
                       self.KEY_RULE: pred_rule,
                       self.KEY_EVIDENCE: pred_evidence,
                       self.KEY_COST: pred_cost,
                       self.KEY_LANG: lang,
                       self.KEY_HEADER: True,
                       self.KEY_TRANSLATED: False}
                l_d.append(d_i)

                # Add paragraphs

                def split_paragraphs(paragraph: str) -> List[str]:
                    l_sent = []
                    for sub_par in paragraph.splitlines():
                        l_sent.extend(sent_tokenize(sub_par))

                    # Filter away empty lines
                    l_sent = list(filter(str, l_sent))

                    return l_sent

                for sent in split_paragraphs(paragraph):
                    d_i = {self.KEY_TEXT: sent,
                           self.KEY_CRIT_REQ: pred_crit_req,
                           self.KEY_RULE: pred_rule,
                           self.KEY_EVIDENCE: pred_evidence,
                           self.KEY_COST: pred_cost,
                           self.KEY_LANG: lang,
                           self.KEY_HEADER: False,
                           self.KEY_TRANSLATED: False}
                    l_d.append(d_i)

        df_all = pd.DataFrame(l_d)

        print(df_all[[self.KEY_TEXT, self.KEY_CRIT_REQ, self.KEY_RULE, self.KEY_EVIDENCE, self.KEY_COST]])

        print("Summary labels:")
        print(df_all['criterion_requirement'].value_counts())

        def get_l_text(df: pd.DataFrame) -> List[str]:
            titles = list(df[self.KEY_TEXT])
            return titles

        # TODO translate all to English.
        # Group by language.
        # titles_NL = get_l_text(df_all[df_all["lang"] == "NL"])
        # titles_EN_trans = translator.trans_list_blocking(titles_NL, target=EN,
        #                                                  source="NL")

        target = EN

        # Add English translations to the dataset
        for source, df_source in df_all.groupby(self.KEY_LANG):

            l_text_source = get_l_text(df_source)
            l_text_target = translator.trans_list_blocking(l_text_source,
                                                           target=target,
                                                           source=source)

            rows_trans = []

            for (_, row), title_target in zip(df_source.iterrows(), l_text_target):
                # Add info
                row[self.KEY_LANG_ORIG] = row[self.KEY_LANG]
                row[self.KEY_TRANSLATED] = True
                # Update info
                row[self.KEY_LANG] = target
                row[self.KEY_TEXT] = title_target

                rows_trans.append(row)

            df_target = pd.DataFrame(rows_trans, index=None).reset_index(drop=True)

            # Extend the original dataframe.
            df_all = pd.concat([df_all, df_target], ignore_index=True)

        df_all
        titles_target_all = get_l_text(df_all[df_all[self.KEY_LANG] == target])

        # Sort of return value?
        self.df_all = df_all

        if filename:
            df_all.to_csv(filename, sep=separator, index=False, encoding='utf-8')

        return df_all

    def load(self, filename, separator=SEP):

        df_all = pd.read_csv(filename, sep=separator, encoding="utf-8")

        self.df_all = df_all
        return self.df_all

    def get_english_training_data(self):
        # Only English
        return self.df_all[self.df_all[self.KEY_LANG] == EN][[self.KEY_TEXT,
                                                              self.KEY_CRIT_REQ,
                                                              self.KEY_RULE,
                                                              self.KEY_EVIDENCE,
                                                              self.KEY_COST]]

    def export_BERT_train_data(self,
                               lang: str,
                               p_train=.6,
                               filename_train="train.jsonl",
                               filename_valid="validation.jsonl"):
        """
        Export the BERT training data

        Step 1: Filter data that we are interested in.
        Step 2: Save to appropriate format.

        Args:
            lang: Filter on lang.

        Returns:
            saved to jsonl
        """

        assert 0 <= p_train <= 1, p_train

        df_filter = self.df_all
        if lang:
            df_filter = df_filter[self.df_all[self.KEY_LANG] == lang]

        l_d_json = []
        for i, row in df_filter.iterrows():

            text = row[self.KEY_TEXT]
            labels = []

            for key in [self.KEY_CRIT_REQ, self.KEY_RULE, self.KEY_EVIDENCE, self.KEY_COST]:
                if row[key]:
                    labels.append(key)

            d_json = {"name_labels": labels,
                      "text": text
                      }
            l_d_json.append(d_json)

            # if len(labels) == 0:
            # labels.append("NONE") # Add "else"

        # Export to file

        # Cleanse
        with open(filename_train, 'w+') as f:
            f.truncate(0)
        with open(filename_valid, 'w+') as f:
            f.truncate(0)

        for i, d_json in enumerate(l_d_json):
            json_string = json.dumps(d_json)
            if i / len(l_d_json) <= p_train:
                with open(filename_train, "a") as f:
                    f.write(json_string + "\n")
            else:
                with open(filename_valid, "a") as f:
                    f.write(json_string + "\n")


class GeneralClassifier(CPSVAPRelationsClassifier):
    """
    General classifier
    """

    COST = "cost"
    RULE = "rule"
    EVIDENCE = "evidence"
    CRITERION_REQUIREMENT = "criterion_requirement"

    def __init__(self, lang: str, target=EN):
        super(GeneralClassifier, self).__init__()

        self.bert_connector = BERTConnector()
        self.translator = ETranslationConnector(username=CEF_LOGIN,
                                                password=CEF_PASSW,
                                                url=CEF_API)

        self.lang = lang  # language of source files
        self.target = target
        self.pretranslated_source_target: dict = {}

    def predict_criterion_requirement(self, title: str = None, paragraph: str = None) -> bool:
        """
        Get general classification, then use CACHE to save result temporarily.
        Args:
            title:
            paragraph:

        Returns:

        """

        return self._shared_predict(title, paragraph, self.CRITERION_REQUIREMENT)

    def predict_rule(self, title: str = None, paragraph: str = None) -> bool:
        return self._shared_predict(title, paragraph, self.RULE)

    def predict_evidence(self, title: str = None, paragraph: str = None) -> bool:
        return self._shared_predict(title, paragraph, self.EVIDENCE)

    def predict_cost(self, title: str = None, paragraph: str = None) -> bool:
        return self._shared_predict(title, paragraph, self.COST)

    def _shared_predict(self, title: str, paragraph: str, key: str):
        """

        Args:
            title:
            paragraph:
            key:

        Returns:

        TODO:
         - (?) Include paragraph info into the prediction
        """

        results = self._get_results_cache(title, self.lang)
        # results = self.bert_connector.post_classify_text(title)
        idx = results.names.index(key)
        prob = results.probabilities[idx]

        return bool(round(prob))

    @lru_cache(maxsize=1)
    def _get_results_cache(self, text: str, lang):
        """
        Use cache for retrieving results as we will call it multiple times in a row with the same value.

        Args:
            text:

        Returns:

        """

        text_EN = self._get_text_target(text, lang, self.target)

        results = self.bert_connector.post_classify_text(text_EN)
        return results

    @lru_cache(maxsize=20)
    def _get_text_target(self, text, lang, target):

        if lang.upper() == target:
            return text

        # Check pretranslated
        text_EN = self.pretranslated_source_target.get(text)
        if text_EN:
            return text_EN

        # Last resort: translate single sentence
        text_EN = self.translator.trans_snippet_blocking(
            source=lang.upper(),
            target=target.upper(),
            snippet=text)

        return text_EN

    def pretranslate(self, l_text):

        l_text_translated = self.translator.trans_list_blocking(l_text,
                                                                source=self.lang,
                                                                target=self.target)

        d_pretranslated_new = {text_source: text_target for text_source, text_target in zip(l_text, l_text_translated)}
        self.pretranslated_source_target = d_pretranslated_new


class GeneralCityParser(ClassifierCityParser):
    """
    City parser with a general classifier and HTML chunker.
    """

    def __init__(self,
                 lang_code: str,
                 parser_model: ParserModel = None,
                 filename_html_parsing: str = None):
        """

        Args:
            lang_code:
            parser_model:
            filename_html_parsing (Optional): filename to where to save html parsing
        """

        classifier = GeneralClassifier(lang=lang_code)

        super(GeneralCityParser, self).__init__(classifier=classifier)

        # Not needed, but remove warning for pretranslate method
        self.classifier: GeneralClassifier = classifier
        self.lang_code = lang_code

        if parser_model is None:
            parser_model = ParserModel(titles=ParserModel.titlesChoices.text_classifier)
        self.parser_model = parser_model

        self._filename_html_parsing = filename_html_parsing

    def extract_relations(self, s_html, *args, include_sub=True, **kwargs):
        """
        To speed up things, we should pre-translate things
        Args:
            *args:
            **kwargs:

        Returns:

        """

        l_titles = [title for title, _ in self._paragraph_generator(s_html, include_sub=include_sub)]
        self.classifier.pretranslate(l_titles)

        return super(GeneralCityParser, self).extract_relations(s_html, *args, **kwargs)

    # Is slow, so trying to use with cache
    @lru_cache(maxsize=1)
    def parse_page(self,
                   s_html,
                   include_sub: bool = True,
                   ) -> List[GeneralSection]:
        justext_wrapper_class = self.parser_model.get_justext_wrapper_class()
        html_parser = GeneralHTMLParser(s_html,
                                        language=self.lang_code,
                                        justext_wrapper_class=justext_wrapper_class
                                        )

        if (filename_html_parsing := self._filename_html_parsing) is not None:
            try:
                html_parser._justext_wrapper._export_debugging(filename_html_parsing)
            except Exception as e:
                warnings.warn(f"Tried to export HTML parsing result to {filename_html_parsing}, but failed",
                              UserWarning)

        sections = html_parser.get_sections(include_sub=include_sub)

        return sections
