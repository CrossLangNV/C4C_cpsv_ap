import json
import os
import re
from typing import List

import fasttext
import pandas as pd
from nltk.tokenize import sent_tokenize

from connectors.translation import ETranslationConnector
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

SEP = '⚫'


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
                                           password=CEF_PASSW)
        EN = "EN"

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
        # titles_EN_trans = translator.trans_list_blocking(titles_NL, target="EN",
        #                                                  source="NL")

        target = "EN"

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
        return self.df_all[self.df_all[self.KEY_LANG] == "EN"][[self.KEY_TEXT,
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
    A general classifier regarding classifying different relationships defined within CPSV-AP.

    TODO (based on https://fasttext.cc/docs/en/supervised-tutorial.html)
     * Preprocess the data: >> cat cooking.stackexchange.txt | sed -e "s/\([.\!?,'/()]\)/ \1 /g" | tr "[:upper:]" "[:lower:]" > cooking.preprocessed.txt
     * optimize hyperparams. (e.g. epochs) but can't we do this automaticaly? Autotune?
        * epochs
        * lr
        * wordNgrams
    """

    def __init__(self, filename_train,
                 filename_valid):
        super(GeneralClassifier, self).__init__()

        # Load/train classifiers.

        t_train_min = 5  # min
        t_train = t_train_min * 60  # sec

        # TODO remove
        model = fasttext.train_supervised(input=filename_train,
                                          autotuneValidationFile=filename_valid,
                                          autotuneDuration=t_train,  # Will be unaccessible for this time.
                                          loss="ova"
                                          )

        conf = {
            "epoch": model.epoch,
            "dim": model.dim,
            "minCount": model.minCount,
            "wordNgrams": model.wordNgrams,
        }

        kwargs = {}
        if filename_valid:
            kwargs["autotuneValidationFile"] = filename_valid
            kwargs["autotuneDuration"] = 600
            # kwargs[""]

        model.test(filename_valid)

        # Fasttext
        model = fasttext.train_supervised(input=filename_train,

                                          # loss="ova",
                                          **kwargs,
                                          # autotuneMetric="f1:__label__crit_req",
                                          # lr=1, # TODO We should use autotune instead

                                          epoch=2,
                                          dim=10,

                                          minCount=1,
                                          wordNgrams=1,
                                          minn=0,
                                          maxn=0,
                                          bucket=1000,  # TODO this might be important for autotume!
                                          # dsub = 2, # TODO find out what this does.
                                          # loss = hs,

                                          )

        # Quick test
        print(model.predict("Conditions", k=2), "\n",
              model.predict("Deadlines and dates", k=2))

        print('vocab size: ', len(model.words))
        print('label size: ', len(model.names))
        print('example vocab: ', model.words[:5])
        print('example label: ', model.names[:5])

        # model.save_model("model_cooking.bin")
        return model

    def predict_rule(self, title: str = None, paragraph: str = None) -> bool:
        pass  # TODO

    def predict_evidence(self, title: str = None, paragraph: str = None) -> bool:
        pass  # TODO

    def predict_cost(self, title: str = None, paragraph: str = None) -> bool:
        pass  # TODO

    def predict_criterion_requirement(self, title: str = None, paragraph: str = None):
        pass  # TODO
