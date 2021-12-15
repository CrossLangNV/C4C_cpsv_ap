import os
import unittest
import codecs
from relation_extraction.methods import get_requirements, get_public_service, generator_html
from relation_extraction.ES_connector import ElasticSearchConnector

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

        requirement = next(get_requirements(self.html))

        self.assertTrue(requirement)

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


class TestGeneratorHTML(unittest.TestCase):
    def test_generator_HTML(self):
        html = get_html(FILENAME_HTML)

        for _ in generator_html(html):
            print(_)

        self.assertEqual(0, 1)
