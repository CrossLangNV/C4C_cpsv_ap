from relation_extraction.aalter import AalterParser
from relation_extraction.cities import RegexCPSVAPRelationsClassifier


class ZagrebCPSVAPRelationsClassifier(RegexCPSVAPRelationsClassifier):
    """
    Austrheim
    """

    def __init__(self,
                 pattern_criterion_requirement=r"(?=x)(?!x)",  # TODO NOT IMPLEMENTED YET
                 pattern_rule=r"(?=x)(?!x)",  # TODO NOT IMPLEMENTED YET
                 pattern_evidence=r"(?=x)(?!x)",  # TODO NOT IMPLEMENTED YET
                 pattern_cost=r"(?=x)(?!x)",  # TODO NOT IMPLEMENTED YET
                 ):
        super(ZagrebCPSVAPRelationsClassifier, self).__init__(
            pattern_criterion_requirement=pattern_criterion_requirement,
            pattern_rule=pattern_rule,
            pattern_evidence=pattern_evidence,
            pattern_cost=pattern_cost
        )


class ZagrebParser(AalterParser):  # CityParser
    """
    Parser for Zagreb
    """

    def __init__(self, classifier: ZagrebCPSVAPRelationsClassifier = None):
        if classifier is None:
            # Default behaviour
            classifier = ZagrebCPSVAPRelationsClassifier()

        super(ZagrebParser, self).__init__(classifier=classifier)
