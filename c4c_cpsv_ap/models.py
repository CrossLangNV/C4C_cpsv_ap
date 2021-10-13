"""
TODO reuse open_linked_data.node

As defined in SC2015DI07446_D02.02_CPSV-AP-2.2.1_v1.00.pdf
https://joinup.ec.europa.eu/collection/semantic-interoperability-community-semic/solution/core-public-service-vocabulary-application-profile/distribution/cpsv-ap-specification-v221-pdf
"""
import abc
from typing import Optional, List, Dict, Union

from pydantic import BaseModel


class CPSVAPModel(abc.ABC, BaseModel):
    """
    Abstract class for the RDF object models.
    """
    pass


class ContactPoint(CPSVAPModel):
    """
    CPSV-AP Contact Point
    """
    pass
    # TODO


class Concept(CPSVAPModel):
    """
    SKOS Concept
    """
    # TODO add language
    pref_label: str


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
    spatial: str


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
    classified_by: Optional[List[Concept]] = []
