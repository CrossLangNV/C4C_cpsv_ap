import glob
import json
import os
import re
import unittest
from configparser import ConfigParser

from datasets import load_dataset

from bert_based_classifier.trainer_bert_sequence_classifier import TrainerBertSequenceClassifier

DIRNAME_DATA = os.path.join(os.path.dirname(__file__), "../DATA")
class MyTestCase(unittest.TestCase):
    def test_create_dataset(self):

        # Read current training + valid data.
        # Save to new format.

        filename_fasttext_train = os.path.join(os.path.dirname(__file__), "../DATA/cpsv_ap_relations/crit_req.train")
        filename_fasttext_valid = os.path.join(os.path.dirname(__file__), "../DATA/cpsv_ap_relations/crit_req.valid")

        filename_jsonl_train = os.path.join(os.path.dirname(__file__), "../DATA/cpsv_ap_relations/train.jsonl.example")
        filename_jsonl_valid = os.path.join(os.path.dirname(__file__),
                                            "../DATA/cpsv_ap_relations/validation.jsonl.example")

        self.assertTrue(os.path.exists(filename_fasttext_train))
        self.assertTrue(os.path.exists(filename_fasttext_valid))

        def generate_jsonl(filename_fasttext: str,
                           filename_jsonl_out: str):
            """
            Transform fasttext format to JSONL format according to our BERT based classifier.

            Args:
                filename_fasttext:
                filename_jsonl_out:

            Returns:

            """
            with open(filename_fasttext) as f:
                l = list(map(str.strip, f.readlines()))

            pattern_labels = r"(__label__([^ ]+))"
            pattern_text = r"(__label__([^ ]+) )+(.*)"

            l_d_json = []

            for line in l:
                labels = [label for _, label in re.findall(pattern_labels, line)]
                text = re.findall(pattern_text, line)[0][-1]

                d_json = {"labels": labels,
                          "text": text}
                l_d_json.append(d_json)

            with open(filename_jsonl_out, "w") as f:

                for d_json in l_d_json:
                    json_string = json.dumps(d_json)
                    f.write(json_string + "\n")
            return l_d_json

        generate_jsonl(filename_fasttext_train,
                       filename_jsonl_train)

        generate_jsonl(filename_fasttext_valid,
                       filename_jsonl_valid)

        return

    def test_something(self):
        classifier = TrainerBertSequenceClassifier()

        self.assertEqual(True, False)  # add assertion here

    def test_predict(self):
        FILENAME_PREDICT_CONFIG = os.path.join(os.path.dirname(__file__), "../configuration_files_bert",
                                               "predict.config")



        output_file = os.path.join(DIRNAME_DATA,
                                   "cpsv_ap_relations/test_predict_distilbert_base_uncased_1epoch_warmup_cpsv_ap_relations.jsonl")
        model_dir = os.path.join(DIRNAME_DATA,
                                 "results/results_distilbert_base_uncased_1epoch_warmup_cpsv_ap_relations/epoch_35_Tue_Mar_15_152702_2022_5d3e04cca47411ec9e850242ac1a0002")
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

    def test_evaluation(self):

        collection_models_dir = os.path.join(DIRNAME_DATA,
                                             "results/results_distilbert_base_uncased_1epoch_warmup_cpsv_ap_relations")

        input_file = os.path.join(DIRNAME_DATA, "cpsv_ap_relations/validation.jsonl")
        dataset_valid = load_dataset('json', data_files=input_file, split='train')

        BATCH_SIZE = 16
        GPU = 0

        for epoch in range(0, 36, 5):
            name = f'epoch_{epoch}_Tue_Mar_15_152432_2022_03d0f35ea47411ec9e850242ac1a0002'
            model_dir = glob.glob(collection_models_dir + f"/epoch_{epoch}_*")[0]
            # model_dir = os.path.join(collection_models_dir, name)
            output_file = os.path.join(DIRNAME_DATA,
                                       f"cpsv_ap_relations/test_predict_distilbert_base_uncased_{epoch}epoch_warmup_cpsv_ap_relations.jsonl")

            self.assertTrue(os.path.exists(model_dir))

            trainer_bert_sequence_classifier = TrainerBertSequenceClassifier(model_dir, None,
                                                                             os.path.dirname(output_file))

            preds_labels, preds_proba = trainer_bert_sequence_classifier.predict(documents=dataset_valid['text'],
                                                                                 batch_size=BATCH_SIZE, gpu=GPU)

            preds_proba

if __name__ == '__main__':
    unittest.main()
