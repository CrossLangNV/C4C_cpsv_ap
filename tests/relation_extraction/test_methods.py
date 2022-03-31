import unittest

from connectors.elastic_search import ElasticSearchConnector
from data.html import FILENAME_HTML, get_html
from relation_extraction.methods import get_chunks, get_concepts, get_public_service_description, \
    get_public_service_name, get_requirements


class TestExtraction(unittest.TestCase):

    def setUp(self) -> None:
        self.html = get_html(FILENAME_HTML)

    def test_get_requirements(self):
        # Get an HTML with x in.

        reqs = get_requirements(self.html)

        self.assertEqual(1, len(reqs), reqs)

        requirement0 = reqs[0]

        self.assertTrue(requirement0)

    def test_get_public_service(self):
        title = get_public_service_name(self.html)

        with self.subTest("Matching substring"):
            self.assertIn("financial plan".lower(), title.lower(), "Expected title to contain this")

        with self.subTest("Exact results"):
            self.assertEqual(title, "Financial plan: how to prepare an effective financial plan",
                             "Unexpected public service name.")

    def test_get_public_service_description(self):
        description = get_public_service_description(self.html)

        with self.subTest("Matching substring"):
            s_sub = "The financial plan is a dynamic instrument"

            self.assertIn(s_sub.lower(),
                          description.lower())

        with self.subTest("begin"):
            s_begin = "The financial plan is a dynamic instrument"

            self.assertEqual(s_begin.lower(), description[:len(s_begin)].lower(),
                             "Expected the description to start with this sentence")

        with self.subTest("end"):
            s_end = "What should it include? Who can help?"

            self.assertEqual(s_end.lower(), description[-len(s_end):].lower(),
                             "Expected the description to start with this sentence")

    def test_get_concepts(self):
        concepts = get_concepts(self.html)

        for concept_expected in ["business",
                                 "project"]:
            with self.subTest(f"Concept: '{concept_expected}'"):
                self.assertIn(concept_expected, concepts)


class TestElasticSearch(unittest.TestCase):
    def test_query(self):
        connector = ElasticSearchConnector()
        html = connector.get_random_html()

        with self.subTest("Retrieve html"):
            title = get_public_service_name(html)

        self.assertTrue(title, "Assert the return value is non-empty")


class TestGeneratorHTML(unittest.TestCase):
    def test_generator_HTML(self):
        html = get_html(FILENAME_HTML)

        chunks = get_chunks(html)

        with self.subTest("Titles"):
            for chunk in chunks:
                title = chunk[0]

                self.assertIsInstance(title, str)
