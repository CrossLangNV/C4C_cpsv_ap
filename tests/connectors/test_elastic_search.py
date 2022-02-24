import unittest

from connectors.elastic_search import ElasticSearchConnector


class TestElasticSearchConnector(unittest.TestCase):
    def test_random(self):
        connector = ElasticSearchConnector()
        html = connector.get_random_html()

        self.assertTrue(html)


class TestQuery(unittest.TestCase):
    def setUp(self) -> None:
        self.es_conn = ElasticSearchConnector()

    def test_keys(self):
        size = 16

        with self.subTest("Municipality"):
            municipality = "aalter"

            l = self.es_conn.query(municipality=municipality, size=size)

            self.assertEqual(len(l), size)

    def test_municipality(self):
        size = 16

        municipality = "1819"

        l = self.es_conn.query(municipality=municipality, size=size)

        with self.subTest("# hits"):
            self.assertEqual(len(l), size)

        with self.subTest("muni"):
            for i, a in enumerate(l):
                with self.subTest(i):
                    self.assertTrue(a.content_html)

    def test_query_example(self):
        l = self.es_conn.query_example()


class TestAalter(unittest.TestCase):

    def setUp(self) -> None:
        self.es_conn = ElasticSearchConnector()

    def test_aalter(self):

        # filter on webpages with
        #  * html
        #  * with a acceptance rate above x

        n_max = 100

        self.es_conn.query(municipality="aalter")

        gen_htmls = self.es_conn.generate_htmls(municipality="aalter",
                                                min_acceptance=0.5)

        for i, source in enumerate(gen_htmls):

            if i >= n_max:
                break

            source.url
            source.content_html

class TestGetLanguages(unittest.TestCase):
    def setUp(self) -> None:
        self.es_conn = ElasticSearchConnector()

    def test_summary(self):
        languages = self.es_conn.get_languages()
        print(languages)
        self.assertEqual(0, 1)
