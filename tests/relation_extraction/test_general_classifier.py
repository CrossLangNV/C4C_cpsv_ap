import os.path
import unittest

from relation_extraction.general_classifier import Dataset, GeneralClassifier

FILENAME_DATA = os.path.join(os.path.dirname(__file__), "headers_training.csv")


class TestDataset(unittest.TestCase):
    def setUp(self) -> None:
        self.dataset = Dataset()

    def test_init(self):
        # Check that you can get something
        self.assertTrue(self.dataset.df_all)

    def test_generate_data(self):

        df_all = self.dataset.generate(FILENAME_DATA)

        self.assertGreaterEqual(len(df_all), 1)

        with self.subTest("Size 18/03"):
            self.assertEqual(668, len(df_all))

    def test_load(self):

        df_all = self.dataset.load(FILENAME_DATA)

        self.assertGreaterEqual(len(df_all), 1)

    def test_get_english_training_data(self):
        self.dataset.load(FILENAME_DATA)

        data = self.dataset.get_english_training_data()

        l_title = data[self.dataset.KEY_TEXT].tolist()
        l_b_crit_req = data[self.dataset.KEY_CRIT_REQ].tolist()

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


class TestBERTTrainData(unittest.TestCase):
    def setUp(self) -> None:
        self.dataset = Dataset()
        self.df_all = self.dataset.load(FILENAME_DATA)

    def test_export(self):
        DIR_DATA_REL = os.path.join(os.path.dirname(__file__), "../../data/relation_extraction")
        self.assertTrue(os.path.exists(DIR_DATA_REL))

        self.dataset.export_BERT_train_data(lang="EN",
                                            filename_train=os.path.join(DIR_DATA_REL, "train.jsonl"),
                                            filename_valid=os.path.join(DIR_DATA_REL, "validation.jsonl"),
                                            )


class TestGeneralClassifier(unittest.TestCase):

    def test_train(self,
                   deprecated=True,
                   generate_file: bool = False):

        # Deprecated
        if deprecated:
            return

        filename_train = os.path.join(os.path.dirname(__file__), "crit_req.train")
        filename_valid = os.path.join(os.path.dirname(__file__), "crit_req.valid")

        if generate_file:

            dataset = Dataset()
            dataset.load(FILENAME_DATA)
            data = dataset.get_english_training_data()

            p_train = .6
            p_valid = 1 - p_train

            # Cleanse
            with open(filename_train, 'w+') as f:
                f.truncate(0)
            with open(filename_valid, 'w+') as f:
                f.truncate(0)

            for i, (_, row) in enumerate(data.iterrows()):

                line = ""
                # Add labels
                if row.criterion_requirement:
                    line += f"__label__{'crit_req'} "
                else:
                    # Only when no label is found
                    line += f"__label__NONE "

                line += f"{row.title}\n"

                if i / len(data) <= p_train:
                    with open(filename_train, "a") as f:
                        f.write(line)
                else:
                    with open(filename_valid, "a") as f:
                        f.write(line)

        classifier = GeneralClassifier(filename_train,
                                       filename_valid)

        self.assertEqual(0, 1, "TODO")
