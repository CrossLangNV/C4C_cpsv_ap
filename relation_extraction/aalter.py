import re
from typing import Generator, List, Tuple, Union

from bs4 import BeautifulSoup, Tag

from relation_extraction.cities import CityParser, Relations
from relation_extraction.utils import clean_text


class AalterParser(CityParser):
    """
    Parser for Aalter.be
    """

    criterionRequirement = r"voorwaarden(.)*"
    rule = r"hoe(.)*"
    evidence = r"wat meebrengen(.)*"  # with or without ?
    cost = r"prijs(.)*"

    def extract_relations(self, s_html: str, url: str) -> Relations:
        """
        (Copied from super method)
        Extracts important CPSV-AP relations from a webpage containing an adminstrative procedure.

        Args:
            s_html: HTML as string
            url: original URL to the webpage

        Returns:
            extracted relations saved in Relations object.
        """

        d = Relations()

        for title, paragraph in self._paragraph_generator(s_html):

            if re.match(self.criterionRequirement, title, re.IGNORECASE):
                d.criterionRequirement = paragraph

            if re.match(self.rule, title, re.IGNORECASE):
                d.rule = paragraph

            if re.match(self.evidence, title, re.IGNORECASE):
                d.evidence = paragraph

            if re.match(self.cost, title, re.IGNORECASE):
                d.cost = paragraph

        return d

    def parse_page(self, s_html) -> List[List[str]]:
        soup = BeautifulSoup(s_html, 'html.parser')

        # Find the Title
        h_title = soup.find('h1')
        page_procedure = self._get_page_procedure(h_title)

        l = [[]]

        l_headers = get_all_headers(page_procedure)
        for header in l_headers:

            l_par = []

            # Header text
            text_header = header.get_text(separator=" ", strip=True)
            text_header = clean_text(text_header, remove_newlines=True)
            l_par.append(text_header)

            # All following text.
            for sib in header.find_next_siblings():
                text = clean_text(sib.get_text(separator=" ", strip=True), remove_newlines=True)
                if sib.name in ["div", "p"]:  # TODO <ul/> <li/> items
                    l_par.append(text)
                elif sib.name == "ul":

                    for li in sib.findChildren("li"):
                        text_li = clean_text(li.get_text(separator=" ", strip=True), remove_newlines=True)

                        l_par.append(f"* {text_li}")

                if sib in l_headers:
                    # Only return if sib header is of same depth or higher

                    # Depth
                    def get_depth(tag: Tag) -> Union[int, None]:
                        name = tag.name
                        match = re.match(r"h([0-9]+)", name, re.IGNORECASE)
                        if match:
                            depth = int(match.groups()[0])
                            return depth

                    depth_header = get_depth(header)
                    depth_sib = get_depth(sib)
                    if (depth_header is None) or (depth_sib is None):
                        # No depth information, just break.
                        break
                    if depth_sib <= depth_header:
                        # Equal or higher level header. Thus break
                        break

                    # Else
                    l_par.append(text)

            l.append(l_par)

        # Filter empty subs:
        l = list(filter(lambda l_sub: len(l_sub), l))

        return l

    def _get_page_procedure(self, page_procedure_child, n_headers_min=2, n_headers_max=None):
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

        # recursively go up
        return self._get_page_procedure(page_procedure,
                                        n_headers_min=n_headers_min,
                                        n_headers_max=n_headers_max)

    def _paragraph_generator(self, s_html) -> Generator[Tuple[str, str], None, None]:
        """
        Generates the header-paragraph pairs out of the HTML.

        Args:
            s_html: HTML of page as string.

        Returns:
            generates (title, paragraph) pairs.
        """
        for l_sub in self.parse_page(s_html):
            title = l_sub[0]
            paragraphs = l_sub[1:]
            paragraphs_clean = "\n".join(filter(lambda s: s, paragraphs))

            yield title, paragraphs_clean


def get_all_headers(soup: Union[BeautifulSoup, Tag]) -> List[Tag]:
    return soup.find_all(re.compile('^h[1-6]$'))
