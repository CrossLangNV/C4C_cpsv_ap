from typing import List

import requests

from BERT_classifier.app.models import Labels, Results, ResultsLines, Text, TextLines


class BERTConnector:
    def __init__(self, url="http://relations_classifier_bert_api_cpu:5000"):
        self.url = url

    def get_home(self) -> dict:
        response = requests.get(self.url)

        response.raise_for_status()

        return response.json()

    def get_labels(self) -> Labels:
        response = requests.get(self.url + "/labels")

        response.raise_for_status()

        labels = Labels(**response.json())

        return labels

    def post_classify_text(self, text) -> Results:
        response = requests.post(self.url + "/classify_text",
                                 json=Text(text=text).dict())

        response.raise_for_status()

        results = Results(**response.json())

        return results

    def post_classify_text_lines(self, text_lines: List[str]) -> ResultsLines:
        response = self._post("/classify_text_lines",
                              json=TextLines(text=text_lines).dict())

        response.raise_for_status()

        results_lines = ResultsLines(**response.json())

        return results_lines

    def _post(self, url_path, json=None):
        response = requests.post(self.url + url_path,
                                 json=json)

        response.raise_for_status()

        return response
