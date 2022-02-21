import os
import warnings
from typing import Generator, List

import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel

from c4c_cpsv_ap.connector.hierarchy import Provider
from c4c_cpsv_ap.models import Concept, ContactPoint, PublicOrganisation, PublicService
from connectors.term_extraction import ConnectorContactInfoClassification, ConnectorTermExtraction, TypesContactInfo
from connectors.term_extraction_utils.cas_utils import cas_from_cas_content, SOFA_ID

TERM_EXTRACTION = os.environ["TERM_EXTRACTION"]
CONTACT_CLASSIFICATION = os.environ["CONTACT_CLASSIFICATION"]


class ContactInfoSplit(BaseModel):
    """
    Contains all info regarding the contact info
    """
    email: List[str] = []
    telephone: List[str] = []
    opening_hours: List[str] = []
    address: List[str] = []

    def add_email(self, s: str, unique=True):
        self._add_x(s=s, unique=unique, el=self.email)

    def add_telephone(self, s: str, unique=True):
        self._add_x(s=s, unique=unique, el=self.telephone)

    def add_opening_hours(self, s: str, unique=True):
        self._add_x(s=s, unique=unique, el=self.opening_hours)

    def add_address(self, s: str, unique=True):
        self._add_x(s=s, unique=unique, el=self.address)

    @staticmethod
    def _add_x(s: str, unique: bool, el) -> None:
        """
        private class to add a sentence/string to the element (el)

        Args:
            s: sentence/string to add to the list.
            unique: flag to check for duplicates.
            el: one of parameters of this class.

        Returns:
            None
        """
        if unique and s in el:
            return
        el.append(s)


class RelationExtractor:
    def __init__(self, html, context,
                 country_code: str):
        # Save data
        self.html = html
        self.context = context
        self.country_code = country_code

        # Init provider
        self.provider = Provider()

    def extract_all(self,
                    extract_concepts=True):
        """
        """

        contact_info = self.extract_contact_info()
        public_org = self.extract_public_organisation()

        if extract_concepts:
            concepts = self.extract_concepts()
        else:
            concepts = []

        self.extract_public_service(contact_info=contact_info,
                                    public_org=public_org,
                                    concepts=concepts)

    def extract_public_organisation(self):
        contact_info_split = self.get_contact_info_split()
        l_address = contact_info_split.address
        address = '\n'.join(l_address)

        # Prefered label can most likely be extracted from the name of the service
        # within the contact information.
        public_org = PublicOrganisation(pref_label=f"# TODO",  # TODO
                                        spatial=self.context,
                                        has_address=address)  # TODO
        self.provider.public_organisations.add(public_org, context=self.context)

        return public_org

    def extract_public_service(self,
                               contact_info: ContactPoint,
                               public_org: PublicOrganisation,
                               concepts: List[Concept]
                               ) -> PublicService:
        """
        Extract all public service information

        TODO
         * add the identifier extraction results
        """

        public_service = PublicService(name=get_public_service_name(self.html),
                                       description=get_public_service_description(self.html),
                                       identifier=None,
                                       has_competent_authority=public_org,
                                       has_contact_point=contact_info,
                                       is_classified_by=concepts,
                                       )

        self.provider.public_services.add(public_service=public_service,
                                          context=self.context)

        return public_service

    def extract_contact_info(self) -> ContactPoint:
        contact_info_split = self.get_contact_info_split()

        contact_info = ContactPoint(email=contact_info_split.email,
                                    telephone=contact_info_split.telephone,
                                    opening_hours=contact_info_split.opening_hours
                                    )

        return contact_info

    def get_contact_info_split(self) -> ContactInfoSplit:
        conn = ConnectorTermExtraction(TERM_EXTRACTION)
        l_info_text = conn.get_contact_info(html=self.html,
                                            # language=language
                                            )
        contact_info_split = _split_contact_info(l_info_text, country_code=self.country_code)
        return contact_info_split

    def extract_concepts(self) -> List[Concept]:
        l_label = get_concepts(self.html)

        l_concept_cpsv_ap = [Concept(pref_label=label) for label in l_label]

        return l_concept_cpsv_ap

    def export(self, destination=None):
        """
        Export to RDF
        """

        print(self.provider.graph.serialize(destination))


