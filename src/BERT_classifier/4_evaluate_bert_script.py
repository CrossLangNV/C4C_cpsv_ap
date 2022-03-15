import os.path

from evaluate_bert import main

if __name__ == '__main__':
    FILENAME_EVALUATE_CONFIG = os.path.join(os.path.dirname(__file__), "configuration_files_bert",
                                            "evaluate.config")
    main(FILENAME_EVALUATE_CONFIG)
