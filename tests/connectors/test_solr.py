import csv
import unittest

from connectors.solr import SOLRConnector


class TestSOLR(unittest.TestCase):
    def setUp(self) -> None:
        self.connector = SOLRConnector()

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

    def test_sum(self,
                 debug=True,
                 hard_check=False):
        """

        Args:
            debug:
                Flag to print
            hard_check:
                As long as not all webpages are scraped,
                we expect the sum to be smaller or equal to the unfiltered results.

        Returns:

        """

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

                f_assert = self.assertEqual if hard_check else self.assertGreaterEqual

                f_assert(n_tot, n_acc + n_not_acc, f"{n_tot} != {n_acc} + {n_not_acc}")


class TestWebsiteInfo(unittest.TestCase):

    def setUp(self) -> None:
        self.connector = SOLRConnector()

    def test_get_different_websites(self, debug=True):
        websites = self.connector.get_different_websites()

        if debug:
            print(f"Municipality info: {websites}")

            b = 0
            if b:
                # Write to CSV
                with open('solr_websites.csv', "w") as f:
                    writer = csv.writer(f)

                    writer.writerow(["municipality", "number"])

                    for k in sorted(websites):
                        v = websites.get(k)

                        _k = k.capitalize()

                        writer.writerow([_k, v])

        with self.subTest("Type"):
            self.assertIsInstance(websites, dict)

        with self.subTest("Type key"):
            for code in websites.keys():
                self.assertIsInstance(code, str)

        with self.subTest("Type value"):
            for n in websites.values():
                self.assertIsInstance(n, int)
