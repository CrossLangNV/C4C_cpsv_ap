import os
import re
import unittest

from connectors.term_extraction import ConnectorTermExtraction, ConnectionWarning, _get_content
from connectors.term_extraction_utils.models import ChunkModel
from connectors.utils import PARAGRAPH_TYPE, cas_from_cas_content
from data.html import get_html, FILENAME_HTML

TERM_EXTRACTION = os.environ["TERM_EXTRACTION"]


class TestConnectorTermExtraction(unittest.TestCase):

    def test_init(self):
        conn = ConnectorTermExtraction(TERM_EXTRACTION,
                                       test_connection=True)

        self.assertEqual(conn.url, TERM_EXTRACTION)

    def test_good_connection(self):

        try:
            with self.assertWarns(ConnectionWarning) as cm:

                ConnectorTermExtraction(TERM_EXTRACTION,
                                        test_connection=True)

        except AssertionError as e:
            # Great! We were able to connect to the API.
            pass
        else:
            self.fail(f"Should not raised a warning.\n{cm.warning}")

    def test_bad_connection(self):
        with self.assertWarns(ConnectionWarning) as cm:
            ConnectorTermExtraction("https://no_connection.io",
                                    test_connection=True)

        w = cm.warning

        with self.subTest("Test return value"):
            self.assertTrue(w, "Expected a warning")

        with self.subTest("Number of warnings"):
            self.assertEqual(len(cm.warnings), 1, "expected one warning")

        with self.subTest("Type of warning"):
            self.assertIsInstance(w, ConnectionWarning)

        with self.subTest("Message"):
            self.assertIn("connection", str(w).lower())


class TestConnectorTermExtractionContactInfo(unittest.TestCase):
    def setUp(self) -> None:
        self.conn = ConnectorTermExtraction(TERM_EXTRACTION,
                                            test_connection=False)

        self.html = get_html(FILENAME_HTML)

    def test_return(self):
        l_contact_info = self.conn.get_contact_info(self.html,
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
        chunk = self.conn.post_chunking(self.html,
                                        )

        self.assertTrue(chunk, "Expected something back.")
        self.assertIsInstance(chunk, ChunkModel)


class TestConnectorTermExtractionText(unittest.TestCase):
    """
    For some files, the returned text within the CAS is lackluster.
    Within these tests, this content is tested to be equal between the different requests.
    """

    def setUp(self) -> None:
        self.conn = ConnectorTermExtraction(TERM_EXTRACTION,
                                            test_connection=False)

        self.html = get_html(FILENAME_HTML)

    def test_(self):
        # Text from
        chunk = self.conn.post_chunking(self.html)
        text_chunking = chunk.text

        # Text from TIKA parsing
        contact_info = self.conn._post_contact_info(self.html)
        text_contact_info = contact_info.text

        def clean_text_concat(s: str) -> str:
            lines = [line.strip() for line in s.splitlines()]
            concat = " ".join(lines)

            concat_clean = re.sub('\s+', ' ', concat)
            # concat_clean = concat.replace("  "," ") # Remove double spaces

            return concat_clean

        self.assertIn(clean_text_concat(text_chunking),
                      clean_text_concat(text_contact_info))

    def test_get_paragraphs(self):
        contact_info = self.conn._post_contact_info(self.html)

        cas = cas_from_cas_content(contact_info.cas_content)
        l_par = _get_content(cas, PARAGRAPH_TYPE)

        self.assertEqual(0, 1)
