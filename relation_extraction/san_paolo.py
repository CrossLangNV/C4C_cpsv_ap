import re
from typing import List, Union

from bs4 import BeautifulSoup, Tag

from relation_extraction.aalter import AalterParser
from relation_extraction.cities import RegexCPSVAPRelationsClassifier
from relation_extraction.utils import clean_text, get_page_procedure


class SanPaoloCPSVAPRelationsClassifier(RegexCPSVAPRelationsClassifier):
    """
    San Paolo
    """

    def __init__(self,
                 # Ignore ":"
                 pattern_criterion_requirement=r"(?=x)(?!x)",  # TODO, not implemented
                 pattern_rule=r"(?=x)(?!x)",  # TODO, not implemented
                 pattern_evidence=r"moduli da compilare e documenti da allegare(.)*",  # with or without ?
                 pattern_cost=r"pagamenti(.)*"
                 ):
        super(SanPaoloCPSVAPRelationsClassifier, self).__init__(
            pattern_criterion_requirement=pattern_criterion_requirement,
            pattern_rule=pattern_rule,
            pattern_evidence=pattern_evidence,
            pattern_cost=pattern_cost
        )


class SanPaoloParser(AalterParser):
    """
    Parser for https://www.comune.sanpaolo.bs.it/
    """

    def __init__(self, classifier: SanPaoloCPSVAPRelationsClassifier = None):

        if classifier is None:
            # Default behaviour
            classifier = SanPaoloCPSVAPRelationsClassifier()

        super(SanPaoloParser, self).__init__(classifier=classifier)

    def parse_page(self, s_html) -> List[List[str]]:
        soup = BeautifulSoup(s_html, 'html.parser')

        # Find the Title
        h_title = soup.find_all('h1')[-1]
        page_procedure = get_page_procedure(h_title,
                                            get_all_headers=self.get_all_headers)

        l = [[]]

        l_headers = self.get_all_headers(page_procedure)
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

    def get_all_headers(self, soup: Union[BeautifulSoup, Tag]) -> List[Tag]:
        return soup.find_all(self._filter_header)

    def _filter_header(self, tag: Tag):
        if re.match(r'^h[1-6]$', tag.name) or self._filter_accordion_header(tag):
            return True

        return False

    @staticmethod
    def _filter_accordion_header(tag: Tag,
                                 ARG_CLASS="class",
                                 HEADER="header"
                                 ):
        """
        For San Paolo website and possibly most Italian websites, to work with these accordions.

        Args:
            tag:

        Returns:

        """

        # Get accordion header
        if tag.get(ARG_CLASS):
            for c in tag[ARG_CLASS]:
                if HEADER in c.lower():
                    return True