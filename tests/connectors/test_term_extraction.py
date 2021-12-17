import os
import unittest

from connectors.term_extraction import ConnectorTermExtraction, ConnectionWarning

TERM_EXTRACTION = os.environ["TERM_EXTRACTION"]


class TestConnectorTermExtraction(unittest.TestCase):

    def test_init(self):
        conn = ConnectorTermExtraction(TERM_EXTRACTION,
                                       test_connection=True)

        self.assertEqual(conn.url, TERM_EXTRACTION)

    def test_bad_connection(self):
        with self.assertWarns(ConnectionWarning):
            ConnectorTermExtraction("https://no_connection.io",
                                    test_connection=True)

        ConnectorTermExtraction("https://no_connection.io",
                                test_connection=True)
