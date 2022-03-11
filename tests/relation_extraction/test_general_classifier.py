import os.path
import unittest

from relation_extraction.general_classifier import Dataset

FILENAME_DATA = os.path.join(os.path.dirname(__file__), "headers_training.csv")


class TestDataset(unittest.TestCase):
    def test_init(self):
        self.assertEqual(0, 1)

    def test_generate_data(self):
        dataset = Dataset()

        df_all = dataset.generate(FILENAME_DATA)

        self.assertGreaterEqual(len(df_all), 1)

        with self.subTest("Size 11/03"):
            self.assertEqual(140, len(df_all))

    def test_load(self):
        dataset = Dataset()

        dataset.load(FILENAME_DATA)
