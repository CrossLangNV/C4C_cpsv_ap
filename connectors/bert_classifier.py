import requests

from app.models import Labels, Results, Text


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
