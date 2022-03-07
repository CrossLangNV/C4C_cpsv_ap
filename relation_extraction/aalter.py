import re
from typing import List, Union

from bs4 import BeautifulSoup, Tag

from relation_extraction.cities import CityParser, Relations
from relation_extraction.utils import clean_text


class AalterParser(CityParser):
    """
    Parser for Aalter.be
    """

    def extract_relations(self, s_html) -> Relations:
        pass

    @staticmethod
    def parse_page(s_html) -> List[List[str]]:
        soup = BeautifulSoup(s_html, 'html.parser')

        def get_page_procedure(page_procedure_child, n_headers_min=2, n_headers_max=None):
            """
             Start from single element and go up untill multiple headers are returned.

            Args:
                page_procedure_child:
                n_headers_min: Minimum number of headers to retrieve before returning
                n_headers_max: Maximum number of headers to retrieve before returning

             """

            if n_headers_max is None:
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
                # TODO check that we don't go too much up. Use n_headers_max!
                return get_page_procedure(page_procedure)

            return page_procedure

        # Find the Title
        h_title = soup.find('h1')
        page_procedure = get_page_procedure(h_title)

        l = [[]]

        l_headers = get_all_headers(page_procedure)
        for header in l_headers:

            l_par = []

            # Header text
            text_header = header.get_text(separator=" ", strip=True)
            text_header = clean_text(text_header)
            l_par.append(text_header)

            # All following text.
            for sib in header.find_next_siblings():
                text = clean_text(sib.get_text(separator=" ", strip=True))
                if sib.name in ["div", "p"]:  # TODO <ul/> <li/> items
                    l_par.append(text)
                elif sib.name == "ul":

                    for li in sib.findChildren("li"):
                        text_li = clean_text(li.get_text(separator=" ", strip=True))

                        l_par.append(f"* {text_li}")

                if sib in l_headers:
                    break

            l.append(l_par)

        # Filter empty subs:
        l = list(filter(lambda l_sub: len(l_sub), l))

        return l


def get_all_headers(soup: Union[BeautifulSoup, Tag]) -> List[Tag]:
    return soup.find_all(re.compile('^h[1-6]$'))
