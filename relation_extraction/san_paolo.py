import re

from bs4 import Tag

from relation_extraction.aalter import AalterParser
from relation_extraction.cities import RegexCPSVAPRelationsClassifier


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

    def _filter_header(self, tag: Tag) -> bool:
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
