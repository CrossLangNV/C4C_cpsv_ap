"""
For Belgium see:
 - https://data.vlaanderen.be/doc/applicatieprofiel/generiek-basis/
 - https://data.vlaanderen.be/doc/applicatieprofiel/dienstencataloog/
"""
import abc
from typing import Optional

from pydantic import BaseModel


class Relations(BaseModel):
    criterionRequirement: Optional[str]
    rule: Optional[str]
    evidence: Optional[str]
    cost: Optional[str]

    # Event
    life_event: Optional[str]
    business_event: Optional[str]

    def get_life_event(self):
        return self.life_event

    def get_business_event(self):
        return self.business_event


class CityParser(abc.ABC):
    """
    Abstract class for city procedure parsers
    """

    @abc.abstractmethod
    def parse_page(self, s_html):
        """
        Converts a html page to paragraphs with their title.

        Args:
            s_html:

        Returns:

        """
        pass

    @abc.abstractmethod
    def extract_relations(self, s_html) -> Relations:
        pass


