import re
from typing import List, Union

from bs4 import BeautifulSoup, Tag


def clean_text(text, remove_newlines=False):
    if remove_newlines:
        return " ".join([clean_text(line, remove_newlines=False) for line in text.splitlines()])

    text_clean = text.strip(" \n\r\xa0\t").replace("\xa0", " ")
    return text_clean


def get_all_headers(soup: Union[BeautifulSoup, Tag]) -> List[Tag]:
    return soup.find_all(re.compile('^h[1-6]$'))


def get_page_procedure(page_procedure_child: Tag,
                       n_headers_min=2,
                       n_headers_max=None,
                       get_all_headers=get_all_headers) -> Tag:
    """
    Start from single element and go up untill multiple headers are returned.

    Args:
        page_procedure_child:
        n_headers_min: Minimum number of headers to retrieve before returning
        n_headers_max: Maximum number of headers to retrieve before returning

    """

    if n_headers_max is None:
        soup = page_procedure_child.find_parents()[-1]
        n_headers_max = len(get_all_headers(soup))

    page_procedure = page_procedure_child.parent

    # Check that we can find other headers.
    headers = get_all_headers(page_procedure)

    n_headers = len(headers)
    if n_headers >= n_headers_min:
        return page_procedure

    elif n_headers >= n_headers_max:
        # Max number found
        return page_procedure

    else:
        # recursively go up
        return get_page_procedure(page_procedure,
                                  n_headers_min=n_headers_min,
                                  n_headers_max=n_headers_max,
                                  get_all_headers=get_all_headers)

    # Fall back, should never reach this.
    return page_procedure
