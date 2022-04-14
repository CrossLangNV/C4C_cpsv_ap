import re
from typing import List

from bs4 import BeautifulSoup, Tag

from relation_extraction.aalter import AalterParser
from relation_extraction.cities import RegexCPSVAPRelationsClassifier
from relation_extraction.html_parsing.parsers import Section
from relation_extraction.utils import clean_text


class NovaGoricaCPSVAPRelationsClassifier(RegexCPSVAPRelationsClassifier):
    """
    Nova Gorica
    """

    def __init__(self,
                 # Ignore ":"
                 pattern_criterion_requirement=r"obrazci(.)*",
                 pattern_rule=r"opis postopka(.)*",
                 pattern_evidence=r"zahtevane priloge(.)*",
                 pattern_cost=r"taksa(.)*",
                 ):
        super(NovaGoricaCPSVAPRelationsClassifier, self).__init__(
            pattern_criterion_requirement=pattern_criterion_requirement,
            pattern_rule=pattern_rule,
            pattern_evidence=pattern_evidence,
            pattern_cost=pattern_cost
        )


class NovaGoricaParser(AalterParser):  # CityParser
    """
    Parser for https://www.nova-gorica.si/
    """

    def __init__(self, classifier: NovaGoricaCPSVAPRelationsClassifier = None):

        if classifier is None:
            # Default behaviour
            classifier = NovaGoricaCPSVAPRelationsClassifier()

        super(NovaGoricaParser, self).__init__(classifier=classifier)

    def parse_page(self,
                   s_html,
                   include_sub: bool = True
                   ) -> List[Section]:
        soup = BeautifulSoup(s_html, 'html.parser')

        # Find the Title
        h_title = soup.find_all('h1')[-1]
        page_procedure = self._get_page_procedure(h_title)

        def get_text_within_tag(tag, header, next_header) -> str:
            text_tag = clean_text(tag.get_text(separator=" ", strip=True))

            text_header = header.get_text(separator=" ", strip=True)

            # Remove header text.
            text_tag = text_tag.split(text_header, 1)[-1]

            if next_header is not None:
                text_next_header = next_header.get_text(separator=" ", strip=True)
                text_tag = text_tag.rsplit(text_next_header, 1)[0]

            return text_tag.strip()  # Cleaning

        filter_text_tags = lambda s: s.name in ["div", "p", "strong", "a", "li"]

        l = []

        l_headers = self._get_all_headers(page_procedure)
        for i_header, header in enumerate(l_headers):

            l_par = []

            # Header text
            text_header = header.get_text(separator=" ", strip=True)
            text_header = clean_text(text_header)
            l_par.append(text_header)

            next_header = l_headers[i_header + 1] if i_header < len(l_headers) - 1 else None
            l_skip = []

            # -- Find paragraph text. --

            # Special case check
            if 1:
                # Check if contained in text

                tag = header.parent

                l_text_within_parent = list(
                    filter(lambda s: s,
                           map(lambda s: str(s).strip(), tag.findAll(text=True, recursive=False))))

                if l_text_within_parent:
                    text_tag = get_text_within_tag(tag, header, next_header)

                    if tag.name == "li":
                        text_tag = f"* {text_tag}"

                    l_skip.extend(tag.find_all())
                    l_par.append(text_tag)

            for tag in header.find_all_next(filter_text_tags):

                # Stay within page_procedure.
                if tag not in page_procedure.find_all():
                    # Out of bounds.
                    break

                if tag in l_headers:
                    # Found next header.
                    break

                if tag in l_skip:
                    continue

                text_tag = clean_text(tag.get_text(separator=" ", strip=True),
                                      remove_newlines=True)
                if tag.name == "li":
                    text_tag = f"* {text_tag}"

                # Check if next header in children
                if next_header in tag.find_all():
                    l_text_within_tag = list(
                        filter(lambda s: s, map(lambda s: str(s).strip(), tag.findAll(text=True, recursive=False))))

                    if not l_text_within_tag:
                        continue

                    text_tag = get_text_within_tag(tag, header, next_header)
                    if tag.name == "li":
                        text_tag = f"* {text_tag}"

                    l_skip.extend(tag.find_all())
                    l_par.append(text_tag)  # Extra cleaning.

                    break

                else:
                    l_skip.extend(tag.find_all())
                    l_par.append(text_tag)

            # Clean l_par
            l_par = list(filter(lambda s: s, l_par))
            l.append(l_par)

        # Filter empty subs:
        l = list(filter(lambda l_sub: len(l_sub), l))

        # Convert to sections
        l = [Section(l_sub[0], l_sub[1:]) for l_sub in l]

        return l

    def _filter_header(self, tag: Tag):

        if super(NovaGoricaParser, self)._filter_header(tag):
            return True

        # TODO Also do something with accordion headers.

        # Bold title and ":" at the end
        if tag.name == "strong":
            text = tag.get_text(separator=" ", strip=True)
            if re.match(r'^(.)+:$', text):
                return True

        return False
