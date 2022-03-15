import argparse
import os
import uuid
import warnings
from configparser import ConfigParser
from datetime import datetime
from pathlib import Path
from typing import Dict, Union

import numpy as np
from datasets import load_dataset

from bert_based_classifier.trainer_bert_sequence_classifier import TrainerBertSequenceClassifier
from utils.metrics import calculate_micro_f1_score, mean_rprecision, ndcg_at_k, precision_at_k


def main(path_to_config: Union[str, Path]):
    '''
    Evaluation given a Bert model fine tuned for sequence classification.
    '''

    config = ConfigParser()
    config.read(path_to_config)

    output_dir = config['INPUT/OUTPUT']['OUTPUT_DIR']
    model_dir = config['INPUT/OUTPUT']['MODEL_DIR']
    input_file = config['INPUT/OUTPUT']['INPUT_FILE']
    key_labels = config['INPUT/OUTPUT']['LABELS']

    batch_size = config.getint('MODEL_INFERENCE_CONFIGURATIONS', 'BATCH_SIZE')
    gpu = config.getint('MODEL_INFERENCE_CONFIGURATIONS', 'GPU')

    # make output_dir where evaluation results will be saved
    os.makedirs(output_dir, exist_ok=True)

    # initialize a trained bert sequence classifier (fine tuned on classification task)
    trainer_bert_sequence_classifier = TrainerBertSequenceClassifier(model_dir, None, output_dir)

    dataset_test = load_dataset('json', data_files=input_file, split='train')

    # Get the predicted labels:
    preds_labels, preds_proba = trainer_bert_sequence_classifier.predict(documents=dataset_test['text'],
                                                                         batch_size=batch_size, gpu=gpu)

    # Get the eurovoc_concepts (eurovoc id's) in the test set:
    test_labels = dataset_test[key_labels]
    test_labels = [item for sublist in test_labels for item in sublist]
    test_labels = list(set(test_labels))

    train_labels = trainer_bert_sequence_classifier.model.config.eurovoc_concept_2_id.keys()
    eurovoc_concept_2_id_extended = trainer_bert_sequence_classifier.model.config.eurovoc_concept_2_id.copy()
    index = len(train_labels)
    for label in test_labels:
        if label not in train_labels:
            eurovoc_concept_2_id_extended[label] = index
            index = index + 1

    def _one_hot_encoding(item: Dict,
                          key_one_hot="one_hot") -> Dict:

        '''
        One hot encoding with the extended (test_labels+train_labels) list of eurovoc concepts.
        '''

        if key_one_hot in item:
            warnings.warn(f"item did already contain key: {key_one_hot} in {item}")

        item[key_one_hot] = []

        item[key_one_hot] = [0] * len(eurovoc_concept_2_id_extended.keys())
        for label in item[key_labels]:
            item[key_one_hot][eurovoc_concept_2_id_extended[label]] = 1

        return item

    key_one_hot = "one_hot"
    dataset_test_one_hot = dataset_test.map(lambda x: _one_hot_encoding(x, key_one_hot))

    true_labels = dataset_test_one_hot[key_one_hot]
    true_labels = np.array(true_labels)

    # Additional_columns_length are the labels the model (labels in test set, but not in train set) was not trained on (and will thus not predict), for a fair evaluation, we have to include them in our evaluation.
    additional_columns_length = len(true_labels[0]) - len(
        trainer_bert_sequence_classifier.model.config.eurovoc_concept_2_id.keys())

    # We assign probability zero to the labels that are in test set, but not in train set
    preds_proba_concat = np.concatenate([preds_proba, np.zeros((preds_proba.shape[0], additional_columns_length))],
                                        axis=1)

    # write to scores file in output_dir
    today = "_".join(datetime.now().ctime().split())
    scores_file_name = f"{today}_{uuid.uuid1().hex}"

    results_file = os.path.join(output_dir, scores_file_name)
    with open(results_file, "w") as f:

        f.write(f"Results on test set {os.path.abspath(input_file)} for model: {os.path.abspath(model_dir)}\n")

        threshold = trainer_bert_sequence_classifier.model.config.threshold
        f1_score = calculate_micro_f1_score(true_labels, preds_proba_concat, threshold=threshold)

        f.write(f"Micro f1 score at threshold {threshold} is: {f1_score}\n")

        for k in [1, 3, 5, 10]:
            try:
                precision_at_k_score = precision_at_k(true_labels, preds_proba_concat, k)

                f.write(f"ranking precision at k={k}: {precision_at_k_score}\n")
            except:
                break

        for k in [1, 3, 5, 10]:
            try:
                ndcg_at_k_score = ndcg_at_k(true_labels, preds_proba_concat, k)
                f.write(f"nDCG at k={k}: {ndcg_at_k_score}\n")
            except:
                break

        try:
            mrp, _ = mean_rprecision(true_labels, preds_proba_concat)

            f.write(f"mrp is: {mrp}\n")
        except:
            pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--config_path", dest="config_path",
                        help="path to the config file", required=True)

    args = parser.parse_args()

    main(args.config_path)
