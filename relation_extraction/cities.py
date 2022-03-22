"""
For Belgium see:
 - https://data.vlaanderen.be/doc/applicatieprofiel/generiek-basis/
 - https://data.vlaanderen.be/doc/applicatieprofiel/dienstencataloog/
"""
import abc
import re
from typing import Generator, List, Optional, Tuple, Union

from bs4 import BeautifulSoup, Tag
from pydantic import BaseModel

from c4c_cpsv_ap.models import BusinessEvent, Event, LifeEvent
from relation_extraction.utils import clean_text


class Relations(BaseModel):
    criterionRequirement: Optional[str]
    rule: Optional[str]
    evidence: Optional[str]
    cost: Optional[str]

    # Event
    events: Optional[List[Event]]

    # life_event: Optional[List[Event]]
    # business_event: Optional[List[Event]]

    def get_events(self) -> List[Event]:
        return self.events

    def get_life_events(self) -> List[LifeEvent]:
        return [event for event in self.events if isinstance(event, LifeEvent)]

    def get_business_events(self) -> List[BusinessEvent]:
        return [event for event in self.events if isinstance(event, BusinessEvent)]


class CPSVAPRelationsClassifier(abc.ABC):

    @abc.abstractmethod
    def predict_criterion_requirement(self,
                                      title: str = None,
                                      paragraph: str = None) -> bool:
        """
        Predicts whether a paragraph is a criterion requirement.

        While paragraph information might not yet be used, we already this as an optional argument to be future proof.

        Args:
            title: The header, title or subtitle, corresponding to this paragraph.
            paragraph: The paragraph itself.

        Returns:
            Boolean: True if the paragraph contains criterion requirement info.
        """

        pass

    @abc.abstractmethod
    def predict_rule(self,
                     title: str = None,
                     paragraph: str = None) -> bool:
        """
        Predicts whether a paragraph is a rule.

        While paragraph information might not yet be used, we already this as an optional argument to be future proof.

        Args:
            title: The header, title or subtitle, corresponding to this paragraph.
            paragraph: The paragraph itself.

        Returns:
            Boolean: True if the paragraph contains rule info.
        """

        pass

    @abc.abstractmethod
    def predict_evidence(self,
                         title: str = None,
                         paragraph: str = None) -> bool:
        """
        Predicts whether a paragraph is an evidence.

        While paragraph information might not yet be used, we already this as an optional argument to be future proof.

        Args:
            title: The header, title or subtitle, corresponding to this paragraph.
            paragraph: The paragraph itself.

        Returns:
            Boolean: True if the paragraph contains evidence info.
        """

        pass

    @abc.abstractmethod
    def predict_cost(self,
                     title: str = None,
                     paragraph: str = None) -> bool:
        """
        Predicts whether a paragraph is a cost.

        While paragraph information might not yet be used, we already this as an optional argument to be future proof.

        Args:
            title: The header, title or subtitle, corresponding to this paragraph.
            paragraph: The paragraph itself.

        Returns:
            Boolean: True if the paragraph contains cost info.
        """

        pass


class RegexCPSVAPRelationsClassifier(CPSVAPRelationsClassifier):
    """
    Classify the headers based on Regular Expressions.
    """

    def __init__(self,
                 pattern_criterion_requirement: str,
                 pattern_rule: str,
                 pattern_evidence: str,
                 pattern_cost: str,
                 *args,
                 **kwargs):
        super(RegexCPSVAPRelationsClassifier, self).__init__(*args,
                                                             **kwargs)

        self.pattern_criterion_requirement = pattern_criterion_requirement
        self.pattern_rule = pattern_rule
        self.pattern_evidence = pattern_evidence
        self.pattern_cost = pattern_cost

    def predict_criterion_requirement(self,
                                      title: str = None,
                                      paragraph: str = None):
        return bool(re.match(self.pattern_criterion_requirement, title, re.IGNORECASE))

    def predict_rule(self,
                     title: str = None,
                     paragraph: str = None):
        return bool(re.match(self.pattern_rule, title, re.IGNORECASE))

    def predict_evidence(self,
                         title: str = None,
                         paragraph: str = None):
        return bool(re.match(self.pattern_evidence, title, re.IGNORECASE))

    def predict_cost(self,
                     title: str = None,
                     paragraph: str = None):
        return bool(re.match(self.pattern_cost, title, re.IGNORECASE))


class CityParser(abc.ABC):
    """
    Abstract class for city procedure parsers
    """

    @abc.abstractmethod
    def parse_page(self,
                   s_html: str,
                   include_sub: bool = True):
        """
        Converts a html page to paragraphs with their title.

        Args:
            s_html:
            include_sub (bool):
                Flag whether to include subsections as well.
                Only if possible/has header level info.

        Returns:

        """
        pass

    @abc.abstractmethod
    def extract_relations(self, s_html: str, url: str) -> Relations:
        """
        Extracts important CPSV-AP relations from a webpage containing an administrative procedure.

        Args:
            s_html: HTML as string
            url: original URL to the webpage

        Returns:
            extracted relations saved in Relations object.
        """
        pass

    def _paragraph_generator(self,
                             s_html,
                             include_sub: bool = True
                             ) -> Generator[Tuple[str, str], None, None]:
        """
        Generates the header-paragraph pairs out of the HTML.

        Args:
            s_html: HTML of page as string.

        Returns:
            generates (title, paragraph) pairs.
        """
        for l_sub in self.parse_page(s_html, include_sub=include_sub):
            title = l_sub[0]
            paragraphs = l_sub[1:]
            paragraphs_clean = "\n".join(filter(lambda s: s, paragraphs))

            yield title, paragraphs_clean


class ClassifierCityParser(CityParser):
    """
    Originally AalterParser
    """

    def __init__(self, classifier: CPSVAPRelationsClassifier, *args, **kwargs):
        super(ClassifierCityParser, self).__init__(*args, **kwargs)

        self.classifier = classifier

    def parse_page(self,
                   s_html,
                   include_sub: bool = True
                   ) -> List[List[str]]:
        """
        AKA Chunking

        Args:
            s_html:
            include_sub:

        Returns:

        """
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

    def extract_relations(self, s_html: str, url: str) -> Relations:
        """
        Extracts important CPSV-AP relations from a webpage containing an adminstrative procedure.

        Args:
            s_html: HTML as string
            url: original URL to the webpage

        Returns:
            extracted relations saved in Relations object.
        """

        d = Relations()

        for title, paragraph in self._paragraph_generator(s_html):

            if self.classifier.predict_criterion_requirement(title, paragraph):
                d.criterionRequirement = paragraph

            if self.classifier.predict_rule(title, paragraph):
                d.rule = paragraph

            if self.classifier.predict_evidence(title, paragraph):
                d.evidence = paragraph

            if self.classifier.predict_cost(title, paragraph):
                d.cost = paragraph

        return d

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
