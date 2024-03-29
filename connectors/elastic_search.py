import itertools
import json
import os
import warnings
from collections import Counter
from typing import Dict, Generator, List, Optional, Union

import pydantic
import requests
from pydantic import BaseModel

ES_LOGIN = os.environ.get("ES_LOGIN")
ES_PASSW = os.environ.get("ES_PASSW")

if (ES_LOGIN is None) or (ES_PASSW is None):
    warnings.warn("Did not find any login information for Elastic Search.")


class Source(BaseModel):
    content_html: str
    language: str
    content: str

    # -- Extra --
    # website: Union[str, dict]
    title: str
    url: str
    acceptance_state_max_probability: Optional[float]  # TODO Not really optional tho, as we need this info

    # # -- less useful? --
    # id: str
    # title_prefix: str
    # author: str
    # status: str
    # type: str
    # date: str
    # date_of_effect: Optional[str]
    # date_last_update: Optional[str]
    # summary: str
    # various: str
    # file: str
    # file_url: Optional[str]
    # created_at: str
    # updated_at: str
    # unvalidated: str

    @pydantic.validator("acceptance_state_max_probability", pre=True)
    def to_float(cls, v: Union[str, float]):
        if isinstance(v, str):
            return float(v)
        return v


class ElasticSearchConnector:
    HEADERS = {"content-type": "application/json"}
    url = "https://elasticsearch.cefat4cities.crosslang.com/documents/_search?pretty=true"

    def __init__(self):
        pass
        # self.elastic_client = Elasticsearch(hosts=["https://elasticsearch.cefat4cities.crosslang.com"])

    def query(self,
              municipality: str = None,
              i_start: int = None,
              size: int = None,
              min_acceptance: float = 0,
              ) -> List[Source]:
        """

        Returns:
        """

        s_muni = f"&q=url:{municipality}" if municipality is not None else ""
        s_from = f"&from={i_start}" if i_start is not None else ""
        s_size = f"&size={size}" if size is not None else ""

        s_min_acceptance = f"&q=acceptance_state_max_probability:>={min_acceptance}" if min_acceptance else ""

        query = f"https://elasticsearch.cefat4cities.crosslang.com/documents/_search?{s_muni}{s_from}{s_size}{s_min_acceptance}"

        r = requests.get(query, auth=(ES_LOGIN, ES_PASSW))

        assert r.ok, (r, r.text)

        j = r.json()

        hits = j["hits"]["hits"]

        return [Source(**hit["_source"]) for hit in hits]

    def query_example(self):
        """
        TODO work out.
        """

        d = {
            "query": {
                "match": {
                    "title": "Aalterbon - Gemeente Aalter"
                }
            },
            "sort": [
                {"_id": "asc"}
            ]
        }

        response = requests.get(self.url,
                                data=json.dumps(d),
                                auth=(ES_LOGIN, ES_PASSW),
                                headers=self.HEADERS)

        j = response.json()["hits"]["hits"]

        # Languages
        l_lang = [doc["_source"]["language"] for doc in j]
        s_lang = set(l_lang)

        return j

    def generate_htmls(self, municipality="aalter",
                       min_acceptance=.5) -> Generator[Source, None, None]:

        size = 10

        for i in itertools.count():

            l_sources = self.query(municipality=municipality, i_start=i * size, size=size,
                                   min_acceptance=min_acceptance)

            for source in l_sources:
                # if source.content_html: # We should not have to check this here.
                yield source

    def get_random_html(self,
                        lang: str = None):

        sources = self.query(municipality="1819",
                             i_start=100,
                             size=10
                             )

        if lang is None:
            # Return last one
            source = sources[-1]
            html = source.content_html
            return html

        for source in sources:
            html = source.content_html

            if source.language == lang:
                return html

        # backup/last one
        warnings.warn("Could not find an html with desired language.", UserWarning)
        return html

    def get_languages(self, size=100) -> Dict[str, int]:
        """
        TODO language information does not seem to be saved atm in Elastic Search.
        """

        field = "language"

        def process_single_item(l):
            if isinstance(l, list) and len(l) == 1:
                return l[0]
            return l

        lang_count = Counter()

        for i in itertools.count():

            _from = i * size

            print(f"#{i}: {_from} -> {_from + size - 1} ")

            d = {
                "fields": [
                    field
                ],
                "_source": False,  # We don't need the whole sources.
                "from": _from,
                "size": size
            }

            HEADERS = {"content-type": "application/json"}
            url = "https://elasticsearch.cefat4cities.crosslang.com/documents/_search?pretty=true"
            response = requests.get(url,
                                    data=json.dumps(d),
                                    auth=(ES_LOGIN, ES_PASSW),
                                    headers=HEADERS)

            try:
                hits = response.json()["hits"]["hits"]
            except:
                # Finished
                break

            lang_sub = [process_single_item(hit["fields"][field]) for hit in hits]

            lang_count.update(lang_sub)

        return lang_count
