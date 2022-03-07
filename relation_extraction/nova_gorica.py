import re
from typing import List, Union

from bs4 import BeautifulSoup, Tag

from relation_extraction.cities import CityParser, Relations
from relation_extraction.utils import get_page_procedure


class NovaGoricaParser(CityParser):
    """
    Parser for https://www.nova-gorica.si/
    """

    def extract_relations(self, s_html) -> Relations:
        raise NotImplementedError()

    def parse_page(self, s_html) -> List[List[str]]:
        # TODO still has some issues, but is functional in it's current form.
        soup = BeautifulSoup(s_html, 'html.parser')

        # Find the Title
        h_title = soup.find_all('h1')[-1]
        page_procedure = get_page_procedure(h_title,
                                            get_all_headers=self.get_all_headers)

        l = [[]]

        filter_p_strong = lambda s: s.name in ["p", "strong", "a"]

        # Idea: regex parsing what is important.
        for p_tag in page_procedure.find_all(filter_p_strong):

            # has paragraph children, continue
            if p_tag.find_all("p"):
                continue

            text = p_tag.get_text(separator=" ", strip=True)

            if self._filter_header(p_tag):
                # New header + paragraph section
                l.append([text])

            elif p_tag.name == "p":
                l[-1].append(text)

        # Filter empty subs:
        l = list(filter(lambda l_sub: len(l_sub), l))

        return l

    def get_all_headers(self, soup: Union[BeautifulSoup, Tag]) -> List[Tag]:

        # TODO Also do something with accordion headers.

        return soup.find_all(self._filter_header)

    def _filter_header(self, tag: Tag):
        if re.match(r'^h[1-6]$', tag.name):
            return True

        # Bold title
        if tag.name == "strong":
            text = tag.get_text(separator=" ", strip=True)
            if re.match(r'^(.)+:$', text):
                return True

        return False

#     @staticmethod
#     def _filter_accordion_header(tag: Tag,
#                                  ARG_CLASS="class",
#                                  HEADER="header"
#                                  ):
#         """
#         For San Paolo website and possibly most Italian websites, to work with these accordions.
#
#         Args:
#             tag:
#
#         Returns:
#
#         """
#
#         # Get accordion header
#         if tag.get(ARG_CLASS):
#             for c in tag[ARG_CLASS]:
#                 if HEADER in c.lower():
#                     return True
