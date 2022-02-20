import itertools
import os
import warnings
from typing import Generator, List, Optional, Union

import pydantic
import requests
from pydantic import BaseModel

ES_LOGIN = os.environ.get("ES_LOGIN")
ES_PASSW = os.environ.get("ES_PASSW")


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
    def __init__(self):
        pass

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

        j = r.json()

        hits = j["hits"]["hits"]

        return [Source(**hit["_source"]) for hit in hits]

    def generate_htmls(self, municipality="aalter",
                       min_acceptance=.5) -> Generator[Source, None, None]:

        size = 10

        for i in itertools.count():

            l_sources = self.query(municipality=municipality, i_start=i * size, size=size,
                                   min_acceptance=min_acceptance)

            for source in l_sources:

                if source.content_html:
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
