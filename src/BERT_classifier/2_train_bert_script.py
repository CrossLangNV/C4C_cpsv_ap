from train_bert import main_with_args

if __name__ == '__main__':

    if 1:
        DEFAULT_ARGS = {
            "preprocessed_data_dir": "./DATA/only_train_preprocessed_distilbert_base_uncased_cpsv_ap_relations",
            "output_dir": "./DATA/results/results_only_train_distilbert_base_uncased_1epoch_warmup_cpsv_ap_relations",
            "model_name_or_path": "distilbert-base-uncased",
            "batch_size": 4,
            "epochs": 36,
            "initial_lr": 5e-5,
            "warm_up": True,
            "gpu": 0,
            "save_model_each": 1
        }

        main_with_args(**DEFAULT_ARGS)
    else:
        FILENAME_TRAIN_CONFIG = os.path.join(os.path.dirname(__file__), "configuration_files_bert/train.config")
        main(FILENAME_TRAIN_CONFIG)

    # Train on all data
