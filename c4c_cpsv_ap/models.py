"""
TODO reuse open_linked_data.node

As defined in SC2015DI07446_D02.02_CPSV-AP-2.2.1_v1.00.pdf
https://joinup.ec.europa.eu/collection/semantic-interoperability-community-semic/solution/core-public-service-vocabulary-application-profile/distribution/cpsv-ap-specification-v221-pdf
"""
import abc
from typing import Optional, List, Dict, Union
from uuid import uuid4

from pydantic import BaseModel, validator


class CPSVAPModel(abc.ABC, BaseModel):
    """
    Abstract class for the RDF object models.
    """
    pass


class Concept(CPSVAPModel):
    """
    SKOS Concept
    """
    # TODO add language
    pref_label: str


class ContactPoint(CPSVAPModel):
    """
    CPSV-AP Contact Point
    """
    email: List[str] = None
    telephone: List[str] = None
    opening_hours: List[str] = None


class Event(CPSVAPModel):
    """
    Event
    """

    identifier: str
    name: str

    description: Optional[str] = None
    type: Optional[int] = None

    # Links
    ## PublicService
    related_service: Optional[List] = []

    def add_related_service(self, public_service):
        self.related_service.append(public_service)


class BusinessEvent(Event):
    pass


class LifeEvent(Event):
    pass


class PublicOrganisation(CPSVAPModel):
    """
    The CPSV-AP reuses the Core Public Organisation Vocabulary that defines the
    concept of a Public Organization and associated properties and relationships. It is
    largely based on the W3C Organization Ontology.

    TODO
     * Would like to add a validator for the pref label, with the language codes.
     * Make a validator that only allows a single label for pref_label (as defined by CPSV-AP)!
    """
    # With either label OR {language code: label} to add language info
    pref_label: Union[str, Dict[str, str]]

    # URI, according to ATU The value of the latter should be a URI from the Administrative Territorial
    # Units Named Authority List maintained by the Publications Office's Metadata Registry
    # spatial: Union[str, List[str]]
    spatial: List[str]

    @validator("spatial", pre=True)
    def spatial_list(cls, v: Union[str, List[str]]):
        """
        When a single string is given, put it in a list

        Args:
            v:
            pre:

        Returns:

        """
        if isinstance(v, str):
            return [v]
        else:
            return v


class PublicService(CPSVAPModel):
    """
    CPSV-AP Public Service
    """
    description: str
    identifier: str
    name: str

    # Optional
    keyword: Optional[List[str]] = []

    # Links
    has_competent_authority: PublicOrganisation
    is_classified_by: Optional[List[Concept]] = []
    is_grouped_by: Optional[List[Event]] = []
    has_contact_point: Optional[List[ContactPoint]] = []

    def __init__(self, *args, **kwargs):
        super(PublicService, self).__init__(*args, **kwargs)

        self._add_related_service()

    def _add_related_service(self):
        """
        """

        for event in self.is_grouped_by:
            event.add_related_service(self)

    @validator("has_contact_point", pre=True)
    def spatial_list(cls, v: Union[ContactPoint, List[ContactPoint]]) -> List[ContactPoint]:
        """
        When a single contact point is given, put it in a list

        Returns:
            Contact point within a list
        """
        if isinstance(v, ContactPoint):
            return [v]
        else:
            return v


def _id_generator() -> str:
    """
    Generates UUID4-based but ncname-compliant identifiers.
    """

    return uuid4().hex
