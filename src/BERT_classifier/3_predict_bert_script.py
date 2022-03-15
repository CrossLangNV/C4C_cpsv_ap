import os.path

from predict_bert import main

if __name__ == '__main__':
    FILENAME_PREDICT_CONFIG = os.path.join(os.path.dirname(__file__), "configuration_files_bert",
                                           "predict.config")
    main(FILENAME_PREDICT_CONFIG)
