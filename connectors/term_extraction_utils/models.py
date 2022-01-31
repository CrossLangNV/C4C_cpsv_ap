from typing import Optional, Union

import cassis
from pydantic import BaseModel, validator

from connectors.term_extraction_utils.cas_utils import cas_from_cas_content


class Document(BaseModel):
    """
    Model for input of request.
    """
    html: str
    # Can't be None, even though it was specified in the API as 'Union[str, type(None)]'
    language: Union[str, type(None)]  # str


class ExtractModel(BaseModel):
    """
    Abstract Model for returned data by Term Extraction API.
    Shared between ChunkModel and TermsModel.
    """
    title: str
    tags: str
    # description of a webpage, see Package "trafilatura"
    excerpt: str
    text: str
    hostname: Optional[str]  # TODO check if optional
    source_hostname: str  # Make sure to de-hyphenate
    source: Optional[str]  # TODO check if optional
    language: Union[str, type(None)]  # str
    cas_content: str

    @classmethod
    def from_json(cls, j_return: dict):
        """

        Args:
            j: JSON from the request return

        Returns:

        """
        j_return_dehyphenated = {key.replace("-", "_"): value for key, value in j_return.items()}
        return cls(**j_return_dehyphenated)

    def get_cas(self) -> cassis.Cas:
        return cas_from_cas_content(self.cas_content)

    @validator('excerpt', pre=True)
    def not_none(cls, v: str):
        if v is None:
            return ''
        return v


class ChunkModel(ExtractModel):
    pass


class ContactInfo(BaseModel):
    text: str
    cas_content: str
    language: Union[str, type(None)]  # str


class TermsModel(ChunkModel):
    pass


class QuestionAnswersModel(ExtractModel):
    pass
