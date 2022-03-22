import re
from typing import List, Union

from bs4 import BeautifulSoup, Tag

from relation_extraction.cities import ClassifierCityParser, RegexCPSVAPRelationsClassifier
from relation_extraction.utils import clean_text


class AalterCPSVAPRelationsClassifier(RegexCPSVAPRelationsClassifier):
    """
    For https://www.aalter.be/
    """

    def __init__(self,
                 pattern_criterion_requirement=r"voorwaarden(.)*",
                 pattern_rule=r"hoe(.)*",
                 pattern_evidence=r"wat meebrengen(.)*",  # with or without ?
                 pattern_cost=r"prijs(.)*",
                 ):
        super(AalterCPSVAPRelationsClassifier, self).__init__(
            pattern_criterion_requirement=pattern_criterion_requirement,
            pattern_rule=pattern_rule,
            pattern_evidence=pattern_evidence,
            pattern_cost=pattern_cost
        )


class AalterParser(ClassifierCityParser):
    """
    Parser for Aalter.be
    """

    def __init__(self, classifier: AalterCPSVAPRelationsClassifier = None):
        if classifier is None:
            # Default behaviour
            classifier = AalterCPSVAPRelationsClassifier()

        super(AalterParser, self).__init__(classifier)

    def parse_page(self,
                   s_html,
                   include_sub: bool = True
                   ) -> List[List[str]]:
        soup = BeautifulSoup(s_html, 'html.parser')

        # Find the Title
        h_title = soup.find_all('h1')[-1]
        page_procedure = self._get_page_procedure(h_title)

        l = [[]]

        l_headers = self._get_all_headers(page_procedure)
        for header in l_headers:

            l_par = []

            # Header text
            text_header = header.get_text(separator=" ", strip=True)
            text_header = clean_text(text_header, remove_newlines=True)
            l_par.append(text_header)

            # All following text.
            for sib in header.find_next_siblings():
                text = clean_text(sib.get_text(separator=" ", strip=True), remove_newlines=True)
                if sib.name in ["div", "p", "a"]:
                    l_par.append(text)
                elif sib.name == "li":
                    l_par.append(f"* {text}")
                elif sib.name == "ul":
                    for li in sib.findChildren("li"):
                        text_li = clean_text(li.get_text(separator=" ", strip=True), remove_newlines=True)

                        l_par.append(f"* {text_li}")

                if sib in l_headers:
                    # Only return if sib header is of same depth or higher
                    if not include_sub:
                        # No need to check.
                        break

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
                    elif depth_sib <= depth_header:
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
            n_headers_max = len(self._get_all_headers(soup))

        page_procedure = page_procedure_child.parent

        # Check that we can find other headers.
        headers = self._get_all_headers(page_procedure)

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

    def _get_all_headers(self, soup: Union[BeautifulSoup, Tag]) -> List[Tag]:
        return soup.find_all(self._filter_header)

    def _filter_header(self, tag: Tag) -> bool:
        if re.match(r'^h[1-6]$', tag.name):
            return True

        return False
