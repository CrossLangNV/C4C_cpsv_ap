import argparse
from configparser import ConfigParser
from pathlib import Path
from typing import Union

from BERT_classifier.bert_based_classifier.trainer_bert_sequence_classifier import TrainerBertSequenceClassifier


def main_with_args(preprocessed_data_dir: str,
                   output_dir: str,
                   model_name_or_path: str,
                   batch_size: int = 4,
                   epochs: int = 40,
                   initial_lr: float = 5e-5,
                   warm_up: bool = True,
                   gpu: int = 0,
                   save_model_each: int = 10):
    # initialize a Trainer
    trainer_bert_sequence_classifier = TrainerBertSequenceClassifier(model_name_or_path, preprocessed_data_dir,
                                                                     output_dir)

    # train the model
    trainer_bert_sequence_classifier.train(batch_size=batch_size, epochs=epochs, lr=initial_lr, warm_up=warm_up,
                                           gpu=gpu, save_model_each=save_model_each)


def main(path_to_config: Union[str, Path]):
    '''
    Training of a Bert model for sequence classification.
    '''

    config = ConfigParser()
    config.read(path_to_config)

    # input-output
    # data dir with jsonl files (should contain train.jsonl and validation.jsonl )
    preprocessed_data_dir = config['INPUT/OUTPUT']['PREPROCESSED_DATA']
    # output dir where trained models will be saved (will be created if it does not exist already)
    output_dir = config['INPUT/OUTPUT']['OUTPUT_DIR']

    # model training parameters
    model_name_or_path = config.get('MODEL_TRAINING_CONFIGURATIONS', 'MODEL_NAME_OR_PATH')
    batch_size = config.getint('MODEL_TRAINING_CONFIGURATIONS', 'BATCH_SIZE')
    epochs = config.getint('MODEL_TRAINING_CONFIGURATIONS', 'EPOCHS')
    initial_lr = config.getfloat('MODEL_TRAINING_CONFIGURATIONS', 'INITIAL_LEARNING_RATE')
    warm_up = config.getboolean('MODEL_TRAINING_CONFIGURATIONS', 'WARM_UP')
    gpu = config.getint('MODEL_TRAINING_CONFIGURATIONS', 'GPU')
    save_model_each = config.getint('MODEL_TRAINING_CONFIGURATIONS', 'SAVE_MODEL_EACH')

    main_with_args(preprocessed_data_dir=preprocessed_data_dir,
                   output_dir=output_dir,
                   model_name_or_path=model_name_or_path,
                   batch_size=batch_size,
                   epochs=epochs,
                   initial_lr=initial_lr,
                   warm_up=warm_up,
                   gpu=gpu,
                   save_model_each=save_model_each,
                   )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--config_path", dest="config_path",
                        help="path to the config file", required=True)

    args = parser.parse_args()

    main(args.config_path)
