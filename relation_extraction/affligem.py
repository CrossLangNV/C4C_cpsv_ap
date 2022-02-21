from typing import List

import bs4.element
from bs4 import BeautifulSoup

from relation_extraction.cities import CityParser, Relations


class AffligemParser(CityParser):
    """
    Parser for Affligem.be
    """

    criterionRequirement = "Voorwaarden"
    rule = "Procedure"
    evidence = "Wat meebrengen"
    cost = "Bedrag"

    # e = "Uitzonderingen"

    def parse_page(self, s_html) -> List[List[str]]:
        soup = BeautifulSoup(s_html, 'html.parser')

        def clean_text(text):
            return text.strip(" \n\r\xa0\t")

        def get_title(link: bs4.element.Tag):
            title = link.text

            title = clean_text(title)
            return title

        h1 = soup.find('h1')
        page_procedure = h1.parent

        l = [[]]

        for tag in page_procedure.find_all():

            text = clean_text(tag.text)
            if not text:
                continue

            if tag.name in ['h1', 'h2']:  # title
                l.append([text])

            else:
                l[-1].append(text)

        # Filter empty subs:
        l = list(filter(lambda l_sub: len(l_sub), l))

        return l

    def extract_relations(self, s_html) -> Relations:

        l = self.parse_page(s_html)

        d = Relations()

        for l_sub in l:
            title = l_sub[0]
            paragraphs = l_sub[1:]
            paragraphs_clean = "\n".join(filter(lambda s: s, paragraphs))

            if title == self.criterionRequirement:
                d.criterionRequirement = paragraphs_clean

            elif title == self.rule:
                d.rule = paragraphs_clean

            elif title == self.evidence:
                d.evidence = paragraphs_clean

            elif title == self.cost:
                d.cost = paragraphs_clean

        return d
