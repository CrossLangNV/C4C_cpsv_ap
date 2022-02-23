"""
For Belgium see:
 - https://data.vlaanderen.be/doc/applicatieprofiel/generiek-basis/
 - https://data.vlaanderen.be/doc/applicatieprofiel/dienstencataloog/
"""
import abc
import urllib.request
from typing import Optional

import chardet
from pydantic import BaseModel


class Relations(BaseModel):
    criterionRequirement: Optional[str]
    rule: Optional[str]
    evidence: Optional[str]
    cost: Optional[str]


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

    def url2html(self, url, filename=None):
        def get_encoding(rawdata):
            result = chardet.detect(rawdata)
            charenc = result['encoding']
            return charenc

        with urllib.request.urlopen(url) as fp:
            mybytes = fp.read()

            enc = get_encoding(mybytes)

            mystr = mybytes.decode(enc)

        if filename:
            with open(filename, "w", encoding="utf-8") as fp:
                fp.write(mystr)

        return mystr
