import os.path

from train_bert import main

if __name__ == '__main__':
    FILENAME_TRAIN_CONFIG = os.path.join(os.path.dirname(__file__), "configuration_files_bert",
                                         "train.config")
    main(FILENAME_TRAIN_CONFIG)
