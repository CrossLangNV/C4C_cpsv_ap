import os
from configparser import ConfigParser

from BERT_classifier import preprocess_data_bert


class ConfigParserTitles(ConfigParser):
    @property
    def input_output(self, section="INPUT/OUTPUT"):
        return self[section]

    @property
    def preprocessing_configurations(self, section="PREPROCESSING_CONFIGURATIONS"):
        return self[section]

    @property
    def input_output_input_dir(self,
                               option="INPUT_DIR"
                               ) -> str:
        return self.input_output.get(option)

    @property
    def input_output_preprocessed_data_dir(self,
                                           option="PREPROCESSED_DATA_DIR"
                                           ) -> str:
        return self.input_output.get(option)

    @property
    def input_output_label_input(self,
                                 option="LABEL_INPUT"
                                 ) -> str:
        return self.input_output.get(option)

    @property
    def input_output_labels(self,
                            option="LABELS"
                            ) -> str:
        return self.input_output.get(option)

    @property
    def preprocessing_configurations_model_name(self,
                                                option="MODEL_NAME_OR_PATH"
                                                ) -> str:
        return self.preprocessing_configurations.get(option)


def main(config: ConfigParserTitles,
         preprocess: bool = True):
    input_dir = config.input_output_input_dir
    preprocessed_data_dir = config.input_output_preprocessed_data_dir
    key_labels = config.input_output_labels
    model_name = config.preprocessing_configurations_model_name

    # TODO use LABEL_INPUT
    os.path.exists(input_dir)

    if preprocess:
        preprocess_data_bert.main_with_args(input_dir=input_dir,
                                            preprocessed_data_dir=preprocessed_data_dir,
                                            key_labels=key_labels,
                                            model_name=model_name)

    return


if __name__ == '__main__':
    FILENAME_CONFIG = os.path.join(os.path.dirname(__file__),
                                   "../configuration_files_bert/titles.config")

    assert os.path.exists(FILENAME_CONFIG), FILENAME_CONFIG

    config = ConfigParserTitles()
    config.read(FILENAME_CONFIG)

    main(config,
         preprocess=False)
