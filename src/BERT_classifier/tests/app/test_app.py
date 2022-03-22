import unittest

from fastapi.testclient import TestClient

from app.main import app

TEST_CLIENT = TestClient(app)


class TestApp(unittest.TestCase):
    def test_get_homepage(self):
        r = TEST_CLIENT.get('/')

        self.assertTrue(r.ok, r.text)

    def test_classify_text(self):
        r = TEST_CLIENT.post("/classify_text",
                             json={"text": "Cost"})

        self.assertTrue(r.ok)
