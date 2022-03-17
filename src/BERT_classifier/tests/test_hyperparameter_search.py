"""
We could not just use the same hyperparameters as copied from an other project.
Here we will try a couple of different parameters to see what works best/gives acceptable results.
"""
import os
import unittest

from datasets import load_from_disk

from train_bert import main_with_args

FILENAME_TRAIN_CONFIG = os.path.join(os.path.dirname(__file__), "configuration_files_bert",
                                     "train.config")

DEFAULT_ARGS = {
    "preprocessed_data_dir": "../DATA/preprocessed_distilbert_base_uncased_cpsv_ap_relations",
    "output_dir": "../DATA/results/results_TESTING",
    "model_name_or_path": "distilbert-base-uncased",
    "batch_size": 4,
    "epochs": 36,
    "initial_lr": 5e-5,
    "warm_up": True,
    "gpu": 0,
    "save_model_each": 5,
}


class TestTrain(unittest.TestCase):

    def test_data_train(self):
        filename_train = "../DATA/preprocessed_distilbert_base_uncased_cpsv_ap_relations"
        _dataset = load_from_disk(filename_train)

        # SHould find some non-zero/one hot encodig in here.
        labels = _dataset["train"]["labels"]
        with self.subTest("number of labels"):
            self.assertGreaterEqual(len(labels), 1)

        with self.subTest("At least one label per item"):
            for label in labels:
                self.assertTrue(any(label), label)

    def test_data_valid(self):
        filename_train = "../DATA/preprocessed_distilbert_base_uncased_cpsv_ap_relations"
        _dataset = load_from_disk(filename_train)

        # SHould find some non-zero/one hot encodig in here.
        labels = _dataset["validation"]["labels"]
        with self.subTest("number of labels"):
            self.assertGreaterEqual(len(labels), 1)

        with self.subTest("At least one label per item"):
            for label in labels:
                self.assertTrue(any(label), label)

    def test_train_script(self):
        # main(FILENAME_TRAIN_CONFIG)
        main_with_args(**DEFAULT_ARGS,
                       )

        self.assertEqual(0, 1)
