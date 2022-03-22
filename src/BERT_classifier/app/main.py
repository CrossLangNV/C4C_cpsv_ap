import os
import warnings

from fastapi import FastAPI

from BERT_classifier.app.models import Labels, Results, Text
from BERT_classifier.bert_based_classifier.trainer_bert_sequence_classifier import TrainerBertSequenceClassifier

# See Dockerfile for file.
path_model = "/tmp/app_model"

# Sanity check
if not os.path.exists(path_model):
    warnings.warn(f"Could not find {path_model}")
else:
    if not os.listdir(path_model):
        warnings.warn(f"Dir is empty: {path_model}")

# load the model:

trainer_bert_sequence_classifier = TrainerBertSequenceClassifier(
    pretrained_model_name_or_path=path_model,
    preprocessed_data_dir=None,
    output_dir=os.path.dirname(__file__)
)

app = FastAPI()


@app.get("/")
async def hello():
    return {"msg": "BERT Classifier API"}


@app.post("/classify_text", response_model=Results)
async def classify_text(text: Text) -> Results:
    """
    Predict the likelihood of the text corresponding to one the labels.
    To find the name of these labels, see */labels*

    Args:
        text:

    Returns:

    """
    _, probabilities = trainer_bert_sequence_classifier.predict([text.text])

    labels = (await get_labels())

    results = Results(probabilities=probabilities[0].tolist(),
                      **labels.dict())

    return results


# @lru_cache(maxsize=1)
@app.get("/labels", response_model=Labels)
async def get_labels() -> Labels:
    """
    Get the labels corresponding to the indices.

    Returns:

    """

    if not hasattr(trainer_bert_sequence_classifier, 'model'):
        trainer_bert_sequence_classifier.load_model()

    d = trainer_bert_sequence_classifier.model.config.eurovoc_concept_2_id

    d_inverse = {int(label_id): label_name for label_name, label_id in d.items()}

    names = [d_inverse[i] for i in range(len(d_inverse))]

    return Labels(names=names)
