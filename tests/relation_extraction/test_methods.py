import os
import unittest
import codecs
from relation_extraction.methods import foo, get_public_service
from tests.relation_extraction.ES_connector import ElasticSearchConnector

FILENAME_HTML = os.path.join(os.path.dirname(__file__),
                             'Financial plan_ how to prepare an effective financial plan.html')


def get_html(filename, encoding='utf-8') -> str:
    with codecs.open(filename, 'r', encoding=encoding) as f:
        return f.read()


class TestFoo(unittest.TestCase):

    def setUp(self) -> None:
        self.html = get_html(FILENAME_HTML)

    def test_foo(self):
        # Get an HTML with x in.

        foo(self.html)

        self.assertEqual(0, 1)

    def test_get_public_service(self):
        title = get_public_service(self.html)

        self.assertIn("financial plan".lower(), title.lower(), "Expected title to contain this")


class TestElasticSearch(unittest.TestCase):
    def test_query(self):
        connector = ElasticSearchConnector()
        html = connector.get_random_html()

        with self.subTest("Retrieve html"):
            title = get_public_service(html)

        self.assertTrue(title, "Assert the return value is non-empty")
