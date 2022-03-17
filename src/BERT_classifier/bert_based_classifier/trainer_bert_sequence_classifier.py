import abc
import json
import logging
import os
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Union

import numpy as np
import torch
from datasets import Dataset, load_dataset, load_from_disk
from numpy import ndarray
from sklearn.metrics import accuracy_score, f1_score
from torch.utils.data import DataLoader
from tqdm import tqdm, trange
from tqdm.auto import tqdm
from transformers import AdamW, AutoModelForSequenceClassification, AutoTokenizer, CONFIG_NAME, get_scheduler, \
    WEIGHTS_NAME

# to dismiss warning message related to FastTokenizers.
os.environ["TOKENIZERS_PARALLELISM"] = "true"


class TrainerBertSequenceClassifier():
    '''
    A trainer for a BertForSequenceClassification model.
    '''

    def __init__(self, pretrained_model_name_or_path: Union[str, Path],
                 preprocessed_data_dir: Union[str, Path, type(None)], output_dir: Union[str, Path]):

        '''
        :param pretrained_model_name_or_path: Path or str. Path to a trained BertForSequenceClassification model, or model name with untrained classification layer.
        :param preprocessed_data_dir: Path, str or None. Path to the preprocessed data. Preprocessed with the preprocess_data method.
        :param output_dir: Path or str. Path to the output directory (where trained model will be saved), or path to where the log file will be saved when only doing inference.
        :return: None.
        '''

        self._pretrained_model_name_or_path = pretrained_model_name_or_path
        self._preprocessed_data_dir = preprocessed_data_dir
        self._output_dir = output_dir
        os.makedirs(self._output_dir, exist_ok=True)

        # when using TrainerBertSequenceClassifier only for evaluation, the preprocessed_data_dir is None, and preprocessed_data dir is not necessary.
        if self._preprocessed_data_dir:
            os.makedirs(self._preprocessed_data_dir, exist_ok=True)

        logging.basicConfig(filename=os.path.join(self._output_dir, "output.log"), level=logging.DEBUG)

        self._logger = logging.getLogger(__name__)
        # sys.stdout = StreamToLogger(self._logger, logging.INFO)
        # sys.stderr = StreamToLogger(self._logger,logging.ERROR)
        # self._logger.addHandler(logging.StreamHandler(sys.stdout))

    def preprocess_data(self,
                        input_dir: Union[str, Path],
                        key_labels: str
                        ):

        '''
        Method for preprocessing the data provided in the input_dir (train.jsonl and validation.jsonl). Method filters the data to corpus, languages; one hot encoding of the labels; tokenization of the 'text' field of the jsonl files. Preprocessed data is saved in the self._preprocessed_data_dir directory.
        
        :param input_dir: path where train.jsonl and validation.jsonl files are stored. I.e. the files containing the training and validation data.
        :param corpora: list of corpora to consider, via the 'appears_in' field of the provided jsonl files, and the _filter_to_corpus method. 
        :param languages: list of languages to consider, via the 'language' field of the provided jsonl files, and the _filter_to_language method.
        :return: None.
        '''

        self.config = {}

        self._logger.info(f"Loading the data from {input_dir}")
        self.load_data(input_dir,
                       key_labels=key_labels)

        self.config['NUM_LABELS'] = self._num_labels
        self.config['EUROVOC_CONCEPT_2_ID'] = self._eurovoc_concept_2_id

        # load tokenizer
        self.load_tokenizer()

        # check if has attr model and tokenizer... hasattr

        self._logger.info("One hot encoding of train/validation set...")
        self._dataset = self._dataset.map(lambda item: self._one_hot_encoding(item, key_labels=key_labels))

        self._logger.info('Tokenizing train/validation set...')
        self._dataset = self._tokenize(self._dataset)

        self._logger.info('Removing irrelevant columns train/validation set...')
        self._dataset['train'] = self._remove_irrelevant_columns(self._dataset['train'])
        self._dataset['validation'] = self._remove_irrelevant_columns(self._dataset['validation'])

        self._dataset.set_format(type='torch', columns=['input_ids', 'attention_mask', 'labels'])

        self._logger.info('Casting to float train/validation set...')
        self._dataset = self._cast_to_float(self._dataset)

        self._dataset.save_to_disk(self._preprocessed_data_dir)

        # writing config to file
        # save num labels # save eurovoc concept to config file in preprocessed_data_dir...
        with open(os.path.join(self._preprocessed_data_dir, "config_preprocess.json"), 'w') as f:
            json.dump(self.config, f)

    def train(self, batch_size: int = 16, epochs: int = 1, lr=5e-5, warm_up: bool = False, gpu: int = 0,
              save_model_each: int = 5,
              ):
        '''
        Method to train a Bert for sequence classification model.
        
        :param corpora: List of strings. Corpora to consider (i.e. via the 'appears in' field of self._dataset).
        :param batch_size: int.
        :param epochs: int. Number of epochs.
        :param lr: float. Learning rate.
        :param warm_up: Boolean. If true, the first epoch will be warm up.
        :param gpu: int. GPU number.
        :param save_model_each: int. Model will be saved in self._output_dir each save_model_each epoch.     
        :return: None.
        '''

        output_dir = self._output_dir

        os.makedirs(output_dir, exist_ok=True)

        device = torch.device(f'cuda:{gpu}') if torch.cuda.is_available() else torch.device('cpu')

        # loading the preprocessed data.
        self._logger.info(f"Loading the preprocessed data from {self._preprocessed_data_dir}")

        self._dataset = load_from_disk(self._preprocessed_data_dir)

        # debugging
        # self._dataset['train']=self._dataset[ 'train' ].shuffle(seed=42).select(range(1000))
        # self._dataset['validation']=self._dataset[ 'validation' ].shuffle(seed=42).select(range(1000))

        # preprocess the data:

        self._logger.info(f"Setting to torch format.")
        self._dataset.set_format(type='torch', columns=['input_ids', 'attention_mask', 'labels'])

        preprocessed_config = json.loads(
            open(os.path.join(self._preprocessed_data_dir, 'config_preprocess.json')).read())

        self._num_labels = preprocessed_config['NUM_LABELS']
        self._eurovoc_concept_2_id = preprocessed_config['EUROVOC_CONCEPT_2_ID']

        # loading the model (and the accompanying tokenizer):
        self._logger.info(
            f"Loading the untrained model (i.e. untrained classification layer) from {self._pretrained_model_name_or_path}")

        # we pass self._num_labels and self._eurovoc_concept_2_id (both created during self.load_data) to the config file, so it will be saved when saving the model.
        self.load_model(self._num_labels, self._eurovoc_concept_2_id)

        train_dataloader = DataLoader(self._dataset['train'], shuffle=True, batch_size=batch_size)
        validation_dataloader = DataLoader(self._dataset['validation'], shuffle=False, batch_size=batch_size)

        # get the optimizer
        optimizer = AdamW(self.model.parameters(), lr=lr, correct_bias=False)

        # define a scheduler
        num_training_steps = epochs * len(train_dataloader)

        # warm up for one epoch if warm_up==True
        if warm_up:
            num_warmup_steps = len(train_dataloader)
        else:
            num_warmup_steps = 0

        lr_scheduler = get_scheduler(
            "linear",
            optimizer=optimizer,
            num_warmup_steps=num_warmup_steps,
            num_training_steps=num_training_steps
        )

        # activation and loss function for multi-label classification:
        activation = torch.nn.Sigmoid()
        self._loss_function = torch.nn.BCEWithLogitsLoss(pos_weight=None)

        # put model on device:
        self.model.to(device)

        # freeze layers (but don't freeze last two layers (i.e. pooler and last encoder layer) ):
        # if freeze_bert:
        #    self._freeze_bert_encoder()
        #    self._unfreeze_bert_encoder_last_layers()

        progress_bar = tqdm(range(num_training_steps))

        start = time.time()

        val_labels = self._dataset['validation']['labels'].numpy()

        for epoch in trange(epochs, desc="Epoch"):

            self._logger.info(f"Start training epoch {epoch}.")

            ## TRAINING
            class Metric(abc.ABC):
                def __init__(self, logger: logging.Logger):
                    self._logger = logger

                def on_batch_end(self, y_true, y_pred, *args, **kwargs):
                    """ For each batch add the necessary data."""
                    pass

                def on_epoch_end(self):
                    """ a print function to share the results."""
                    pass

            class LossMetric(Metric):

                def __init__(self, *args, **kwargs):
                    super(LossMetric, self).__init__(*args, **kwargs)

                    self.tr_loss = 0
                    self.nb_tr_steps = 0

                def on_batch_end(self, loss, *args, **kwargs):
                    """"""

                    self.tr_loss += loss
                    self.nb_tr_steps += 1

                def on_epoch_end(self):
                    """Log"""

                    self._logger.info("Train loss: {}".format(self.tr_loss / self.nb_tr_steps))

            class AccuracyMetric(Metric):

                def __init__(self, *args, **kwargs):
                    super(AccuracyMetric, self).__init__(*args, **kwargs)

                    self.tr_accuracy = 0
                    self.nb_tr_steps = 0

                def on_batch_end(self, y_pred, y_true, *args, **kwargs):
                    """"""

                    tmp_tr_accuracy = self._accuracy(y_pred, y_true)
                    self.tr_accuracy += tmp_tr_accuracy
                    self.nb_tr_steps += 1

                def on_epoch_end(self):
                    """Log"""

                    if self.nb_tr_steps:
                        acc = self.tr_accuracy / self.nb_tr_steps
                        self._logger.info(f"Training Accuracy: {acc}")
                    else:
                        self._logger.info(f"Training Accuracy: None. No steps done!")

                def _accuracy(self, preds, labels, threshold=0.5):
                    outputs = np.array(preds) >= threshold
                    labels_bool = np.array(labels, dtype=bool)

                    return np.mean(np.equal(outputs, labels_bool))

            class AccuracyExactMatchMetric(Metric):
                """"""

                def __init__(self, *args, **kwargs):
                    super(AccuracyExactMatchMetric, self).__init__(*args, **kwargs)

                    self.tr_accuracy = 0
                    self.nb_tr_steps = 0

                def on_batch_end(self, y_true, y_pred, *args, **kwargs):
                    """"""

                    tmp_tr_accuracy = self._flat_accuracy(y_pred, y_true)
                    self.tr_accuracy += tmp_tr_accuracy
                    self.nb_tr_steps += 1

                def on_epoch_end(self):
                    """Log"""
                    if self.nb_tr_steps:
                        acc = self.tr_accuracy / self.nb_tr_steps
                        self._logger.info(f"Training Accuracy Exact Match: {acc}")
                    else:
                        self._logger.info(f"Training Accuracy  Exact Match: None. No steps done!")

                def _flat_accuracy(self, preds, labels, threshold=0.5):
                    outputs = np.array(preds) >= threshold
                    return accuracy_score(labels, outputs)

            # class LossMetric(Metric):
            #     pass

            def train_step(metrics: List = None):
                if metrics is None:
                    metrics = []

                # Set our model to training mode
                self.model.train()
                # Tracking metrics
                tr_loss, tr_accuracy = 0, 0
                nb_tr_steps = 0

                # Train the data for one epoch
                for step, batch in enumerate(train_dataloader):
                    optimizer.zero_grad()
                    input_ids = batch['input_ids'].to(device)
                    attention_mask = batch['attention_mask'].to(device)
                    labels = batch['labels'].to(device)
                    outputs = self.model(input_ids, attention_mask=attention_mask)
                    logits = outputs[0]
                    loss = self._loss_function(logits, labels)
                    loss.backward()

                    optimizer.step()
                    lr_scheduler.step()

                    tr_loss += loss.item()
                    labels_cpu = labels.to('cpu').numpy()
                    pred_proba = activation(logits).detach().to('cpu').numpy()
                    tmp_tr_accuracy = self._flat_accuracy(pred_proba, labels_cpu)
                    tr_accuracy += tmp_tr_accuracy
                    nb_tr_steps += 1

                    progress_bar.update(1)

                    for metric in metrics:
                        metric.on_batch_end(y_true=labels_cpu,
                                            y_pred=pred_proba,
                                            loss=tr_loss)

                for metric in metrics:
                    metric.on_epoch_end()

                # if eval_train:
                #     self._logger.info("Training Accuracy: {}".format(tr_accuracy / nb_tr_steps))
                #     self._logger.info("Train loss: {}".format(tr_loss / nb_tr_steps))

                return

            train_step(metrics=[AccuracyExactMatchMetric(logger=self._logger),
                                AccuracyMetric(logger=self._logger),
                                LossMetric(logger=self._logger)
                                ])

            ## VALIDATION (after each epoch)

            self._logger.info(f"Evaluating epoch {epoch}.")

            # Put model in evaluation mode
            self.model.eval()
            # Tracking variables

            eval_loss, eval_accuracy = 0, 0
            nb_eval_steps = 0
            preds_proba = np.empty((0, self.model.config.num_labels), np.float32)

            # Evaluate data for one epoch
            for batch in validation_dataloader:
                input_ids = batch['input_ids'].to(device)
                attention_mask = batch['attention_mask'].to(device)
                labels = batch['labels'].to(device)
                with torch.no_grad():
                    outputs = self.model(input_ids, attention_mask=attention_mask)
                logits = outputs[0]
                loss = self._loss_function(logits, labels)
                labels_cpu = labels.to('cpu').numpy()
                eval_loss += loss.item()
                pred_proba = activation(logits).detach().to('cpu').numpy()
                tmp_eval_accuracy = self._flat_accuracy(pred_proba, labels_cpu)
                eval_accuracy += tmp_eval_accuracy
                nb_eval_steps += 1
                preds_proba = np.append(preds_proba, pred_proba, axis=0)

            self._logger.info("Validation Accuracy: {}".format(eval_accuracy / nb_eval_steps))
            self._logger.info("Validation Loss: {}".format(eval_loss / nb_eval_steps))
            self._logger.info("Getting optimal threshold on validation set:")

            # get optimal threshold:
            low = 0
            high = 0.51
            f1_best = -10
            optimal_thresh = 0
            f1_debug = False
            for thresh in np.arange(low, high, 0.01):
                preds_labels = (np.array(preds_proba) >= thresh) * 1
                f1_pred = f1_score(val_labels, preds_labels, average='micro')
                if f1_debug:
                    self._logger.info(f"f1 score is {f1_pred}, when using threshold {thresh}.")
                if f1_pred > f1_best:
                    f1_best = f1_pred
                    optimal_thresh = thresh
            self._logger.info(f"f1 score is {f1_best}, when using OPTIMAL threshold {optimal_thresh}.")

            # save the optimal threshold calculated on validation set (used during evaluation).
            self.model.config.threshold = optimal_thresh

            preds_labels = (np.array(preds_proba) >= optimal_thresh) * 1

            self._logger.info(
                f"f1 score at optimal tresh {optimal_thresh} is {f1_score(val_labels, preds_labels, average='micro')}")

            # Saving model each 'save_model_each' epochs...

            if epoch % save_model_each == 0:
                today = "_".join(datetime.now().ctime().split())
                file_name_info = f"{today}_{uuid.uuid1().hex}"

                output_dir_epoch = os.path.join(output_dir, f'epoch_{epoch}_{file_name_info}')

                os.makedirs(output_dir_epoch, exist_ok=True)

                self._logger.info(f"Saving trained model to {output_dir_epoch}")

                output_model_file = os.path.join(output_dir_epoch, WEIGHTS_NAME)
                output_config_file = os.path.join(output_dir_epoch, CONFIG_NAME)

                torch.save(self.model.state_dict(), output_model_file)
                self.model.config.to_json_file(output_config_file)
                self.tokenizer.save_vocabulary(output_dir_epoch)

        end = time.time()
        self._logger.info(f"Training took: {end - start:.3f} s")

    def predict(self, documents: List[str], batch_size: int = 16, gpu: int = 0) -> Tuple[ndarray, ndarray]:

        '''
        Inference on set of documents using a trained BertForSequenceClassification model.
        
        :param documents: List of strings
        :param batch_size: int. 
        :param gpu. int.
        '''

        device = torch.device(f'cuda:{gpu}') if torch.cuda.is_available() else torch.device('cpu')

        # create a hugging face dataset from the list of strings provided (the documents to do inference on...)

        dataset = Dataset.from_dict({'text': documents})

        if not hasattr(self, 'model') or not hasattr(self, 'tokenizer'):
            self._logger.info(
                f"Loading  model finetuned for classification task from {self._pretrained_model_name_or_path}")
            self.load_model()

        self._logger.info('Tokenizing documents...')
        dataset = self._tokenize(dataset)

        # remove the 'text' row from the dataset
        dataset = self._remove_irrelevant_columns(dataset)
        # convert to torch format
        dataset.set_format('torch')

        # Define dataloaders...
        test_dataloader = DataLoader(dataset, shuffle=False, batch_size=batch_size)

        preds_proba = np.empty((0, self.model.config.num_labels), np.float32)

        activation = torch.nn.Sigmoid()

        # Put model in evaluation mode and on GPU
        self.model.eval()
        self.model.to(device)

        ## INFERENCE
        for batch in test_dataloader:
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)

            with torch.no_grad():
                outputs = self.model(input_ids, attention_mask=attention_mask)

            preds_proba = np.append(preds_proba, activation(outputs[0]).to('cpu').numpy(), axis=0)

        threshold = self.model.config.threshold

        preds_labels = (np.array(preds_proba) >= threshold) * 1

        return preds_labels, preds_proba

    def load_model(self, num_labels: Union[int, type(None)] = None,
                   eurovoc_concept_2_id: Union[Dict[str, int], type(None)] = None):

        '''
        Load a trained BertForSequenceClassification models, and accompanying BertTokenizer. Classification layers can be both trained or untrained.
        
        :param num_labels. Number of unique labels for multi_label classification problem.
        :param eurovoc_concept_2_id. Dict. Eurovoc concepts (i.e. descriptors) as keys, and id as value.
        :return: None.
        '''

        kwargs = dict(pretrained_model_name_or_path=self._pretrained_model_name_or_path, \
                      num_labels=num_labels)
        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        self.model = AutoModelForSequenceClassification.from_pretrained(**kwargs)

        # fine-tuned models will have this 'model_name', which is the name of the base architecture, for non fine-tuned models, we save it in the config file.
        if not hasattr(self.model.config, 'model_name'):
            self.model.config.model_name = self._pretrained_model_name_or_path

        # Autotokenizer does not load correct tokenizer when loading from fine-tuned sequence classifier (therefore always load from base model name)
        self.tokenizer = AutoTokenizer.from_pretrained(pretrained_model_name_or_path=self.model.config.model_name)

        # when calling .train() eurovoc_concept_2_id is not None
        if eurovoc_concept_2_id:
            self.model.config.eurovoc_concept_2_id = eurovoc_concept_2_id

    def load_tokenizer(self):

        # Autotokenizer does not load correct tokenizer when loading from fine-tuned sequence classifier (therefore always load from base model name)
        self.tokenizer = AutoTokenizer.from_pretrained(
            pretrained_model_name_or_path=self._pretrained_model_name_or_path)

    def load_data(self, input_dir: Union[str, Path],
                  key_labels: str):

        train_file = os.path.join(input_dir, 'train.jsonl')
        validation_file = os.path.join(input_dir, 'validation.jsonl')

        self._dataset = load_dataset('json', data_files={"train": train_file, "validation": validation_file},
                                     streaming=False)

        # DEBUGGING:
        # self._dataset['train']=self._dataset[ 'train' ].shuffle(seed=42).select(range(1000))
        # self._dataset['validation']=self._dataset[ 'validation' ].shuffle(seed=42).select(range(1000))

        # limit to corpora (e.g.  ['EURLEX57K', 'jex', 'jrc_acquis']  ) and language
        # self._dataset=self._dataset.filter( self._filter_to_corpus, fn_kwargs={ 'corpora': corpora } )
        # self._dataset=self._dataset.filter( self._filter_to_language, fn_kwargs={ 'languages': languages } )

        # collect all eurovoc labels that appear in train data:
        labels = self._dataset['train'][key_labels]
        labels = [item for sublist in labels for item in sublist]
        labels = list(set(labels))

        # number of unique labels in the (train) dataset
        self._num_labels = len(labels)

        self._eurovoc_concept_2_id = {}
        for i, eurovoc_concept in enumerate(labels):
            self._eurovoc_concept_2_id[eurovoc_concept] = i

        # self._id_2_eurovoc_concept={}
        # for i in range( len( labels)  ):
        #    self._id_2_eurovoc_concept[ i ]=labels[i]

    def _one_hot_encoding(self,
                          item: Dict,
                          key_labels
                          ) -> Dict:

        '''
        Helper function to preprocess data.
        '''

        # Make a copy
        l_inter = item[key_labels][:]

        item['labels'] = []

        item['labels'] = [0] * len(self._eurovoc_concept_2_id.keys())
        for label in l_inter:
            # need to do this check, because validation dataset can contain labels that are not present in train dataset
            if label in self._eurovoc_concept_2_id.keys():
                item['labels'][self._eurovoc_concept_2_id[label]] = 1

        return item

    def _tokenize(self, dataset: Dataset) -> Dataset:

        # tokenize (use batches)
        return dataset.map(self._tokenize_function, batched=True)

    def _tokenize_function(self, items: Dict) -> Dict:

        # tokenizer will truncate to max_length of the model.

        return self.tokenizer(items["text"], truncation=True, padding=True)  # , max_length=1024 )

    def _remove_irrelevant_columns(self, dataset: Dataset) -> Dataset:

        features_list = list(dataset.features.keys())

        for item in ['attention_mask', 'input_ids', 'token_type_ids', 'labels', 'appears_in']:
            if item in features_list:
                features_list.remove(item)

        return dataset.remove_columns(features_list)

    def _cast_to_float(self, dataset: Dataset) -> Dataset:

        def _cast_to_float_map_function(item):
            item['labels_float'] = item['labels'].float()

            return item

        dataset = dataset.map(_cast_to_float_map_function)

        dataset = dataset.remove_columns('labels')

        dataset = dataset.rename_column("labels_float", "labels")

        return dataset

    def _flat_accuracy(self, preds, labels, threshold=0.5):
        outputs = np.array(preds) >= threshold
        return accuracy_score(labels, outputs)

    def _filter_to_corpus(self, item, corpora):

        for corpus in corpora:
            if corpus in item['appears_in']:
                return True
        return False

    def _filter_to_language(self, item, languages):

        for lang in languages:
            if lang.lower() == item['language'].lower():
                return True
        return False

    # def _freeze_bert_encoder( self ): #TO DO: account for distilbert
    #    for param in self.model.bert.parameters():
    #        param.requires_grad = False

    # def _unfreeze_bert_encoder_last_layers( self ): #TO DO: account for distilbert
    #    for name, param in self.model.bert.named_parameters():
    #        if "encoder.layer.11" in name or "pooler" in name:
    #            param.requires_grad = True
