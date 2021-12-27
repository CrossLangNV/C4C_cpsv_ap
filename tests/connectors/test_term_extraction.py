import os
import unittest

from connectors.term_extraction import ConnectorTermExtraction, ConnectionWarning
from data.html import get_html, FILENAME_HTML

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


class TestConnectorTermExtractionContactInfo(unittest.TestCase):
    def setUp(self) -> None:
        self.conn = ConnectorTermExtraction(TERM_EXTRACTION,
                                            test_connection=False)

        self.html = get_html(FILENAME_HTML)

    def test_return(self):
        l_contact_info = self.conn.post_contact_info(self.html,
                                                     )

        with self.subTest("type"):
            self.assertIsInstance(l_contact_info, list)

            for item in l_contact_info:
                self.assertIsInstance(item, str)

        with self.subTest("Find address"):
            address = "Chaussée de Charleroi 110"

            self.assert_substring_in_list(l_contact_info, address)

        with self.subTest("Find mail"):
            address = "info@1819.brussels"

            self.assert_substring_in_list(l_contact_info, address)

    def assert_substring_in_list(self, l: list, substring: str):
        b_found = False
        for item in l:
            if substring in item:
                b_found = True
        if not b_found:
            self.fail(f"could not find '{substring}' in {l}")


class TestConnectorTermExtractionChunking(unittest.TestCase):
    def setUp(self) -> None:
        self.conn = ConnectorTermExtraction(TERM_EXTRACTION,
                                            test_connection=False)

        self.html = get_html(FILENAME_HTML)

    def test_return(self):
        cas = self.conn.post_chunking(self.html,
                                      )

        self.assertEqual(0, 1)
