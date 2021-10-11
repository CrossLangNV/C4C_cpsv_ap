"""
TODO reuse open_linked_data.node

As defined in SC2015DI07446_D02.02_CPSV-AP-2.2.1_v1.00.pdf
https://joinup.ec.europa.eu/collection/semantic-interoperability-community-semic/solution/core-public-service-vocabulary-application-profile/distribution/cpsv-ap-specification-v221-pdf
"""
import abc
from typing import Optional, List

from pydantic import BaseModel


class CPSVAPModel(abc.ABC, BaseModel):
    pass


class ContactPoint(CPSVAPModel):
    pass


class Concept(CPSVAPModel):
    # TODO add language
    pref_label: str


class PublicService(CPSVAPModel):
    description: str
    identifier: str
    name: str

    # Optional
    keyword: Optional[List[str]] = []

    # Links
    classified_by: Optional[List[Concept]] = []
