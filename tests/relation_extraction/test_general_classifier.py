import os.path
import unittest

from relation_extraction.general_classifier import Dataset

FILENAME_DATA = os.path.join(os.path.dirname(__file__), "headers_training.csv")


class TestDataset(unittest.TestCase):
    def setUp(self) -> None:
        self.dataset = Dataset()

    def test_init(self):
        # Check that you can get something
        self.aasertTrue(self.dataset.df_all)

    def test_generate_data(self):

        df_all = self.dataset.generate(FILENAME_DATA)

        self.assertGreaterEqual(len(df_all), 1)

        with self.subTest("Size 11/03"):
            self.assertEqual(140, len(df_all))

    def test_load(self):

        df_all = self.dataset.load(FILENAME_DATA)

        self.assertGreaterEqual(len(df_all), 1)

    def test_get_english_training_data(self):
        self.dataset.load(FILENAME_DATA)

        data = self.dataset.get_english_training_data()

        l_title, l_b_crit_req = data["title"], data["criterion_requirement"]

        with self.subTest("Multiple elements"):
            self.assertGreaterEqual(len(l_title), 1)
            self.assertGreaterEqual(len(l_b_crit_req), 1)

        with self.subTest("titles type"):
            for title in l_title:
                self.assertIsInstance(title, str)

        with self.subTest("crit req type"):
            for crit_req in l_b_crit_req:
                self.assertIsInstance(crit_req, bool)

        with self.subTest("Both types"):
            self.assertIn(True, l_b_crit_req)
            self.assertIn(False, l_b_crit_req)