def get_public_service_name(html: str) -> str:
    """
    Returns the public service of an HTML

    We
    """
    # urllib2.urlopen("https://www.google.com")
    soup = BeautifulSoup(html, "html.parser")

    # Cast to string instead of using NavigableString
    title = str(soup.title.string)

    return title


def get_public_service_description(html) -> str:
    """
    Use description from chunk extraction API.
    """

    conn = ConnectorTermExtraction(TERM_EXTRACTION)
    chunk = conn._post_chunking(html=html,
                                # language=language # TODO
                                )
    description = chunk.excerpt

    return description


def get_requirements(html: str) -> str:
    """
    Extracts the x

    TODO
     * In the future we might add an annotation to the HTML.
    """

    # Get a pyramid with the tags. Return the part which is most likely.

    soup = _get_soup_text(html)
    for section in _get_children_text(soup):

        if "required" in section.text():
            yield section


def get_concepts(html: str,
                 language="en"):
    j = {
        "html": html,
        "language": language
    }
    r = requests.post(TERM_EXTRACTION + "/extract_terms",
                      json=j)
    j_r = r.json()

    cas = cas_from_cas_content(j_r['cas_content'])

    l_term_typesystem = cas.get_view(SOFA_ID).select("cassis.Token")

    l_term = list(set(map(lambda ts: ts.lemma, l_term_typesystem)))

    return l_term


def generator_html(html: str) -> Generator[str, None, None]:
    """
    Make a generator from the HTML to go over all text in a pyramid-like manner:
    Higher level tags will return all text contained within.
    """

    soup = _get_soup_text(html)

    for text in _get_children_text(soup):
        yield text


def get_requirements(html):
    """
    For Criterion Requirements.
    """

    # TODO use Chunks.

    conn = ConnectorTermExtraction(TERM_EXTRACTION)
    chunk = conn._post_chunking(html=html,
                                # language=language # TODO
                                )
    # chunk.
    description = chunk.excerpt

    soup = _get_soup_text(html)
    for section in _get_children_text(soup):

        if "required" in section.text():
            yield section


def _clean_text(text):
    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines
    text_clean = '\n'.join(chunk for chunk in chunks if chunk)

    return text_clean


def _get_soup_text(html: str) -> BeautifulSoup:
    soup = BeautifulSoup(html, "html.parser")

    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()  # rip it out

    return soup


def _get_children_text(soup) -> list:
    # Goes over every tag.
    for child in soup.findChildren():
        text = child.get_text()
        # TODO clean up text

        text_clean = _clean_text(text)
        yield text_clean


def _split_contact_info(l_info_text: List[str],
                        country_code: str) -> ContactInfoSplit:
    """
    Split up contact info into email, telephone and opening hours.
    Args:
        l_ci_info:

    Returns:

    """

    contact_info_split = ContactInfoSplit()

    conn = ConnectorContactInfoClassification(CONTACT_CLASSIFICATION)

    for text in l_info_text:

        l_labels = conn._post_classify_contact_type(text,
                                                    country_code=country_code)

        if len(l_labels) == 0:
            warnings.warn(f"Could not find a type of contact info: {text}")

        for label in l_labels:
            if label.name == TypesContactInfo.EMAIL.name:
                contact_info_split.add_email(text)

            if label.name == TypesContactInfo.PHONE.name:
                contact_info_split.add_telephone(text)

            if label.name == TypesContactInfo.HOURS.name:
                contact_info_split.add_opening_hours(text)

            if label.name == TypesContactInfo.ADDRESS.name:
                contact_info_split.add_address(text)

    return contact_info_split
