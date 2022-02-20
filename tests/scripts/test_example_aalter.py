import unittest

from connectors.elastic_search import ElasticSearchConnector


class TestMain(unittest.TestCase):
    def test_es(self):
        """
        Before continuing we need to extract some files/pages from Aalter.
        There seem to be some files saved in ES.

        Returns:

        """

        es_conn = ElasticSearchConnector()

        es_conn
