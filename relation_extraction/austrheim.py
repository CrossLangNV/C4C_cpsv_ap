from typing import List

from bs4 import BeautifulSoup

from relation_extraction.cities import CityParser, Relations
from relation_extraction.utils import clean_text, get_all_headers, get_page_procedure


class AustrheimParser(CityParser):
    """
    Parser for https://www.comune.sanpaolo.bs.it/
    """

    criterionRequirement = "Krav til søkjar"
    rule = "Kva skjer vidare?"
    evidence = "NOT IMPLEMENTED YET"
    cost = "Kva kostar det?"

    def extract_relations(self, s_html: str, url: str) -> Relations:
        """

        Args:
            s_html:
            url:

        Returns:

        """
        l = self.parse_page(s_html)

        d = Relations()

        # TODO implement events extraction
        # events = list(self.extract_event(s_html, url))
        # d.events = events

        for l_sub in l:
            title = l_sub[0]
            paragraphs = l_sub[1:]
            paragraphs_clean = "\n".join(filter(lambda s: s, paragraphs))

            if title == self.criterionRequirement:
                d.criterionRequirement = paragraphs_clean

            elif title == self.rule:
                d.rule = paragraphs_clean

            elif title == self.cost:
                d.cost = paragraphs_clean

        return d

    def parse_page(self, s_html) -> List[List[str]]:
        soup = BeautifulSoup(s_html, 'html.parser')

        # Find the Title
        h_title = soup.find_all('h1')[-1]
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
                if sib.name in ["div", "p", "a"]:
                    l_par.append(text)
                elif sib.name == "li":
                    l_par.append(f"* {text}")
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
