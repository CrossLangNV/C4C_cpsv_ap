import os.path

from preprocess_data_bert import main_with_args

DIR_SOURCE = os.path.join(os.path.dirname(__file__), "../..")

DEFAULT_ARGS = {
    "input_dir": os.path.join(DIR_SOURCE, "data/relation_extraction"),
    "preprocessed_data_dir": "./DATA/preprocessed_distilbert_base_uncased_cpsv_ap_relations",
    "key_labels": "name_labels",
    "model_name": "distilbert-base-uncased"
}

if __name__ == '__main__':
    if 0:
        FILENAME_PREPROCESS_CONFIG = os.path.join(os.path.dirname(__file__),
                                                  "configuration_files_bert/preprocessing.config")
        main(FILENAME_PREPROCESS_CONFIG)
    else:
        main_with_args(**DEFAULT_ARGS)
