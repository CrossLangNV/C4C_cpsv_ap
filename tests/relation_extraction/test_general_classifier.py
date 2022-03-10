import unittest

from relation_extraction.general_classifier import Dataset


class TestDataset(unittest.TestCase):
    def test_init(self):
        self.assertEqual(0, 1)

    def test_generate_data(self):
        dataset = Dataset()

        self.assertEqual(1, dataset)
