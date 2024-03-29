"""
We could not just use the same hyperparameters as copied from an other project.
Here we will try a couple of different parameters to see what works best/gives acceptable results.
"""
import os
import unittest

import datasets.arrow_dataset
import numpy as np
from datasets import load_dataset, load_from_disk
from sklearn.metrics import confusion_matrix

from BERT_classifier.bert_based_classifier.trainer_bert_sequence_classifier import TrainerBertSequenceClassifier
from BERT_classifier.train_bert import main_with_args

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
    "save_model_each": 1,
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

            non_zero = False
            for label in labels:
                if any(label):
                    non_zero = True

            self.assertTrue(non_zero, f"Expect at least one non-zero item: {labels}")

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

    # def test_prediction(self):
    #
    #     DIR_MODELS = "../DATA/results/results_TESTING"
    #
    #     MODEL_UNDERTRAINED = os.path.join(DIR_MODELS,
    #                                       "epoch_0_Thu_Mar_17_124553_2022_2e7b6968a5f011ec8bd10242ac1a0002")
    #     MODEL_OK_ISH = os.path.join(DIR_MODELS, "epoch_5_Thu_Mar_17_125311_2022_33a7f6f8a5f111ec8bd10242ac1a0002")
    #     MODEL_OVERTRAINED = os.path.join(DIR_MODELS,
    #                                      "epoch_35_Thu_Mar_17_125533_2022_8861ebeaa5f111ec8bd10242ac1a0002")
    #
    #     OUTPUT_DIR = os.path.join(DIR_MODELS, "prediction")
    #
    #     with self.subTest("Sanity check, folder exists"):
    #         for folder in [MODEL_UNDERTRAINED, MODEL_OK_ISH, MODEL_OVERTRAINED]:
    #             self.assertTrue(os.path.exists(folder))
    #
    #     filename_data_train = "../DATA/cpsv_ap_relations/train.jsonl"
    #     filename_data_valid = "../DATA/cpsv_ap_relations/validation.jsonl"
    #
    #     dataset_train = load_dataset('json', data_files=filename_data_train, split='train')
    #     dataset_valid = load_dataset('json', data_files=filename_data_valid, split='train')
    #
    #     # Overtrained, training data should give perfect results.
    #     model_dir = MODEL_OVERTRAINED
    #     trainer_bert_sequence_classifier = TrainerBertSequenceClassifier(model_dir, None,
    #                                                                      OUTPUT_DIR  # os.path.dirname(output_file)
    #                                                                      )
    #
    #     def evaluate_exact_match_acc(
    #             trainer_bert_sequence_classifier: bert_based_classifier.trainer_bert_sequence_classifier.TrainerBertSequenceClassifier,
    #             dataset: datasets.arrow_dataset.Dataset):
    #
    #         preds_labels, preds_proba = trainer_bert_sequence_classifier.predict(documents=dataset['text'],
    #                                                                              batch_size=4, gpu=0)
    #
    #         d_name_label: dict = trainer_bert_sequence_classifier.model.config.eurovoc_concept_2_id
    #
    #         l_pred_names = []
    #
    #         for pred in preds_labels:
    #
    #             l_names = []
    #
    #             for i, b in enumerate(pred):
    #                 if b:
    #                     for k_name, v_label in d_name_label.items():
    #                         if v_label == i:
    #                             l_names.append(k_name)
    #
    #             l_pred_names.append(l_names)
    #
    #         T = 0
    #         N = 0
    #         for pred_label, true_label in zip(l_pred_names, dataset["labels"]):
    #
    #             if set(pred_label) == set(true_label):
    #                 T += 1
    #             else:
    #                 N += 1
    #
    #         acc_exact = T / (T + N)
    #
    #         # Confusion matrix for every label
    #         for name_label, i_label in d_name_label.items():
    #             true_label_i = np.array([(name_label in item_labels) for item_labels in dataset["labels"]], dtype=int)
    #             pred_label_i = preds_labels[:, i_label]
    #
    #             conf = confusion_matrix(true_label_i,
    #                                     pred_label_i,
    #                                     labels=[0, 1])
    #
    #             print(f"conf matrix [{name_label}]:\n{conf}")
    #
    #         return acc_exact
    #
    #     print(" -- TRAINING DATA -- ")
    #     acc_exact_train = evaluate_exact_match_acc(trainer_bert_sequence_classifier,
    #                                                dataset_train)
    #     print(f"Training accuracy exact match: {acc_exact_train:.1%}")
    #
    #     print(" -- VALIDATION DATA -- ")
    #     acc_exact_valid = evaluate_exact_match_acc(trainer_bert_sequence_classifier,
    #                                                dataset_valid)
    #     print(f"Validation accuracy exact match: {acc_exact_valid:.1%}")
    #
    #     return


