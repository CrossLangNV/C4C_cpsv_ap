import unittest

from data.html import FILENAME_HTML, get_html
from relation_extraction.elastic_search import ElasticSearchConnector
from relation_extraction.methods import get_requirements, get_public_service_name, generator_html, \
    get_public_service_description, get_contact_info_stuff, get_concepts


class TestExtraction(unittest.TestCase):

    def setUp(self) -> None:
        self.html = get_html(FILENAME_HTML)

    def test_get_requirements(self):
        # Get an HTML with x in.

        requirement = next(get_requirements(self.html))

        self.assertTrue(requirement)

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
            self.assertIn("The financial plan is a dynamic instrument".lower(),
                          description)

        with self.subTest("begin"):
            s_begin = "The financial plan is a dynamic instrument"

            self.assertEqual(s_begin, description[:len(s_begin)],
                             "Expected the description to start with this sentence")

        with self.subTest("end"):
            s_end = "the project should be seriously re-examined."

            self.assertEqual(s_begin, description[-len(s_end):], "Expected the description to start with this sentence")

        pass

        self.assertEqual(0, 1)

    def test_get_contact_info_stuff(self):
        ci_stuff = get_contact_info_stuff(self.html)

        self.assertIsInstance(ci_stuff, list)

        for i, ci_stuff_i in enumerate(ci_stuff):
            with self.subTest(f"#{i}"):
                self.assertIsInstance(ci_stuff_i, str)

    def test_get_concepts(self):
        concepts = get_concepts(self.html)

        self.assertEqual(0, 1)


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

        for _ in generator_html(html):
            print(_)

        self.assertEqual(0, 1)
