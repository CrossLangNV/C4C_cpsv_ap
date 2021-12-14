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


def foo(html: str) -> str:
    """
    Extracts the x

    TODO
     * In the future we might add an annotation to the HTML.
    """
    # Get a pyramid with the tags. Return the part which is most likely.

    return
