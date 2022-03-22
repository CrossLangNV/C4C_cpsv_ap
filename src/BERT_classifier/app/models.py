from typing import List

from pydantic import BaseModel


class Text(BaseModel):
    text: str


class Labels(BaseModel):
    names: List[str]


class Results(Labels):
    """
    Includes labels
    """
    probabilities: List[float]
