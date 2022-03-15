import os
import unittest
from configparser import ConfigParser

from datasets import load_dataset

from bert_based_classifier.trainer_bert_sequence_classifier import TrainerBertSequenceClassifier


class MyTestCase(unittest.TestCase):
    def test_something(self):
        classifier = TrainerBertSequenceClassifier()

        self.assertEqual(True, False)  # add assertion here

    def test_predict(self):
        FILENAME_PREDICT_CONFIG = os.path.join(os.path.dirname(__file__), "../configuration_files_bert",
                                               "predict.config")

        DIRNAME_DATA = os.path.join(os.path.dirname(__file__), "../DATA")

        output_file = os.path.join(DIRNAME_DATA,
                                   "cpsv_ap_relations/test_predict_distilbert_base_uncased_1epoch_warmup_cpsv_ap_relations.jsonl")
        model_dir = os.path.join(DIRNAME_DATA,
                                 "results/results_distilbert_base_uncased_1epoch_warmup_cpsv_ap_relations/epoch_35_Tue_Mar_15_112514_2022_95d7d708a45211ecb0400242ac1a0002")
        input_file = os.path.join(DIRNAME_DATA, "cpsv_ap_relations/validation.jsonl")

        with self.subTest("Sanity check - Read files"):
            for filename in [FILENAME_PREDICT_CONFIG,
                             output_file,
                             model_dir,
                             input_file]:
                self.assertTrue(os.path.exists(filename), filename)

        config = ConfigParser()
        config.read(FILENAME_PREDICT_CONFIG)

        key_labels = config['INPUT/OUTPUT']['LABELS']

        batch_size = config.getint('MODEL_INFERENCE_CONFIGURATIONS', 'BATCH_SIZE')
        gpu = config.getint('MODEL_INFERENCE_CONFIGURATIONS', 'GPU')
        top_n = config.getint('MODEL_INFERENCE_CONFIGURATIONS', 'TOP_N')

        trainer_bert_sequence_classifier = TrainerBertSequenceClassifier(model_dir, None, os.path.dirname(output_file))

        dataset_test = load_dataset('json', data_files=input_file, split='train')

        preds_labels, preds_proba = trainer_bert_sequence_classifier.predict(documents=dataset_test['text'],
                                                                             batch_size=batch_size, gpu=gpu)

        for a, b in zip(dataset_test, preds_proba):
            print(f"{a['text']}: GT = {a[key_labels]} ; pred = {b}")


if __name__ == '__main__':
    unittest.main()
