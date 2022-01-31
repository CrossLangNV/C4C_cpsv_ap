import os
import warnings

import requests
from pydantic import BaseModel

ES_LOGIN = os.environ.get("ES_LOGIN")
ES_PASSW = os.environ.get("ES_PASSW")


class ElasticSearchConnector:
    def __init__(self):
        pass

    class Source(BaseModel):
        content_html: str
        language: str
        content: str

    def get_random_html(self,
                        lang: str = None):
        query = "https://elasticsearch.cefat4cities.crosslang.com/documents/_search?q=url:1819&from=100&size=10"

        r = requests.get(query, auth=(ES_LOGIN, ES_PASSW))

        j = r.json()

        hits = j["hits"]["hits"]

        for hit in hits:

            source = self.Source(**hit["_source"])
            html = source.content_html

            if lang is not None and source.language == lang:
                return html

        # Return last one
        if lang is not None:
            warnings.warn("Could not find an html with desired language.", UserWarning)
        return html
