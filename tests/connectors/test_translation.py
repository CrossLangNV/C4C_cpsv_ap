"""
Swagger at https://mtapi.occam.crosslang.com/swagger-ui.html
"""

import os
import random
import signal
import string
import tempfile
import time
import unittest
import warnings

from connectors.translation import ETranslationConnector

CEF_LOGIN = os.environ.get("CEF_LOGIN")
CEF_PASSW = os.environ.get("CEF_PASSW")

ROOT_MEDIA = os.path.join(os.path.dirname(__file__))
FILENAME_TXT = os.path.join(ROOT_MEDIA,
                            'EXAMPLE_TEXT.txt')

for filename in [FILENAME_TXT]:
    if not os.path.exists(filename):
        warnings.warn(f'Sanity check. Could not find {filename}', UserWarning)


class TestTimeout(Exception):
    pass


class test_timeout:
    """
    To timeout methods if taking too long
    """

    def __init__(self, seconds, error_message=None):
        if error_message is None:
            error_message = 'test timed out after {}s.'.format(seconds)
        self.seconds = seconds
        self.error_message = error_message

    def handle_timeout(self, signum, frame):
        raise TestTimeout(self.error_message)

    def __enter__(self):
        signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.alarm(self.seconds)

    def __exit__(self, exc_type, exc_val, exc_tb):
        signal.alarm(0)


class TestETranslationConnector(unittest.TestCase):

    def setUp(self) -> None:
        self.connector = ETranslationConnector(username=CEF_LOGIN,
                                               password=CEF_PASSW)

    def test_info(self):

        r = self.connector._get(self.connector.url_info)
        with self.subTest('Status code'):
            self.assertLess(r.status_code, 300, r.content)

        j = self.connector.info()

        with self.subTest('Non-empty'):
            self.assertTrue(j)

        with self.subTest('Password'):
            self.assertEqual('***', j.get("etranslation_password"), 'Password should not be publically visible!')

        return

    def test_docs(self):
        r = self.connector._get(self.connector.url_info)

        self.assertTrue(r.ok, r.content)

    def test_trans_snippet(self):

        source = 'fr'
        target = 'en'
        snippet = 'This is a test sentence.'

        request_id = self.connector.trans_snippet(source, target, snippet)

        self.assertIsInstance(request_id, str)

        return request_id

    def test_trans_snippet_id(self,
                              t_max=60  # Seconds
                              ):

        with self.subTest("Sanity check: Generate ID"):
            i = self.test_trans_snippet()

        # Try for x time:
        t0 = time.time()

        while time.time() <= t0 + t_max:
            snippet_trans = self.connector.trans_snippet_id(i)
            if snippet_trans is not None:
                break

        self.assertIsNotNone(snippet_trans, 'Should be non-empty')

        return

    def test_trans_snippet_and_result(self):

        source = 'fr'
        target = 'en'
        # snippet = 'This is a test sentence.'
        # snippet =
        snippet = random_text_generator(15)

        request_id = self.connector.trans_snippet(source, target, snippet)

        t0 = time.time()
        delta_t_max = 10  # in seconds
        i = 0
        while True:

            r = self.connector.trans_snippet_id(request_id)
            i += 1
            if r is not None:
                break

            if time.time() - t0 > delta_t_max:
                # Took too long
                break

        t1 = time.time()
        print(f"Took {t1 - t0} before translation finished.")
        print(f"#Requests = {i}.")

        # r = self.connector.trans_snippet_id(request_id)

        self.assertIsNotNone(r, 'Should be non-empty')

        with self.subTest('Type'):
            self.assertIsInstance(r, str, f'Should contain translated text of "{snippet}"')

    def test_trans_snippet_blocking(self):

        source = 'fr'
        target = 'en'
        snippet = 'This is a test sentence.'

        t0 = time.time()
        snippet_trans = self.connector.trans_snippet_blocking(source, target, snippet)
        t1 = time.time()
        print(f"Took {t1 - t0} before translation finished.")

        self.assertIsInstance(snippet_trans, str)

        return

    def test_is_there_a_TM(self):

        source = 'fr'
        target = 'en'

        snippet = random_text_generator(5000)

        t0 = time.time()
        snippet_trans = self.connector.trans_snippet_blocking(source, target, snippet)
        t1 = time.time()

        print(f"Took {t1 - t0:.2f} s before translation finished.")

        t0 = time.time()
        snippet_trans = self.connector.trans_snippet_blocking(source, target, snippet)
        t1 = time.time()

        print(f"Took {t1 - t0:.2f} s before translation finished.")

        t0 = time.time()
        snippet_trans = self.connector.trans_snippet_blocking(source, target, snippet)
        t1 = time.time()

        print(f"Took {t1 - t0:.2f} s before translation finished.")

    def test_trans_doc(self):

        source = 'fr'
        target = 'en'

        request_id = self.connector.trans_doc(source, target, FILENAME_TXT)

        self.assertIsInstance(request_id, str)

        return request_id

    def test_trans_doc_id(self):

        with self.subTest("Sanity check: Generate ID"):
            i = self.test_trans_doc()

        # Try for x time:
        t0 = time.time()
        t_max = 60  # Seconds
        while time.time() <= t0 + t_max:
            r = self.connector.trans_doc_id(i)
            if r is not None:
                break

        self.assertIsNotNone(r, 'Should be non-empty')

        filename = r.get('filename')

        with tempfile.TemporaryDirectory() as tmp:
            path_filename = os.path.join(tmp, filename)

            with open(path_filename, 'wb') as f:
                f.write(r.get('content'))

            print(f'File temporarily saved to {path_filename}')

            with open(path_filename) as f:
                txt = f.readlines()

        return

    def test_trans_doc_blocking(self):

        source = 'fr'
        target = 'en'

        with open(FILENAME_TXT) as f:
            txt_orig = f.readlines()

        r = self.connector.trans_doc_blocking(source, target, FILENAME_TXT)

        self.assertIsNotNone(r, 'Should be non-empty')

        filename = r.get('filename')

        with tempfile.TemporaryDirectory() as tmp:
            tmp_filename = os.path.join(tmp, filename)

            with open(tmp_filename, 'wb') as f:
                f.write(r.get('content'))

            print(f'File temporarily saved to {tmp_filename}')

            with open(tmp_filename) as f:
                txt_trans = f.readlines()

        len(txt_trans)

        self.assertEqual(len(txt_orig), len(txt_trans),
                         "After translation, amount of text lines should stay the same as it's translated per line.")

        return


def random_text_generator(n: int):
    return "".join([random.choice(string.ascii_letters[:26] + ' ' * 10) for i in range(n)])


if __name__ == '__main__':
    unittest.main()
