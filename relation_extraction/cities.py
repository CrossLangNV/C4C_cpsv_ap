"""
For Belgium see:
 - https://data.vlaanderen.be/doc/applicatieprofiel/generiek-basis/
 - https://data.vlaanderen.be/doc/applicatieprofiel/dienstencataloog/
"""
import abc
import re
from typing import List, Optional

from pydantic import BaseModel

from c4c_cpsv_ap.models import BusinessEvent, Event, LifeEvent


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

    def get_business_events(self) -> List[LifeEvent]:
        return [event for event in self.events if isinstance(event, BusinessEvent)]


class CityParser(abc.ABC):
    """
    Abstract class for city procedure parsers
    """

    @staticmethod
    @abc.abstractmethod
    def parse_page(s_html):
        """
        Converts a html page to paragraphs with their title.

        Args:
            s_html:

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
        return re.match(self.pattern_criterion_requirement, title, re.IGNORECASE)

    def predict_rule(self,
                     title: str = None,
                     paragraph: str = None):
        return re.match(self.pattern_rule, title, re.IGNORECASE)

    def predict_evidence(self,
                         title: str = None,
                         paragraph: str = None):
        return re.match(self.pattern_evidence, title, re.IGNORECASE)

    def predict_cost(self,
                     title: str = None,
                     paragraph: str = None):
        return re.match(self.pattern_cost, title, re.IGNORECASE)
