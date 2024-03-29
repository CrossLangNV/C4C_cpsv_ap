import os
import re
import unittest

from connectors.term_extraction import ConnectionWarning, ConnectorContactInfoClassification, ConnectorTermExtraction, \
    Label
from connectors.term_extraction_utils.cas_utils import _get_annotation_text, cas_from_cas_content, CasWrapper, \
    CONTACT_PARAGRAPH_TYPE
from connectors.term_extraction_utils.models import ChunkModel, QuestionAnswersModel, TermsModel
from data.html import FILENAME_HTML, get_html

TERM_EXTRACTION = os.environ["TERM_EXTRACTION"]
CONTACT_CLASSIFICATION = os.environ["CONTACT_CLASSIFICATION"]


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

    def test_cleaned_contact_info(self):
        """
        Within the CAS

        Returns:

        """

        def get_baseline():
            contact_info_response = self.conn._post_extract_contact_info(self.html,
                                                                         )

            cas = cas_from_cas_content(contact_info_response.cas_content)

            l_contact = _get_annotation_text(cas,
                                             CONTACT_PARAGRAPH_TYPE,
                                             remove_duplicate=True,
                                             strip=True)

            def clean(s):
                # Replace double newlines

                s_lines = s.splitlines()
                # Removes empty lines
                s = "\n".join(filter(lambda l: l, s_lines))

                return s

            # cleaning + sorting
            l_contact = list(sorted(map(clean, l_contact)))

            return l_contact

        with self.subTest("Sanity check: baseline contacts"):
            l_contact_baseline = get_baseline()

            self.assertLess(0, len(l_contact_baseline))

        l_contact = self.conn.get_contact_info(self.html)

        with self.subTest("Length"):
            self.assertEqual(len(l_contact_baseline), len(l_contact))

        with self.subTest("Identical content"):
            self.assertSetEqual(set(l_contact_baseline), set(l_contact), )

        # Not important for now.
        # with self.subTest("Identical order/sorting"):
        #     self.assertListEqual(l_contact_baseline, l_contact)

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
        chunk = self.conn._post_chunking(self.html,
                                         )

        self.assertTrue(chunk, "Expected something back.")
        self.assertIsInstance(chunk, ChunkModel)


class TestConnectorTermExtractionTerms(unittest.TestCase):
    def setUp(self) -> None:
        self.conn = ConnectorTermExtraction(TERM_EXTRACTION,
                                            test_connection=False)

        self.html = get_html(FILENAME_HTML)
        self.language = "en"

    def test_return(self):
        terms = self.conn._post_extract_terms(self.html,
                                              )

        self.assertTrue(terms, "Expected something back.")
        self.assertIsInstance(terms, TermsModel)

    def test_get_terms(self):
        """
        Test that you get a list of terms within a webpage

        Returns:

        """

        l_terms = self.conn.get_terms(self.html,
                                      self.language)

        with self.subTest("Type"):
            self.assertIsInstance(l_terms, list)

        with self.subTest("Non-empty"):
            self.assertTrue(len(l_terms), "Should be non-empty")

        with self.subTest("List of strings"):
            for s in l_terms:
                self.assertIsInstance(s, str)


class TestConnectorTermExtractionQuestionsAnswers(unittest.TestCase):
    def setUp(self) -> None:
        self.conn = ConnectorTermExtraction(TERM_EXTRACTION,
                                            test_connection=False)

        self.html = get_html(FILENAME_HTML)

    def test_return(self):
        qa = self.conn._post_extract_questions_answers(self.html,
                                                       )

        self.assertTrue(qa, "Expected something back.")
        self.assertIsInstance(qa, QuestionAnswersModel)


class TestConnectorTermExtractionText(unittest.TestCase):
    """
    For some files, the returned text within the CAS is lackluster.
    Within these tests, this content is tested to be equal between the different requests.
    """

    def setUp(self) -> None:
        self.conn = ConnectorTermExtraction(TERM_EXTRACTION,
                                            test_connection=False)

        self.html = get_html(FILENAME_HTML)

        self.filename_cas = os.path.join(os.path.dirname(__file__), "cas_contact_info_example.xml")

    def test_(self):
        # Text from
        chunk = self.conn._post_chunking(self.html)
        text_chunking = chunk.text

        # Text from TIKA parsing
        contact_info = self.conn._post_extract_contact_info(self.html)
        text_contact_info = contact_info.text

        def clean_text_concat(s: str) -> str:
            lines = [line.strip() for line in s.splitlines()]
            concat = " ".join(lines)

            concat_clean = re.sub('\s+', ' ', concat)
            # concat_clean = concat.replace("  "," ") # Remove double spaces

            return concat_clean

        self.assertIn(clean_text_concat(text_chunking),
                      clean_text_concat(text_contact_info))

    def test_get_paragraphs(self, update_file=False):
        if update_file:
            # Run contact info extraction from connector and export to xml.
            contact_info = self.conn._post_extract_contact_info(self.html)
            cas_wrapper = CasWrapper.from_cas_content(contact_info.cas_content)
            cas_wrapper.to_xmi(self.filename_cas)

        cas_wrapper_contact_info = CasWrapper.from_xmi(self.filename_cas)

        with self.subTest("contact paragraphs"):
            l_par__contact_info = cas_wrapper_contact_info.get_paragraphs()
            self.assertEqual(141, len(l_par__contact_info))

        with self.subTest("contact paragraphs"):
            l_contact_par__contact_info = cas_wrapper_contact_info.get_contact_paragraph()
            self.assertEqual(7, len(l_contact_par__contact_info))

        with self.subTest("get_sentences"):
            l_sentence = cas_wrapper_contact_info.get_sentences()

        with self.subTest("Number of elements"):
            self.assertGreaterEqual(len(l_sentence), len(l_par__contact_info))
            self.assertGreaterEqual(len(l_par__contact_info), len(l_contact_par__contact_info))

        # TODO check if text is covered by all the paragraphs
        print(l_par__contact_info)
        # This is indeed all the text within the HTML
        print(cas_wrapper_contact_info.get_all_text())
        # More for debugging


class TestConnectorContactInfoClassification(unittest.TestCase):
    s_email = "This is an email@host.com"

    label_email = "EMAIL"

    def test_connect(self):

        try:
            with self.assertWarns(ConnectionWarning) as cm:

                ConnectorContactInfoClassification(CONTACT_CLASSIFICATION,
                                                   test_connection=True)

        except AssertionError as e:
            # Great! We were able to connect to the API.
            pass
        else:
            self.fail(f"Should not raised a warning.\n{cm.warning}")

    def test_classify_contact_type(self):
        conn = ConnectorContactInfoClassification(CONTACT_CLASSIFICATION)
        label = conn._post_classify_contact_type(self.s_email)

        self.assertIsInstance(label, Label)
        self.assertEqual(self.label_email, label.name)

    def test_labels(self):
        conn = ConnectorContactInfoClassification(CONTACT_CLASSIFICATION)
        labels = conn._get_classify_contact_type_labels()

        self.assertIn(self.label_email, labels)

    def test_classify_email(self):
        conn = ConnectorContactInfoClassification(CONTACT_CLASSIFICATION)
        b = conn._post_classify_contact_type_email(self.s_email)

        self.assertEqual(True, b)
