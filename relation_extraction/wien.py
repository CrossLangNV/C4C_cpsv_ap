from relation_extraction.aalter import AalterParser
from relation_extraction.cities import RegexCPSVAPRelationsClassifier


class WienCPSVAPRelationsClassifier(RegexCPSVAPRelationsClassifier):
    """
    San Paolo
    """

    def __init__(self,
                 pattern_criterion_requirement=r"voraussetzungen(.)*",
                 pattern_rule=r"allgemeine informationen(.)*",
                 pattern_evidence=r"erforderliche unterlagen(.)*",
                 pattern_cost=r"kosten(.)*",
                 ):
        super(WienCPSVAPRelationsClassifier, self).__init__(
            pattern_criterion_requirement=pattern_criterion_requirement,
            pattern_rule=pattern_rule,
            pattern_evidence=pattern_evidence,
            pattern_cost=pattern_cost
        )


class WienParser(AalterParser):
    """
    Use AalterParser or AffligemParser
    """

    criterionRequirement = r"voraussetzungen(.)*"
    rule = r"allgemeine informationen(.)*"
    evidence = r"erforderliche unterlagen(.)*"
    cost = r"kosten(.)*"

    def __init__(self, classifier: WienCPSVAPRelationsClassifier = None):
        if classifier is None:
            # Default behaviour
            classifier = WienCPSVAPRelationsClassifier()

        super(WienParser, self).__init__(classifier=classifier)
