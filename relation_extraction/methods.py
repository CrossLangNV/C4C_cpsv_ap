from typing import Generator

from bs4 import BeautifulSoup


def get_public_service(html: str) -> str:
    """
    Returns the public service of an HTML

    We
    """
    # urllib2.urlopen("https://www.google.com")
    soup = BeautifulSoup(html, "html.parser")

    title = soup.title.string

    return title


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

    for text in  _get_children_text(soup):
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
