import unittest

from connectors.bert_classifier import BERTConnector


class TestElasticSearchConnector(unittest.TestCase):
    def setUp(self) -> None:
        self.connector = BERTConnector()

    def test_home(self):
        r = self.connector.get_home()

        self.assertTrue(r)

    def test_get_labels(self):
        labels = self.connector.get_labels()

        self.assertTrue(labels.names)

        self.assertGreaterEqual(len(labels.names), 1)

    def test_post_classify_text(self):
        text = "cost"

        results = self.connector.post_classify_text(text)

        with self.subTest("Name"):
            self.assertTrue(results.names)

        with self.subTest("Labels"):
            self.assertTrue(results.names)