class TestPrediction(unittest.TestCase):

    def setUp(self) -> None:
        self.DIR_MODELS = os.path.join(os.path.dirname(__file__),
                                       "../DATA/results/results_distilbert_base_uncased_1epoch_warmup_cpsv_ap_relations")

    def test_prediction_undertrained(self):

        MODEL_UNDERTRAINED = os.path.join(self.DIR_MODELS,
                                          "epoch_1_Fri_Mar_18_151957_2022_dedc115ca6ce11ec928e0242ac1a0002")

        self._test_predict_xyz(MODEL_UNDERTRAINED)

    def test_prediction_ok_ish(self):

        MODEL_OK_ISH = os.path.join(self.DIR_MODELS,
                                    "epoch_20_Fri_Mar_18_154007_2022_afe9fe06a6d111ec928e0242ac1a0002")

        self._test_predict_xyz(MODEL_OK_ISH)

    def test_prediction_overtrained(self):

        MODEL_OVERTRAINED = os.path.join(self.DIR_MODELS,
                                         "epoch_35_Fri_Mar_18_155412_2022_a7ab227ca6d311ec928e0242ac1a0002")

        self._test_predict_xyz(MODEL_OVERTRAINED)

    def _test_predict_xyz(self, model_path):
        DIR_DATA = os.path.join(os.path.dirname(__file__), "../../../data/relation_extraction")

        filename_data_train = os.path.join(DIR_DATA, "train.jsonl")
        filename_data_valid = os.path.join(DIR_DATA, "validation.jsonl")

        OUTPUT_DIR = os.path.join(self.DIR_MODELS, "prediction")

        with self.subTest("Sanity check, folder exists"):
            for filename in [model_path,
                             filename_data_train,
                             filename_data_valid,
                             ]:
                self.assertTrue(os.path.exists(filename))

        dataset_train = load_dataset('json', data_files=filename_data_train, split='train')
        dataset_valid = load_dataset('json', data_files=filename_data_valid, split='train')

        trainer_bert_sequence_classifier = TrainerBertSequenceClassifier(model_path,
                                                                         None,
                                                                         OUTPUT_DIR  # os.path.dirname(output_file)
                                                                         )

        print(" -- TRAINING DATA -- ")
        acc_exact_train = self._evaluate_exact_match_acc(trainer_bert_sequence_classifier,
                                                         dataset_train)
        print(f"Training accuracy exact match: {acc_exact_train:.1%}")

        print(" -- VALIDATION DATA -- ")
        acc_exact_valid = self._evaluate_exact_match_acc(trainer_bert_sequence_classifier,
                                                         dataset_valid)
        print(f"Validation accuracy exact match: {acc_exact_valid:.1%}")

        return

    def _evaluate_exact_match_acc(self,
                                  trainer_bert_sequence_classifier: TrainerBertSequenceClassifier,
                                  dataset: datasets.arrow_dataset.Dataset,
                                  KEY_LABEL="name_labels"):

        preds_labels, preds_proba = trainer_bert_sequence_classifier.predict(documents=dataset['text'],
                                                                             batch_size=4, gpu=0)

        d_name_label: dict = trainer_bert_sequence_classifier.model.config.eurovoc_concept_2_id

        l_pred_names = []

        for pred in preds_labels:

            l_names = []

            for i, b in enumerate(pred):
                if b:
                    for k_name, v_label in d_name_label.items():
                        if v_label == i:
                            l_names.append(k_name)

            l_pred_names.append(l_names)

        T = 0
        N = 0
        for pred_label, true_label in zip(l_pred_names, dataset[KEY_LABEL]):

            if set(pred_label) == set(true_label):
                T += 1
            else:
                N += 1

        acc_exact = T / (T + N)

        # Confusion matrix for every label
        for name_label, i_label in d_name_label.items():
            true_label_i = np.array([(name_label in item_labels) for item_labels in dataset[KEY_LABEL]], dtype=int)
            pred_label_i = preds_labels[:, i_label]

            conf = confusion_matrix(true_label_i,
                                    pred_label_i,
                                    labels=[0, 1])

            print(f"conf matrix [{name_label}]:\n{conf}")

        return acc_exact
