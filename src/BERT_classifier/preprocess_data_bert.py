import argparse
from configparser import ConfigParser
from pathlib import Path
from typing import Union

from bert_based_classifier.trainer_bert_sequence_classifier import TrainerBertSequenceClassifier


def main_with_args(input_dir: str,
                   preprocessed_data_dir: str,
                   key_labels: str,
                   model_name: str
                   ):
    # initialize a preprocessor/trainer
    trainer_bert_sequence_classifier = TrainerBertSequenceClassifier(model_name, preprocessed_data_dir,
                                                                     preprocessed_data_dir)

    # preprocess the data
    trainer_bert_sequence_classifier.preprocess_data(input_dir,
                                                     key_labels)

    return


def main(path_to_config: Union[str, Path]):
    '''
    Training of a Bert model for sequence classification.
    '''

    config = ConfigParser()
    config.read(path_to_config)

    # input-output
    # data dir with jsonl files (should contain train.jsonl and validation.jsonl )
    input_dir = config['INPUT/OUTPUT']['INPUT_DIR']
    preprocessed_data_dir = config['INPUT/OUTPUT']['PREPROCESSED_DATA_DIR']
    key_labels = config['INPUT/OUTPUT']['LABELS']

    # model training parameters
    model_name = config.get('PREPROCESSING_CONFIGURATIONS', 'MODEL_NAME_OR_PATH')

    main_with_args(input_dir=input_dir,
                   preprocessed_data_dir=preprocessed_data_dir,
                   key_labels=key_labels,
                   model_name=model_name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--config_path", dest="config_path",
                        help="path to the config file", required=True)

    args = parser.parse_args()

    main(args.config_path)

# from src.bert_based_classifier.trainer_bert_sequence_classifier import TrainerBertSequenceClassifier

# trainer_bert_sequence_classifier=TrainerBertSequenceClassifier(  'distilbert-base-multilingual-cased' , '../DATA/preprocessed_data' , '../DATA/preprocessed_data'  )

# trainer_bert_sequence_classifier.preprocess_data( '../DATA/EN_FR_PL_SCRAPED' , ["MULTI_LANG_EURLEX_EN","MULTI_LANG_EURLEX_FR","MULTI_LANG_EURLEX_PL" ] )
