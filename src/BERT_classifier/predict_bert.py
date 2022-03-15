import argparse
import json
import os
from configparser import ConfigParser
from pathlib import Path
from typing import Union

import numpy as np
from datasets import load_dataset

from bert_based_classifier.trainer_bert_sequence_classifier import TrainerBertSequenceClassifier


def main(path_to_config: Union[str, Path]):
    '''
    Predict Eurovoc labels given a fine tuned model for sequence classification
    '''

    config = ConfigParser()
    config.read(path_to_config)

    output_file = config['INPUT/OUTPUT']['OUTPUT_FILE']
    model_dir = config['INPUT/OUTPUT']['MODEL_DIR']
    input_file = config['INPUT/OUTPUT']['INPUT_FILE']
    # path_eurovoc_concepts=config[ 'INPUT/OUTPUT' ][ 'PATH_EUROVOC_CONCEPTS' ]
    key_labels = config['INPUT/OUTPUT']['LABELS']

    batch_size = config.getint('MODEL_INFERENCE_CONFIGURATIONS', 'BATCH_SIZE')
    gpu = config.getint('MODEL_INFERENCE_CONFIGURATIONS', 'GPU')
    top_n = config.getint('MODEL_INFERENCE_CONFIGURATIONS', 'TOP_N')

    # make output_dir where evaluation results will be saved
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # initialize a trained bert sequence classifier (fine tuned on classification task)
    trainer_bert_sequence_classifier = TrainerBertSequenceClassifier(model_dir, None, os.path.dirname(output_file))

    dataset_test = load_dataset('json', data_files=input_file, split='train')

    preds_labels, preds_proba = trainer_bert_sequence_classifier.predict(documents=dataset_test['text'],
                                                                         batch_size=batch_size, gpu=gpu)

    id_2_eurovoc_concept = [''] * len(trainer_bert_sequence_classifier.model.config.eurovoc_concept_2_id)

    for key, value in trainer_bert_sequence_classifier.model.config.eurovoc_concept_2_id.items():
        id_2_eurovoc_concept[value] = key

    # top_n=10
    best_n_labels = np.argsort(preds_proba)[:, -top_n:]  # we take best 10 via argsort

    # take the top 10 predicted eurovoc concepts:
    pred_eurovoc_concept = []
    for row in best_n_labels:
        row_pred_eurovoc_concept = []
        for item in row:
            row_pred_eurovoc_concept.append(id_2_eurovoc_concept[item])
        # because sorted from small to large prob, still need to reverse
        row_pred_eurovoc_concept.reverse()
        pred_eurovoc_concept.append(row_pred_eurovoc_concept)

    # eurovoc_concepts=load_dataset(  'json', data_files= path_eurovoc_concepts, split='train' )

    # convert predicted descriptors to their labels:
    # eurovoc_concepts_ids=eurovoc_concepts['id']
    pred_eurovoc_concept_title = []
    for row in pred_eurovoc_concept:
        row_pred_eurovoc_concept_title = []
        for item in row:
            # try:
            #     row_pred_eurovoc_concept_title.append( eurovoc_concepts[ eurovoc_concepts_ids.index( item )][ 'title' ] )
            # except:
            #     print( f"Eurovoc descriptor {item} not found in provided jsonl" )
            #     row_pred_eurovoc_concept_title.append( item  )
            row_pred_eurovoc_concept_title.append(item)

        pred_eurovoc_concept_title.append(row_pred_eurovoc_concept_title)

    # convert gold standard descriptors to their labels:
    gold_standard_eurovoc_concept_title = []
    for row in dataset_test[key_labels]:
        row_gold_standard_eurovoc_concept_title = []
        for item in row:
            # try:
            #     row_gold_standard_eurovoc_concept_title.append(
            #         eurovoc_concepts[eurovoc_concepts_ids.index(item)]['title'])
            # except:
            #     print(f"Eurovoc descriptor {item} not found in provided jsonl")
            #     row_gold_standard_eurovoc_concept_title.append(item)
            row_gold_standard_eurovoc_concept_title.append(item)

        gold_standard_eurovoc_concept_title.append(row_gold_standard_eurovoc_concept_title)

    assert len(gold_standard_eurovoc_concept_title) == len(pred_eurovoc_concept_title) == len(dataset_test)

    with open(output_file, "w") as outfile:

        for item, gold_standard, pred in zip(dataset_test, gold_standard_eurovoc_concept_title,
                                             pred_eurovoc_concept_title):
            data = {}

            data['text'] = item['text']
            data['gold_standard'] = gold_standard
            data['predicted'] = pred

            json.dump(data, outfile)
            outfile.write("\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--config_path", dest="config_path",
                        help="path to the config file", required=True)

    args = parser.parse_args()

    main(args.config_path)
