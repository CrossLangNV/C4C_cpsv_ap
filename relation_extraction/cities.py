"""
For Belgium see:
 - https://data.vlaanderen.be/doc/applicatieprofiel/generiek-basis/
 - https://data.vlaanderen.be/doc/applicatieprofiel/dienstencataloog/
"""
import abc
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
