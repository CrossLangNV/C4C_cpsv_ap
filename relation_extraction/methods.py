import base64
import os
from typing import Generator, List, Tuple

import requests
from bs4 import BeautifulSoup
from cassis.typesystem import load_typesystem
from cassis.xmi import load_cas_from_xmi

from c4c_cpsv_ap.connector.hierarchy import Provider
from c4c_cpsv_ap.models import PublicService, PublicOrganisation, ContactPoint

TERM_EXTRACTION = os.environ["TERM_EXTRACTION"]
CONTACT_PARAGRAPH_TYPE = "de.tudarmstadt.ukp.dkpro.core.api.segmentation.type.ContactParagraph"
SOFA_ID = "html2textView"

MEDIA_ROOT = os.path.join(os.path.dirname(__file__), '../data')
with open(os.path.join(MEDIA_ROOT, 'typesystem.xml'), 'rb') as f:
    TYPESYSTEM = load_typesystem(f)


class RelationExtractor:
    def __init__(self, html, context):
        # Save data
        self.html = html
        self.context = context

        # Init provider
        self.provider = Provider()

        # Prefered label can most likely be extracted from the name of the service
        # within the contact information.
        self.public_org = PublicOrganisation(pref_label=f"TODO",  # TODO
                                             spatial=context)  # TODO
        self.provider.public_organisations.add(self.public_org, context=context)

    def extract_all(self):
        """
        TODO add more in the future
        """

        contact_info = self.extract_contact_info()

        self.extract_public_service(contact_info=contact_info)

    def extract_public_service(self,
                               contact_info: ContactPoint) -> PublicService:
        """
        Extract all public service information

        TODO
         * add the identifier extraction results
        """

        public_service = PublicService(name=get_public_service_name(self.html),
                                       description=get_public_service_description(self.html),
                                       identifier="#TODO",
                                       has_competent_authority=self.public_org,
                                       has_contact_point=contact_info
                                       )

        self.provider.public_services.add(public_service=public_service,
                                          context=self.context)

        return public_service

    def extract_contact_info(self) -> ContactPoint:
        l_info_text = get_contact_info_stuff(self.html)

        email, telephone, opening_hours = _split_contact_info(l_info_text)

        contact_info = ContactPoint(email=email,  # TODO
                                    telephone=telephone,  # TODO
                                    opening_hours=opening_hours  # TODO
                                    )

        return contact_info

    def extract_concepts(self):
        return

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
    Idea: We can find the section with the description based on
    XX is ... . This does mean that we have to know what XX is.

    Algorithm: the first paragraph <p/> is returned.

    TODO
     * Implement noun phrase extraction?
     * After noun-phrase extraction, Find section with description.
    """

    title = get_public_service_name(html)

    main_noun_phrase = None  # TODO

    soup = BeautifulSoup(html, "html.parser")
    first_paragraph = soup.findAll('p', text=True)[0]  # Paragraph

    text = first_paragraph.get_text()
    text_clean = _clean_text(text)

    return text_clean


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


def get_contact_info_stuff(html: str,
                           language: str = "en",

                           ) -> List[str]:
    """

    Args:
        html:
        language:

    Returns:
        List of contact info text.

    TODO
     * Rename method
    """

    j = {
        "html": html,
        "language": language
    }
    r = requests.post(TERM_EXTRACTION + "/extract_contact_info",
                      json=j)

    # print(r.json()["text"])

    def get_decoded_cas_content(cas_content: str):
        return base64.b64decode(cas_content).decode('utf-8')

    decoded_cas_content = get_decoded_cas_content(r.json()["cas_content"])

    cas = load_cas_from_xmi(decoded_cas_content,
                            typesystem=TYPESYSTEM,
                            trusted=True)

    l_contact_typesystem = cas.get_view(SOFA_ID).select(CONTACT_PARAGRAPH_TYPE)

    """
    [TYPESYSTEM.get_type(CONTACT_PARAGRAPH_TYPE)]
    l_contact_typesystem[0].content_context
    l_contact_typesystem[0].content
    """

    return list(set(map(lambda ts: ts.content, l_contact_typesystem)))


def get_concepts(html: str):
    return


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


def _split_contact_info(l_info_text: List[str]) -> Tuple[List[str], List[str], List[str]]:
    """
    Split up contact info into email, telephone and opening hours.
    Args:
        l_ci_info:

    Returns:

    """
    email = []
    telephone = []
    opening_hours = []

    def filter_func_opening_hours(text) -> bool:

        text_lower = text.lower()

        whitelist = [
            "week"
            "day",  # And all days: Monday, Tuesday...
            # Mon.Mo.
            # Tue.Tu.
            # Wed.We.
            # Thu.Th.
            # Fri.Fr.
            # Sat.Sa.
            # Sun.Su
        ]
        for day in whitelist:
            if day in text_lower:
                return True
        return False

    for text in l_info_text:

        # TODO Implement a proper classifier
        if "@" in text:
            # Filter unique
            if text not in email:
                email.append(text)

        elif filter_func_opening_hours(text):
            if text not in opening_hours:
                opening_hours.append(text)

        else:
            if text not in telephone:
                telephone.append(text)

    return email, telephone, opening_hours
