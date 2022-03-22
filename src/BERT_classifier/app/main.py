import os
import warnings
from typing import List

from fastapi import FastAPI
from pydantic import BaseModel

from bert_based_classifier.trainer_bert_sequence_classifier import TrainerBertSequenceClassifier

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


class Text(BaseModel):
    text: str


class Results(BaseModel):
    probablities: List[float]


app = FastAPI()


@app.get("/")
async def hello():
    return {"msg": "BERT Classifier API"}


@app.post("/classify_text")
async def classify_text(text: Text) -> Results:
    _, probabilities = trainer_bert_sequence_classifier.predict([text.text],
                                                                # cleaning=True
                                                                )

    output_json = Results(probabilities=probabilities[0].tolist())

    return output_json
