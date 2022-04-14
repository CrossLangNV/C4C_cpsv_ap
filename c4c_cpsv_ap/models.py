"""
TODO reuse open_linked_data.node

As defined in SC2015DI07446_D02.02_CPSV-AP-2.2.1_v1.00.pdf
https://joinup.ec.europa.eu/collection/semantic-interoperability-community-semic/solution/core-public-service-vocabulary-application-profile/distribution/cpsv-ap-specification-v221-pdf
"""
import abc
from typing import Dict, List, Optional, Union
from uuid import uuid4

from pydantic import BaseModel, validator
from rdflib import URIRef

from c4c_cpsv_ap.namespace import C4C


class lang_str(str):
    """
    Mock of an RDF literal. Can be string or string with language information.
    """

    def __new__(cls, value: str, language_code=None):
        obj = super().__new__(cls, value)
        obj._language_code = language_code
        return obj

    @property
    def language_code(self):
        return self._language_code

    @language_code.setter
    def language_code(self, value):
        # TODO check that it matches an existing language code
        self._language_code = value


class CPSVAPModel(abc.ABC, BaseModel):
    """
    Abstract class for the RDF object models.
    """

    identifier: str

    @validator("identifier", pre=True, check_fields=False)
    def create_identifier(cls, v: Union[str, None]) -> str:
        """
        Automatically generates an ID if not provided.
        """
        if not v:
            return f"{cls.__name__}_{_id_generator()}"

        return v

    def get_uri(self, base=C4C) -> URIRef:
        """ Generate a URI based on identifier """
        return URIRef(self.identifier, base=base)


class Info(BaseModel):
    # Title and paragraph text
    name: Union[lang_str, List[lang_str]]
    description: Optional[Union[lang_str, List[lang_str]]]

    @validator("name", "description", pre=True, check_fields=False)
    def cast_from_string(cls, value: Union[str, lang_str, List[lang_str]]) -> Union[lang_str, List[lang_str]]:
        """
        If a string is given, cast
        """

        if not isinstance(value, (lang_str, list)):
            return lang_str(value)

        return value


class Event(CPSVAPModel, Info, abc.ABC):
    """
    Event
    """

    identifier: str

    description: Optional[str] = None
    type: Optional[int] = None

    # Links
    ## PublicService
    related_service: Optional[List[CPSVAPModel]] = []

    def add_related_service(self, public_service: CPSVAPModel):
        self.related_service.append(public_service)


class Code(str):
    """
    A series of alpha-numeric or other
    characters
    E.g. a microchip code, access code,
    social security number, enterprise
    number
    """


class Concept(BaseModel):
    """
    SKOS Concept
    """
    # TODO add language
    pref_label: str


class ContactPoint(BaseModel):
    """
    CPSV-AP Contact Point
    """
    email: List[str] = None
    telephone: List[str] = None
    opening_hours: List[str] = None


class Cost(CPSVAPModel):
    identifier: str

    # Optional
    currency: Optional[Code]
    description: Optional[str]
    value: Optional[float]


class CriterionRequirement(CPSVAPModel, Info):
    """
    CPSV-AP Criterion Requirement
    """
    identifier: str
    # Code [0..n] TODO find definition
    type: List[Code]


class Evidence(CPSVAPModel, Info):
    identifier: str

    # Linguistic system
    language: Optional[List[str]]
    # Document
    relatedDocumentation: Optional[List[str]]
    type: Optional[Code]


class BusinessEvent(Event):
    pass


class LifeEvent(Event):
    pass


class Address(CPSVAPModel):
    """
    TODO

    could be an VCARD. Should at least have a string represenation for street etc.
    """


class PublicOrganisation(BaseModel):
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

    # This property represents an Address related to an Agent. Asserting the address
    # relationship implies that the Agent has an Address.
    has_address: Optional[str]  # TODO link to address

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
        elif v is None:
            return []  # empty
        else:
            return v


class Rule(CPSVAPModel):
    description: str
    identifier: str
    name: str

    # -- Optional --
    # Language: Linguistic system
    language: Optional[List[Code]]


def _id_generator() -> str:
    """
    Generates UUID4-based but ncname-compliant identifiers.
    """

    return uuid4().hex
