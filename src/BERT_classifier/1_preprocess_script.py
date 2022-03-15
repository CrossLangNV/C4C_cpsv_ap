import os.path

from preprocess_data_bert import main

if __name__ == '__main__':
    FILENAME_PREPROCESS_CONFIG = os.path.join(os.path.dirname(__file__), "configuration_files_bert",
                                              "preprocessing.config")
    main(FILENAME_PREPROCESS_CONFIG)
