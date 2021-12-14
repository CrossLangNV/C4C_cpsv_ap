import os

import requests

ES_LOGIN = os.environ.get("ES_LOGIN")
ES_PASSW = os.environ.get("ES_PASSW")


class ElasticSearchConnector:
    def __init__(self):
        pass

    def get_random_html(self):
        query = "https://elasticsearch.cefat4cities.crosslang.com/documents/_search?q=url:1819&from=100&size=10"

        r = requests.get(query, auth=(ES_LOGIN, ES_PASSW))

        j = r.json()

        hits = j["hits"]["hits"]

        hit0 = hits[0]

        source = hit0["_source"]

        html = source["content_html"]

        return html
