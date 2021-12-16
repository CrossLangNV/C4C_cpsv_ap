from typing import Generator

from bs4 import BeautifulSoup

from c4c_cpsv_ap.connector.hierarchy import Provider
from c4c_cpsv_ap.models import PublicService, PublicOrganisation


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

    def extract_public_service(self):
        """
        Extract all public service information

        TODO
         * add the description extraction results
         * add the identifier extraction results
        """

        public_service = PublicService(name=get_public_service_name(self.html),
                                       description="#TODO",
                                       identifier="#TODO",
                                       has_competent_authority=self.public_org
                                       )

        self.provider.public_services.add(public_service=public_service,
                                          context=self.context)

    def export(self):
        """
        Export to RDF
        """

        print(self.provider.graph.serialize())


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


def get_public_service_description(html):
    """
    Idea: We can find the section with the description based on
    XX is ... . This does mean that we have to know what XX is.

    TODO
     * Implement noun phrase extraction?
     * After noun-phrase extraction, Find section with description.
    """

    title = get_public_service_name(html)

    main_noun_phrase = None  # TODO

    return


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
