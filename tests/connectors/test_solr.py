import unittest

from connectors.solr import SOLRConnector


class TestSOLR(unittest.TestCase):
    def setUp(self) -> None:
        self.connector = SOLRConnector()

    def test_random(self):
        html = self.connector.random_query()

        self.assertTrue(html)

    def test_get_accepted(self):
        l = self.connector._get_accepted()

        self.assertEqual(10, len(l), "Default length items")


class TestLanguageInfo(unittest.TestCase):
    def setUp(self) -> None:
        self.connector = SOLRConnector()

    def test_get_different_languages(self, debug=True):
        lang = self.connector.get_different_languages()

        if debug:
            print(f"Lang info: {lang}")

        with self.subTest("Type"):
            self.assertIsInstance(lang, dict)

        with self.subTest("Type key"):
            for code in lang.keys():
                self.assertIsInstance(code, str)

        with self.subTest("Type value"):
            for n in lang.values():
                self.assertIsInstance(n, int)

        with self.subTest("Numbers"):
            for n in lang.values():
                self.assertGreater(n, 0)

        with self.subTest("Dutch"):
            self.assertIn("nl", lang, "Expected at least nl within the keys.")

    def test_get_accepted_languages(self, debug=True):
        lang = self.connector.get_different_languages(acceptance_state=True)

        if debug:
            print(f"Lang info: {lang}")

    def test_get_not_accepted_languages(self, debug=True):
        lang = self.connector.get_different_languages(acceptance_state=False)

        if debug:
            print(f"Lang info: {lang}")

    def test_sum(self, debug=True):

        lang_tot = self.connector.get_different_languages(acceptance_state=None)
        lang_acc = self.connector.get_different_languages(acceptance_state=True)
        lang_not_acc = self.connector.get_different_languages(acceptance_state=False)

        # Summary:
        if debug:
            print("lang\ttot\tacc\trej")
            print("-------------------")
        for key in lang_tot:
            n_tot = lang_tot.get(key, 0)
            n_acc = lang_acc.get(key, 0)
            n_not_acc = lang_not_acc.get(key, 0)

            if debug:
                print(f"{key}\t{n_tot}\t{n_acc}\t{n_not_acc}")

            with self.subTest(f"{key}"):
                self.assertEqual(n_tot, n_acc + n_not_acc, f"{n_tot} != {n_acc} + {n_not_acc}")
