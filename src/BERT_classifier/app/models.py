from typing import List

from pydantic import BaseModel


class Text(BaseModel):
    text: str


class TextLines(BaseModel):
    text: List[str]


class Labels(BaseModel):
    names: List[str]


class Results(Labels):
    """
    Includes labels
    """
    probabilities: List[float]


class ResultsLines(Labels):
    """
    Includes labels
    """
    probabilities: List[List[float]]
