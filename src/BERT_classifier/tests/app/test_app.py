import unittest

from fastapi.testclient import TestClient

from BERT_classifier.app.main import app

TEST_CLIENT = TestClient(app)


class TestApp(unittest.TestCase):
    def test_get_homepage(self):
        r = TEST_CLIENT.get('/')

        self.assertTrue(r.ok, r.text)

    def test_classify_text(self):
        r = TEST_CLIENT.post("/classify_text",
                             json={"text": "Cost"})

        self.assertTrue(r.ok, r.text)

        with self.subTest("Find probabilities"):
            j = r.json()
            probs = j["probabilities"]

        with self.subTest("Type return"):
            self.assertIsInstance(probs, list)

        with self.subTest("Type list items"):
            for p in probs:
                self.assertIsInstance(p, float)

        with self.subTest("Labels"):
            self.assertTrue(j["labels"], j)

    def test_get_labels(self):
        r = TEST_CLIENT.get("/labels")

        self.assertTrue(r.ok, r.text)

        d_labels = r.json()
        labels = d_labels["labels"]

        with self.subTest("Type value"):
            for v in labels:
                self.assertIsInstance(v, str)
